# -*- coding: utf-8 -*-
"""
utils/portfolio_data.py
DATA SIMULASI (dummy) untuk Ringkasan Portofolio & Analisis Per Perusahaan.

- Daftar emiten = perusahaan PERBANKAN & ASURANSI yang tercatat di Bursa Efek Indonesia.
- SELURUH angka, status, skor, rasio, dan temuan di file ini dibuat secara acak
  dengan seed tetap (hasilnya selalu sama setiap dijalankan). Ini BUKAN hasil analisis
  laporan keuangan sebenarnya — hanya untuk demo tampilan dashboard.
- Analisis sungguhan hanya terjadi saat file PDF/Excel di-upload (utils/pipeline.py).

Cara mengubah data dummy:
  * Tambah/hapus emiten  -> IDX_EMITEN_LIST (ticker, nama, sektor)
  * Ubah sektor          -> SEKTOR_LIST, SEKTOR_TYPE, SEKTOR_SHORT
  * Ubah rasio & acuan   -> BANK_RATIOS, BUS_RATIOS, ASR_RATIOS
  * Ubah akun komparasi  -> BANK_ACCOUNTS, BUS_ACCOUNTS, ASR_ACCOUNTS
  * Tahun laporan        -> TAHUN_LAPORAN
  * Ambang komparasi APOLO -> KOMPARASI_TOLERANSI_PCT
"""

import random
import pandas as pd

TAHUN_LAPORAN = 2025
TAHUN_PEMBANDING = TAHUN_LAPORAN - 1
DATA_LABEL = "Data Simulasi (Dummy)"

# Analisis Komparasi: angka di Laporan Keuangan (LK) dibandingkan dengan laporan
# terstruktur yang disampaikan ke OJK melalui APOLO (Laporan Tahunan).
SUMBER_LK = f"Laporan Keuangan Audited {TAHUN_LAPORAN}"
SUMBER_APOLO = f"Laporan Tahunan APOLO {TAHUN_LAPORAN}"
KOMPARASI_TOLERANSI_PCT = 5.0   # selisih > 5% dari nilai APOLO -> "Tidak Sesuai"

# ── Kategori entitas & sektor ─────────────────────────────────────────────────
ENTITAS_TYPES = {
    "BANK": "Bank Umum Konvensional",
    "BUS": "Bank Umum Syariah",
    "ASR": "Asuransi & Reasuransi",
}

SEKTOR_LIST = [
    "Bank BUMN",
    "Bank Swasta Nasional",
    "Bank Asing & Campuran",
    "Bank Pembangunan Daerah",
    "Bank Digital",
    "Bank Syariah",
    "Asuransi Umum",
    "Asuransi Jiwa & Reasuransi",
]

SEKTOR_TYPE = {
    "Bank BUMN": "BANK",
    "Bank Swasta Nasional": "BANK",
    "Bank Asing & Campuran": "BANK",
    "Bank Pembangunan Daerah": "BANK",
    "Bank Digital": "BANK",
    "Bank Syariah": "BUS",
    "Asuransi Umum": "ASR",
    "Asuransi Jiwa & Reasuransi": "ASR",
}

# Label pendek untuk sumbu grafik
SEKTOR_SHORT = {
    "Bank BUMN": "BUMN",
    "Bank Swasta Nasional": "Swasta Nas.",
    "Bank Asing & Campuran": "Asing/Campuran",
    "Bank Pembangunan Daerah": "BPD",
    "Bank Digital": "Digital",
    "Bank Syariah": "Syariah",
    "Asuransi Umum": "Asuransi Umum",
    "Asuransi Jiwa & Reasuransi": "Jiwa & Reas.",
}

# Kisaran total aset simulasi per sektor (Rp miliar)
SEKTOR_ASET = {
    "Bank BUMN": (450_000, 2_200_000),
    "Bank Swasta Nasional": (5_000, 150_000),
    "Bank Asing & Campuran": (10_000, 300_000),
    "Bank Pembangunan Daerah": (8_000, 200_000),
    "Bank Digital": (4_000, 40_000),
    "Bank Syariah": (6_000, 120_000),
    "Asuransi Umum": (500, 12_000),
    "Asuransi Jiwa & Reasuransi": (1_000, 40_000),
}
# Skala kasar untuk bank besar supaya urutan ukuran terlihat wajar (tetap simulasi)
ASET_HINT = {
    "BBCA": 1_500_000, "BRIS": 400_000, "PNBN": 230_000, "MEGA": 130_000,
    "BNGA": 330_000, "BDMN": 230_000, "NISP": 270_000, "BNLI": 270_000,
    "BNII": 170_000, "BTPN": 230_000, "BJBR": 200_000, "BJTM": 110_000,
}

