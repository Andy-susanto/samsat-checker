#!/usr/bin/env python3
"""
Samsat Indonesia Checker - Web UI
Flask + Tailwind CSS + CSS Spring Animations
"""

from flask import Flask, render_template, request, jsonify
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from samsat_api import SamsatAPI
from samsat_provinces import PROVINCES, get_province
from njkb_scraper import NJKBScraper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def check_vehicle():
    """API endpoint untuk cek kendaraan"""
    data = request.get_json()
    nopol = data.get('nopol', '').upper().strip()
    
    if not nopol:
        return jsonify({'success': False, 'error': 'Nopol tidak boleh kosong'}), 400
    
    # Parse nopol
    import re
    match = re.match(r'^([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})$', nopol)
    if not match:
        return jsonify({'success': False, 'error': 'Format nopol tidak valid'}), 400
    
    kode = match.group(1)
    province = get_province(kode)
    
    if not province:
        return jsonify({'success': False, 'error': f'Kode provinsi {kode} tidak dikenal'}), 400
    
    # Query API
    try:
        api = SamsatAPI(verbose=False)
        result = api.query(nopol, province)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result['data'],
                'method': result.get('method', 'unknown'),
                'province': province['name']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Data tidak ditemukan')
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/provinces')
def get_provinces():
    """Get list of provinces"""
    provinces = []
    for kode, info in sorted(PROVINCES.items(), key=lambda x: x[1]['name']):
        provinces.append({
            'kode': kode,
            'name': info['name'],
            'status': info['api_status']
        })
    return jsonify(provinces)

# ═══════════════════════════════════════════════════════════
# NJKB API - SAMSAT DKI Jakarta
# ═══════════════════════════════════════════════════════════

_njkb_scraper = NJKBScraper()

@app.route('/api/njkb/jenis')
def njkb_jenis():
    """Get list jenis kendaraan untuk NJKB"""
    return jsonify(_njkb_scraper.get_jenis_kendaraan())

@app.route('/api/njkb/merek')
def njkb_merek():
    """Get list merek kendaraan untuk NJKB"""
    merek_list = _njkb_scraper.get_merek_list()
    return jsonify(merek_list)

@app.route('/api/njkb/search', methods=['POST'])
def njkb_search():
    """
    Search NJKB kendaraan
    
    Body JSON:
    {
        "jenis": "70",        // kode jenis (10=Sedan, 70=Motor, dll)
        "tahun": 2024,        // tahun pembuatan
        "merek": "HONDA",     // merek kendaraan
        "page": 1,            // halaman (opsional, default 1)
        "pupd": "...",        // pagination token (opsional, untuk page > 1)
        "all_pages": false    // jika true, scrape semua halaman
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Body JSON diperlukan'}), 400
    
    jenis = data.get('jenis', '').strip()
    tahun = data.get('tahun')
    merek = data.get('merek', '').strip().upper()
    
    if not jenis or not tahun or not merek:
        return jsonify({
            'success': False, 
            'error': 'Parameter jenis, tahun, dan merek wajib diisi'
        }), 400
    
    try:
        tahun = int(tahun)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Tahun harus angka'}), 400
    
    if tahun < 1978 or tahun > 2030:
        return jsonify({'success': False, 'error': 'Tahun harus antara 1978-2030'}), 400
    
    try:
        # Check if user wants all pages
        all_pages = data.get('all_pages', False)
        
        if all_pages:
            max_pages = min(data.get('max_pages', 10), 50)  # cap at 50
            result = _njkb_scraper.search_all_pages(jenis, tahun, merek, max_pages)
        else:
            page = data.get('page', 1)
            pupd = data.get('pupd')
            result = _njkb_scraper.search_njkb(jenis, tahun, merek, page, pupd)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=59191)
