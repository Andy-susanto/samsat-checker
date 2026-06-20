"""
Samsat API Client - Handle query ke berbagai backend API samsat
Mendukung: Modern API, Legacy PHP, Web Scraping
"""

import json
import time
import re
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Try imports
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[!] Module 'requests' tidak terinstall. Install: pip install requests")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# Load .env if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SamsatAPI:
    """Main API client untuk query data samsat"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.api_keys = {}
        self._load_api_keys()

        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            })
        else:
            self.session = None

    def _load_api_keys(self):
        """Load API keys from .env file"""
        # Jambi API key
        key = os.getenv('SAMSAT_JAMBI_KEY') or os.getenv('API_KEY_JAMBI')
        if key:
            self.api_keys['BH'] = key

    def query(self, nopol: str, province: dict) -> dict:
        """Main query method - routes to appropriate backend"""
        if not self.session:
            return {
                'success': False,
                'error': 'Module requests tidak terinstall. Jalankan: pip install requests',
                'method': 'none'
            }

        kode = nopol[:2] if len(nopol) > 2 and nopol[:1].isalpha() else nopol[:1]
        api_url = province.get('api_url')
        method = province.get('method')

        if self.verbose:
            print(f"  [DEBUG] Kode: {kode}, API: {api_url}, Method: {method}")
            print(f"  [DEBUG] API Keys loaded: {list(self.api_keys.keys())}")

        # Route based on province method
        if kode == 'BH':
            # Jambi - try multiple methods
            return self._query_jambi(nopol)
        elif method == 'web_scrape':
            return self._query_web_scrape(nopol, province)
        elif api_url and province.get('api_status') == 'READY':
            return self._query_api_key(nopol, api_url)
        else:
            return self._query_fallback(nopol, province)

    def _query_jambi(self, nopol: str) -> dict:
        """Query Jambi using multiple methods and combine results"""
        api_url = "https://api-pkb.jambisamsat.net/api"
        
        api_data = {}
        legacy_data = {}
        
        # Step 1: Get token from frontend (always try first)
        token = self._get_jambi_token()
        
        # Step 2: Query Modern API (more detailed vehicle data)
        if token:
            result = self._query_jambi_api(nopol, api_url, token)
            if result.get('success'):
                api_data = result.get('data', {})
                if self.verbose:
                    print(f"  [DEBUG] API data keys: {list(api_data.keys())}")
        
        # Step 3: Query Legacy PHP (for owner/address)
        result = self._query_jambi_legacy(nopol)
        if result.get('success'):
            legacy_data = result.get('data', {})
            if self.verbose:
                print(f"  [DEBUG] Legacy data keys: {list(legacy_data.keys())}")
        
        # Step 4: Merge results (API data is more complete, legacy has owner)
        if api_data or legacy_data:
            merged = self._merge_jambi_results(api_data, legacy_data)
            return {
                'success': True,
                'data': merged,
                'method': 'jambi_combined'
            }
        
        # All methods failed
        return {
            'success': False,
            'error': 'Semua metode query gagal. Pastikan nopol benar.',
            'method': 'all_failed'
        }

    def _get_jambi_token(self) -> str:
        """Get API token from frontend page"""
        try:
            r = self.session.get('https://www.jambisamsat.net/service/cek-pkb/', timeout=15)
            if r.status_code == 200:
                token_match = re.search(r"API_TOKEN\s*=\s*['\"]([^'\"]+)['\"]", r.text)
                if token_match:
                    token = token_match.group(1)
                    if self.verbose:
                        print(f"  [DEBUG] Token extracted from frontend")
                    return token
        except Exception as e:
            if self.verbose:
                print(f"  [DEBUG] Token extraction error: {e}")
        return None

    def _merge_jambi_results(self, api_data: dict, legacy_data: dict) -> dict:
        """Merge API and legacy data into unified format"""
        merged = {
            'wilayah': 'Jambi',
            'api_source': 'api-pkb.jambisamsat.net + jambisamsat.net (legacy)'
        }
        
        # From API (more complete vehicle data)
        if api_data:
            merged.update({
                'nopol': api_data.get('nopol', ''),
                'merek': api_data.get('merek', ''),
                'model': api_data.get('model', ''),
                'jenis': api_data.get('jenis', ''),
                'tahun': api_data.get('tahun', ''),
                'warna': api_data.get('warna', ''),
                'cc': api_data.get('cc', ''),
                'bbm': api_data.get('bbm', ''),
                'njkb': api_data.get('njkb', ''),
                'lokasi': api_data.get('lokasi', ''),
                'tgl_akhir_pkb': api_data.get('tgl_akhir_pkb', ''),
                'tgl_akhir_stnk': api_data.get('tgl_akhir_stnk', ''),
            })
        
        # From Legacy (owner/address data - only from legacy)
        if legacy_data:
            if legacy_data.get('nama_pemilik'):
                merged['nama_pemilik'] = legacy_data['nama_pemilik']
            if legacy_data.get('alamat'):
                merged['alamat'] = legacy_data['alamat']
            # Fill in missing data from legacy
            if not merged.get('model') and legacy_data.get('model'):
                merged['model'] = legacy_data['model']
            if not merged.get('jenis') and legacy_data.get('jenis'):
                merged['jenis'] = legacy_data['jenis']
            if not merged.get('tahun') and legacy_data.get('tahun'):
                merged['tahun'] = legacy_data['tahun']
            if not merged.get('warna') and legacy_data.get('warna'):
                merged['warna'] = legacy_data['warna']
            if not merged.get('cc') and legacy_data.get('cc'):
                merged['cc'] = legacy_data['cc']
            if not merged.get('tgl_akhir_pkb') and legacy_data.get('tgl_akhir_pkb'):
                merged['tgl_akhir_pkb'] = legacy_data['tgl_akhir_pkb']
        
        return merged

    def _query_jambi_api(self, nopol: str, api_url: str, api_key: str) -> dict:
        """Query Jambi via modern API with authentication"""
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        endpoints = [
            ('/kendaraan/detail', 'kendaraan'),
            ('/pajak/detail', 'pajak'),
            ('/jr/detail', 'jasa_raharja'),
            ('/kendaraan/pnbp', 'pnbp'),
        ]

        results = {}
        for endpoint, key in endpoints:
            url = f"{api_url}{endpoint}"
            try:
                r = self.session.get(url, headers=headers, params={'nopol': nopol}, timeout=15)
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if data.get('status') or data.get('data'):
                            results[key] = data
                            if self.verbose:
                                print(f"  [DEBUG] {endpoint}: OK")
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                if self.verbose:
                    print(f"  [DEBUG] {endpoint} error: {e}")

        if results:
            return {
                'success': True,
                'data': self._merge_jambi_data(results),
                'method': 'jambi_api'
            }

        return {'success': False, 'error': 'API key tidak valid', 'method': 'jambi_api'}

    def _try_api_without_auth(self, nopol: str, api_url: str) -> dict:
        """Try API without authentication"""
        url = f"{api_url}/kendaraan/detail"
        try:
            r = self.session.get(url, params={'nopol': nopol}, timeout=15)
            if r.status_code == 200:
                try:
                    data = r.json()
                    if data.get('status') or data.get('data'):
                        return {
                            'success': True,
                            'data': {'kendaraan': data},
                            'method': 'api_no_auth'
                        }
                except json.JSONDecodeError:
                    pass

            # Check error
            try:
                err = r.json()
                msg = str(err.get('message', ''))
                if 'API Key' in msg or 'key' in msg.lower():
                    if self.verbose:
                        print(f"  [DEBUG] API requires auth: {msg}")
            except Exception:
                pass

        except Exception as e:
            if self.verbose:
                print(f"  [DEBUG] No-auth error: {e}")

        return {'success': False, 'error': 'API memerlukan autentikasi', 'method': 'api_no_auth'}

    def _query_jambi_legacy(self, nopol: str) -> dict:
        """Query Jambi via legacy PHP endpoints"""
        if not HAS_BS4:
            return {
                'success': False,
                'error': 'Module beautifulsoup4 tidak terinstall',
                'method': 'jambi_legacy'
            }

        base_url = "https://www.jambisamsat.net"

        # Try infokb.php (vehicle info)
        try:
            r = self.session.post(
                f"{base_url}/infokb.php",
                data={'no_polisi': nopol, 'nm_pemilik': ''},
                timeout=15
            )

            if r.status_code == 200 and 'DATA TIDAK ADA' not in r.text:
                soup = BeautifulSoup(r.text, 'html.parser')
                data = self._parse_html_table(soup, nopol)

                # Extract owner data from HTML comments
                owner_data = self._extract_commented_data(r.text)
                if owner_data:
                    data.update(owner_data)

                if data and (data.get('merek') or data.get('model')):
                    return {
                        'success': True,
                        'data': data,
                        'method': 'jambi_legacy'
                    }

        except Exception as e:
            if self.verbose:
                print(f"  [DEBUG] Legacy PHP error: {e}")

        return {'success': False, 'error': 'Legacy PHP tidak mengembalikan data', 'method': 'jambi_legacy'}

    def _query_jambi_frontend(self, nopol: str) -> dict:
        """Query Jambi via frontend web scrape"""
        if not HAS_BS4:
            return {
                'success': False,
                'error': 'Module beautifulsoup4 tidak terinstall',
                'method': 'jambi_frontend'
            }

        # Try to scrape the frontend page
        try:
            url = f"https://www.jambisamsat.net/service/cek-pkb/"
            r = self.session.get(url, timeout=15)

            if r.status_code == 200:
                # The frontend uses JavaScript to query API
                # We can't easily scrape it without a browser
                # But we can try to extract any embedded data
                soup = BeautifulSoup(r.text, 'html.parser')

                # Check for any data in the page
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'API_TOKEN' in str(script.string):
                        # Found token reference
                        if self.verbose:
                            print(f"  [DEBUG] Found API_TOKEN reference in frontend")
                        # Extract token (if visible)
                        token_match = re.search(r"API_TOKEN\s*=\s*['\"]([^'\"]+)['\"]", str(script.string))
                        if token_match:
                            token = token_match.group(1)
                            if token and len(token) > 10:
                                # Found a real token
                                self.api_keys['BH'] = token
                                return self._query_jambi_api(
                                    nopol,
                                    "https://api-pkb.jambisamsat.net/api",
                                    token
                                )

        except Exception as e:
            if self.verbose:
                print(f"  [DEBUG] Frontend scrape error: {e}")

        return {'success': False, 'error': 'Frontend scrape tidak berhasil', 'method': 'jambi_frontend'}

    def _parse_html_table(self, soup: 'BeautifulSoup', nopol: str) -> dict:
        """Parse HTML table from legacy PHP response"""
        data = {'nopol': nopol, 'wilayah': 'Jambi', 'api_source': 'jambisamsat.net (legacy)'}

        # Find tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                # Handle 3-column layout: label : value
                if len(cells) >= 3:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[2].get_text(strip=True)
                elif len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                else:
                    continue

                if not key or not value or key == ':':
                    continue

                # Map keys
                if any(k in key for k in ['merek', 'brand']):
                    data['merek'] = value
                elif any(k in key for k in ['model', 'tipe']):
                    data['model'] = value
                elif any(k in key for k in ['jenis']):
                    data['jenis'] = value
                elif any(k in key for k in ['tahun', 'year', 'rakitan']):
                    data['tahun'] = value
                elif any(k in key for k in ['warna', 'color']):
                    data['warna'] = value
                elif any(k in key for k in ['cc']):
                    data['cc'] = value
                elif any(k in key for k in ['bayar']):
                    data['tgl_bayar'] = value
                elif any(k in key for k in ['lokasi bayar']):
                    data['lokasi_bayar'] = value
                elif any(k in key for k in ['akhir pkb', 'tgl. akhir pkb']):
                    data['tgl_akhir_pkb'] = value
                elif any(k in key for k in ['akhir stnk', 'tgl. akhir stnk']):
                    data['tgl_akhir_stnk'] = value

        return data

    def _query_api_key(self, nopol: str, api_url: str) -> dict:
        """Query generic API with key"""
        # Try without auth first
        return self._try_api_without_auth(nopol, api_url)

    def _query_web_scrape(self, nopol: str, province: dict) -> dict:
        """Query via web scraping"""
        if not HAS_BS4:
            return {
                'success': False,
                'error': 'Module beautifulsoup4 tidak terinstall',
                'method': 'web_scrape'
            }

        # Try known web endpoints
        kode = nopol[:2] if len(nopol) > 2 and nopol[:1].isalpha() else nopol[:1]
        province_name = province.get('name', '').lower()

        # Build possible URLs based on province
        web_urls = []

        if 'jakarta' in province_name:
            web_urls = [
                "https://e-samsat.jakarta.go.id/",
                "https://samsat.jakarta.go.id/",
            ]
        elif 'jawa tengah' in province_name:
            web_urls = [
                "https://samsat.jatengprov.go.id/",
                "https://esamsat.jatengprov.go.id/",
            ]
        elif 'jawa barat' in province_name:
            web_urls = [
                "https://samsat.jabarprov.go.id/",
                "https://esamsat.jabarprov.go.id/",
            ]
        elif 'jawa timur' in province_name:
            web_urls = [
                "https://samsat.jatimprov.go.id/",
                "https://esamsat.jatimprov.go.id/",
            ]
        elif 'banten' in province_name:
            web_urls = [
                "https://samsat.bantenprov.go.id/",
                "https://esamsat.bantenprov.go.id/",
            ]
        elif 'bali' in province_name:
            web_urls = [
                "https://samsat.baliprov.go.id/",
                "https://esamsat.baliprov.go.id/",
            ]

        for url in web_urls:
            try:
                r = self.session.get(url, timeout=10, allow_redirects=True)
                if r.status_code == 200 and len(r.text) > 500:
                    # Try to find API endpoints in the page
                    soup = BeautifulSoup(r.text, 'html.parser')
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            # Look for API URLs
                            api_matches = re.findall(r'(https?://[^"\']+api[^"\']+)', str(script.string))
                            for api_url_found in api_matches:
                                if self.verbose:
                                    print(f"  [DEBUG] Found API URL: {api_url_found}")
                                # Try this API
                                result = self._try_web_api(nopol, api_url_found)
                                if result.get('success'):
                                    return result

            except Exception as e:
                if self.verbose:
                    print(f"  [DEBUG] Web scrape error {url}: {e}")

        return {
            'success': False,
            'error': f'Web scraping belum tersedia untuk {province["name"]}',
            'method': 'web_scrape'
        }

    def _try_web_api(self, nopol: str, api_url: str) -> dict:
        """Try a discovered web API"""
        try:
            # Try common API patterns
            endpoints = [
                f"{api_url}?nopol={nopol}",
                f"{api_url}/detail?nopol={nopol}",
                f"{api_url}/cek?nopol={nopol}",
            ]

            for url in endpoints:
                try:
                    r = self.session.get(url, timeout=10)
                    if r.status_code == 200:
                        try:
                            data = r.json()
                            if data.get('success') or data.get('data'):
                                return {
                                    'success': True,
                                    'data': data,
                                    'method': 'web_api'
                                }
                        except json.JSONDecodeError:
                            pass
                except Exception:
                    continue

        except Exception as e:
            if self.verbose:
                print(f"  [DEBUG] Web API error: {e}")

        return {'success': False, 'error': 'Web API tidak tersedia', 'method': 'web_api'}

    def _query_fallback(self, nopol: str, province: dict) -> dict:
        """Fallback query using common patterns"""
        # Try Signal app API (nasional)
        signal_urls = [
            "https://signal.id/api/v1/cek-nopol",
            "https://api.signal.id/v1/kendaraan",
            "https://apps.signal.id/api/cek",
        ]

        for url in signal_urls:
            try:
                r = self.session.post(url, json={'nopol': nopol}, timeout=10)
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if data.get('success') or data.get('data'):
                            return {
                                'success': True,
                                'data': data,
                                'method': 'signal_api'
                            }
                    except json.JSONDecodeError:
                        pass
            except Exception:
                continue

        return {
            'success': False,
            'error': f'API belum tersedia untuk {province["name"]}',
            'method': 'fallback'
        }

    def _extract_commented_data(self, html: str) -> dict:
        """Extract owner data from HTML comments (hidden by developer)"""
        data = {}
        
        # Find all HTML comments
        comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
        
        for comment in comments:
            # Look for NAMA PEMILIK in comments
            nama_match = re.search(r'NAMA\s*PEMILIK.*?<td[^>]*>.*?<strong>(.*?)</strong>', comment, re.DOTALL | re.IGNORECASE)
            if nama_match:
                nama = nama_match.group(1).strip()
                if nama:
                    data['nama_pemilik'] = nama
            
            # Look for ALAMAT in comments (3 td tags pattern)
            alamat_match = re.search(r'ALAMAT.*?</td>.*?</td>.*?<td[^>]*>(.*?)</td>', comment, re.DOTALL | re.IGNORECASE)
            if alamat_match:
                alamat = alamat_match.group(1).strip()
                if alamat:
                    data['alamat'] = alamat
        
        return data

    def _merge_jambi_data(self, results: dict) -> dict:
        """Merge multiple API responses into unified format"""
        data = {
            'wilayah': 'Jambi',
            'api_source': 'api-pkb.jambisamsat.net',
        }

        # Kendaraan data
        if 'kendaraan' in results:
            kend = results['kendaraan'].get('data', {})
            if isinstance(kend, dict):
                data['nopol'] = kend.get('no_polisi', '')
                data['merek'] = kend.get('nm_merek_kb', '')
                data['model'] = kend.get('nm_model_kb', '')
                data['jenis'] = kend.get('nm_jenis_kb', '')
                data['tahun'] = kend.get('th_rakitan', '')
                data['warna'] = kend.get('warna_kb', '')
                data['cc'] = kend.get('jumlah_cc', '')
                data['bbm'] = kend.get('bbm', {}).get('nama', '') if isinstance(kend.get('bbm'), dict) else ''
                data['njkb'] = kend.get('njkb', {}).get('nilai_jual', '') if isinstance(kend.get('njkb'), dict) else ''
                data['lokasi'] = kend.get('lokasi_transaksi_terakhir', {}).get('nama', '') if isinstance(kend.get('lokasi_transaksi_terakhir'), dict) else ''
                data['tgl_akhir_pkb'] = kend.get('tg_akhir_pkb', '')
                data['tgl_akhir_stnk'] = kend.get('tg_akhir_stnk', '')

        # Pajak data
        if 'pajak' in results:
            pajak = results['pajak'].get('data', {})
            if isinstance(pajak, dict):
                data['pkb'] = pajak.get('pkb', pajak.get('nilai_pkb', ''))
                data['swdklljj'] = pajak.get('swdklljj', pajak.get('swdkllj_pkb', ''))
                data['pajak_progresif'] = pajak.get('pajak_progresif', '')
                data['total_pajak'] = pajak.get('total_pajak', pajak.get('total', ''))
                data['denda_pkb'] = pajak.get('denda_pkb', pajak.get('denda', ''))

        # Jasa Raharja
        if 'jasa_raharja' in results:
            jr = results['jasa_raharja'].get('data', {})
            if isinstance(jr, dict):
                data['jr_pkb'] = jr.get('pkb', jr.get('swdkllj_pkb', ''))
                data['jr_denda'] = jr.get('denda_pkb', jr.get('denda', ''))
                data['jr_total'] = jr.get('total_jr', jr.get('total', ''))

        # PNBP
        if 'pnbp' in results:
            pnbp = results['pnbp'].get('data', {})
            if isinstance(pnbp, dict):
                data['pnbp_stnk'] = pnbp.get('stnk', pnbp.get('pnbp_stnk', ''))
                data['pnbp_tnkb'] = pnbp.get('tnkb', pnbp.get('pnbp_tnkb', ''))

        return data
