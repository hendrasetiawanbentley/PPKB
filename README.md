# OJK — Sistem Analisis AI Kepatuhan & Kewajaran Laporan Keuangan

## Cara jalankan
```bash
pip install -r requirements.txt --break-system-packages   # atau di virtualenv biasa
cp .env.example .env      # lalu isi GEMINI_API_KEY
python app.py
```
Buka `http://localhost:8050`. Sidebar berisi 6 menu: Beranda + 5 modul + Kesimpulan Keseluruhan.

## Struktur folder
```
ojk_dashboard/
├── app.py                  # entry point, sidebar navigasi (dash multi-page)
├── pages/
│   ├── home.py              # Beranda
│   ├── 1_kepatuhan.py        # Modul 1 — Simpulan Kepatuhan
│   ├── 2_komparasi.py        # Modul 2 — Simpulan Komparasi
│   ├── 3_rasio.py            # Modul 3 — Simpulan Rasio
│   ├── 4_calk.py             # Modul 4 — Simpulan CaLK
│   ├── 5_ml_voting.py        # Modul 5 — ML Voting (SUDAH lengkap, dari fraud_dashboard.py lama)
│   └── 6_kesimpulan.py       # Kesimpulan Keseluruhan (gabungan 5 modul di atas)
├── ml/
│   └── voting_model.py       # logic ensemble 5 model + parsing Excel, direfactor dari fraud_dashboard.py
├── utils/
│   ├── genai_narrator.py     # semua prompt GenAI per modul ada di sini
│   ├── export_excel.py       # 1 fungsi generik: dict of DataFrame -> file .xlsx
│   └── export_pdf.py         # 1 fungsi generik: list of section -> file .pdf
├── requirements.txt
└── .env.example
```

## Yang SUDAH bisa jalan (semua 5 modul + kesimpulan, tidak ada placeholder lagi)
- **Modul 1 (Kepatuhan)**: upload 1 dokumen laporan (.pdf) → checklist 22 kriteria emiten
  sudah tertanam di `CHECKLIST_ITEMS` (`pages/1_kepatuhan.py`) → GenAI isi Status/Hasil AI/
  Halaman/Catatan AI, nama entitas & periode diekstrak otomatis dari dokumen.
- **Modul 2 (Komparasi)**: upload Excel (format sama modul 5), pilih sheet/emiten → sistem
  hitung selisih tiap akun antar kuartal berurutan, tandai MISMATCH bila perubahan
  ≥30% (`MISMATCH_THRESHOLD_PCT`), GenAI simpulkan implikasinya.
- **Modul 3 (Rasio)**: upload Excel, pilih sheet/emiten → hitung 9 rasio keuangan kuartal
  terbaru, banding ke `THRESHOLDS`, GenAI simpulkan kondisi kesehatan keuangan.
- **Modul 4 (CaLK)**: upload 1 dokumen laporan (.pdf) → GenAI baca isi & ekstrak catatan
  dengan temuan signifikan beserta level risiko, tanpa perlu template terpisah.
- **Modul 5 (ML Voting)**: upload Excel, ensemble 5 model + Leave-One-Out CV, voting,
  narasi GenAI. Diambil & dirapikan dari `fraud_dashboard.py` lama kamu.
- **Kesimpulan Keseluruhan**: gabungkan narasi 5 modul di atas jadi satu simpulan akhir.
- Navigasi sidebar, upload file, tombol proses, tombol download Excel & PDF di semua modul.
- Kesimpulan Keseluruhan sudah bisa menggabungkan narasi 5 modul jadi satu — TAPI baru
  jalan kalau kelima modul di atasnya sudah pernah diproses (data disimpan di
  `sessionStorage` browser per modul).

