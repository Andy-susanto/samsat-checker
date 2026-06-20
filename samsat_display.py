"""
Samsat Display - Format output data kendaraan
"""

from datetime import datetime
from typing import Dict, Any


def display_vehicle_data(data: dict, province: dict):
    """Display vehicle data in formatted table"""

    print("=" * 60)
    print("  DATA KENDARAAN")
    print("=" * 60)

    if isinstance(data, dict):
        # Check if data is wrapped (has 'data' key)
        if 'data' in data and isinstance(data['data'], dict):
            data = data['data']

        # Vehicle info section
        vehicle_fields = [
            ('nopol', 'Nomor Polisi'),
            ('wilayah', 'Wilayah'),
            ('merek', 'Merek'),
            ('model', 'Model'),
            ('jenis', 'Jenis'),
            ('tahun', 'Tahun'),
            ('warna', 'Warna'),
            ('cc', 'Kapasitas Mesin'),
            ('bbm', 'Bahan Bakar'),
            ('njkb', 'NJKB'),
            ('lokasi', 'Lokasi Samsat'),
        ]

        has_vehicle = False
        for key, label in vehicle_fields:
            value = data.get(key, '')
            if value:
                print(f"  {label:<20}: {value}")
                has_vehicle = True

        if not has_vehicle:
            # Try raw data
            if 'no_polisi' in data:
                print(f"  {'Nomor Polisi':<20}: {data.get('no_polisi', '')}")
                print(f"  {'Merek':<20}: {data.get('nm_merek_kb', '')}")
                print(f"  {'Model':<20}: {data.get('nm_model_kb', '')}")
                print(f"  {'Jenis':<20}: {data.get('nm_jenis_kb', '')}")
                print(f"  {'Tahun':<20}: {data.get('th_rakitan', '')}")
                print(f"  {'Warna':<20}: {data.get('warna_kb', '')}")

        # Owner info section
        owner_fields = [
            ('nama_pemilik', 'Nama Pemilik'),
            ('pemilik', 'Pemilik'),
            ('owner', 'Owner'),
        ]
        has_owner = False
        for key, label in owner_fields:
            value = data.get(key, '')
            if value:
                if not has_owner:
                    print()
                    print("  --- PEMILIK ---")
                    has_owner = True
                print(f"  {label:<20}: {value}")

        # Address
        address_fields = ['alamat', 'address', 'alamat_pemilik']
        for key in address_fields:
            value = data.get(key, '')
            if value:
                if not has_owner:
                    print()
                    print("  --- PEMILIK ---")
                    has_owner = True
                print(f"  {'Alamat':<20}: {value}")

        # Tax info section
        tax_fields = [
            ('tgl_akhir_pkb', 'Akhir PKB'),
            ('tgl_akhir_stnk', 'Akhir STNK'),
            ('pajak_pkb', 'PKB'),
            ('pkb', 'PKB'),
            ('swdklljj', 'SWDKLLJJ'),
            ('swdkllj_pkb', 'SWDKLLJJ'),
            ('pajak_progresif', 'Pajak Progresif'),
            ('denda', 'Denda'),
            ('denda_pkb', 'Denda PKB'),
            ('total_pajak', 'Total Pajak'),
            ('total', 'Total'),
        ]

        has_tax = False
        for key, label in tax_fields:
            value = data.get(key, '')
            if value:
                if not has_tax:
                    print()
                    print("  --- PAJAK ---")
                    has_tax = True
                print(f"  {label:<20}: {value}")

        # Jasa Raharja
        jr_fields = [
            ('jr_pkb', 'JR PKB'),
            ('jr_denda', 'JR Denda'),
            ('jr_total', 'JR Total'),
        ]
        has_jr = False
        for key, label in jr_fields:
            value = data.get(key, '')
            if value:
                if not has_jr:
                    print()
                    print("  --- JASA RAHARJA ---")
                    has_jr = True
                print(f"  {label:<20}: {value}")

        # PNBP
        pnbp_fields = [
            ('pnbp_stnk', 'PNBP STNK'),
            ('pnbp_tnkb', 'PNBP TNKB'),
        ]
        has_pnbp = False
        for key, label in pnbp_fields:
            value = data.get(key, '')
            if value:
                if not has_pnbp:
                    print()
                    print("  --- PNBP ---")
                    has_pnbp = True
                print(f"  {label:<20}: {value}")

    else:
        print(f"  Data: {data}")

    print()
    print("=" * 60)

    # Source info
    source = data.get('api_source', 'unknown')
    print(f"  Source : {source}")
    print(f"  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def display_error(error: str, province: dict = None):
    """Display error message"""
    print()
    print("=" * 60)
    print("  ERROR")
    print("=" * 60)
    print()
    print(f"  Pesan  : {error}")
    if province:
        print(f"  Wilayah: {province.get('name', 'Unknown')}")
        print(f"  Status : {province.get('api_status', 'Unknown')}")
    print()
    print("  Solusi:")
    print("  1. Pastikan nopol benar (format: BH1234AB)")
    print("  2. Cek apakah API tersedia untuk wilayah ini")
    print("  3. Gunakan --verbose untuk debug")
    print()
    print("=" * 60)


def display_info(message: str):
    """Display info message"""
    print()
    print(f"  [i] {message}")
    print()
