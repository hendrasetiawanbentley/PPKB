# -*- coding: utf-8 -*-
"""
Wrapper pemanggilan GenAI untuk menyusun narasi/simpulan tiap modul.
Ganti isi _call_genai() sesuai provider yang dipakai (google-genai / Anthropic / dll).
Prinsip: modul lain (kepatuhan.py, komparasi.py, dst) HANYA mengirim data
terstruktur (dict/DataFrame ringkas) ke sini — GenAI tidak menghitung angka,
GenAI hanya menyusun bahasa + rekomendasi dari angka yang sudah pasti benar.
"""

import os
from pathlib import Path

# ── Load .env ─────────────────────────────────────────────────────────────────
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

# ── Provider auto-detect ──────────────────────────────────────────────────────
# Prioritas: 1) Gemini (free, kualitas bagus)  2) Anthropic  3) Ollama (fallback lokal)
_PROVIDER      = None
_anth_client   = None
_gemini_client = None
_OLLAMA_MODEL  = os.environ.get("OLLAMA_MODEL", "gemma3:1b")

_ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_GEMINI_KEY    = os.environ.get("GEMINI_API_KEY", "")

# 1) Google Gemini (recommended — free & high quality)
if _GEMINI_KEY and not _GEMINI_KEY.startswith("your_"):
    try:
        from google import genai as _genai
        _gemini_client = _genai.Client(api_key=_GEMINI_KEY)
        _PROVIDER = "gemini"
        print("[GenAI] Provider: Google Gemini ✓")
    except Exception:
        pass

# 2) Anthropic Claude
if _PROVIDER is None and _ANTHROPIC_KEY and _ANTHROPIC_KEY.startswith("sk-ant-"):
    try:
        import anthropic as _anthropic
        _anth_client = _anthropic.Anthropic(api_key=_ANTHROPIC_KEY)
        _PROVIDER = "anthropic"
        print("[GenAI] Provider: Anthropic Claude ✓")
    except Exception:
        pass

# 3) Ollama lokal (fallback)
def _check_ollama():
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

if _PROVIDER is None and _check_ollama():
    _PROVIDER = "ollama"
    print(f"[GenAI] Provider: Ollama lokal (model: {_OLLAMA_MODEL})")

if _PROVIDER is None:
    print("[GenAI] ⚠️  Tidak ada provider AI. Set GEMINI_API_KEY atau jalankan Ollama.")


def _call_genai(prompt: str) -> str:
    """Panggil GenAI — otomatis pakai provider yang tersedia."""

    if _PROVIDER == "ollama":
        import urllib.request, json as _json
        payload = _json.dumps({
            "model": _OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": 32768, "temperature": 0.3},
        }).encode()
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = _json.loads(resp.read().decode())
                return body.get("response", "")
        except Exception as e:
            return f"[Ollama error: {e}]"

    if _PROVIDER == "anthropic":
        msg = _anth_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

    if _PROVIDER == "gemini":
        resp = _gemini_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return resp.text

    return (
        "[GenAI belum terkonfigurasi]\n"
        "Jalankan Ollama: ollama serve && ollama pull gemma3:4b\n"
        "Atau tambahkan API key ke .env\n"
    )


def narrate_kepatuhan(data: dict) -> str:
    """data: {'ya': int, 'tidak': int, 'na': int, 'items_tidak': [...], 'deadline_info': str}"""
    prompt = f"""
Buat ringkasan singkat (maks 4 kalimat) hasil pengecekan kepatuhan laporan keuangan.
Gunakan bahasa Indonesia formal seperti laporan resmi OJK — langsung ke poin, tanpa header/numbering.

JANGAN tulis "Kosongkan" atau placeholder. Jika data tidak ada, abaikan saja.

Hasil: {data.get('ya')} terpenuhi, {data.get('tidak')} tidak terpenuhi, {data.get('na')} tidak dapat dievaluasi.
Item yang tidak terpenuhi: {data.get('items_tidak')}

Contoh output yang diharapkan:
"Dari 22 kriteria yang diuji, 6 kriteria terpenuhi dan 12 kriteria belum terpenuhi. Ketidakpatuhan utama terkait kelengkapan komponen laporan keuangan dan laporan auditor independen. Diperlukan tindak lanjut untuk memastikan kelengkapan penyampaian seluruh komponen wajib."
"""
    return _call_genai(prompt)