## Yang masih perlu di-tuning (bukan bug, tapi angka/aturan yang perlu disesuaikan)
| Modul | File | Yang perlu disesuaikan |
|---|---|---|
| 1. Kepatuhan | `pages/1_kepatuhan.py` → `CHECKLIST_ITEMS` | Lengkapi/perbarui kalau checklist resmi berubah |
| 2. Komparasi | `pages/2_komparasi.py` → `MISMATCH_THRESHOLD_PCT` | Ambang batas 30% masih asumsi, sesuaikan kebijakan supervisor |
| 3. Rasio | `pages/3_rasio.py` → `THRESHOLDS` | Threshold rasio masih asumsi umum, ganti dengan ketentuan/benchmark sektor riil |
| 4. CaLK | — | Sudah jalan penuh, GenAI yang menentukan signifikansi temuan |
| 5. ML Voting | `pages/5_ml_voting.py` → `TRAIN_LABELS` | Ganti daftar emiten fraud/clean dummy dengan histori kasus riil OJK |

## Catatan penting
- **GenAI narrator** (`utils/genai_narrator.py`) sengaja dipisah dari logic hitung-hitungan.
  Prinsipnya: angka/status dihitung oleh kode Python (pasti benar), GenAI cuma menyusun
  bahasa & rekomendasi dari angka itu — jangan biarkan GenAI menghitung sendiri.
- Kalau `GEMINI_API_KEY` belum diisi, `genai_narrator.py` tetap jalan (fallback ke pesan
  placeholder) supaya kamu bisa tes alur UI dulu sebelum API key siap.
- Semua download pakai `dcc.send_bytes` — tidak perlu simpan file ke disk server, langsung stream ke browser user.
- Kalau nanti CaLK/Rasio/Komparasi butuh data lintas-emiten (bukan cuma 1 file), pola
  upload-nya bisa disamakan dengan modul 5 (`target_companies` dari input text, bukan cuma 1 file).

## Data dummy (Ringkasan Portofolio & Analisis Per Perusahaan)
Data di beranda dan saat memilih perusahaan dari daftar adalah **data simulasi** emiten
perbankan & asuransi yang tercatat di IDX (`utils/portfolio_data.py`). Nama emitennya nyata,
tetapi semua angka, status, rasio, dan temuan dibuat acak dengan seed tetap — bukan hasil
analisis laporan keuangan sebenarnya. Analisis sungguhan hanya terjadi saat file PDF/Excel di-upload.
Petunjuk mengubah daftar emiten, rasio, akun, dan tahun laporan ada di bagian atas file tersebut.

## Menjalankan di Spyder (Anaconda)
1. Install dependensi di environment yang dipakai Spyder (Anaconda Prompt):
   ```bash
   pip install -r requirements.txt
   ```
   Kalau Spyder memakai environment lain, cek lewat *Tools > Preferences > Python interpreter*.
2. Salin `.env.example` jadi `.env` lalu isi API key (sama seperti versi biasa).
3. Buka **`app_spyder.py`** di Spyder, tekan **F5**. Browser otomatis membuka `http://127.0.0.1:8050`.
4. Server jalan di background, konsol tetap bisa dipakai:
   - `hentikan_dashboard()` → matikan server
   - **F5** lagi → server lama otomatis dimatikan, kode terbaru dimuat ulang
   - Variabel `app` (objek Dash) dan `server` (Flask) tersedia di Variable Explorer/konsol
5. Pengaturan ada di sel `# %% 0. Konfigurasi` di bagian atas file (port, buka browser
   otomatis, panel debug, mode blokir).

Jangan jalankan `app.py` langsung dengan F5 di Spyder: `debug=True` memakai reloader Flask
yang bentrok dengan konsol IPython. `app.py` tetap dipakai untuk `python app.py` di terminal.

## Deploy online (Render)
Repo ini sudah berisi `render.yaml`, jadi bisa langsung di-deploy:
1. Login ke [render.com](https://render.com) dengan akun GitHub.
2. **New > Blueprint** → pilih repo `PPKB` → isi `GEMINI_API_KEY` saat diminta → **Apply**.
3. Setelah build selesai, dashboard bisa dibuka di alamat `https://<nama-service>.onrender.com`.

Setiap push ke branch `main` otomatis memicu deploy ulang. API key **jangan** ditulis di kode
atau di-commit; isi lewat menu *Environment* di Render.
