#!/usr/bin/env python3
"""
Samsat Indonesia Checker - Cek data kendaraan seluruh Indonesia
Membaca nopol -> tentukan provinsi -> query API -> tampilkan data lengkap

Author: Hermes Agent
Version: 1.0.0
"""

import sys
import json
import time
import re
from datetime import datetime
from typing import Optional, Dict, Any

# Import modules
from samsat_provinces import get_province, get_all_prefixes, PROVINCES
from samsat_api import SamsatAPI
from samsat_display import display_vehicle_data, display_error

__version__ = "1.0.0"


def parse_nopol(nopol: str) -> Optional[Dict[str, str]]:
    """
    Parse nomor polisi Indonesia
    Format: [KODE_PROVINSI][NOMOR][SERI]
    Contoh: BH1234AB -> kode=BH, nomor=1234, seri=AB
    """
    nopol = nopol.upper().strip()
    match = re.match(r'^([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})$', nopol)
    if not match:
        return None
    return {
        'full': nopol,
        'kode': match.group(1),
        'nomor': match.group(2),
        'seri': match.group(3),
    }


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    if sys.argv[1] in ['-h', '--help']:
        print_help()
        sys.exit(0)
    if sys.argv[1] in ['-v', '--version']:
        print(f"Samsat Checker v{__version__}")
        sys.exit(0)
    if sys.argv[1] in ['--list-provinces', '-l']:
        print_provinces()
        sys.exit(0)

    nopol_input = sys.argv[1].upper().strip()
    parsed = parse_nopol(nopol_input)
    if not parsed:
        print(f"[X] Format nopol tidak valid: {nopol_input}")
        print("    Format: [KODE][NOMOR][SERI] - Contoh: BH1234AB")
        sys.exit(1)

    province = get_province(parsed['kode'])
    if not province:
        print(f"[X] Kode provinsi tidak dikenal: {parsed['kode']}")
        print("    Gunakan --list-provinces untuk melihat daftar kode")
        sys.exit(1)

    json_mode = '--json' in sys.argv or '-j' in sys.argv
    verbose = '--verbose' in sys.argv or '-vv' in sys.argv
    raw = '--raw' in sys.argv or '-r' in sys.argv

    print()
    print("=" * 60)
    print("  SAMSAT INDONESIA CHECKER")
    print("=" * 60)
    print()
    print(f"  Nopol     : {parsed['full']}")
    print(f"  Wilayah   : {province['name']}")
    print(f"  Status    : {province['api_status']}")
    print()

    try:
        api = SamsatAPI(verbose=verbose)
        print("  [~] Mengambil data kendaraan...")
        print()

        start_time = time.time()
        result = api.query(nopol_input, province)
        elapsed = time.time() - start_time

        if result.get('success'):
            data = result['data']
            if json_mode or raw:
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                display_vehicle_data(data, province)
            if verbose:
                print()
                print(f"  Query time: {elapsed:.2f}s")
                print(f"  Method    : {result.get('method', 'unknown')}")
        else:
            display_error(result.get('error', 'Unknown error'), province)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n  [!] Dibatalkan oleh user")
        sys.exit(130)
    except Exception as e:
        print(f"\n  [X] Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_usage():
    print("""
SAMSAT INDONESIA CHECKER

Usage:
  samsat <nopol>              Cek data kendaraan
  samsat <nopol> --json       Output dalam format JSON
  samsat <nopol> --verbose    Mode verbose (debug)
  samsat --list-provinces     Lihat daftar provinsi
  samsat --help               Bantuan lengkap

Contoh:
  samsat BH1234AB             Cek kendaraan Jambi
  samsat B1234CD              Cek kendaraan Jakarta
  samsat D1234EF --json       Output JSON
""")


def print_help():
    print(f"""
SAMSAT INDONESIA CHECKER v{__version__}
============================================================

Deskripsi:
  Tools untuk mengecek data kendaraan bermotor di seluruh
  Indonesia berdasarkan nomor polisi (nopol).

  Mendukung:
  - 34 provinsi di Indonesia
  - Multiple API backends (modern API, legacy PHP, web scrape)
  - Data: kendaraan, pajak, Jasa Raharja, PNBP
  - Nama pemilik dan alamat (jika tersedia)

Options:
  -h, --help              Tampilkan bantuan
  -v, --version           Tampilkan versi
  -l, --list-provinces    Daftar provinsi yang didukung
  -j, --json              Output format JSON
  -vv, --verbose          Mode verbose (debug)
  -r, --raw               Tampilkan raw API response

Format Nopol:
  [KODE_PROVINSI][NOMOR][SERI]

  Contoh:
  BH1234AB  -> Jambi, nomor 1234, seri AB
  B1234CD   -> Jakarta, nomor 1234, seri CD
  D1234EF   -> Bandung/Jawa Barat, nomor 1234, seri EF

API Status:
  READY     : API tersedia dan bisa digunakan langsung
  PARTIAL   : API tersedia tapi perlu auth/data terbatas
  UNAVAIL   : API tidak tersedia publik
  LEGACY    : Menggunakan sistem lama (PHP)
""")


def print_provinces():
    print()
    print("DAFTAR PROVINSI DAN KODE NOPOL")
    print("=" * 60)
    print()
    print(f"{'Kode':<8} {'Provinsi':<30} {'Status':<10}")
    print("-" * 60)
    for kode, info in sorted(PROVINCES.items(), key=lambda x: x[1]['name']):
        print(f"{kode:<8} {info['name']:<30} {info['api_status']:<10}")
    print()
    print(f"Total: {len(PROVINCES)} kode provinsi")
    print()


if __name__ == '__main__':
    main()