# ── Emiten Perbankan & Asuransi di IDX ────────────────────────────────────────
IDX_EMITEN_LIST = [
    # Bank BUMN
    ("BBRI", "PT Bank Rakyat Indonesia (Persero) Tbk", "Bank BUMN"),
    ("BMRI", "PT Bank Mandiri (Persero) Tbk", "Bank BUMN"),
    ("BBNI", "PT Bank Negara Indonesia (Persero) Tbk", "Bank BUMN"),
    ("BBTN", "PT Bank Tabungan Negara (Persero) Tbk", "Bank BUMN"),

    # Bank Swasta Nasional
    ("BBCA", "PT Bank Central Asia Tbk", "Bank Swasta Nasional"),
    ("PNBN", "PT Bank Pan Indonesia Tbk", "Bank Swasta Nasional"),
    ("MEGA", "PT Bank Mega Tbk", "Bank Swasta Nasional"),
    ("BBMD", "PT Bank Mestika Dharma Tbk", "Bank Swasta Nasional"),
    ("BMAS", "PT Bank Maspion Indonesia Tbk", "Bank Swasta Nasional"),
    ("NOBU", "PT Bank Nationalnobu Tbk", "Bank Swasta Nasional"),
    ("MAYA", "PT Bank Mayapada Internasional Tbk", "Bank Swasta Nasional"),
    ("BSIM", "PT Bank Sinarmas Tbk", "Bank Swasta Nasional"),
    ("BABP", "PT Bank MNC Internasional Tbk", "Bank Swasta Nasional"),
    ("BNBA", "PT Bank Bumi Arta Tbk", "Bank Swasta Nasional"),
    ("BACA", "PT Bank Capital Indonesia Tbk", "Bank Swasta Nasional"),
    ("BVIC", "PT Bank Victoria International Tbk", "Bank Swasta Nasional"),
    ("BINA", "PT Bank Ina Perdana Tbk", "Bank Swasta Nasional"),
    ("MASB", "PT Bank Multiarta Sentosa Tbk", "Bank Swasta Nasional"),
    ("BGTG", "PT Bank Ganesha Tbk", "Bank Swasta Nasional"),
    ("AMAR", "PT Bank Amar Indonesia Tbk", "Bank Swasta Nasional"),

    # Bank Asing & Campuran
    ("BNGA", "PT Bank CIMB Niaga Tbk", "Bank Asing & Campuran"),
    ("BDMN", "PT Bank Danamon Indonesia Tbk", "Bank Asing & Campuran"),
    ("NISP", "PT Bank OCBC NISP Tbk", "Bank Asing & Campuran"),
    ("BNLI", "PT Bank Permata Tbk", "Bank Asing & Campuran"),
    ("BNII", "PT Bank Maybank Indonesia Tbk", "Bank Asing & Campuran"),
    ("BTPN", "PT Bank SMBC Indonesia Tbk", "Bank Asing & Campuran"),
    ("BBKP", "PT Bank KB Indonesia Tbk", "Bank Asing & Campuran"),
    ("MCOR", "PT Bank China Construction Bank Indonesia Tbk", "Bank Asing & Campuran"),
    ("SDRA", "PT Bank Woori Saudara Indonesia 1906 Tbk", "Bank Asing & Campuran"),
    ("BCIC", "PT Bank JTrust Indonesia Tbk", "Bank Asing & Campuran"),
    ("BSWD", "PT Bank of India Indonesia Tbk", "Bank Asing & Campuran"),
    ("DNAR", "PT Bank Oke Indonesia Tbk", "Bank Asing & Campuran"),

    # Bank Pembangunan Daerah
    ("BJBR", "PT Bank Pembangunan Daerah Jawa Barat dan Banten Tbk", "Bank Pembangunan Daerah"),
    ("BJTM", "PT Bank Pembangunan Daerah Jawa Timur Tbk", "Bank Pembangunan Daerah"),
    ("BEKS", "PT Bank Pembangunan Daerah Banten Tbk", "Bank Pembangunan Daerah"),

    # Bank Digital
    ("ARTO", "PT Bank Jago Tbk", "Bank Digital"),
    ("BBYB", "PT Bank Neo Commerce Tbk", "Bank Digital"),
    ("AGRO", "PT Bank Raya Indonesia Tbk", "Bank Digital"),
    ("BBHI", "PT Allo Bank Indonesia Tbk", "Bank Digital"),
    ("BBSI", "PT Krom Bank Indonesia Tbk", "Bank Digital"),

    # Bank Syariah
    ("BRIS", "PT Bank Syariah Indonesia Tbk", "Bank Syariah"),
    ("BTPS", "PT Bank BTPN Syariah Tbk", "Bank Syariah"),
    ("PNBS", "PT Bank Panin Dubai Syariah Tbk", "Bank Syariah"),
    ("BANK", "PT Bank Aladin Syariah Tbk", "Bank Syariah"),

    # Asuransi Umum
    ("ASRM", "PT Asuransi Ramayana Tbk", "Asuransi Umum"),
    ("ABDA", "PT Asuransi Bina Dana Arta Tbk", "Asuransi Umum"),
    ("AMAG", "PT Asuransi Multi Artha Guna Tbk", "Asuransi Umum"),
    ("ASBI", "PT Asuransi Bintang Tbk", "Asuransi Umum"),
    ("ASDM", "PT Asuransi Dayin Mitra Tbk", "Asuransi Umum"),
    ("ASJT", "PT Asuransi Jasa Tania Tbk", "Asuransi Umum"),
    ("ASMI", "PT Asuransi Maximus Graha Persada Tbk", "Asuransi Umum"),
    ("AHAP", "PT Asuransi Harta Aman Pratama Tbk", "Asuransi Umum"),
    ("LPGI", "PT Lippo General Insurance Tbk", "Asuransi Umum"),
    ("TUGU", "PT Asuransi Tugu Pratama Indonesia Tbk", "Asuransi Umum"),
    ("VINS", "PT Victoria Insurance Tbk", "Asuransi Umum"),
    ("YOII", "PT Asuransi Digital Bersama Tbk", "Asuransi Umum"),
    ("PNIN", "PT Paninvest Tbk", "Asuransi Umum"),

    # Asuransi Jiwa & Reasuransi
    ("LIFE", "PT MSIG Life Insurance Indonesia Tbk", "Asuransi Jiwa & Reasuransi"),
    ("JMAS", "PT Asuransi Jiwa Syariah Jasa Mitra Abadi Tbk", "Asuransi Jiwa & Reasuransi"),
    ("PNLF", "PT Panin Financial Tbk", "Asuransi Jiwa & Reasuransi"),
    ("MREI", "PT Maskapai Reasuransi Indonesia Tbk", "Asuransi Jiwa & Reasuransi"),
]

# ── Akun komparasi per jenis entitas: (nama akun, bobot terhadap total aset) ───
BANK_ACCOUNTS = [
    ("Kas & Penempatan pada Bank Indonesia", 0.08),
    ("Kredit yang Diberikan (Neto)", 0.62),
    ("Cadangan Kerugian Penurunan Nilai (CKPN)", 0.024),
    ("Dana Pihak Ketiga (Giro, Tabungan, Deposito)", 0.76),
    ("Pendapatan Bunga Bersih", 0.045),
    ("Beban Operasional Lainnya", 0.026),
    ("Laba Bersih Tahun Berjalan", 0.017),
    ("Total Ekuitas", 0.15),
]
BUS_ACCOUNTS = [
    ("Kas & Penempatan pada Bank Indonesia", 0.09),
    ("Pembiayaan Syariah (Neto)", 0.60),
    ("Cadangan Kerugian Penurunan Nilai (CKPN)", 0.025),
    ("Dana Simpanan Wadiah & Dana Syirkah Temporer", 0.78),
    ("Pendapatan Pengelolaan Dana sebagai Mudharib", 0.07),
    ("Beban Operasional Lainnya", 0.03),
    ("Laba Bersih Tahun Berjalan", 0.016),
    ("Total Ekuitas", 0.14),
]
ASR_ACCOUNTS = [
    ("Investasi (Deposito, Obligasi, Saham, Reksa Dana)", 0.62),
    ("Piutang Premi", 0.06),
    ("Aset Reasuransi", 0.10),
    ("Liabilitas Kontrak Asuransi (Cadangan Teknis)", 0.55),
    ("Pendapatan Premi Neto", 0.32),
    ("Beban Klaim Neto", 0.18),
    ("Hasil Investasi", 0.035),
    ("Laba Bersih Tahun Berjalan", 0.025),
    ("Total Ekuitas", 0.30),
]
ACCOUNTS_BY_TYPE = {"BANK": BANK_ACCOUNTS, "BUS": BUS_ACCOUNTS, "ASR": ASR_ACCOUNTS}

# ── Rasio per jenis entitas ───────────────────────────────────────────────────
# (key, nama rasio, kategori, acuan, kisaran sehat, kisaran bermasalah) — semua dalam %
# acuan: ("min", x) = minimal x%, ("max", x) = maksimal x%, ("range", a, b) = antara a–b%
BANK_RATIOS = [
    ("car", "KPMM / Capital Adequacy Ratio (CAR)", "Permodalan", ("min", 12.0), (15, 35), (9, 11.5)),
    ("npl", "Non Performing Loan (NPL) Gross", "Kualitas Aset", ("max", 5.0), (0.8, 3.8), (5.3, 8.5)),
    ("npl_net", "Non Performing Loan (NPL) Neto", "Kualitas Aset", ("max", 5.0), (0.3, 1.8), (5.1, 6.5)),
    ("ldr", "Loan to Deposit Ratio (LDR)", "Likuiditas", ("range", 84.0, 94.0), (84.5, 93.5), (97, 112)),
    ("lcr", "Liquidity Coverage Ratio (LCR)", "Likuiditas", ("min", 100.0), (130, 260), (86, 98)),
    ("nim", "Net Interest Margin (NIM)", "Rentabilitas", ("min", 3.0), (3.5, 7.5), (1.5, 2.8)),
    ("bopo", "Beban Operasional terhadap Pendapatan Operasional (BOPO)", "Efisiensi", ("max", 85.0), (55, 84), (88, 108)),
    ("roa", "Return on Asset (ROA)", "Rentabilitas", ("min", 1.25), (1.4, 3.6), (-1.5, 0.9)),
    ("roe", "Return on Equity (ROE)", "Rentabilitas", ("min", 5.0), (8, 20), (-6, 4)),
]
BUS_RATIOS = [
    ("car", "Kewajiban Penyediaan Modal Minimum (CAR)", "Permodalan", ("min", 12.0), (16, 40), (9, 11.5)),
    ("npl", "Non Performing Financing (NPF) Gross", "Kualitas Aset", ("max", 5.0), (1.0, 3.5), (5.3, 8.0)),
    ("npl_net", "Non Performing Financing (NPF) Neto", "Kualitas Aset", ("max", 5.0), (0.3, 1.5), (5.1, 6.2)),
    ("ldr", "Financing to Deposit Ratio (FDR)", "Likuiditas", ("range", 84.0, 94.0), (84.5, 93.5), (97, 110)),
    ("lcr", "Liquidity Coverage Ratio (LCR)", "Likuiditas", ("min", 100.0), (140, 280), (86, 98)),
    ("nim", "Net Operating Margin (NOM)", "Rentabilitas", ("min", 1.5), (1.8, 5.0), (0.2, 1.2)),
    ("bopo", "Beban Operasional terhadap Pendapatan Operasional (BOPO)", "Efisiensi", ("max", 85.0), (60, 84), (89, 110)),
    ("roa", "Return on Asset (ROA)", "Rentabilitas", ("min", 1.25), (1.3, 3.5), (-1.2, 0.8)),
    ("roe", "Return on Equity (ROE)", "Rentabilitas", ("min", 5.0), (7, 18), (-5, 4)),
]
ASR_RATIOS = [
    ("rbc", "Tingkat Solvabilitas / Risk Based Capital (RBC)", "Permodalan", ("min", 120.0), (180, 650), (95, 118)),
    ("liq", "Rasio Likuiditas", "Likuiditas", ("min", 100.0), (120, 260), (85, 98)),
    ("inv", "Rasio Kecukupan Investasi", "Investasi", ("min", 100.0), (110, 210), (80, 97)),
    ("loss", "Rasio Klaim (Loss Ratio)", "Underwriting", ("max", 70.0), (35, 66), (74, 95)),
    ("expense", "Rasio Beban Usaha (Expense Ratio)", "Efisiensi", ("max", 35.0), (18, 33), (37, 45)),
    ("combined", "Combined Ratio", "Underwriting", ("max", 100.0), (78, 97), (102, 118)),
    ("roa", "Return on Asset (ROA)", "Rentabilitas", ("min", 1.0), (1.5, 6.5), (-3, 0.5)),
    ("roe", "Return on Equity (ROE)", "Rentabilitas", ("min", 5.0), (6, 16), (-8, 3)),
]
RATIOS_BY_TYPE = {"BANK": BANK_RATIOS, "BUS": BUS_RATIOS, "ASR": ASR_RATIOS}

