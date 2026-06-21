"""
Samsat Province Mapping - Mapping kode nopol ke provinsi & API endpoints
"""

# Status: READY, PARTIAL, UNAVAIL, LEGACY
PROVINCES = {
    # ===== SUMATERA =====
    'BL': {'name': 'Banda Aceh - Aceh', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BB': {'name': 'Sumatera Utara', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BK': {'name': 'Sumatera Utara (Medan)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BA': {'name': 'Sumatera Barat', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BM': {'name': 'Riau', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BH': {'name': 'Jambi', 'api_status': 'READY', 'api_url': 'https://api-pkb.jambisamsat.net/api', 'method': 'api_key'},
    'BG': {'name': 'Sumatera Selatan', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BD': {'name': 'Bengkulu', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BE': {'name': 'Lampung', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BN': {'name': 'Kepulauan Bangka Belitung', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'BP': {'name': 'Kepulauan Riau', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},

    # ===== JAWA =====
    'A':  {'name': 'Banten', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'B':  {'name': 'DKI Jakarta', 'api_status': 'PARTIAL', 'api_url': None, 'method': 'web_scrape'},
    'D':  {'name': 'Jawa Barat (Bandung)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'E':  {'name': 'Jawa Barat (Cirebon)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'F':  {'name': 'Jawa Barat (Bogor)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'G':  {'name': 'Jawa Tengah', 'api_status': 'PARTIAL', 'api_url': None, 'method': 'web_scrape'},
    'H':  {'name': 'Jawa Tengah (Semarang)', 'api_status': 'PARTIAL', 'api_url': None, 'method': 'web_scrape'},
    'K':  {'name': 'Jawa Tengah (Pekalongan)', 'api_status': 'PARTIAL', 'api_url': None, 'method': 'web_scrape'},
    'R':  {'name': 'Jawa Tengah (Banyumas)', 'api_status': 'PARTIAL', 'api_url': None, 'method': 'web_scrape'},
    'AA': {'name': 'Jawa Timur (Kediri)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'AB': {'name': 'DIY Yogyakarta', 'api_status': 'READY', 'api_url': 'https://samsatsleman.jogjaprov.go.id/cek/pages/getpajak', 'method': 'json_api'},
    'AG': {'name': 'Jawa Timur (Madiun)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'AD': {'name': 'Jawa Timur (Surabaya)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'AE': {'name': 'Jawa Timur (Jember)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'N':  {'name': 'Jawa Timur (Malang)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'L':  {'name': 'Jawa Timur (Surabaya)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'M':  {'name': 'Jawa Timur (Madura)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'S':  {'name': 'Jawa Timur (Ponorogo)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'W':  {'name': 'Jawa Timur (Surabaya)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'P':  {'name': 'Jawa Timur (Surabaya)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'T':  {'name': 'Jawa Timur (Tulungagung)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'AG': {'name': 'Jawa Timur (Madiun)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'Z':  {'name': 'DIY Yogyakarta (Bantul)', 'api_status': 'READY', 'api_url': 'https://samsatsleman.jogjaprov.go.id/cek/pages/getpajak', 'method': 'json_api'},

    # ===== KALIMANTAN =====
    'KB': {'name': 'Kalimantan Barat', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'KH': {'name': 'Kalimantan Tengah', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DA': {'name': 'Kalimantan Selatan', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'KT': {'name': 'Kalimantan Timur', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'KU': {'name': 'Kalimantan Utara', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},

    # ===== SULAWESI =====
    'DN': {'name': 'Sulawesi Selatan', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DB': {'name': 'Sulawesi Barat', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DM': {'name': 'Sulawesi Tengah', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DL': {'name': 'Sulawesi Utara', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DC': {'name': 'Sulawesi Tenggara', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DD': {'name': 'Sulawesi Selatan (Makassar)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DE': {'name': 'Gorontalo', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DG': {'name': 'Sulawesi Selatan (Bone)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DT': {'name': 'Sulawesi Tengah (Palu)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DS': {'name': 'Sulawesi Selatan (Palopo)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},

    # ===== BALI & NUSA TENGGARA =====
    'DK': {'name': 'Bali', 'api_status': 'READY', 'api_url': 'https://portal.bpdbali.id/infosamsat/', 'method': 'form_post'},
    'EA': {'name': 'Nusa Tenggara Barat', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'EB': {'name': 'Nusa Tenggara Timur', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DH': {'name': 'Nusa Tenggara Timur (Kupang)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'DR': {'name': 'Nusa Tenggara Barat (Mataram)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'ED': {'name': 'Nusa Tenggara Timur (Ende)', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},

    # ===== MALUKU & PAPUA =====
    'DE': {'name': 'Maluku', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'PA': {'name': 'Papua', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
    'PB': {'name': 'Papua Barat', 'api_status': 'UNAVAIL', 'api_url': None, 'method': None},
}


def get_province(kode: str) -> dict:
    """Get province info by nopol kode"""
    kode = kode.upper()
    return PROVINCES.get(kode)


def get_all_prefixes() -> list:
    """Get list of all nopol prefixes"""
    return sorted(PROVINCES.keys())


def get_ready_provinces() -> list:
    """Get list of provinces with READY API"""
    return [
        {'kode': k, 'name': v['name']}
        for k, v in PROVINCES.items()
        if v['api_status'] == 'READY'
    ]
