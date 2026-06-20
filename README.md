# Samsat Checker

Cek data kendaraan dan pajak (PKB/NJKB) seluruh Indonesia via nomor polisi.

**Web UI + CLI + REST API** — powered by Flask, with real-time NJKB data from SAMSAT DKI Jakarta.

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/flask-3.0+-black?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Fitur

- **Cek Kendaraan by Nopol** — masukkan nomor polisi, otomatis detect provinsi & query API
- **Cek NJKB DKI Jakarta** — 592+ merek kendaraan, 13 jenis, pagination
- **Web UI** — dark theme Tailwind CSS, responsive, spring animations
- **CLI** — `python3 samsat.py BH1234AB` langsung dari terminal
- **REST API** — JSON endpoint untuk integrasi ke app lain
- **Provinsi Mapping** — 40+ kode plat kendaraan seluruh Indonesia

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/samsat-checker.git
cd samsat-checker

# Install deps
pip install -r requirements.txt

# Jalankan web UI
python3 app.py
# -> http://localhost:59191

# Atau CLI
python3 samsat.py BH1234AB
python3 samsat.py --list-provinces
```

## REST API

### Cek Kendaraan
```bash
curl -X POST http://localhost:59191/api/check \
  -H 'Content-Type: application/json' \
  -d '{"nopol": "BH1234AB"}'
```

Response:
```json
{
  "success": true,
  "data": {
    "nopol": "BH1234AB",
    "province": "Jambi",
    "owner": "...",
    "vehicle": {...}
  }
}
```

### Cek NJKB (Nilai Jual Kendaraan Bermotor)
```bash
# List jenis kendaraan
curl http://localhost:59191/api/njkb/jenis

# List merek (592 merek)
curl http://localhost:59191/api/njkb/merek

# Search NJKB
curl -X POST http://localhost:59191/api/njkb/search \
  -H 'Content-Type: application/json' \
  -d '{"jenis": "70", "tahun": 2024, "merek": "HONDA"}'
```

### List Provinsi
```bash
curl http://localhost:59191/api/provinces
```

## Arsitektur

```
samsat-checker/
├── app.py              # Flask web server + REST API
├── samsat.py           # CLI entry point
├── samsat_api.py       # API client (multi-backend)
├── samsat_provinces.py # Mapping kode plat -> provinsi
├── samsat_display.py   # Format output CLI
├── njkb_scraper.py     # Scraper NJKB DKI Jakarta
├── templates/
│   └── index.html      # Web UI (Tailwind CSS)
├── requirements.txt
└── .env.example
```

### Alur Query

```
User Input (Nopol)
       │
       ▼
  Parse Nopol ──→ Detect Province (BH = Jambi, B = Jakarta, dll)
       │
       ▼
  Route ke Backend yg sesuai:
       ├── Jambi (BH)  → api-pkb.jambisamsat.net [API Key]
       ├── Jakarta (B)  → web_scrape (NJKB only)
       └── Lainnya      → fallback / coming soon
       │
       ▼
  Response JSON → Format & Display
```

## Status Per Provinsi

| Kode | Provinsi | Status |
|------|----------|--------|
| BH | Jambi | ✅ READY (API) |
| B | DKI Jakarta | 🟡 PARTIAL (NJKB only) |
| G,H,K,R | Jawa Tengah | 🟡 PARTIAL |
| A | Banten | 🟡 PARTIAL |
| Lainnya | - | 🔴 Coming Soon |

## NJKB DKI Jakarta

Endpoint: `POST https://samsat-pkb.jakarta.go.id/INFO_NJKB`

Parameter:
- `JEN` — Jenis kendaraan (10=Sedan, 20=Jeep, 70=Sepeda Motor, dll)
- `THN` — Tahun (1978–2026)
- `MER` — Merek (HONDA, TOYOTA, DAIHATSU, dll)
- `FLAG` — 2 (default)

Tidak perlu auth, tidak perlu captcha.

## Kontribusi

1. Fork repo ini
2. Buat branch: `git checkout -b feat/provinsi-baru`
3. Tambah API endpoint provinsi baru di `samsat_api.py`
4. Update mapping di `samsat_provinces.py`
5. Submit PR

### Menambah Provinsi Baru

```python
# samsat_provinces.py
'XX': {
    'name': 'Nama Provinsi',
    'api_status': 'READY',         # READY / PARTIAL / UNAVAIL
    'api_url': 'https://...',      # API endpoint
    'method': 'api_key'            # api_key / web_scrape / form_post
}
```

```python
# samsat_api.py — tambah handler
def _query_xx(self, nopol: str) -> dict:
    # implementasi query ke API provinsi
    pass
```

## License

MIT