# Rasio yang diringkas di tab "Rasio Keuangan" beranda: (key, label, tipe entitas)
PORTFOLIO_RATIO_SUMMARY = [
    ("car", "KPMM / CAR", ("BANK", "BUS")),
    ("npl", "NPL / NPF Gross", ("BANK", "BUS")),
    ("ldr", "LDR / FDR", ("BANK", "BUS")),
    ("bopo", "BOPO", ("BANK", "BUS")),
    ("roa", "Return on Asset (ROA) Bank", ("BANK", "BUS")),
    ("rbc", "Risk Based Capital (RBC)", ("ASR",)),
    ("loss", "Rasio Klaim (Loss Ratio)", ("ASR",)),
    ("combined", "Combined Ratio", ("ASR",)),
]

# ── Checklist kepatuhan (sama dengan pipeline) ────────────────────────────────
# Bank & asuransi tercatat = emiten, jadi memakai filter checklist "EPP".
CHECKLIST_ENTITAS = "EPP"
MASTER_CHECKLIST = [
    {"no": 2,  "komponen": "Validasi Format & Audit",          "entitas": "ALL",         "kriteria": "Potensi Anomali Halaman Hilang / Mismatch", "catatan_ok": "Urutan halaman konsisten"},
    {"no": 3,  "komponen": "Validasi Format & Audit",          "entitas": "RD",          "kriteria": "Nama Reksa Dana sesuai dengan Pernyataan Efektif beserta Perubahan Terakhir", "catatan_ok": "Nama sesuai pernyataan efektif"},
    {"no": 4,  "komponen": "Validasi Format & Audit",          "entitas": "RD",          "kriteria": "Nama Reksa Dana mencerminkan nama Manajer Investasi", "catatan_ok": "Nama mencerminkan nama MI"},
    {"no": 5,  "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "EPP, MI",     "kriteria": "Tanda Tangan Seluruh Direksi", "catatan_ok": "Tercantum tanda tangan direksi lengkap", "min_skor": 80, "gagal": "PERLU REVIU", "catatan_gagal": "Tanda tangan direksi tidak lengkap / tidak ditemukan"},
    {"no": 6,  "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "EPP, MI",     "kriteria": "Tanda Tangan Satu Orang Komisaris", "catatan_ok": "Tercantum tanda tangan komisaris", "min_skor": 75, "gagal": "PERLU REVIU", "catatan_gagal": "Tanda tangan komisaris tidak ditemukan"},
    {"no": 7,  "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "DES",         "kriteria": "Tanda Tangan Direksi", "catatan_ok": "Tanda tangan direksi lengkap"},
    {"no": 8,  "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "DES",         "kriteria": "Tanda Tangan Komisaris", "catatan_ok": "Tanda tangan komisaris lengkap"},
    {"no": 9,  "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "RD",          "kriteria": "Tanda Tangan Anggota Direksi Manajer Investasi", "catatan_ok": "Tercantum tanda tangan Direksi MI"},
    {"no": 10, "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "RD",          "kriteria": "Tanda Tangan Penanggung Jawab Bank Kustodian", "catatan_ok": "Tanda tangan Kustodian lengkap"},
    {"no": 11, "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "ALL",         "kriteria": "Materai", "catatan_ok": "Materai terverifikasi"},
    {"no": 12, "komponen": "Surat Pernyataan Tanggung Jawab",  "entitas": "ALL",         "kriteria": "Pernyataan tanggung jawab atas sistem pengendalian internal", "catatan_ok": "Klausul SPI disajikan lengkap"},
    {"no": 13, "komponen": "Komponen Laporan Keuangan",        "entitas": "ALL",         "kriteria": "Laporan Posisi Keuangan", "catatan_ok": "Laporan Posisi Keuangan disajikan"},
    {"no": 14, "komponen": "Komponen Laporan Keuangan",        "entitas": "ALL",         "kriteria": "Laporan Laba Rugi dan Penghasilan Komprehensif Lain", "catatan_ok": "Laporan Laba Rugi disajikan"},
    {"no": 15, "komponen": "Komponen Laporan Keuangan",        "entitas": "ALL",         "kriteria": "Laporan Arus Kas", "catatan_ok": "Laporan Arus Kas disajikan"},
    {"no": 16, "komponen": "Komponen Laporan Keuangan",        "entitas": "ALL",         "kriteria": "Laporan Perubahan Ekuitas", "catatan_ok": "Laporan Perubahan Ekuitas disajikan"},
    {"no": 17, "komponen": "Komponen Laporan Keuangan",        "entitas": "ALL",         "kriteria": "Catatan Atas Laporan Keuangan (CaLK)", "catatan_ok": "CaLK disajikan lengkap", "min_skor": 70, "gagal": "PERLU REVIU", "catatan_gagal": "Beberapa pengungkapan CaLK penting tidak lengkap"},
    {"no": 18, "komponen": "Komponen Laporan Keuangan",        "entitas": "RD",          "kriteria": "Periode tahun buku 1 Januari - 31 Desember", "catatan_ok": "Periode buku sesuai ketentuan"},
    {"no": 19, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Opini atau Hasil Reviu Auditor", "catatan_ok": "Opini Wajar Tanpa Modifikasian", "min_skor": 70, "gagal": "TIDAK PATUH", "catatan_gagal": "Opini dengan modifikasian (Wajar Dengan Pengecualian)"},
    {"no": 20, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Hal Audit Utama", "catatan_ok": "Tercantum Hal Audit Utama (KAM)"},
    {"no": 21, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Paragraf Kelangsungan Usaha", "catatan_ok": "Tidak terdapat ketidakpastian material kelangsungan usaha", "min_skor": 65, "gagal": "TIDAK PATUH", "catatan_gagal": "Terdapat paragraf ketidakpastian material kelangsungan usaha"},
    {"no": 22, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Paragraf Respon dan Komunikasi Audit", "catatan_ok": "Komunikasi audit disajikan"},
    {"no": 23, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Paragraf Informasi Lain", "catatan_ok": "Paragraf informasi lain tercantum"},
    {"no": 24, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Paragraf Tanggung Jawab Manajemen", "catatan_ok": "Tanggung jawab manajemen disajikan"},
    {"no": 25, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Paragraf Tanggung Jawab Auditor", "catatan_ok": "Tanggung jawab auditor disajikan"},
    {"no": 26, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Nama Kantor Akuntan Publik", "catatan_ok": "KAP terdaftar di OJK"},
    {"no": 27, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Nama Akuntan Publik", "catatan_ok": "Nama AP tercantum"},
    {"no": 28, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Nomor dan Tanggal Laporan Auditor Independen", "catatan_ok": "Nomor & tanggal laporan auditor tercantum"},
    {"no": 29, "komponen": "Laporan Auditor",                  "entitas": "EPP, MI, RD", "kriteria": "Periode Penugasan AP", "catatan_ok": "Masa penugasan sesuai ketentuan OJK"},
]


# ── Generator daftar perusahaan ───────────────────────────────────────────────
def _generate_companies():
    rng = random.Random(42)  # seed tetap -> data selalu sama
    companies = []
    k_analyzed = 0
    for idx, (ticker, nama, sektor) in enumerate(IDX_EMITEN_LIST, start=1):
        analyzed = (idx % 3 != 0)  # ±2/3 laporan sudah dianalisis
        if analyzed:
            pattern = k_analyzed % 7
            k_analyzed += 1
            if pattern == 3:
                status_kepatuhan, ml_risk = "Tidak Patuh", "Terindikasi Anomali"
                skor = round(rng.uniform(55.0, 74.0), 1)
                mismatch_count = rng.choice([3, 4, 5])
                calk_risk_count = rng.choice([3, 4])
            elif pattern in (1, 5):
                status_kepatuhan, ml_risk = "Perlu Reviu", "Risiko Sedang"
                skor = round(rng.uniform(75.0, 87.0), 1)
                mismatch_count = rng.choice([1, 2, 3])
                calk_risk_count = rng.choice([2, 3])
            else:
                status_kepatuhan, ml_risk = "Patuh", "Risiko Rendah"
                skor = round(rng.uniform(88.0, 98.5), 1)
                mismatch_count = rng.choice([0, 0, 1])
                calk_risk_count = rng.choice([0, 1])
        else:
            status_kepatuhan, ml_risk, skor = "Belum Dianalisis", "Belum Dianalisis", None
            mismatch_count = calk_risk_count = 0

        lo, hi = SEKTOR_ASET[sektor]
        aset = ASET_HINT[ticker] * rng.uniform(0.9, 1.1) if ticker in ASET_HINT else rng.uniform(lo, hi)

        companies.append({
            "id": f"IDX-{ticker}",
            "ticker": ticker,
            "nama": nama,
            "sektor": sektor,
            "entitas_type": SEKTOR_TYPE[sektor],
            "tahun": TAHUN_LAPORAN,
            "status_analisis": "Sudah Dianalisis" if analyzed else "Belum Dianalisis",
            "status_kepatuhan": status_kepatuhan,
            "skor_kepatuhan": skor,
            "ml_risk": ml_risk,
            "mismatch_count": mismatch_count,
            "calk_risk_count": calk_risk_count,
            "total_aset_miliar": round(aset, 2),
        })
    return companies


ALL_COMPANIES = _generate_companies()
COMPANY_BY_ID = {c["id"]: c for c in ALL_COMPANIES}
ANALYZED_COMPANIES = [c for c in ALL_COMPANIES if c["status_analisis"] == "Sudah Dianalisis"]

# Perusahaan default (dipakai halaman modul bila belum ada perusahaan dipilih)
# -> perusahaan pertama yang sudah dianalisis dengan status "Patuh"
DEFAULT_COMPANY_ID = next((c["id"] for c in ANALYZED_COMPANIES if c["status_kepatuhan"] == "Patuh"),
                          ANALYZED_COMPANIES[0]["id"])


# ── Generator detail per perusahaan ───────────────────────────────────────────
def _fmt_pct(v):
    return f"{v:.2f}%"


def _acuan_text(acuan):
    if acuan[0] == "min":
        return f"≥ {acuan[1]:g}%"
    if acuan[0] == "max":
        return f"≤ {acuan[1]:g}%"
    return f"{acuan[1]:g}% – {acuan[2]:g}%"


def _memenuhi(acuan, v):
    if acuan[0] == "min":
        return v >= acuan[1]
    if acuan[0] == "max":
        return v <= acuan[1]
    return acuan[1] <= v <= acuan[2]


def _checklist_for(company):
    skor = company["skor_kepatuhan"]
    rows = []
    for item in MASTER_CHECKLIST:
        ent_list = [e.strip() for e in item["entitas"].split(",")]
        if "ALL" not in ent_list and CHECKLIST_ENTITAS not in ent_list:
            continue
        ok = ("min_skor" not in item) or (skor is not None and skor > item["min_skor"])
        rows.append({
            "no": item["no"], "komponen": item["komponen"], "entitas": item["entitas"],
            "kriteria": item["kriteria"],
            "status": "PATUH" if ok else item["gagal"],
            "catatan": item["catatan_ok"] if ok else item["catatan_gagal"],
        })
    return rows


def _komparasi_for(company, rng):
    """Bandingkan nilai akun di LK dengan nilai di Laporan Tahunan APOLO (simulasi)."""
    accounts = ACCOUNTS_BY_TYPE[company["entitas_type"]]
    aset = company["total_aset_miliar"]
    n_mm = min(company["mismatch_count"], len(accounts))
    mm_idx = set(rng.sample(range(len(accounts)), n_mm))
    items = []
    for i, (akun, bobot) in enumerate(accounts):
        v_lk = aset * bobot * rng.uniform(0.85, 1.15)
        if i in mm_idx:
            # selisih material: lebih dari ambang toleransi
            d = rng.choice([1, -1]) * rng.uniform(KOMPARASI_TOLERANSI_PCT + 0.6, 22.0)
        elif rng.random() < 0.6:
            d = 0.0                                   # sama persis
        else:
            d = rng.choice([1, -1]) * rng.uniform(0.05, 2.5)   # selisih kecil (pembulatan/reklasifikasi)
        v_apolo = v_lk / (1 + d / 100)
        selisih = v_lk - v_apolo
        pct = selisih / v_apolo * 100 if v_apolo else 0.0
        items.append({
            "akun": akun,
            "val_lk": f"{v_lk:,.1f} M", "val_apolo": f"{v_apolo:,.1f} M",
            "selisih_pct": f"{pct:+.2f}%",
            "mismatch": abs(pct) > KOMPARASI_TOLERANSI_PCT,
            "num_lk": round(v_lk, 2), "num_apolo": round(v_apolo, 2),
            "selisih": round(selisih, 2), "pct": round(pct, 2),
        })
    return items


def _rasio_for(company, rng):
    defs = RATIOS_BY_TYPE[company["entitas_type"]]
    n_bad = {"Tidak Patuh": 3, "Perlu Reviu": 1}.get(company["status_kepatuhan"], 0)
    bad_idx = set(rng.sample(range(len(defs)), n_bad))
    items, vals = [], {}
    for i, (key, nama, kategori, acuan, sehat, buruk) in enumerate(defs):
        v_y = rng.uniform(*(buruk if i in bad_idx else sehat))
        v_y1 = rng.uniform(*sehat) if i in bad_idx else v_y * rng.uniform(0.88, 1.10)
        ok = _memenuhi(acuan, v_y)
        items.append({
            "key": key, "nama": nama, "kategori": kategori,
            "nilai_y": _fmt_pct(v_y), "nilai_y1": _fmt_pct(v_y1),
            "num_y": round(v_y, 4), "num_y1": round(v_y1, 4),
            "benchmark": _acuan_text(acuan),
            "status": "Sehat" if ok else "Perlu Perhatian",
        })
        vals[key] = (v_y, v_y1, ok)
    return items, vals


def _calk_for(company, vals, rng):
    etype = company["entitas_type"]
    crc = company["calk_risk_count"]
    hal = lambda: f"hal {rng.randint(40, 180)}"

    def lvl(high_if, mid_if):
        return "Tinggi" if high_if else ("Sedang" if mid_if else "Rendah")

    if etype in ("BANK", "BUS"):
        npl_y, npl_y1, npl_ok = vals["npl"]
        label_npl = "NPF gross" if etype == "BUS" else "NPL gross"
        produk = "pembiayaan" if etype == "BUS" else "kredit"
        restru = rng.uniform(6, 14) if crc >= 3 else rng.uniform(1.5, 6)
        pihak_terkait = rng.uniform(9.0, 12.5) if crc >= 3 else rng.uniform(1.0, 6.0)
        findings = [
            ("Kualitas Kredit & Kecukupan CKPN", f"Catatan {rng.randint(9, 13)}", f"{produk.title()} yang Diberikan",
             f"Rasio {label_npl} tercatat {npl_y:.2f}% (tahun lalu {npl_y1:.2f}%); porsi {produk} Stage 2 dan Stage 3 serta kecukupan CKPN sesuai PSAK 71 perlu dicermati.",
             "Uji kecukupan CKPN atas debitur Stage 3 dan nilai agunan.", "Risiko Kualitas Aset",
             lvl(not npl_ok, crc >= 2)),
            ("Restrukturisasi Kredit", f"Catatan {rng.randint(10, 14)}", f"Restrukturisasi {produk.title()}",
             f"Saldo {produk} restrukturisasi sebesar {restru:.1f}% dari total {produk}, terkonsentrasi pada segmen UMKM dan perdagangan.",
             f"Pantau kolektibilitas {produk} restrukturisasi dan potensi pemburukan.", "Risiko Kredit Bermasalah Lanjutan",
             lvl(restru > 10, crc >= 3)),
            ("Transaksi Pihak Berelasi", f"Catatan {rng.randint(38, 45)}", "Transaksi Pihak Berelasi",
             f"Penyediaan dana kepada pihak terkait sebesar {pihak_terkait:.1f}% dari modal bank; perlu dipastikan dalam batas BMPK pihak terkait (10% modal) dan dengan syarat wajar.",
             "Konfirmasi kepatuhan BMPK dan kewajaran syarat transaksi.", "Risiko Konsentrasi & BMPK",
             lvl(pihak_terkait > 10, pihak_terkait > 8)),
            ("Liabilitas Kontinjensi & Perkara Hukum", f"Catatan {rng.randint(46, 52)}", "Komitmen & Kontinjensi",
             "Terdapat gugatan hukum dari nasabah/debitur dan garansi bank yang diterbitkan; manajemen menilai belum perlu pembentukan provisi.",
             "Monitoring perkembangan perkara dan potensi kewajiban.", "Potensi Kewajiban Kontinjensi",
             lvl(crc >= 4, crc >= 2)),
            ("Peristiwa Setelah Periode Pelaporan", f"Catatan {rng.randint(53, 58)}", "Peristiwa Setelah Periode Pelaporan",
             "Rencana pembagian dividen tunai dan penerbitan obligasi subordinasi yang disetujui setelah tanggal laporan posisi keuangan.",
             "Pastikan keterbukaan informasi telah disampaikan.", "Dampak pada Permodalan Pasca Periode",
             "Rendah"),
        ]
    else:
        loss_y, loss_y1, loss_ok = vals["loss"]
        rbc_y, _, rbc_ok = vals["rbc"]
        findings = [
            ("Kecukupan Cadangan Teknis Asuransi", f"Catatan {rng.randint(15, 19)}", "Liabilitas Kontrak Asuransi",
             f"Liabilitas kontrak asuransi diukur sesuai PSAK 117; tingkat solvabilitas (RBC) {rbc_y:.0f}% dan uji kecukupan liabilitas oleh aktuaris perlu ditelaah.",
             "Telaah asumsi aktuaria dan kecukupan cadangan teknis.", "Risiko Kecukupan Cadangan",
             lvl(not rbc_ok, crc >= 3)),
            ("Klaim dalam Proses & Sengketa Klaim", f"Catatan {rng.randint(20, 24)}", "Klaim & Manfaat",
             f"Rasio klaim {loss_y:.1f}% (tahun lalu {loss_y1:.1f}%); terdapat klaim dalam proses yang masih disengketakan dengan tertanggung.",
             "Pantau penyelesaian klaim dan kecukupan estimasi klaim.", "Risiko Underwriting & Klaim",
             lvl(not loss_ok, crc >= 2)),
            ("Piutang Reasuransi Bermasalah", f"Catatan {rng.randint(8, 12)}", "Piutang & Aset Reasuransi",
             "Piutang reasuransi berumur lebih dari 90 hari meningkat dibanding tahun lalu; cadangan penurunan nilai perlu dievaluasi.",
             "Evaluasi kolektibilitas piutang reasuransi.", "Risiko Kredit Reasuradur",
             lvl(crc >= 4, crc >= 2)),
            ("Transaksi Pihak Berelasi", f"Catatan {rng.randint(30, 36)}", "Transaksi Pihak Berelasi",
             "Penempatan investasi dan polis kumpulan dengan entitas sepengendali; kewajaran syarat transaksi perlu dipastikan.",
             "Konfirmasi kewajaran syarat transaksi pihak berelasi.", "Risiko Konsentrasi Investasi",
             lvl(crc >= 4, crc >= 3)),
            ("Liabilitas Kontinjensi & Perkara Hukum", f"Catatan {rng.randint(37, 42)}", "Komitmen & Kontinjensi",
             "Terdapat gugatan tertanggung terkait penolakan klaim; manajemen menilai belum perlu pembentukan provisi.",
             "Monitoring perkembangan perkara.", "Potensi Kewajiban Kontinjensi",
             lvl(crc >= 4, crc >= 2)),
        ]

    out = []
    for topik, ref, kategori, temuan, ket, implikasi, risiko in findings:
        out.append({
            "referensi": ref, "kategori": kategori, "topik": topik,
            "temuan_ai": temuan, "temuan": temuan, "ringkasan": temuan,
            "catatan_keterangan": ket, "implikasi": implikasi,
            "kategori_risiko": risiko, "halaman": hal(),
        })
    return out


def _ml_for(company, rng):
    risk = company["ml_risk"]
    anomali = risk == "Terindikasi Anomali"
    sedang = risk == "Risiko Sedang"
    benford = 1 if (anomali and rng.random() < 0.8) or (sedang and rng.random() < 0.25) else 0
    beneish = 1 if (anomali and rng.random() < 0.6) or (sedang and rng.random() < 0.2) else 0
    iforest = 1 if anomali or (sedang and rng.random() < 0.6) else 0
    return {
        "ensemble_pred": 1 if anomali else 0,
        "risk_label": risk,
        "probabilitas": round(rng.uniform(0.72, 0.93) if anomali else (rng.uniform(0.35, 0.55) if sedang else rng.uniform(0.04, 0.2)), 2),
        "votes": {"benford": benford, "beneish": beneish, "iforest": iforest},
        "benford_mad": round(rng.uniform(0.016, 0.025) if benford else rng.uniform(0.004, 0.011), 4),
        "beneish_score": round(rng.uniform(-1.6, -1.0) if beneish else rng.uniform(-3.0, -2.3), 2),
    }


_DEEP_CACHE = {}


def get_mock_company_deep_dive(comp_id):
    """Detail simulasi untuk 1 perusahaan (deterministik per ticker)."""
    company = COMPANY_BY_ID.get(comp_id) or COMPANY_BY_ID[DEFAULT_COMPANY_ID]
    if company["id"] in _DEEP_CACHE:
        return _DEEP_CACHE[company["id"]]

    rng = random.Random(f"{company['ticker']}-{TAHUN_LAPORAN}")
    etype = company["entitas_type"]
    status_kp = company["status_kepatuhan"]
    kompar_items = _komparasi_for(company, rng)
    rasio_items, vals = _rasio_for(company, rng)
    calk_findings = _calk_for(company, vals, rng)
    ml = _ml_for(company, rng)
    n_mm = sum(1 for i in kompar_items if i["mismatch"])
    n_warn = sum(1 for r in rasio_items if r["status"] != "Sehat")

    if etype in ("BANK", "BUS"):
        rekomendasi = [
            "Lakukan uji kecukupan CKPN atas kredit/pembiayaan Stage 2 dan Stage 3.",
            "Pastikan penyediaan dana kepada pihak terkait berada dalam batas BMPK.",
            "Pantau pemenuhan rasio permodalan (KPMM) dan likuiditas (LCR/NSFR) sesuai ketentuan OJK.",
        ]
    else:
        rekomendasi = [
            "Telaah kecukupan cadangan teknis dan asumsi aktuaria sesuai PSAK 117.",
            "Pantau tingkat solvabilitas (RBC) agar tetap di atas batas minimum 120%.",
            "Evaluasi kolektibilitas piutang reasuransi dan penyelesaian klaim dalam sengketa.",
        ]

    status_label = status_kp.upper() if status_kp != "Belum Dianalisis" else "PERLU REVIU"
    deep = {
        "file_name": f"{company['ticker']}_LK_Tahunan_{TAHUN_LAPORAN}.pdf",
        "doc_meta": {
            "nama_entitas": company["nama"],
            "tahun": company["tahun"],
            "periode": f"Tahunan {TAHUN_LAPORAN} (Audit)",
            "sektor": company["sektor"],
            "mata_uang": "IDR Miliar",
        },
        "kepatuhan": {
            "skor": company["skor_kepatuhan"] or 90.0,
            "status": status_label,
            "penjelasan": f"Laporan keuangan {company['nama']} secara umum berstatus {status_kp.lower()} terhadap ketentuan penyajian laporan keuangan emiten sektor jasa keuangan.",
            "checklist": _checklist_for(company),
        },
        "komparasi": {
            "mismatch_count": n_mm,
            "summary": (f"Ditemukan {n_mm} dari {len(kompar_items)} akun yang nilainya tidak sesuai antara LK dan {SUMBER_APOLO} "
                        f"(selisih > {KOMPARASI_TOLERANSI_PCT:g}%)." if n_mm
                        else f"Seluruh {len(kompar_items)} akun di LK sesuai dengan {SUMBER_APOLO} (selisih ≤ {KOMPARASI_TOLERANSI_PCT:g}%)."),
            "items": kompar_items,
        },
        "rasio": {"items": rasio_items, "n_perhatian": n_warn},
        "calk": {
            "narrative": f"Pengungkapan Catatan atas Laporan Keuangan {company['nama']} mencakup "
                         + ", ".join(f["topik"].lower() for f in calk_findings[:4]) + ".",
            "findings": calk_findings,
        },
        "ml_voting": ml,
        "kesimpulan": {
            "ringkasan": f"Hasil evaluasi {company['nama']} menunjukkan status {status_kp} dengan klasifikasi risiko ML {company['ml_risk']}.",
            "rekomendasi": rekomendasi,
        },
    }
    _DEEP_CACHE[company["id"]] = deep
    return deep


# ── Agregat Ringkasan Portofolio (dihitung dari data perusahaan di atas) ──────
def _pct(n, total):
    return round(n / total * 100, 1) if total else 0.0


def get_portfolio_summary():
    """Summary KPI metrics for top hero banner."""
    df = pd.DataFrame(ALL_COMPANIES)
    total_lk = len(df)
    analyzed_df = df[df["status_analisis"] == "Sudah Dianalisis"]
    num_analyzed = len(analyzed_df)

    patuh_count = int((analyzed_df["status_kepatuhan"] == "Patuh").sum())
    reviu_count = int((analyzed_df["status_kepatuhan"] == "Perlu Reviu").sum())
    tidak_patuh_count = int((analyzed_df["status_kepatuhan"] == "Tidak Patuh").sum())
    anomali_ml_count = int((analyzed_df["ml_risk"] == "Terindikasi Anomali").sum())

    return {
        "total_lk": total_lk,
        "num_analyzed": num_analyzed,
        "num_pending": total_lk - num_analyzed,
        "pct_analyzed": _pct(num_analyzed, total_lk),
        "patuh_count": patuh_count,
        "reviu_count": reviu_count,
        "tidak_patuh_count": tidak_patuh_count,
        "pct_patuh": _pct(patuh_count, num_analyzed),
        "pct_reviu": _pct(reviu_count, num_analyzed),
        "pct_tidak_patuh": _pct(tidak_patuh_count, num_analyzed),
        "anomali_ml_count": anomali_ml_count,
        "pct_anomali_ml": _pct(anomali_ml_count, num_analyzed),
        "avg_score": round(analyzed_df["skor_kepatuhan"].mean(), 1) if num_analyzed else 0.0,
    }


def get_kepatuhan_portfolio_data():
    """Modul 1: distribusi status + kriteria checklist yang paling sering tidak terpenuhi."""
    df = pd.DataFrame(ANALYZED_COMPANIES)
    status_counts = df["status_kepatuhan"].value_counts().to_dict() if len(df) else {}

    n = len(ANALYZED_COMPANIES)
    counter = {}
    for c in ANALYZED_COMPANIES:
        for item in get_mock_company_deep_dive(c["id"])["kepatuhan"]["checklist"]:
            if item["status"] != "PATUH":
                key = (item["kriteria"], item["komponen"])
                counter[key] = counter.get(key, 0) + 1
    issues = sorted(counter.items(), key=lambda kv: -kv[1])[:6]
    frequent_checklist_issues = [
        {"kriteria": k[0], "komponen": k[1], "non_compliant_count": v, "pct": _pct(v, n)}
        for k, v in issues
    ]
    return {"status_counts": status_counts, "frequent_checklist_issues": frequent_checklist_issues}


def get_komparasi_portfolio_data():
    """Modul 2: akun tidak sesuai (LK vs APOLO) per sektor + akun yang paling sering tidak sesuai."""
    n = len(ANALYZED_COMPANIES)
    mismatch_by_sektor = {s: 0 for s in SEKTOR_LIST}
    counter = {}
    for c in ANALYZED_COMPANIES:
        for item in get_mock_company_deep_dive(c["id"])["komparasi"]["items"]:
            if item["mismatch"]:
                mismatch_by_sektor[c["sektor"]] += 1
                counter[item["akun"]] = counter.get(item["akun"], 0) + 1
    top = sorted(counter.items(), key=lambda kv: -kv[1])[:5]
    mismatch_categories = []
    for akun, flags in top:
        pct = _pct(flags, n)
        severity = "Tinggi" if pct >= 15 else ("Sedang" if pct >= 7 else "Rendah")  # porsi LK terdampak
        mismatch_categories.append({"akun": akun, "flags": flags, "pct": pct, "severity": severity})
    return {"mismatch_by_sektor": mismatch_by_sektor, "mismatch_categories": mismatch_categories}


def get_rasio_portfolio_data():
    """Modul 3: sebaran rasio utama bank & asuransi + persentase yang memenuhi acuan."""
    ratios_summary = []
    for key, label, types in PORTFOLIO_RATIO_SUMMARY:
        values, ok = [], 0
        kategori = "-"
        for c in ANALYZED_COMPANIES:
            if c["entitas_type"] not in types:
                continue
            for r in get_mock_company_deep_dive(c["id"])["rasio"]["items"]:
                if r["key"] == key:
                    values.append(r["num_y"])
                    ok += r["status"] == "Sehat"
                    kategori = r["kategori"]
        if not values:
            continue
        healthy = _pct(ok, len(values))
        ratios_summary.append({
            "rasio": label, "kategori": kategori,
            "mean": _fmt_pct(sum(values) / len(values)),
            "min": _fmt_pct(min(values)), "max": _fmt_pct(max(values)),
            "healthy_pct": healthy, "warning_pct": round(100 - healthy, 1),
        })
    return {"ratios_summary": ratios_summary}


CALK_THEME_DESC = {
    "Kualitas Kredit & Kecukupan CKPN": "Kenaikan kredit/pembiayaan bermasalah (Stage 2–3) dan kecukupan CKPN sesuai PSAK 71.",
    "Restrukturisasi Kredit": "Porsi kredit/pembiayaan restrukturisasi yang masih tinggi dan berpotensi memburuk.",
    "Transaksi Pihak Berelasi": "Penyediaan dana atau investasi kepada pihak terkait yang mendekati batas BMPK / perlu uji kewajaran.",
    "Liabilitas Kontinjensi & Perkara Hukum": "Gugatan hukum nasabah/tertanggung dan garansi yang belum dicadangkan.",
    "Kecukupan Cadangan Teknis Asuransi": "Pengukuran liabilitas kontrak asuransi (PSAK 117) dan tingkat solvabilitas (RBC).",
    "Klaim dalam Proses & Sengketa Klaim": "Rasio klaim meningkat dan klaim yang masih disengketakan dengan tertanggung.",
    "Piutang Reasuransi Bermasalah": "Piutang reasuransi berumur > 90 hari yang memerlukan evaluasi penurunan nilai.",
}


def _build_calk_theme_details():
    details = {}
    for c in ANALYZED_COMPANIES:
        for f in get_mock_company_deep_dive(c["id"])["calk"]["findings"]:
            if f["kategori_risiko"] not in ("Tinggi", "Sedang") or f["topik"] not in CALK_THEME_DESC:
                continue
            details.setdefault(f["topik"], []).append({
                "ticker": c["ticker"], "nama": c["nama"], "temuan": f["temuan_ai"],
                "halaman": f["halaman"],
                "status": "Terindikasi Anomali" if f["kategori_risiko"] == "Tinggi" else "Perlu Reviu",
                "_risk": f["kategori_risiko"],
            })
    for rows in details.values():
        rows.sort(key=lambda r: r["_risk"] != "Tinggi")
    return details


CALK_THEME_DETAILS = _build_calk_theme_details()


def get_calk_portfolio_data():
    """Modul 4: tema CaLK berisiko yang paling sering muncul."""
    themes = []
    for topik, rows in CALK_THEME_DETAILS.items():
        n_high = sum(1 for r in rows if r["_risk"] == "Tinggi")
        themes.append({
            "topik": topik, "count": len(rows),
            "risk": "Tinggi" if n_high >= 2 else "Sedang",
            "desc": CALK_THEME_DESC[topik],
        })
    themes.sort(key=lambda t: -t["count"])
    return {"calk_risk_themes": themes[:5]}


def get_ml_portfolio_data():
    """Modul 5: distribusi risiko ML + jumlah deteksi per sub-model."""
    df = pd.DataFrame(ANALYZED_COMPANIES)
    ml_risk_counts = df["ml_risk"].value_counts().to_dict() if len(df) else {}
    n = len(ANALYZED_COMPANIES)
    totals = {"benford": 0, "beneish": 0, "iforest": 0, "ensemble": 0}
    for c in ANALYZED_COMPANIES:
        ml = get_mock_company_deep_dive(c["id"])["ml_voting"]
        for k in ("benford", "beneish", "iforest"):
            totals[k] += ml["votes"][k]
        totals["ensemble"] += ml["ensemble_pred"]
    labels = [
        ("benford", "Benford's Law (First-Digit Anomaly)"),
        ("beneish", "Beneish M-Score (Earnings Manipulation)"),
        ("iforest", "Isolation Forest (Multivariate Outlier)"),
        ("ensemble", "Ensemble Voting (Consensus Risk High)"),
    ]
    submodel_breakdown = [
        {"model": lbl, "anomaly_count": totals[k], "pct": _pct(totals[k], n)} for k, lbl in labels
    ]
    return {"ml_risk_counts": ml_risk_counts, "submodel_breakdown": submodel_breakdown}


# ── Store lengkap untuk halaman modul 1–6 ─────────────────────────────────────
def build_full_pipeline_store(comp_id=None):
    """
    Bentuk data 'home-pipeline-result' yang kompatibel dengan seluruh halaman modul:
    1_kepatuhan, 2_komparasi, 3_rasio, 4_calk, 5_ml_voting, 6_kesimpulan.
    """
    company = COMPANY_BY_ID.get(comp_id) or COMPANY_BY_ID[DEFAULT_COMPANY_ID]
    deep = get_mock_company_deep_dive(company["id"])
    ticker = company["ticker"]
    q_curr, q_prev = str(TAHUN_LAPORAN), str(TAHUN_PEMBANDING)

    meta = {
        "nama_entitas": company["nama"],
        "jenis_laporan": "Laporan Keuangan Audited",
        "periode_laporan": f"Tahunan {TAHUN_LAPORAN}",
        "sektor": company["sektor"],
    }

    checklist_rows = [
        {
            "No": item["no"],
            "Komponen": item["komponen"],
            "Entitas": item.get("entitas", "ALL"),
            "Kriteria Pemeriksaan": item["kriteria"],
            "Status": "YA" if item["status"] == "PATUH" else "TIDAK",
            "Hasil AI": "Sesuai Pedoman OJK" if item["status"] == "PATUH" else "Ditemukan Deviasi / Ketidaksesuaian",
            "Halaman": f"hal {item['no'] * 2}",
            "Catatan AI": item["catatan"],
        }
        for item in deep["kepatuhan"]["checklist"]
    ]
    ya_cnt = sum(1 for r in checklist_rows if r["Status"] == "YA")
    tidak_cnt = sum(1 for r in checklist_rows if r["Status"] == "TIDAK")

    calk_findings = deep["calk"]["findings"]

    kompar_rows = [
        {"akun": i["akun"], "nilai_lk": i["num_lk"], "nilai_apolo": i["num_apolo"],
         "selisih": i["selisih"], "pct": i["pct"], "mismatch": i["mismatch"]}
        for i in deep["komparasi"]["items"]
    ]
    mismatches = [r for r in kompar_rows if r["mismatch"]]

    rasio_rows = [
        {
            "no": idx + 1,
            "kategori": r["kategori"],
            "rasio": r["nama"],
            "satuan": "%",
            "y1": r["num_y1"] / 100.0,
            "y": r["num_y"] / 100.0,
            "analisis_ai": f"{r['nama']} {r['nilai_y']} (tahun lalu {r['nilai_y1']}); acuan {r['benchmark']} — {r['status']}.",
        }
        for idx, r in enumerate(deep["rasio"]["items"])
    ]
    n_warn = deep["rasio"]["n_perhatian"]
    rasio_narr = (f"{n_warn} dari {len(rasio_rows)} rasio utama berada di luar acuan dan perlu perhatian."
                  if n_warn else f"Seluruh {len(rasio_rows)} rasio utama berada dalam acuan.")

    ml = deep["ml_voting"]
    ml_entry = {
        "benford": {"mad": ml["benford_mad"],
                    "desc": "Distribusi digit pertama menyimpang" if ml["votes"]["benford"] else "Distribusi digit terverifikasi",
                    "verdict": "HIGH" if ml["votes"]["benford"] else "LOW"},
        "beneish": {"score": ml["beneish_score"],
                    "desc": f"Beneish M-Score: {ml['beneish_score']}",
                    "verdict": "HIGH" if ml["votes"]["beneish"] else "LOW"},
        "verdict": "FRAUD" if ml["ensemble_pred"] else "CLEAN",
    }

    kepatuhan = {
        "meta": meta, "rows": checklist_rows, "ya": ya_cnt, "tidak": tidak_cnt, "na": 0,
        "narrative": deep["kepatuhan"]["penjelasan"],
        "tentang_entitas": f"{company['nama']} ({ticker}) adalah emiten sektor {company['sektor']} yang tercatat di Bursa Efek Indonesia. [{DATA_LABEL}]",
    }
    calk = {
        "meta": meta, "catatan_signifikan": calk_findings, "narrative": deep["calk"]["narrative"],
        "tentang_entitas": f"Pengungkapan Catatan atas Laporan Keuangan {company['nama']}. [{DATA_LABEL}]",
    }
    komparasi = {ticker: {
        "mode": "apolo", "threshold_pct": KOMPARASI_TOLERANSI_PCT,
        "sumber_a": SUMBER_LK, "sumber_b": SUMBER_APOLO,
        "total_akun": len(kompar_rows), "rows": kompar_rows, "mismatches": mismatches,
        "q_curr": q_curr, "q_prev": q_prev, "narrative": deep["komparasi"]["summary"],
    }}
    rasio = {ticker: {"q_curr": q_curr, "q_prev": q_prev, "rasio_rows": rasio_rows, "narrative": rasio_narr}}

    return {
        "pdf": {
            "kepatuhan": kepatuhan,
            "calk": calk,
            "komparasi": komparasi,
            "rasio": rasio,
            "ml_voting": {ticker: ml_entry},
        },
        "excel": {
            "komparasi": komparasi,
            "rasio": rasio,
            "ml": {ticker: ml_entry},
            "kepatuhan": {k: v for k, v in kepatuhan.items() if k != "tentang_entitas"},
            "calk": {k: v for k, v in calk.items() if k != "tentang_entitas"},
        },
    }


# ── Kesimpulan & Rekomendasi portofolio (tab ke-5 beranda) ────────────────────
def get_kesimpulan_portfolio_data():
    """Rangkum temuan utama tiap modul + rekomendasi + emiten prioritas tindak lanjut."""
    s = get_portfolio_summary()
    kp = get_kepatuhan_portfolio_data()["frequent_checklist_issues"]
    km = get_komparasi_portfolio_data()
    rs = get_rasio_portfolio_data()["ratios_summary"]
    ck = get_calk_portfolio_data()["calk_risk_themes"]
    ml = get_ml_portfolio_data()["submodel_breakdown"]

    temuan = []
    rekomendasi = []

    # Emiten prioritas: Tidak Patuh dulu, lalu Perlu Reviu, skor terendah di atas
    urut = {"Tidak Patuh": 0, "Perlu Reviu": 1}
    prioritas = sorted(
        [c for c in ANALYZED_COMPANIES if c["status_kepatuhan"] in urut],
        key=lambda c: (urut[c["status_kepatuhan"]], c["skor_kepatuhan"] or 0),
    )
    tidak_patuh = [c for c in prioritas if c["status_kepatuhan"] == "Tidak Patuh"]

    # 1. Kepatuhan
    teks = (f"{s['patuh_count']} dari {s['num_analyzed']} laporan keuangan yang dianalisis berstatus patuh "
            f"({s['pct_patuh']}%), {s['reviu_count']} perlu reviu, dan {s['tidak_patuh_count']} tidak patuh.")
    if kp:
        teks += f" Kriteria yang paling sering tidak terpenuhi: {kp[0]['kriteria']} ({kp[0]['non_compliant_count']} LK)."
        rekomendasi.append(f"Minta klarifikasi dan perbaikan atas kriteria \"{kp[0]['kriteria']}\" yang belum terpenuhi pada {kp[0]['non_compliant_count']} laporan keuangan.")
    temuan.append({"modul": "Pemeriksaan Kepatuhan", "icon": "✅", "teks": teks})

    if tidak_patuh:
        daftar = ", ".join(c["ticker"] for c in tidak_patuh)
        rekomendasi.insert(0, f"Lakukan pemeriksaan lanjutan atas {len(tidak_patuh)} emiten berstatus Tidak Patuh / Terindikasi Anomali: {daftar}.")

    # 2. Komparasi
    total_mm = sum(km["mismatch_by_sektor"].values())
    teks = (f"Terdapat {total_mm} akun yang nilainya di LK tidak sesuai dengan {SUMBER_APOLO} "
            f"(selisih > {KOMPARASI_TOLERANSI_PCT:g}%).")
    if total_mm:
        sektor_top = max(km["mismatch_by_sektor"].items(), key=lambda kv: kv[1])[0]
        teks += f" Terbanyak pada sektor {sektor_top}."
    if km["mismatch_categories"]:
        a = km["mismatch_categories"][0]
        teks += f" Akun paling sering tidak sesuai: {a['akun']} ({a['flags']} LK)."
        rekomendasi.append(f"Konfirmasi ke emiten penyebab perbedaan akun \"{a['akun']}\" antara LK dan APOLO, "
                           f"dan minta koreksi laporan APOLO bila angka LK audited yang benar.")
    temuan.append({"modul": "Analisis Komparasi", "icon": "📊", "teks": teks})

    # 3. Rasio
    if rs:
        terburuk = max(rs, key=lambda r: r["warning_pct"])
        teks = (f"Rasio dengan porsi terbesar di luar acuan: {terburuk['rasio']} "
                f"({terburuk['warning_pct']}% LK; rata-rata {terburuk['mean']}).")
        if terburuk["warning_pct"] > 0:
            rekomendasi.append(f"Pantau {terburuk['rasio']}: {terburuk['warning_pct']}% laporan keuangan berada di luar acuan.")
    else:
        teks = "Belum ada data rasio."
    temuan.append({"modul": "Analisis Rasio Keuangan", "icon": "📐", "teks": teks})

    # 4. CaLK
    if ck:
        teks = f"Tema pengungkapan berisiko paling sering: {ck[0]['topik']} ({ck[0]['count']} LK)"
        teks += f", diikuti {ck[1]['topik']} ({ck[1]['count']} LK)." if len(ck) > 1 else "."
        rekomendasi.append(f"Dalami pengungkapan CaLK terkait \"{ck[0]['topik']}\" pada {ck[0]['count']} laporan keuangan.")
    else:
        teks = "Tidak ada tema CaLK berisiko."
    temuan.append({"modul": "Analisis CALK", "icon": "📝", "teks": teks})

    # 5. ML (dirangkum di kesimpulan)
    ens = next((m for m in ml if m["model"].startswith("Ensemble")), None)
    sub = max((m for m in ml if not m["model"].startswith("Ensemble")), key=lambda m: m["anomaly_count"], default=None)
    teks = (f"{s['anomali_ml_count']} LK ({s['pct_anomali_ml']}%) terindikasi anomali oleh konsensus ensemble machine learning.")
    if sub:
        teks += f" Deteksi terbanyak oleh {sub['model'].split(' (')[0]} ({sub['anomaly_count']} LK)."
    temuan.append({"modul": "Deteksi Anomali (ML)", "icon": "🤖", "teks": teks})

    if s["num_pending"]:
        rekomendasi.append(f"Selesaikan analisis atas {s['num_pending']} laporan keuangan yang belum dianalisis.")

    return {
        "ringkasan": (f"Dari {s['total_lk']} laporan keuangan tahunan {TAHUN_LAPORAN} emiten perbankan & asuransi, "
                      f"{s['num_analyzed']} telah dianalisis dengan rata-rata skor kepatuhan {s['avg_score']}%. "
                      f"{len(prioritas)} emiten memerlukan tindak lanjut ({len(tidak_patuh)} prioritas tinggi)."),
        "temuan": temuan,
        "rekomendasi": rekomendasi,
        "prioritas": prioritas[:10],
    }
