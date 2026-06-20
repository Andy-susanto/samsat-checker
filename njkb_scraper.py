#!/usr/bin/env python3
"""
NJKB Scraper - SAMSAT DKI Jakarta
Scrape Nilai Jual Kendaraan Bermotor dari samsat-pkb.jakarta.go.id
"""

import requests
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class NJKBScraper:
    """Scraper untuk NJKB DKI Jakarta"""
    
    BASE_URL = "https://samsat-pkb.jakarta.go.id/INFO_NJKB"
    
    # Jenis kendaraan mapping
    JENIS_KENDARAAN = {
        '10': 'Sedan',
        '20': 'Jeep',
        '31': 'Bus',
        '32': 'Minibus',
        '33': 'Ambulance',
        '34': 'Micro Bus',
        '41': 'Pick Up',
        '42': 'Light Truck',
        '43': 'Truck',
        '44': 'Dobel Cabin',
        '48': 'Alat-alat Berat',
        '60': 'Kend. Roda Tiga',
        '70': 'Sepeda Motor',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
        })
    
    def get_jenis_kendaraan(self) -> Dict[str, str]:
        """Get list jenis kendaraan"""
        return self.JENIS_KENDARAAN.copy()
    
    def get_merek_list(self) -> List[str]:
        """Get list merek kendaraan dari form"""
        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            merek_select = soup.find('select', {'name': 'MER'})
            
            if not merek_select:
                return []
            
            merek_list = []
            for option in merek_select.find_all('option'):
                value = option.get('value', '').strip()
                if value and value != '':
                    merek_list.append(value)
            
            return sorted(merek_list)
        
        except Exception as e:
            print(f"[ERROR] Gagal get merek list: {e}")
            return []
    
    def search_njkb(
        self, 
        jenis: str, 
        tahun: int, 
        merek: str,
        page: int = 1,
        pupd: Optional[str] = None
    ) -> Dict:
        """
        Search NJKB kendaraan
        
        Args:
            jenis: Kode jenis kendaraan (10=Sedan, 70=Motor, dll)
            tahun: Tahun pembuatan (1978-2026)
            merek: Merek kendaraan (HONDA, TOYOTA, dll)
            page: Halaman (1 = first page, 2+ = pagination)
            pupd: Pagination token (required for page > 1)
        
        Returns:
            Dict dengan keys:
            - success: bool
            - data: list of NJKB entries
            - metadata: info tentang query
            - pagination: info pagination (has_next, has_prev, pupd)
            - error: error message jika gagal
        """
        try:
            # Prepare form data
            data = {
                'JEN': jenis,
                'THN': str(tahun),
                'MER': merek,
                'FLAG': '2',
            }
            
            # First page or pagination
            if page == 1:
                data['TOMBOL'] = 'Proses'
            else:
                if not pupd:
                    return {
                        'success': False,
                        'error': 'PUPD token required for pagination'
                    }
                data['TOMBOL'] = 'NEXT'
                data['PUPD'] = pupd
            
            # Submit form
            response = self.session.post(self.BASE_URL, data=data, timeout=10)
            response.raise_for_status()
            
            # Parse response
            return self._parse_response(response.text, jenis, tahun, merek, page)
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout. Server SAMSAT mungkin sedang lambat.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _parse_response(self, html: str, jenis: str, tahun: int, merek: str, page: int) -> Dict:
        """Parse HTML response dari SAMSAT"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract metadata
        metadata = {
            'jenis': self.JENIS_KENDARAAN.get(jenis, jenis),
            'tahun': tahun,
            'merek': merek,
            'page': page,
        }
        
        # Extract header info (Jenis, Merek, Tahun Buat)
        header_text = soup.get_text()
        jenis_match = re.search(r'Jenis\s*:\s*([A-Z\s]+)', header_text)
        merek_match = re.search(r'Merek\s*:\s*([A-Z\s]+)', header_text)
        tahun_match = re.search(r'Tahun Buat\s*:\s*(\d{4})', header_text)
        
        if jenis_match:
            metadata['jenis_full'] = jenis_match.group(1).strip()
        if merek_match:
            metadata['merek_full'] = merek_match.group(1).strip()
        if tahun_match:
            metadata['tahun_full'] = tahun_match.group(1)
        
        # Extract NJKB data from table
        njkb_data = []
        rows = soup.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            # Look for rows with: No, Type, Nilai Jual
            if len(cells) >= 4:
                no_cell = cells[1]
                type_cell = cells[2]
                nilai_cell = cells[3]
                
                # Check if this is a data row (has number and price)
                no_text = no_cell.get_text().strip()
                if no_text.isdigit():
                    type_text = type_cell.get_text().strip()
                    nilai_text = nilai_cell.get_text().strip()
                    
                    # Parse nilai jual (remove "Rp" and dots)
                    nilai_clean = nilai_text.replace('Rp', '').replace('.', '').replace(',', '').strip()
                    
                    try:
                        nilai_int = int(nilai_clean)
                        
                        njkb_data.append({
                            'no': int(no_text),
                            'type': type_text,
                            'njkb': nilai_int,
                            'njkb_formatted': f"Rp {nilai_text.replace('Rp', '').strip()}",
                        })
                    except ValueError:
                        # Skip rows with invalid nilai
                        continue
        
        # Extract pagination info
        pagination = self._extract_pagination(soup)
        
        return {
            'success': True,
            'data': njkb_data,
            'metadata': metadata,
            'pagination': pagination,
            'total_entries': len(njkb_data),
        }
    
    def _extract_pagination(self, soup: BeautifulSoup) -> Dict:
        """Extract pagination info from response"""
        pagination = {
            'has_next': False,
            'has_prev': False,
            'pupd': None,
            'current_page': 1,
        }
        
        # Check for NEXT button
        next_button = soup.find('input', {'name': 'NEXT'})
        if next_button:
            pagination['has_next'] = True
        
        # Check for PREV button
        prev_button = soup.find('input', {'name': 'PREV'})
        if prev_button:
            pagination['has_prev'] = True
        
        # Extract PUPD token for pagination
        pupd_input = soup.find('input', {'name': 'PUPD'})
        if pupd_input:
            pagination['pupd'] = pupd_input.get('value', '')
        
        # Extract current page number
        page_text = soup.get_text()
        page_match = re.search(r'Hal\s*:\s*(\d+)', page_text)
        if page_match:
            pagination['current_page'] = int(page_match.group(1))
        
        return pagination
    
    def search_all_pages(
        self,
        jenis: str,
        tahun: int,
        merek: str,
        max_pages: int = 10
    ) -> Dict:
        """
        Search NJKB dan ambil semua halaman (pagination)
        
        Args:
            jenis: Kode jenis kendaraan
            tahun: Tahun pembuatan
            merek: Merek kendaraan
            max_pages: Maksimal halaman yang di-scrape (safety limit)
        
        Returns:
            Dict dengan semua data NJKB
        """
        all_data = []
        current_page = 1
        pupd = None
        
        while current_page <= max_pages:
            result = self.search_njkb(jenis, tahun, merek, current_page, pupd)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error'],
                    'data': all_data,
                    'pages_scraped': current_page - 1,
                }
            
            all_data.extend(result['data'])
            
            # Check if there's next page
            if not result['pagination']['has_next']:
                break
            
            # Get PUPD for next page
            pupd = result['pagination']['pupd']
            if not pupd:
                break
            
            current_page += 1
        
        return {
            'success': True,
            'data': all_data,
            'metadata': result['metadata'],
            'total_entries': len(all_data),
            'pages_scraped': current_page,
        }


def main():
    """Test scraper"""
    scraper = NJKBScraper()
    
    print("=" * 60)
    print("NJKB Scraper Test - SAMSAT DKI Jakarta")
    print("=" * 60)
    
    # Test 1: Get merek list
    print("\n[1] Testing get_merek_list()...")
    merek_list = scraper.get_merek_list()
    print(f"    Found {len(merek_list)} merek")
    if merek_list:
        print(f"    Sample: {', '.join(merek_list[:10])}")
    
    # Test 2: Search NJKB - Honda Motor 2024
    print("\n[2] Testing search_njkb() - Honda Motor 2024...")
    result = scraper.search_njkb('70', 2024, 'HONDA')
    
    if result['success']:
        print(f"    Found {result['total_entries']} entries on page {result['metadata']['page']}")
        print(f"    Metadata: {result['metadata']}")
        print(f"    Pagination: {result['pagination']}")
        print(f"\n    Sample entries:")
        for entry in result['data'][:5]:
            print(f"      {entry['no']:>3}. {entry['type']:<30} {entry['njkb_formatted']}")
    else:
        print(f"    ERROR: {result['error']}")
    
    # Test 3: Search with pagination
    print("\n[3] Testing search_all_pages() - Toyota Sedan 2023 (max 2 pages)...")
    result = scraper.search_all_pages('10', 2023, 'TOYOTA', max_pages=2)
    
    if result['success']:
        print(f"    Found {result['total_entries']} entries across {result['pages_scraped']} pages")
        print(f"\n    Sample entries:")
        for entry in result['data'][:5]:
            print(f"      {entry['no']:>3}. {entry['type']:<30} {entry['njkb_formatted']}")
    else:
        print(f"    ERROR: {result['error']}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
