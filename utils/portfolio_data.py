# -*- coding: utf-8 -*-
"""
utils/portfolio_data.py
Generator & Data Layer untuk Laporan Keuangan Tahunan Emiten Pasar Modal IDX.
Semua emiten adalah emiten non-perbankan terdaftar di Bursa Efek Indonesia (IDX).
"""

import random
import pandas as pd

SEKTOR_LIST = [
    "Energi & Pertambangan",
    "Barang Konsumen (FMCG & Ritel)",
    "Infrastruktur & Telekomunikasi",
    "Properti & Real Estat",
    "Perindustrian & Material Dasar"
]

# 100 Emiten Terdaftar di IDX (Bursa Efek Indonesia)
IDX_EMITEN_LIST = [
    # Energi & Pertambangan (20)
    ("ADRO", "PT Adaro Energy Indonesia Tbk", "Energi & Pertambangan"),
    ("PTBA", "PT Bukit Asam Tbk", "Energi & Pertambangan"),
    ("MEDC", "PT Medco Energi Internasional Tbk", "Energi & Pertambangan"),
    ("PGAS", "PT Perusahaan Gas Negara Tbk", "Energi & Pertambangan"),
    ("HRUM", "PT Harum Energy Tbk", "Energi & Pertambangan"),
    ("ITMG", "PT Indo Tambangraya Megah Tbk", "Energi & Pertambangan"),
    ("INDY", "PT Indika Energy Tbk", "Energi & Pertambangan"),
    ("BUMI", "PT Bumi Resources Tbk", "Energi & Pertambangan"),
    ("AKRA", "PT AKR Corporindo Tbk", "Energi & Pertambangan"),
    ("ANTM", "PT Aneka Tambang Tbk", "Energi & Pertambangan"),
    ("INCO", "PT Vale Indonesia Tbk", "Energi & Pertambangan"),
    ("TINS", "PT Timah Tbk", "Energi & Pertambangan"),
    ("ENRG", "PT Energi Mega Persada Tbk", "Energi & Pertambangan"),
    ("DOID", "PT Delta Dunia Makmur Tbk", "Energi & Pertambangan"),
    ("KKGI", "PT Resource Alam Indonesia Tbk", "Energi & Pertambangan"),
    ("BSSR", "PT Baramulti Suksessarana Tbk", "Energi & Pertambangan"),
    ("BYAN", "PT Bayan Resources Tbk", "Energi & Pertambangan"),
    ("GEMS", "PT Golden Energy Mines Tbk", "Energi & Pertambangan"),
    ("TOBA", "PT TBS Energi Utama Tbk", "Energi & Pertambangan"),
    ("ELSA", "PT Elnusa Tbk", "Energi & Pertambangan"),

    # Barang Konsumen (FMCG & Ritel) (20)
    ("INDF", "PT Indofood Sukses Makmur Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("ICBP", "PT Indofood CBP Sukses Makmur Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("UNVR", "PT Unilever Indonesia Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("KLBF", "PT Kalbe Farma Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("CPIN", "PT Charoen Pokphand Indonesia Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("MYOR", "PT Mayora Indah Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("AMRT", "PT Sumber Alfaria Trijaya Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("ACES", "PT Aspirasi Hidup Indonesia Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("MAPI", "PT Mitra Adiperkasa Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("ERAA", "PT Erajaya Swasembada Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("GGRM", "PT Gudang Garam Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("HMSP", "PT H.M. Sampoerna Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("SIDO", "PT Industri Jamu Sido Muncul Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("ULTJ", "PT Ultra Jaya Milk Industry Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("CMRY", "PT Cisarua Mountain Dairy Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("ROTI", "PT Nippon Indosari Corpindo Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("CLEO", "PT Sariguna Primatirta Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("HEAL", "PT Medikaloka Hermina Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("MIKA", "PT Mitra Keluarga Karyasehat Tbk", "Barang Konsumen (FMCG & Ritel)"),
    ("LPPF", "PT Matahari Department Store Tbk", "Barang Konsumen (FMCG & Ritel)"),

    # Infrastruktur & Telekomunikasi (20)
    ("TLKM", "PT Telkom Indonesia (Persero) Tbk", "Infrastruktur & Telekomunikasi"),
    ("ISAT", "PT Indosat Tbk", "Infrastruktur & Telekomunikasi"),
    ("EXCL", "PT XL Axiata Tbk", "Infrastruktur & Telekomunikasi"),
    ("JSMR", "PT Jasa Marga (Persero) Tbk", "Infrastruktur & Telekomunikasi"),
    ("GOTO", "PT GoTo Gojek Tokopedia Tbk", "Infrastruktur & Telekomunikasi"),
    ("BUKA", "PT Bukalapak.com Tbk", "Infrastruktur & Telekomunikasi"),
    ("EMTK", "PT Elang Mahkota Teknologi Tbk", "Infrastruktur & Telekomunikasi"),
    ("SCMA", "PT Surya Citra Media Tbk", "Infrastruktur & Telekomunikasi"),
    ("MNCN", "PT Media Nusantara Citra Tbk", "Infrastruktur & Telekomunikasi"),
    ("TOWR", "PT Sarana Menara Nusantara Tbk", "Infrastruktur & Telekomunikasi"),
    ("TBIG", "PT Tower Bersama Infrastructure Tbk", "Infrastruktur & Telekomunikasi"),
    ("WIKA", "PT Wijaya Karya (Persero) Tbk", "Infrastruktur & Telekomunikasi"),
    ("ADHI", "PT Adhi Karya (Persero) Tbk", "Infrastruktur & Telekomunikasi"),
    ("PTPP", "PT PP (Persero) Tbk", "Infrastruktur & Telekomunikasi"),
    ("WSKT", "PT Waskita Karya (Persero) Tbk", "Infrastruktur & Telekomunikasi"),
    ("MTDL", "PT Metrodata Electronics Tbk", "Infrastruktur & Telekomunikasi"),
    ("FILM", "PT MD Pictures Tbk", "Infrastruktur & Telekomunikasi"),
    ("FREN", "PT Smartfren Telecom Tbk", "Infrastruktur & Telekomunikasi"),
    ("WIFI", "PT Solusi Sinergi Digital Tbk", "Infrastruktur & Telekomunikasi"),
    ("LINK", "PT Link Net Tbk", "Infrastruktur & Telekomunikasi"),

    # Properti & Real Estat (20)
    ("CTRA", "PT Ciputra Development Tbk", "Properti & Real Estat"),
    ("BSDE", "PT Bumi Serpong Damai Tbk", "Properti & Real Estat"),
    ("PWON", "PT Pakuwon Jati Tbk", "Properti & Real Estat"),
    ("SMRA", "PT Summarecon Agung Tbk", "Properti & Real Estat"),
    ("APLN", "PT Agung Podomoro Land Tbk", "Properti & Real Estat"),
    ("ASRI", "PT Alam Sutera Realty Tbk", "Properti & Real Estat"),
    ("DUTI", "PT Duta Pertiwi Tbk", "Properti & Real Estat"),
    ("LPCK", "PT Lippo Cikarang Tbk", "Properti & Real Estat"),
    ("LPKR", "PT Lippo Karawaci Tbk", "Properti & Real Estat"),
    ("MDLN", "PT Modernland Realty Tbk", "Properti & Real Estat"),
    ("MKPI", "PT Metropolitan Kentjana Tbk", "Properti & Real Estat"),
    ("BEST", "PT Bekasi Fajar Industrial Estate Tbk", "Properti & Real Estat"),
    ("SSIA", "PT Surya Semesta Internusa Tbk", "Properti & Real Estat"),
    ("PSSI", "PT Pelangian Indah Can Tbk", "Properti & Real Estat"),
    ("KIJA", "PT Kawasan Industri Jababeka Tbk", "Properti & Real Estat"),
    ("DILD", "PT Intiland Development Tbk", "Properti & Real Estat"),
    ("GWSA", "PT Greenwood Sejahtera Tbk", "Properti & Real Estat"),
    ("JRPT", "PT Jaya Real Property Tbk", "Properti & Real Estat"),
    ("RDTX", "PT Roda Vivatex Tbk", "Properti & Real Estat"),
    ("PPRO", "PT PP Properti Tbk", "Properti & Real Estat"),

    # Perindustrian & Material Dasar (20)
    ("ASII", "PT Astra International Tbk", "Perindustrian & Material Dasar"),
    ("UNTR", "PT United Tractors Tbk", "Perindustrian & Material Dasar"),
    ("SMGR", "PT Semen Indonesia (Persero) Tbk", "Perindustrian & Material Dasar"),
    ("INTP", "PT Indocement Tunggal Prakarsa Tbk", "Perindustrian & Material Dasar"),
    ("TPIA", "PT Chandra Asri Pacific Tbk", "Perindustrian & Material Dasar"),
    ("BRPT", "PT Barito Pacific Tbk", "Perindustrian & Material Dasar"),
    ("MDKA", "PT Merdeka Copper Gold Tbk", "Perindustrian & Material Dasar"),
    ("MBMA", "PT Merdeka Battery Materials Tbk", "Perindustrian & Material Dasar"),
    ("NCKL", "PT Trimegah Bangun Persada Tbk", "Perindustrian & Material Dasar"),
    ("INKP", "PT Indah Kiat Pulp & Paper Tbk", "Perindustrian & Material Dasar"),
    ("TKIM", "PT Pabrik Kertas Tjiwi Kimia Tbk", "Perindustrian & Material Dasar"),
    ("AVIA", "PT Avia Avian Tbk", "Perindustrian & Material Dasar"),
    ("KRAS", "PT Krakatau Steel (Persero) Tbk", "Perindustrian & Material Dasar"),
    ("MARK", "PT Mark Dynamics Indonesia Tbk", "Perindustrian & Material Dasar"),
    ("WOOD", "PT Integra Indocabinet Tbk", "Perindustrian & Material Dasar"),
    ("SMSM", "PT Selamat Sempurna Tbk", "Perindustrian & Material Dasar"),
    ("AUTO", "PT Astra Otoparts Tbk", "Perindustrian & Material Dasar"),
    ("GJTL", "PT Gajah Tunggal Tbk", "Perindustrian & Material Dasar"),
    ("MASB", "PT Mas Murni Indonesia Tbk", "Perindustrian & Material Dasar"),
    ("IMAS", "PT Indomobil Sukses Internasional Tbk", "Perindustrian & Material Dasar"),
]


def _generate_300_companies():
    random.seed(42)  # Consistent mock data
    companies = []
    
    # We multiply the base 100 list to reach exactly 300 unique emiten
    expanded_emiten = []
    for suffix in ["", "B", "C"]:
        for ticker, name, sektor in IDX_EMITEN_LIST:
            if suffix == "":
                expanded_emiten.append((ticker, name, sektor))
            else:
                expanded_emiten.append((f"{ticker}{suffix}", f"{name} (Series {suffix})", sektor))
                
    for idx, (ticker, name, sektor) in enumerate(expanded_emiten, start=1):
        comp_id = f"IDX-{ticker}"
        
        # Categorize entitas
        type_rot = (idx // 2) % 4
        if type_rot == 1:
            entitas_type = "RD"
            full_name = f"RD {ticker} — Reksa Dana Campuran Utama"
        elif type_rot == 2:
            entitas_type = "MI"
            full_name = f"MI {ticker} — Manajer Investasi Aset"
        elif type_rot == 3:
            entitas_type = "DES"
            full_name = f"DES {ticker} — Daftar Efek Syariah Pratama"
        else:
            entitas_type = "EPP"
            full_name = f"{ticker} — {name}"
        
        # 150 companies analyzed (even idx), 150 pending analysis (odd idx)
        analyzed = (idx % 2 == 0)
        
        if analyzed:
            if idx % 10 in [2, 4, 6]:  # Patuh
                status_kepatuhan = "Patuh"
                skor_kepatuhan = round(random.uniform(88.0, 98.5), 1)
                ml_risk = "Risiko Rendah"
                mismatch_count = random.choice([0, 1])
                calk_risk_count = random.choice([0, 1])
            elif idx % 10 in [0, 8]:  # Perlu Reviu
                status_kepatuhan = "Perlu Reviu"
                skor_kepatuhan = round(random.uniform(75.0, 87.0), 1)
                ml_risk = "Risiko Sedang"
                mismatch_count = random.choice([2, 3, 4])
                calk_risk_count = random.choice([2, 3])
            else:  # Tidak Patuh / Anomali
                status_kepatuhan = "Tidak Patuh"
                skor_kepatuhan = round(random.uniform(55.0, 74.0), 1)
                ml_risk = "Terindikasi Anomali"
                mismatch_count = random.choice([5, 6, 8])
                calk_risk_count = random.choice([4, 5])
        else:
            status_kepatuhan = "Belum Dianalisis"
            skor_kepatuhan = None
            ml_risk = "Belum Dianalisis"
            mismatch_count = 0
            calk_risk_count = 0
        
        companies.append({
            "id": comp_id,
            "ticker": ticker,
            "nama": full_name,
            "sektor": sektor,
            "entitas_type": entitas_type,
            "tahun": 2024,
            "status_analisis": "Sudah Dianalisis" if analyzed else "Belum Dianalisis",
            "status_kepatuhan": status_kepatuhan,
            "skor_kepatuhan": skor_kepatuhan,
            "ml_risk": ml_risk,
            "mismatch_count": mismatch_count,
            "calk_risk_count": calk_risk_count,
            "total_aset_miliar": round(random.uniform(2500, 350000), 2)
        })
        
    return companies

ALL_COMPANIES = _generate_300_companies()


def get_portfolio_summary():
    """Summary KPI metrics for top hero banner."""
    df = pd.DataFrame(ALL_COMPANIES)
    total_lk = len(df)
    analyzed_df = df[df["status_analisis"] == "Sudah Dianalisis"]
    num_analyzed = len(analyzed_df)
    num_pending = total_lk - num_analyzed
    
    patuh_count = len(analyzed_df[analyzed_df["status_kepatuhan"] == "Patuh"])
    reviu_count = len(analyzed_df[analyzed_df["status_kepatuhan"] == "Perlu Reviu"])
    tidak_patuh_count = len(analyzed_df[analyzed_df["status_kepatuhan"] == "Tidak Patuh"])
    
    anomali_ml_count = len(analyzed_df[analyzed_df["ml_risk"] == "Terindikasi Anomali"])
    avg_score = round(analyzed_df["skor_kepatuhan"].mean(), 1)
    
    return {
        "total_lk": total_lk,
        "num_analyzed": num_analyzed,
        "num_pending": num_pending,
        "pct_analyzed": round((num_analyzed / total_lk) * 100, 1),
        "patuh_count": patuh_count,
        "reviu_count": reviu_count,
        "tidak_patuh_count": tidak_patuh_count,
        "pct_patuh": round((patuh_count / num_analyzed) * 100, 1),
        "pct_reviu": round((reviu_count / num_analyzed) * 100, 1),
        "pct_tidak_patuh": round((tidak_patuh_count / num_analyzed) * 100, 1),
        "anomali_ml_count": anomali_ml_count,
        "pct_anomali_ml": round((anomali_ml_count / num_analyzed) * 100, 1),
        "avg_score": avg_score,
    }


def get_kepatuhan_portfolio_data():
    """Data for Module 1 Portfolio Overview (Checklist & Component Compliance)."""
    df = pd.DataFrame(ALL_COMPANIES)
    analyzed = df[df["status_analisis"] == "Sudah Dianalisis"]
    
    status_counts = analyzed["status_kepatuhan"].value_counts().to_dict()
    
    frequent_checklist_issues = [
        {"kriteria": "Catatan atas Laporan Keuangan (CaLK) Rincian Pihak Berelasi", "komponen": "CaLK", "non_compliant_count": 14, "pct": 28.0},
        {"kriteria": "Tanda Tangan Seluruh Direktur pada Surat Pernyataan Tanggung Jawab", "komponen": "Surat Pernyataan", "non_compliant_count": 11, "pct": 22.0},
        {"kriteria": "Paragraf Kelangsungan Usaha (Going Concern) Laporan Auditor", "komponen": "Laporan Auditor", "non_compliant_count": 8, "pct": 16.0},
        {"kriteria": "Pengungkapan Aset Terikat Jaminan Utang / Kovenan Kredit", "komponen": "CaLK", "non_compliant_count": 7, "pct": 14.0},
        {"kriteria": "Rincian Liabilitas Kontinjensi & Sengketa Perpajakan (SKPKB)", "komponen": "CaLK", "non_compliant_count": 6, "pct": 12.0},
        {"kriteria": "Kesesuaian Format Barcode & Materai Digital Direksi", "komponen": "Surat Pernyataan", "non_compliant_count": 5, "pct": 10.0},
    ]
    
    return {
        "status_counts": status_counts,
        "frequent_checklist_issues": frequent_checklist_issues
    }


def get_komparasi_portfolio_data():
    """Data for Module 2 Portfolio Overview (Cross-period & Mismatch Analysis)."""
    df = pd.DataFrame(ALL_COMPANIES)
    analyzed = df[df["status_analisis"] == "Sudah Dianalisis"]
    
    mismatch_by_sektor = analyzed.groupby("sektor")["mismatch_count"].sum().to_dict()
    
    mismatch_categories = [
        {"akun": "Pendapatan Usaha (Laporan Audit vs Lampiran Keuangan)", "flags": 12, "pct": 24.0, "severity": "Tinggi"},
        {"akun": "Aset Tetap Netto (Nilai Buku Restatement)", "flags": 9, "pct": 18.0, "severity": "Sedang"},
        {"akun": "Saldo Kas & Setara Kas End-of-Period", "flags": 7, "pct": 14.0, "severity": "Tinggi"},
        {"akun": "Beban Operasional & Penjualan (QoQ Mismatch)", "flags": 6, "pct": 12.0, "severity": "Sedang"},
        {"akun": "Liabilitas Jangka Pendek & Utang Usaha", "flags": 4, "pct": 8.0, "severity": "Rendah"},
    ]
    
    return {
        "mismatch_by_sektor": mismatch_by_sektor,
        "mismatch_categories": mismatch_categories
    }


def get_rasio_portfolio_data():
    """Data for Module 3 Portfolio Overview (Ratio Distributions vs Benchmarks)."""
    ratios_summary = [
        {"rasio": "Return on Assets (ROA)", "kategori": "Profitabilitas", "mean": "4.8%", "min": "-2.5%", "max": "18.2%", "healthy_pct": 82.0, "warning_pct": 18.0},
        {"rasio": "Return on Equity (ROE)", "kategori": "Profitabilitas", "mean": "14.2%", "min": "-8.5%", "max": "32.4%", "healthy_pct": 84.0, "warning_pct": 16.0},
        {"rasio": "Debt to Equity Ratio (DER)", "kategori": "Solvabilitas", "mean": "1.2x", "min": "0.2x", "max": "4.5x", "healthy_pct": 78.0, "warning_pct": 22.0},
        {"rasio": "Current Ratio", "kategori": "Likuiditas", "mean": "165%", "min": "65%", "max": "380%", "healthy_pct": 86.0, "warning_pct": 14.0},
        {"rasio": "Gross Profit Margin (GPM)", "kategori": "Profitabilitas", "mean": "28.5%", "min": "8.2%", "max": "54.0%", "healthy_pct": 85.0, "warning_pct": 15.0},
        {"rasio": "Asset Turnover", "kategori": "Aktivitas", "mean": "0.75x", "min": "0.22x", "max": "2.10x", "healthy_pct": 88.0, "warning_pct": 12.0},
    ]
    return {"ratios_summary": ratios_summary}


def get_calk_portfolio_data():
    """Data for Module 4 Portfolio Overview (CaLK GenAI Risk Highlights)."""
    calk_risk_themes = [
        {"topik": "Transaksi & Saldo Pihak Berelasi", "count": 18, "risk": "Tinggi", "desc": "Pengungkapan pinjaman / transaksi afiliasi entitas anak tanpa jaminan arm's length."},
        {"topik": "Liabilitas Kontinjensi & Sengketa Pajak", "count": 14, "risk": "Tinggi", "desc": "Surat Ketetapan Pajak Kurang Bayar (SKPKB) PPN/PPh dalam proses banding Keberatan Pajak."},
        {"topik": "Restrukturisasi Utang & Kovenan Bank", "count": 10, "risk": "Sedang", "desc": "Pelanggaran rasio kovenan utang bank yang memerlukan waiver tertulis dari kreditur."},
        {"topik": "Penurunan Nilai Aset (Impairment)", "count": 8, "risk": "Sedang", "desc": "Cadangan kerugian penurunan nilai aset eksplorasi / goodwill & piutang usaha."},
        {"topik": "Peristiwa Setelah Tanggal Neraca", "count": 5, "risk": "Rendah", "desc": "Penyesuaian dampak fluktuasi kurs mata uang asing & restrukturisasi internal."},
    ]
    return {"calk_risk_themes": calk_risk_themes}


def get_ml_portfolio_data():
    """Data for Module 5 Portfolio Overview (Machine Learning Anomaly Voting)."""
    df = pd.DataFrame(ALL_COMPANIES)
    analyzed = df[df["status_analisis"] == "Sudah Dianalisis"]
    
    ml_risk_counts = analyzed["ml_risk"].value_counts().to_dict()
    
    submodel_breakdown = [
        {"model": "Benford's Law (First-Digit Anomaly)", "anomaly_count": 7, "pct": 14.0},
        {"model": "Beneish M-Score (Earnings Manipulation)", "anomaly_count": 5, "pct": 10.0},
        {"model": "Isolation Forest (Multivariate Outlier)", "anomaly_count": 9, "pct": 18.0},
        {"model": "Ensemble Voting (Consensus Risk High)", "anomaly_count": 4, "pct": 8.0},
    ]
    
    return {
        "ml_risk_counts": ml_risk_counts,
        "submodel_breakdown": submodel_breakdown
    }


def get_mock_company_deep_dive(comp_id):
    """Generates detailed deep-dive data structure for a selected company ID."""
    company = next((c for c in ALL_COMPANIES if c["id"] == comp_id), ALL_COMPANIES[0])
    
    master_checklist = [
        {"no": 2,  "komponen": "Validasi Format & Audit",             "entitas": "ALL",          "kriteria": "Potensi Anomali Halaman Hilang / Mismatch", "status": "PATUH", "catatan": "Urutan halaman 1-120 konsisten"},
        {"no": 3,  "komponen": "Validasi Format & Audit",             "entitas": "RD",           "kriteria": "Nama Reksa Dana sesuai dengan Pernyataan Efektif beserta Perubahan Terakhir", "status": "PATUH", "catatan": "Nama sesuai pernyataan efektif"},
        {"no": 4,  "komponen": "Validasi Format & Audit",             "entitas": "RD",           "kriteria": "Nama Reksa Dana mencerminkan nama Manajer Investasi", "status": "PATUH", "catatan": "Nama mencerminkan nama MI"},
        {"no": 5,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "EPP, MI",      "kriteria": "Tanda Tangan Seluruh Direktur Utama & Keuangan", "status": "PATUH" if company["skor_kepatuhan"] and company["skor_kepatuhan"] > 80 else "PERLU REVIU", "catatan": "Tercantum tanda tangan direksi lengkap" if (company["skor_kepatuhan"] and company["skor_kepatuhan"] > 80) else "Tanda tangan direksi tidak lengkap / tidak ditemukan"},
        {"no": 6,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "EPP, MI",      "kriteria": "Tanda Tangan Komisaris Utama / Perwakilan", "status": "PATUH" if company["skor_kepatuhan"] and company["skor_kepatuhan"] > 75 else "PERLU REVIU", "catatan": "Tercantum tanda tangan komite/komisaris" if (company["skor_kepatuhan"] and company["skor_kepatuhan"] > 75) else "Tanda tangan Komisaris Utama tidak ditemukan"},
        {"no": 7,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "DES",          "kriteria": "Tanda Tangan Direksi", "status": "PATUH", "catatan": "Tanda tangan direksi lengkap"},
        {"no": 8,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "DES",          "kriteria": "Tanda Tangan Komisaris", "status": "PATUH", "catatan": "Tanda tangan komisaris lengkap"},
        {"no": 9,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "RD",           "kriteria": "Tanda Tangan Anggota Direksi Manajer Investasi", "status": "PATUH", "catatan": "Tercantum tanda tangan Direksi MI"},
        {"no": 10, "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "RD",           "kriteria": "Tanda Tangan Penanggung Jawab Bank Kustodian", "status": "PATUH", "catatan": "Tanda tangan Kustodian lengkap"},
        {"no": 11, "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "ALL",          "kriteria": "Keabsahan Materai Digital & Barcode QR", "status": "PATUH", "catatan": "Materai digital terverifikasi"},
        {"no": 12, "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "ALL",          "kriteria": "Pernyataan Tanggung Jawab atas Sistem Pengendalian Internal (SPI)", "status": "PATUH", "catatan": "Klausul SPI disajikan lengkap"},
        {"no": 13, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Posisi Keuangan (Neraca Konsolidasian)", "status": "PATUH", "catatan": "Laporan Posisi Keuangan disajikan"},
        {"no": 14, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Laba Rugi & Penghasilan Komprehensif", "status": "PATUH", "catatan": "Laporan Laba Rugi disajikan"},
        {"no": 15, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Arus Kas Konsolidasian", "status": "PATUH", "catatan": "Laporan Arus Kas disajikan"},
        {"no": 16, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Perubahan Ekuitas Konsolidasian", "status": "PATUH", "catatan": "Laporan Perubahan Ekuitas disajikan"},
        {"no": 17, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Catatan atas Laporan Keuangan (CaLK) Lengkap", "status": "PATUH" if company["skor_kepatuhan"] and company["skor_kepatuhan"] > 70 else "PERLU REVIU", "catatan": "Catatan CaLK disajikan lengkap" if (company["skor_kepatuhan"] and company["skor_kepatuhan"] > 70) else "Beberapa pengungkapan CaLK penting tidak lengkap"},
        {"no": 18, "komponen": "Komponen Laporan Keuangan",          "entitas": "RD",           "kriteria": "Periode tahun buku 1 Januari - 31 Desember", "status": "PATUH", "catatan": "Periode buku sesuai ketentuan"},
        {"no": 19, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Opini Akuntan Publik (KAP Terdaftar OJK)", "status": "PATUH" if company["skor_kepatuhan"] and company["skor_kepatuhan"] > 70 else "TIDAK PATUH", "catatan": "Opini Wajar Tanpa Pengecualian" if (company["skor_kepatuhan"] and company["skor_kepatuhan"] > 70) else "Opini Wajar Dengan Pengecualian / Modifikasi Opini"},
        {"no": 20, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Hal Audit Utama (Key Audit Matters)", "status": "PATUH", "catatan": "Tercantum Key Audit Matters"},
        {"no": 21, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Kelangsungan Usaha (Going Concern)", "status": "PATUH" if company["skor_kepatuhan"] and company["skor_kepatuhan"] > 65 else "TIDAK PATUH", "catatan": "Tidak ditemukan penjelas going concern anomaly" if (company["skor_kepatuhan"] and company["skor_kepatuhan"] > 65) else "Terdapat paragraf penjelas kelangsungan usaha (going concern)"},
        {"no": 22, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Respon & Komunikasi Audit", "status": "PATUH", "catatan": "Komunikasi audit disajikan"},
        {"no": 23, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Informasi Lain dalam Laporan Auditor", "status": "PATUH", "catatan": "Paragraf informasi lain tercantum"},
        {"no": 24, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Tanggung Jawab Manajemen atas LK", "status": "PATUH", "catatan": "Tanggung jawab manajemen disajikan"},
        {"no": 25, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Tanggung Jawab Auditor atas Audit", "status": "PATUH", "catatan": "Tanggung jawab auditor disajikan"},
        {"no": 26, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Nama Kantor Akuntan Publik (KAP Registered OJK)", "status": "PATUH", "catatan": "KAP terdaftar di OJK"},
        {"no": 27, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Nama & Nomor Izin Akuntan Publik (AP)", "status": "PATUH", "catatan": "Nama AP & No Izin terverifikasi"},
        {"no": 28, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Nomor & Tanggal Laporan Auditor Independen", "status": "PATUH", "catatan": "Nomor & tanggal Lapor Audit tercantum"},
        {"no": 29, "komponen": "Laporan Auditor Independen",         "entitas": "EPP, MI, RD",  "kriteria": "Periode Penugasan Akuntan Publik & KAP", "status": "PATUH", "catatan": "Masa penugasan sesuai ketentuan OJK"}
    ]

    etype = company.get("entitas_type", "EPP")
    checklist = []
    for item in master_checklist:
        ent_list = [e.strip() for e in item["entitas"].split(",")]
        if "ALL" in ent_list or etype in ent_list:
            checklist.append(item)

    return {
        "file_name": f"{company['ticker']}_LK_Tahunan_2024.pdf",
        "doc_meta": {
            "nama_entitas": company["nama"],
            "tahun": company["tahun"],
            "periode": "Tahunan 2024 (Audit)",
            "sektor": company["sektor"],
            "mata_uang": "IDR Miliar"
        },
        "kepatuhan": {
            "skor": company["skor_kepatuhan"] or 90.0,
            "status": company["status_kepatuhan"],
            "penjelasan": f"Laporan keuangan {company['nama']} secara umum {company['status_kepatuhan'].lower()} terhadap Peraturan OJK / Penyajian Laporan Keuangan Emiten IDX.",
            "checklist": checklist
        },
        "komparasi": {
            "mismatch_count": company["mismatch_count"],
            "summary": f"Ditemukan {company['mismatch_count']} variansi material (selisih >30%) antar periode 2024 vs 2023.",
            "items": [
                {"akun": "Pendapatan Usaha Netto", "val_y": "45,250.4 M", "val_y1": "38,120.1 M", "perubahan_pct": "+18.7%", "mismatch": False},
                {"akun": "Beban Pokok Pendapatan", "val_y": "32,180.2 M", "val_y1": "28,450.0 M", "perubahan_pct": "+13.1%", "mismatch": False},
                {"akun": "Laba Bruto", "val_y": "13,070.2 M", "val_y1": "9,670.1 M", "perubahan_pct": "+35.2%", "mismatch": company["mismatch_count"] > 3},
                {"akun": "Beban Penjualan & Pemasaran", "val_y": "3,450.0 M", "val_y1": "2,100.0 M", "perubahan_pct": "+64.3%", "mismatch": company["mismatch_count"] > 1},
                {"akun": "Beban Umum & Administrasi", "val_y": "2,850.5 M", "val_y1": "2,780.0 M", "perubahan_pct": "+2.5%", "mismatch": False},
                {"akun": "Aset Tetap & Mesin (Netto)", "val_y": "12,450.2 M", "val_y1": "8,310.5 M", "perubahan_pct": "+49.8%", "mismatch": company["mismatch_count"] > 0},
                {"akun": "Kas & Setara Kas End-Period", "val_y": "5,120.0 M", "val_y1": "4,950.2 M", "perubahan_pct": "+3.4%", "mismatch": False},
                {"akun": "Total Ekuitas Pemegang Saham", "val_y": "28,600.0 M", "val_y1": "24,500.0 M", "perubahan_pct": "+16.7%", "mismatch": False},
            ]
        },
        "rasio": {
            "items": [
                {"nama": "Return on Asset (ROA)", "nilai_y": "5.85%", "nilai_y1": "4.40%", "benchmark": "", "status": "Sehat"},
                {"nama": "Return on Equity (ROE)", "nilai_y": "16.20%", "nilai_y1": "13.50%", "benchmark": "", "status": "Sehat"},
                {"nama": "Gross Profit Margin (GPM)", "nilai_y": "28.89%", "nilai_y1": "25.37%", "benchmark": "", "status": "Sehat"},
                {"nama": "Net Profit Margin (NPM)", "nilai_y": "11.25%", "nilai_y1": "9.80%", "benchmark": "", "status": "Sehat"},
                {"nama": "Debt to Equity Ratio (DER)", "nilai_y": "1.15x", "nilai_y1": "1.30x", "benchmark": "", "status": "Sehat"},
                {"nama": "Debt to Asset Ratio (DAR)", "nilai_y": "0.52x", "nilai_y1": "0.56x", "benchmark": "", "status": "Sehat"},
                {"nama": "Times Interest Earned Ratio", "nilai_y": "6.45x", "nilai_y1": "5.20x", "benchmark": "", "status": "Sehat"},
                {"nama": "Debt Service Coverage Ratio (DSCR)", "nilai_y": "2.10x", "nilai_y1": "1.85x", "benchmark": "", "status": "Sehat"},
                {"nama": "Current Ratio", "nilai_y": "175.40%", "nilai_y1": "160.20%", "benchmark": "", "status": "Sehat"},
                {"nama": "Quick Ratio", "nilai_y": "128.50%", "nilai_y1": "115.00%", "benchmark": "", "status": "Sehat"},
                {"nama": "Cash Ratio", "nilai_y": "42.30%", "nilai_y1": "38.10%", "benchmark": "", "status": "Sehat"},
                {"nama": "Working Capital to Assets Ratio", "nilai_y": "24.50%", "nilai_y1": "21.80%", "benchmark": "", "status": "Sehat"},
                {"nama": "Asset Turnover Ratio", "nilai_y": "0.85x", "nilai_y1": "0.78x", "benchmark": "", "status": "Sehat"},
                {"nama": "Receivable Turnover Ratio", "nilai_y": "6.20x", "nilai_y1": "5.80x", "benchmark": "", "status": "Sehat"},
                {"nama": "Gearing Ratio", "nilai_y": "0.48x", "nilai_y1": "0.52x", "benchmark": "", "status": "Sehat"},
            ]
        },
        "calk": {
            "narrative": f"Pengungkapan Catatan atas Laporan Keuangan {company['nama']} mencatat poin krusial terkait transaksi afiliasi, sengketa pajak, kovenan utang, dan cadangan kerugian.",
            "findings": [
                {
                    "referensi": "Catatan 34", "kategori": "Transaksi Pihak Berelasi", "topik": "Transaksi & Saldo Pihak Berelasi",
                    "temuan_ai": "Terdapat penjualan kepada anak perusahaan afiliasi sebesar 12.5% dari total pendapatan usaha.",
                    "temuan": "Terdapat penjualan kepada anak perusahaan afiliasi sebesar 12.5% dari total pendapatan usaha.",
                    "ringkasan": "Terdapat penjualan kepada anak perusahaan afiliasi sebesar 12.5% dari total pendapatan usaha.",
                    "catatan_keterangan": "Lakukan konfirmasi arm's length pricing atas transaksi penjualan afiliasi.",
                    "implikasi": "Risiko Kewajaran Harga Afiliasi", "kategori_risiko": "Sedang", "halaman": "hal 45"
                },
                {
                    "referensi": "Catatan 42", "kategori": "Sengketa Perpajakan", "topik": "Sengketa Perpajakan",
                    "temuan_ai": "Perusahaan sedang mengajukan banding atas Surat Ketetapan Pajak Kurang Bayar (SKPKB) PPh senilai 35.4M.",
                    "temuan": "Perusahaan sedang mengajukan banding atas Surat Ketetapan Pajak Kurang Bayar (SKPKB) senilai 35.4M.",
                    "ringkasan": "Perusahaan sedang mengajukan banding atas Surat Ketetapan Pajak Kurang Bayar (SKPKB) senilai 35.4M.",
                    "catatan_keterangan": "Monitoring kelanjutan proses sidang di Pengadilan Pajak.",
                    "implikasi": "Potensi Kewajiban Pajak Kontinjensi", "kategori_risiko": "Tinggi" if company["calk_risk_count"] > 2 else "Rendah", "halaman": "hal 58"
                },
                {
                    "referensi": "Catatan 28", "kategori": "Kovenan UTANG", "topik": "Kovenan Pinjaman Utang Bank",
                    "temuan_ai": "Pemenuhan kovenan rasio utang bersih terhadap EBITDA terverifikasi sesuai batas kreditur.",
                    "temuan": "Pemenuhan kovenan rasio utang bersih terhadap EBITDA terverifikasi sesuai batas kreditur.",
                    "ringkasan": "Pemenuhan kovenan rasio utang bersih terhadap EBITDA terverifikasi sesuai batas kreditur.",
                    "catatan_keterangan": "Kreator kovenan dalam ambang batas aman.",
                    "implikasi": "Risiko Solvabilitas Terkendali", "kategori_risiko": "Rendah", "halaman": "hal 62"
                },
                {
                    "referensi": "Catatan 15", "kategori": "Penyisihan Piutang", "topik": "Cadangan Penurunan Nilai Piutang",
                    "temuan_ai": "Penyisihan kerugian penurunan nilai (ECL) disajikan sesuai PSAK 71.",
                    "temuan": "Penyisihan kerugian penurunan nilai (ECL) disajikan sesuai PSAK 71.",
                    "ringkasan": "Penyisihan kerugian penurunan nilai (ECL) disajikan sesuai PSAK 71.",
                    "catatan_keterangan": "Kecukupan pencadangan terverifikasi akuntan publik.",
                    "implikasi": "Risiko Kualitas Aset Piutang", "kategori_risiko": "Sedang" if company["calk_risk_count"] > 1 else "Rendah", "halaman": "hal 38"
                },
                {
                    "referensi": "Catatan 55", "kategori": "Peristiwa Pasca Tanggal Neraca", "topik": "Peristiwa Setelah Tanggal Neraca",
                    "temuan_ai": "Pembayaran dividen interim periode 2024 telah disetujui dalam RUPS.",
                    "temuan": "Pembayaran dividen interim periode 2024 telah disetujui dalam RUPS.",
                    "ringkasan": "Pembayaran dividen interim periode 2024 telah disetujui dalam RUPS.",
                    "catatan_keterangan": "Keterbukaan informasi telah disampaikan ke portal IDX.",
                    "implikasi": "Dampak pada Kas & Ekuitas Pasca Periode", "kategori_risiko": "Rendah", "halaman": "hal 78"
                }
            ]
        },
        "ml_voting": {
            "ensemble_pred": 1 if company["ml_risk"] == "Terindikasi Anomali" else 0,
            "risk_label": company["ml_risk"],
            "probabilitas": 0.88 if company["ml_risk"] == "Terindikasi Anomali" else (0.45 if company["ml_risk"] == "Risiko Sedang" else 0.12),
            "votes": {
                "benford": 1 if company["ml_risk"] == "Terindikasi Anomali" else 0,
                "beneish": 1 if company["ml_risk"] == "Terindikasi Anomali" else 0,
                "iforest": 1 if company["ml_risk"] != "Risiko Rendah" else 0
            }
        },
        "kesimpulan": {
            "ringkasan": f"Hasil evaluasi pengawasan emiten untuk {company['nama']} menunjukkan status {company['status_kepatuhan']} dengan klasifikasi risiko ML {company['ml_risk']}.",
            "rekomendasi": [
                "Lakukan konfirmasi arm's length pricing atas transaksi pihak berelasi.",
                "Monitoring kelanjutan proses sengketa keberatan pajak di Pengadilan Pajak.",
                "Pastikan kecukupan pemenuhan kovenan utang dan kewajiban keterbukaan informasi di portal IDX."
            ]
        }
    }


def build_full_pipeline_store(comp_id):
    """
    Builds a complete home-pipeline-result dict structure compatible with all 6 modules:
    1_kepatuhan, 2_komparasi, 3_rasio, 4_calk, 5_ml_voting, 6_kesimpulan.
    """
    company = next((c for c in ALL_COMPANIES if c["id"] == comp_id), ALL_COMPANIES[0])
    deep = get_mock_company_deep_dive(company["id"])
    
    meta = {
        "nama_entitas": company["nama"],
        "jenis_laporan": "Laporan Keuangan Audited",
        "periode_laporan": "Tahunan 2024",
        "sektor": company["sektor"]
    }
    
    checklist_rows = [
        {
            "No": item["no"],
            "Komponen": item["komponen"],
            "Entitas": item.get("entitas", "ALL"),
            "Kriteria Pemeriksaan": item["kriteria"],
            "Status": "YA" if item["status"] == "PATUH" else "TIDAK",
            "Hasil AI": "Sesuai Pedoman OJK" if item["status"] == "PATUH" else "Ditemukan Deviasi / Ketidaksesuaian",
            "Halaman": f"hal {item['no']*2}",
            "Catatan AI": item["catatan"]
        }
        for item in deep["kepatuhan"]["checklist"]
    ]
    
    ya_cnt = sum(1 for r in checklist_rows if r["Status"] == "YA")
    tidak_cnt = sum(1 for r in checklist_rows if r["Status"] == "TIDAK")
    
    calk_findings = [
        {
            "referensi": f.get("referensi", f"Catatan {(idx+1)*4}"),
            "kategori": f.get("kategori", f.get("topik", "Umum")),
            "topik": f.get("topik", f.get("kategori", "Umum")),
            "temuan_ai": f.get("temuan_ai", f.get("temuan", "-")),
            "temuan": f.get("temuan", f.get("temuan_ai", "-")),
            "ringkasan": f.get("ringkasan", f.get("temuan_ai", "-")),
            "catatan_keterangan": f.get("catatan_keterangan", f.get("implikasi", "Monitoring OJK")),
            "implikasi": f.get("implikasi", f.get("catatan_keterangan", "Monitoring OJK")),
            "halaman": f.get("halaman", f"hal {35+(idx+1)*4}")
        }
        for idx, f in enumerate(deep["calk"]["findings"])
    ]
    
    mismatches = [
        {"akun": item["akun"], "nilai_y1": 38120.1, "nilai_y": 45250.4, "pct": 18.7}
        for item in deep["komparasi"]["items"] if item.get("mismatch")
    ]
    if not mismatches:
        mismatches = [{"akun": "Aset Tetap & Mesin", "nilai_y1": 8310.5, "nilai_y": 12450.2, "pct": 49.8}]

    rasio_rows = []
    for idx, r in enumerate(deep["rasio"]["items"]):
        try:
            val_y1 = float(r["nilai_y1"].replace("%","").replace("x","")) / 100.0 if "%" in r["nilai_y1"] else float(r["nilai_y1"].replace("%","").replace("x",""))
            val_y = float(r["nilai_y"].replace("%","").replace("x","")) / 100.0 if "%" in r["nilai_y"] else float(r["nilai_y"].replace("%","").replace("x",""))
        except Exception:
            val_y1, val_y = 0.1, 0.15
        
        kat = "Profitabilitas" if "RO" in r["nama"] else ("Solvabilitas" if "DER" in r["nama"] else "Likuiditas")
        rasio_rows.append({
            "no": idx + 1,
            "kategori": kat,
            "rasio": r["nama"],
            "y1": val_y1,
            "y": val_y,
            "analisis_ai": f"Nilai {r['nama']} berada dalam kondisi {r['status']}."
        })

    ticker = company["ticker"]
    
    return {
        "pdf": {
            "kepatuhan": {
                "meta": meta,
                "rows": checklist_rows,
                "ya": ya_cnt,
                "tidak": tidak_cnt,
                "na": 0,
                "narrative": deep["kepatuhan"]["penjelasan"],
                "tentang_entitas": f"{company['nama']} ({company['ticker']}) beroperasi di sektor {company['sektor']} terdaftar di Bursa Efek Indonesia."
            },
            "calk": {
                "meta": meta,
                "catatan_signifikan": calk_findings,
                "narrative": deep["calk"]["narrative"],
                "tentang_entitas": f"Pengungkapan Catatan atas Laporan Keuangan {company['nama']}."
            },
            "komparasi": {
                ticker: {
                    "total_akun": 24, "q_curr": "2024", "q_prev": "2023",
                    "mismatches": mismatches, "narrative": deep["komparasi"]["summary"]
                }
            },
            "rasio": {
                ticker: {
                    "q_curr": "2024", "q_prev": "2023",
                    "rasio_rows": rasio_rows, "narrative": "Hasil evaluasi rasio keuangan emiten."
                }
            },
            "ml_voting": {
                ticker: {
                    "benford": {"mad": 0.008, "desc": "Distribusi digit terverifikasi", "verdict": "LOW"},
                    "beneish": {"score": -2.65, "desc": "Beneish M-Score aman", "verdict": "LOW"},
                    "verdict": "FRAUD" if company["ml_risk"] == "Terindikasi Anomali" else "CLEAN"
                }
            }
        },
        "excel": {
            "komparasi": {
                ticker: {
                    "total_akun": 24, "q_curr": "2024", "q_prev": "2023",
                    "mismatches": mismatches, "narrative": deep["komparasi"]["summary"]
                }
            },
            "rasio": {
                ticker: {
                    "q_curr": "2024", "q_prev": "2023",
                    "rasio_rows": rasio_rows, "narrative": "Hasil evaluasi rasio keuangan emiten."
                }
            },
            "ml": {
                ticker: {
                    "benford": {"mad": 0.008, "desc": "Distribusi digit terverifikasi", "verdict": "LOW"},
                    "beneish": {"score": -2.65, "desc": "Beneish M-Score aman", "verdict": "LOW"},
                    "verdict": "FRAUD" if company["ml_risk"] == "Terindikasi Anomali" else "CLEAN"
                }
            },
            "kepatuhan": {
                "meta": meta, "rows": checklist_rows, "ya": ya_cnt, "tidak": tidak_cnt, "na": 0,
                "narrative": deep["kepatuhan"]["penjelasan"]
            },
            "calk": {
                "meta": meta, "catatan_signifikan": calk_findings, "narrative": deep["calk"]["narrative"]
            }
        }
    }