def narrate_komparasi(data: dict) -> str:
    """data: {'mismatches': [{'akun':..., 'selisih':..., 'pct':...}], 'total_akun': int}"""
    mm = data.get('mismatches', [])
    total = data.get('total_akun', 0)
    if not mm:
        return f"Seluruh {total} akun yang dikomparasikan menunjukkan kesesuaian data antar periode. Tidak ditemukan selisih material."
    prompt = f"""
Buat ringkasan singkat (maks 5 kalimat) hasil komparasi akun keuangan.
Gunakan bahasa Indonesia formal seperti laporan OJK — langsung ke poin, tanpa header/numbering.
Sebutkan jumlah mismatch, akun apa saja, dan implikasinya.

Dari {total} akun yang diperiksa, ditemukan {len(mm)} akun dengan selisih material (≥30%):
{chr(10).join(f'- {m["akun"]}: selisih {m["pct"]}% (Rp {m["selisih"]:,.0f})' for m in mm)}

Contoh output yang diharapkan:
"Dari 15 akun yang dikomparasikan, teridentifikasi 6 akun dengan deviasi material melebihi threshold 30%. Akun kas menunjukkan kenaikan 85,6% yang perlu diverifikasi terhadap sumber penerimaan. Secara keseluruhan, data memerlukan penelaahan lebih lanjut untuk memastikan keandalan penyajian."
"""
    return _call_genai(prompt)


def narrate_rasio(data: dict) -> str:
    """data: {'rasio': [{'nama':..., 'nilai':..., 'threshold':..., 'status':...}]}"""
    import json as _json
    prompt = f"""
Buat ringkasan singkat (maks 5 kalimat) kondisi kesehatan keuangan berdasarkan rasio.
Gunakan bahasa Indonesia formal seperti laporan OJK — langsung ke poin, tanpa header/numbering.
Sebutkan rasio kunci dan tren naik/turunnya.

JANGAN tulis "Kosongkan" atau placeholder. Tulis seperti paragraf laporan eksekutif.

Data rasio: {_json.dumps(data.get('rasio', []), ensure_ascii=False)}

Contoh output yang diharapkan:
"Profitabilitas entitas menunjukkan perbaikan dengan ROA naik dari 0,8% menjadi 0,9% dan GPM stabil di 33,2%. Leverage cukup tinggi dengan DER sebesar 5,78x yang perlu dipantau. Likuiditas masih memadai dengan current ratio 1,01x meskipun mendekati batas minimal."
"""
    return _call_genai(prompt)


def extract_calk_findings(document_context: str) -> list:
    """Baca dokumen (fokus bagian Catatan atas Laporan Keuangan) dan ekstrak
    catatan-catatan dengan temuan signifikan.
    Return: [{"referensi": "Catatan 5", "kategori": "...", "temuan_ai": "...",
               "catatan_keterangan": "...", "halaman": "..."}]"""
    import json as _json

    prompt = f"""
Kamu adalah supervisor OJK yang membaca Catatan atas Laporan Keuangan (CaLK) dalam
dokumen berikut. Identifikasi catatan-catatan dengan TEMUAN SIGNIFIKAN (kebijakan
akuntansi tidak biasa, estimasi material, transaksi pihak berelasi, kontinjensi,
perubahan metode akuntansi, penurunan kas signifikan, jumlah karyawan tidak diaudit, dsb).

Jawab HANYA dengan JSON array valid (tanpa markdown), format:
[
  {{
    "referensi": "<nama/nomor catatan, mis: Catatan 1>", 
    "kategori": "<kategori akun/temuan, mis: Kas dan Setara Kas, Umum, Piutang, dll>",
    "temuan_ai": "<deskripsi detail temuan kuantitatif/kualitatif dari AI>", 
    "catatan_keterangan": "<catatan tindak lanjut atau usulan penjelasan yang diminta kepada perseroan>",
    "halaman": "<nomor halaman ditemukannya catatan tersebut, mis: 12>"
  }}
]

Kalau tidak ada temuan signifikan, kembalikan array kosong [].

Dokumen (ditandai per halaman):
{document_context[:120000]}
"""
    raw = _call_genai(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return _json.loads(cleaned)
    except Exception:
        return [{
            "referensi": "Catatan -",
            "kategori": "Umum",
            "temuan_ai": "Gagal memproses temuan CaLK secara detail.",
            "catatan_keterangan": raw[:300],
            "halaman": "-"
        }]


def narrate_calk(data: dict) -> str:
    """data: {'catatan_signifikan': [{'nomor':..., 'topik':..., 'risiko':..., 'ringkasan':...}]}"""
    import json as _json
    findings = data.get('catatan_signifikan', [])
    if not findings:
        return "Tidak ditemukan temuan signifikan pada catatan atas laporan keuangan."
    prompt = f"""
Buat ringkasan singkat (maks 4 kalimat) temuan signifikan dari Catatan atas Laporan Keuangan.
Gunakan bahasa Indonesia formal seperti laporan OJK — langsung ke poin, tanpa header/numbering.

JANGAN tulis "Kosongkan" atau placeholder. Tulis seperti paragraf laporan eksekutif.

Temuan: {_json.dumps(findings, ensure_ascii=False)[:3000]}

Contoh output yang diharapkan:
"Teridentifikasi 3 temuan signifikan pada CaLK, meliputi perubahan estimasi masa manfaat aset tetap, transaksi pihak berelasi senilai Rp 120 miliar, dan reklasifikasi investasi jangka panjang. Temuan ini memerlukan penelaahan lebih lanjut terkait kewajaran pengungkapan."
"""
    return _call_genai(prompt)


def narrate_ml_voting(data: dict) -> str:
    """data: {'verdict': 'FRAUD'/'CLEAN', 'votes': '3/5', 'avg_prob': 0.62, 'best_model': ..., 'closer_features': [...]}"""
    prompt = f"""
Kamu adalah supervisor OJK. Berdasarkan hasil deteksi anomali machine learning (ensemble
voting 5 model) berikut, jelaskan apakah terdapat indikasi anomali penyajian laporan
keuangan, seberapa kuat sinyalnya, dan fitur apa yang paling menonjol.

Verdict ensemble: {data.get('verdict')} ({data.get('votes')} model vote fraud, avg prob {data.get('avg_prob')})
Model terbaik: {data.get('best_model')}
Fitur yang mendekati profil fraud: {data.get('closer_features')}
"""
    return _call_genai(prompt)


def extract_document_metadata(document_context: str) -> dict:
    """Ekstrak nama entitas, jenis laporan, dan periode laporan langsung dari isi dokumen."""
    import json as _json

    prompt = f"""
Baca cuplikan dokumen laporan berikut (biasanya ada di halaman-halaman awal) dan
ekstrak informasi berikut. Jawab HANYA dengan JSON valid (tanpa markdown), format:
{{"nama_entitas": "<nama perusahaan/emiten>", "jenis_laporan": "<mis. Laporan Tahunan>",
  "periode_laporan": "<mis. 2025 atau Q1 2026>"}}
Jika suatu informasi tidak ditemukan, isi dengan "-".

Dokumen:
{document_context[:20000]}
"""
    raw = _call_genai(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return _json.loads(cleaned)
    except Exception:
        return {"nama_entitas": "-", "jenis_laporan": "-", "periode_laporan": "-"}


def assess_kepatuhan_criteria(criteria_rows: list, document_context: str) -> list:
    """
    Cek tiap baris kriteria checklist terhadap isi dokumen laporan.
    criteria_rows: [{"no":1,"komponen":...,"entitas":...,"kriteria":...}, ...]
    document_context: teks laporan dengan penanda '--- Halaman N ---'
    Return: [{"no":1,"status":"YA/TIDAK/NA","hasil_ai":"...","halaman":"...","catatan_ai":"..."}]
    """
    import json as _json

    prompt = f"""
Kamu adalah supervisor OJK yang memeriksa kepatuhan sebuah dokumen laporan terhadap
daftar kriteria berikut. Untuk SETIAP kriteria, periksa apakah dokumen memenuhinya
berdasarkan isi teks yang diberikan.

Jawab HANYA dengan JSON array valid (tanpa markdown code fence, tanpa teks lain),
dengan format persis:
[{{"no": <int>, "status": "YA"|"TIDAK"|"NA", "hasil_ai": "<alasan singkat 1 kalimat>",
   "halaman": "<nomor halaman ditemukan, atau '-'>",
   "catatan_ai": "<catatan/rekomendasi bila TIDAK, string kosong bila YA>"}}]

Daftar kriteria:
{_json.dumps(criteria_rows, ensure_ascii=False)}

Dokumen (ditandai per halaman):
{document_context[:120000]}
"""
    raw = _call_genai(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return _json.loads(cleaned)
    except Exception:
        return [
            {"no": r["no"], "status": "NA", "hasil_ai": "Gagal parsing hasil GenAI",
             "halaman": "-", "catatan_ai": raw[:200]}
            for r in criteria_rows
        ]


def narrate_kesimpulan_keseluruhan(all_narratives: dict) -> str:
    """all_narratives: {'kepatuhan': str, 'komparasi': str, 'rasio': str, 'calk': str, 'ml_voting': str}"""
    prompt = f"""
Kamu adalah supervisor OJK. Berikut adalah 5 simpulan modul analisis laporan keuangan
sebuah emiten. Satukan SEMUA menjadi satu kesimpulan menyeluruh yang menggambarkan
kondisi entitas dan tingkat kepercayaan atas laporan keuangannya.

ATURAN PENULISAN (wajib diikuti):
- Jangan gunakan kalimat pembuka basa-basi seperti 'Baik, sebagai Supervisor OJK, ...' atau sejenisnya. Langsung mulai dengan judul atau paragraf analisis utama.
- Fokus pada SINTESIS kondisi entitas dan tingkat kepercayaan laporan keuangan lintas semua modul.
- JANGAN tulis bagian Rekomendasi, Tindak Lanjut, atau saran tindakan apapun. Rekomendasi sudah ditangani oleh bagian terpisah.
- Jangan mengulang angka mentah dari modul individual.
- Gunakan bahasa Indonesia formal dan profesional.
- Maksimal 4 paragraf analisis.

1. Kepatuhan: {all_narratives.get('kepatuhan')}
2. Komparasi: {all_narratives.get('komparasi')}
3. Rasio: {all_narratives.get('rasio')}
4. CaLK: {all_narratives.get('calk')}
5. ML Voting: {all_narratives.get('ml_voting')}
"""
    raw_output = _call_genai(prompt)

    # Programmatic post-processing: strip supervisor meta-commentary prefixes
    cleaned = raw_output.strip()
    prefixes_to_strip = [
        "baik, sebagai supervisor ojk, berikut adalah sintesis menyeluruh",
        "baik, sebagai supervisor ojk, berikut adalah kesimpulan",
        "baik, sebagai supervisor ojk, berikut adalah",
        "baik, sebagai supervisor ojk,",
        "sebagai supervisor ojk, berikut adalah",
        "sebagai supervisor ojk,",
        "berikut adalah kesimpulan",
        "berikut adalah",
        "tentu, berikut adalah",
    ]
    cleaned_lower = cleaned.lower()
    for pref in prefixes_to_strip:
        if cleaned_lower.startswith(pref):
            cleaned = cleaned[len(pref):].strip()
            if cleaned.startswith(":") or cleaned.startswith("-"):
                cleaned = cleaned[1:].strip()
            break

    # Strip trailing recommendation/tindak-lanjut sections
    import re
    cleaned = re.sub(
        r'\*?\*?(?:Rekomendasi|Tindak Lanjut|Saran|Langkah Selanjutnya)[^:]*:?\*?\*?[\s\S]*$',
        '',
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned


def extract_tentang_entitas(document_context: str) -> str:
    """Ekstrak profil singkat entitas (tentang entitas) dari teks laporan keuangan."""
    prompt = f"""
Buat profil singkat entitas (2-3 kalimat) berdasarkan data laporan keuangan berikut.
Gunakan bahasa Indonesia formal. Sebutkan nama perusahaan, sektor usaha, dan kondisi keuangan umum.

JANGAN tulis "Kosongkan" atau placeholder. Jika info tidak tersedia, tulis apa yang ada saja.

Data:
{document_context[:15000]}
"""
    return _call_genai(prompt)


def generate_rekomendasi_tindak_lanjut(all_narratives: dict) -> list:
    """Menghasilkan rekomendasi rencana tindak lanjut terstruktur berisi poin utama dan rencana usulan."""
    import json as _json
    prompt = f"""
Kamu adalah supervisor OJK. Berdasarkan ringkasan analisis dari berbagai modul laporan keuangan berikut, susunlah minimal 3 rekomendasi rencana tindak lanjut yang konkret, terurut berdasarkan prioritas dan urgensi.

Jawab HANYA dengan JSON array valid (tanpa markdown), format:
[
  {{"no": 1, "poin_utama": "<identifikasi hal kritis yang perlu fokus utama>", "usulan_rencana": "<usulan tindakan konkret untuk pengawas>"}}
]

Analisis Modul:
1. Kepatuhan: {all_narratives.get('kepatuhan')}
2. Komparasi: {all_narratives.get('komparasi')}
3. Rasio: {all_narratives.get('rasio')}
4. CaLK: {all_narratives.get('calk')}
5. ML Voting: {all_narratives.get('ml_voting')}
"""
    raw = _call_genai(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return _json.loads(cleaned)
    except Exception:
        return [
            {"no": 1, "poin_utama": "Verifikasi manual kepatuhan & komparasi", "usulan_rencana": "Lakukan audit onsite atau klarifikasi tertulis kepada emiten."},
            {"no": 2, "poin_utama": "Analisis rasio dan kesehatan keuangan", "usulan_rencana": "Pantau likuiditas dan rasio leverage pada periode berikutnya."},
            {"no": 3, "poin_utama": "Penyelidikan temuan CaLK & ML", "usulan_rencana": "Mintakan penjelasan atas transaksi pihak berelasi atau akun anomali."}
        ]


def analyze_ratios_individually(ratios_list: list) -> dict:
    """
    Mendapatkan analisis AI singkat (1 kalimat) untuk masing-masing rasio.
    ratios_list: list of dict, e.g. [{'nama': 'Return on Asset (ROA)', 'y1': 0.05, 'y': 0.06}]
    Return: dict {ratio_name: analisis_singkat}
    """
    import json as _json
    prompt = f"""
Kamu adalah analis keuangan senior di OJK. Berdasarkan tabel data rasio keuangan berikut (membandingkan tahun lalu Y-1 dan tahun ini Y), berikan analisis singkat (maksimal 1 kalimat) dalam Bahasa Indonesia untuk masing-masing rasio yang menunjukkan peningkatan, penurunan, atau kondisi kesehatannya.

Kembalikan jawaban HANYA dalam format JSON object (tanpa markdown), di mana key adalah NAMA RASIO persis, dan value adalah kalimat analisis singkat.
Contoh format:
{{
  "Return on Asset (ROA)": "ROA naik menjadi 6% menunjukkan peningkatan efisiensi aset dalam menghasilkan laba.",
  "Current Ratio": "Likuiditas aman meskipun sedikit turun dari periode sebelumnya."
}}

Data rasio:
{_json.dumps(ratios_list, ensure_ascii=False)}
"""
    raw = _call_genai(prompt)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return _json.loads(cleaned)
    except Exception:
        return {}


def _parse_json_from_ai(raw: str):
    import json, re
    if not raw or not isinstance(raw, str):
        return None
    cleaned = raw.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    match_arr = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
    if match_arr:
        try:
            return json.loads(match_arr.group(0))
        except Exception:
            pass
    match_obj = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match_obj:
        try:
            return json.loads(match_obj.group(0))
        except Exception:
            pass
    return None


def extract_pdf_komparasi(document_context: str) -> dict:
    """Ekstrak komparasi akun keuangan (Y vs Y-1) dari dokumen PDF."""
    prompt = f"""
Bacalah laporan posisi keuangan (neraca) dan laporan laba rugi dalam dokumen berikut.
Ekstrak akun-akun utama (Kas dan Setara Kas, Piutang, Aset Tetap, Total Aset, Total Liabilitas, Total Ekuitas, Pendapatan/Penjualan, Beban Pokok, Laba Kotor, Laba Bersih, Arus Kas Operasi, dll) beserta nilainya pada Periode Berjalan (Y) dan Periode Lalu (Y-1). Hitung selisih dan persentase perubahannya.

Jawab HANYA dengan JSON array valid (tanpa markdown code fence), format:
[
  {{
    "akun": "Kas dan Setara Kas",
    "nilai_y1": 1500000000,
    "nilai_y": 2800000000,
    "selisih": 1300000000,
    "pct": 86.6
  }}
]

Dokumen Laporan Keuangan:
{document_context[:120000]}
"""
    raw = _call_genai(prompt)
    mismatches = _parse_json_from_ai(raw) or []
    if not isinstance(mismatches, list):
        mismatches = []

    for m in mismatches:
        if isinstance(m, dict):
            y1 = float(m.get("nilai_y1", 0) or 0)
            y  = float(m.get("nilai_y", 0) or 0)
            if "selisih" not in m or not m["selisih"]:
                m["selisih"] = round(y - y1, 2)
            if "pct" not in m or not m["pct"]:
                m["pct"] = round((y - y1) / y1 * 100, 1) if y1 else 0.0

    narrative = narrate_komparasi({"mismatches": mismatches, "total_akun": len(mismatches)})
    return {
        "mismatches": mismatches,
        "total_akun": len(mismatches),
        "q_curr": "Tahun Berjalan (Y)",
        "q_prev": "Tahun Lalu (Y-1)",
        "narrative": narrative,
    }


def extract_pdf_ratios(document_context: str) -> dict:
    """Ekstrak/hitung rasio keuangan utama dari dokumen PDF."""
    prompt = f"""
Bacalah laporan posisi keuangan dan laporan laba rugi dalam dokumen berikut. Hitung atau ekstrak minimal 10 rasio keuangan utama untuk Periode Berjalan (Y) dan Periode Lalu (Y-1).

Rasio wajib yang dihitung jika data tersedia:
1. Return on Asset (ROA)
2. Return on Equity (ROE)
3. Net Profit Margin (NPM)
4. Gross Profit Margin (GPM)
5. Debt to Asset Ratio (DAR)
6. Debt to Equity Ratio (DER)
7. Current Ratio
8. Quick Ratio
9. Cash Ratio
10. Asset Turnover

Jawab HANYA dengan JSON array valid (tanpa markdown code fence), format:
[
  {{
    "no": 1,
    "kategori": "Profitabilitas",
    "rasio": "Return on Asset (ROA)",
    "y1": 0.05,
    "y": 0.06,
    "analisis_ai": "ROA mengalami peningkatan efisiensi aset."
  }}
]

Dokumen Laporan Keuangan:
{document_context[:120000]}
"""
    raw = _call_genai(prompt)
    rows = _parse_json_from_ai(raw) or []
    if not isinstance(rows, list):
        rows = []

    narrative = narrate_rasio({"rasio": [{"nama": r.get("rasio",""), "nilai": r.get("y",0)} for r in rows if isinstance(r, dict)]})
    return {
        "rasio_rows": rows,
        "q_curr": "Tahun Berjalan (Y)",
        "q_prev": "Tahun Lalu (Y-1)",
        "narrative": narrative,
    }



