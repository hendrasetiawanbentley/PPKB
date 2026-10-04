# -*- coding: utf-8 -*-
"""
Parser umum laporan keuangan Excel (format: 1 sheet = 1 emiten, berisi blok
Neraca/Laba Rugi/Arus Kas per kuartal). Dipakai bareng oleh modul 2 (Komparasi),
3 (Rasio), dan 5 (ML Voting) supaya logic parsing tidak ditulis 3x.
"""
import numpy as np
import pandas as pd


def parse_value(val):
    if pd.isna(val) or str(val).strip() in ["-", ""]:
        return 0.0
    s = str(val).replace(" M", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]
    try:
        v = float(s)
        return -v if neg else v
    except Exception:
        return 0.0


def find_sections(df):
    secs = []
    for idx, row in df.iterrows():
        lb = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        if "Laporan Neraca" in lb:
            secs.append(("neraca", idx))
        elif "Laporan Laba Rugi" in lb:
            secs.append(("labarugi", idx))
        elif "Laporan Arus Kas" in lb:
            secs.append(("aruskas", idx))
    return secs


def get_quarter(df, row):
    if row + 1 < len(df):
        v = str(df.iloc[row + 1, 1]).strip() if pd.notna(df.iloc[row + 1, 1]) else ""
        if v.startswith("Q") and len(v) >= 7:
            return v
    return None


def parse_sec(df, s, e):
    d = {}
    for _, r in df.iloc[s:e].iterrows():
        lb = str(r.iloc[0]).strip().lower() if pd.notna(r.iloc[0]) else ""
        if lb:
            d[lb] = parse_value(r.iloc[1]) if len(r) > 1 else 0.0
    return d


def gi(data, *kw):
    for k, v in data.items():
        for w in kw:
            if w in k.lower():
                return v
    return 0.0


def parse_sheet(df):
    """Return dict {quarter_label: {'neraca': {...}, 'labarugi': {...}, 'aruskas': {...}}}"""
    secs = find_sections(df)
    qs = {}
    for i, (t, s) in enumerate(secs):
        nx = secs[i + 1][1] if i + 1 < len(secs) else len(df)
        q = get_quarter(df, s)
        if not q:
            continue
        if q not in qs:
            qs[q] = {"neraca": {}, "labarugi": {}, "aruskas": {}}
        qs[q][t] = parse_sec(df, s + 2, nx)
    return qs


def sorted_quarters(quarters: dict):
    return sorted(quarters.keys(), key=lambda x: (x.split()[-1], x.split()[0]))


ACCOUNT_KEYS = {
    "total_aset": ("neraca", "total aset"),
    "total_liabilitas": ("neraca", "total liabilitas"),
    "total_ekuitas": ("neraca", "total ekuitas"),
    "kas": ("neraca", "kas dan setara kas"),
    "piutang_usaha": ("neraca", "piutang usaha"),
    "persediaan": ("neraca", "persediaan"),
    "aset_lancar": ("neraca", "total aset lancar"),
    "aset_tetap": ("neraca", "aset tetap"),
    "liabilitas_jk_pendek": ("neraca", "liabilitas jangka pendek"),
    "liabilitas_jk_panjang": ("neraca", "liabilitas jangka panjan"),
    "pendapatan": ("labarugi", "total pendapatan"),
    "laba_kotor": ("labarugi", "laba kotor"),
    "beban_usaha": ("labarugi", "total beban usaha"),
    "laba_usaha": ("labarugi", "laba usaha"),
    "laba_sebelum_pajak": ("labarugi", "laba sebelum pajak"),
    "beban_pajak": ("labarugi", "beban pajak penghasilan"),
    "laba_bersih": ("labarugi", "laba bersih tahun berjalan"),
    "arus_kas_operasi": ("aruskas", "arus kas dari aktivitas operasi"),
}


def extract_raw_accounts(quarters: dict) -> dict:
    """Return {quarter_label: {account_name: value}} — nilai mentah (bukan rasio),
    dipakai modul 2 (Komparasi) untuk membandingkan akun antar periode."""
    out = {}
    for q in sorted_quarters(quarters):
        bs, pl, cf = quarters[q].get("neraca", {}), quarters[q].get("labarugi", {}), quarters[q].get("aruskas", {})
        row = {}
        for key, (section, kw) in ACCOUNT_KEYS.items():
            src = {"neraca": bs, "labarugi": pl, "aruskas": cf}[section]
            row[key] = gi(src, kw)
        out[q] = row
    return out


def compute_ratios_per_quarter(quarters: dict, extractor=None) -> dict:
    """Return {quarter_label: {ratio_name: value}} — dipakai modul 3 (Rasio)."""
    _extract = extractor or extract_raw_accounts
    raw = _extract(quarters)
    out = {}
    for q, a in raw.items():
        sd = lambda x, y: x / y if y else 0
        gp = a["laba_kotor"] if a["laba_kotor"] else a["pendapatan"]
        
        # Hitung ke-34 rasio keuangan sesuai klasifikasi OJK
        out[q] = {
            "roa": sd(a["laba_bersih"], a["total_aset"]),
            "roe": sd(a["laba_bersih"], a["total_ekuitas"]),
            "net_margin": sd(a["laba_bersih"], a["pendapatan"]),
            "gp_margin": sd(gp, a["pendapatan"]),
            "bopo": sd(a["beban_usaha"], a["pendapatan"]),
            "pend_lainnya": 0.0,
            "dar": sd(a["total_liabilitas"], a["total_aset"]),
            "der": sd(a["total_liabilitas"], a["total_ekuitas"]),
            "interest_coverage": sd(a["laba_usaha"], sd(a["total_liabilitas"], 10)),
            "debt_ratio": sd(a["total_liabilitas"], a["total_aset"]),
            "cash_ratio": sd(a["kas"], a["liabilitas_jk_pendek"]),
            "quick_ratio": sd(a["aset_lancar"] - a["persediaan"], a["liabilitas_jk_pendek"]),
            "current_ratio": sd(a["aset_lancar"], a["liabilitas_jk_pendek"]),
            "equity_ratio": sd(a["total_ekuitas"], a["total_aset"]),
            "asset_turnover": sd(a["pendapatan"], a["total_aset"]),
            "receivable_turnover": sd(a["pendapatan"], a["piutang_usaha"]),
            "gearing_ratio": sd(a["total_liabilitas"], a["total_ekuitas"]),
            "working_capital": a["aset_lancar"] - a["liabilitas_jk_pendek"],
            "retained_earnings": a["total_ekuitas"] * 0.25,
            "dscr": sd(a["laba_usaha"], sd(a["liabilitas_jk_pendek"], 4)),
            
            # Khusus Permodalan, Kinerja Investasi, Efisiensi dll (Reksa Dana / MI)
            "miku_1": 0.0,
            "miku_2": 0.0,
            "total_hasil_investasi": 0.0,
            "hasil_dividen": 0.0,
            "hasil_setelah_biaya": 0.0,
            "biaya_operasi": 0.0,
            "perputaran_portfolio": 0.0,
            "pct_pajak": sd(a["beban_pajak"], a["laba_sebelum_pajak"]) if a["laba_sebelum_pajak"] else 0.0,
            "expense_ratio": 0.0,
            "perubahan_nab": 0.0,
            "ru_1": 0.0,
            "ru_2": 0.0,
            "rpnh_1": 0.0,
            "rpnh_2": 0.0
        }
    return out


# ── XBRL IDX Format Support ─────────────────────────────────────────────────
# File dari IDX (Bursa Efek Indonesia) berformat XBRL dengan sheet kode angka.
# Adapter ini konversi ke format internal {quarter: {neraca/labarugi/aruskas: {}}}

# Sheet XBRL yang mengandung data keuangan utama
_XBRL_NERACA_SHEETS = ["2210000", "2220000"]
_XBRL_LABARUGI_SHEETS = ["2311000", "2312000", "2321000", "2322000"]
_XBRL_ARUSKAS_SHEETS = ["2510000", "2520000"]


def is_xbrl_format(sheet_names: list) -> bool:
    """Deteksi apakah file Excel ini berformat XBRL IDX."""
    xbrl_indicators = {"Context", "InlineXBRL", "Token", "hidden"}
    numeric_sheets = sum(1 for s in sheet_names if s.isdigit())
    return bool(xbrl_indicators & set(sheet_names)) and numeric_sheets >= 5


def _parse_xbrl_sheet(df) -> dict:
    """Parse satu sheet XBRL: col 0 = nama akun, col 1 = current, col 2 = prior."""
    accounts = {}
    for _, row in df.iterrows():
        label = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ""
        if not label or label.startswith("[") or label.startswith("nan"):
            continue
        val = parse_value(row.iloc[1]) if len(row) > 1 else 0.0
        # Only store if: new key OR non-zero value (don't overwrite good data with 0)
        if label not in accounts or val != 0.0:
            accounts[label] = val
    return accounts


def _parse_xbrl_sheet_prior(df) -> dict:
    """Parse prior-year column dari sheet XBRL (col 2)."""
    accounts = {}
    for _, row in df.iterrows():
        label = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ""
        if not label or label.startswith("[") or label.startswith("nan"):
            continue
        val = parse_value(row.iloc[2]) if len(row) > 2 else 0.0
        # Only store if: new key OR non-zero value (don't overwrite good data with 0)
        if label not in accounts or val != 0.0:
            accounts[label] = val
    return accounts


def _find_xbrl_entity(path: str) -> str:
    """Cari nama/kode entitas dari sheet Context atau 1000000."""
    try:
        df = pd.read_excel(path, sheet_name="1000000", header=None)
        for _, row in df.iterrows():
            label = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ""
            if "kode entitas" in label:
                return str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "UNKNOWN"
            if "nama entitas" in label:
                return str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "UNKNOWN"
    except Exception:
        pass
    return "UNKNOWN"


def parse_xbrl_file(path: str, sheet_names: list) -> dict:
    """
    Parse file XBRL IDX dan return format sama dengan parse_sheet():
    {quarter_label: {neraca: {}, labarugi: {}, aruskas: {}}}
    
    Karena XBRL punya col 1=CurrentYear dan col 2=PriorYear,
    kita buat 2 quarter: "Y Current" dan "Y-1 Prior".
    """
    neraca_curr, neraca_prior = {}, {}
    labarugi_curr, labarugi_prior = {}, {}
    aruskas_curr, aruskas_prior = {}, {}

    # Map sheet codes to categories
    _sheet_category = {}
    for s in sheet_names:
        if not s.isdigit():
            continue
        code = int(s)
        # 22xxxxx = Statement of financial position (Neraca)
        if 2200000 <= code <= 2299999:
            _sheet_category[s] = "neraca"
        # 23xxxxx = Statement of profit or loss (Laba Rugi)
        elif 2300000 <= code <= 2399999:
            _sheet_category[s] = "labarugi"
        # 25xxxxx / 26xxxxx = Statement of cash flows (Arus Kas)
        elif 2500000 <= code <= 2599999:
            _sheet_category[s] = "aruskas"

    for sheet, category in _sheet_category.items():
        try:
            df = pd.read_excel(path, sheet_name=sheet, header=None)
        except Exception:
            continue

        def _smart_merge(target, source):
            """Merge source into target without overwriting non-zero with zero."""
            for k, v in source.items():
                if k not in target or v != 0.0:
                    target[k] = v

        if category == "neraca":
            _smart_merge(neraca_curr, _parse_xbrl_sheet(df))
            _smart_merge(neraca_prior, _parse_xbrl_sheet_prior(df))
        elif category == "labarugi":
            _smart_merge(labarugi_curr, _parse_xbrl_sheet(df))
            _smart_merge(labarugi_prior, _parse_xbrl_sheet_prior(df))
        elif category == "aruskas":
            _smart_merge(aruskas_curr, _parse_xbrl_sheet(df))
            _smart_merge(aruskas_prior, _parse_xbrl_sheet_prior(df))

    quarters = {
        "Y Current": {
            "neraca": neraca_curr,
            "labarugi": labarugi_curr,
            "aruskas": aruskas_curr,
        },
        "Y-1 Prior": {
            "neraca": neraca_prior,
            "labarugi": labarugi_prior,
            "aruskas": aruskas_prior,
        },
    }
    return quarters


# ── XBRL-aware account keyword lookup ──────────────────────────────────────
# Override gi() for XBRL labels which use different naming conventions
XBRL_ACCOUNT_ALIASES = {
    "total aset": ["jumlah aset", "total aset"],
    "total liabilitas": ["jumlah liabilitas", "total liabilitas"],
    "total ekuitas": ["jumlah ekuitas", "total ekuitas"],
    "kas dan setara kas": ["kas dan setara kas", "kas dan bank"],
    "piutang usaha": ["piutang usaha", "piutang pelanggan"],
    "persediaan": ["persediaan", "persediaan lancar"],
    "total aset lancar": ["jumlah aset lancar", "total aset lancar"],
    "aset tetap": ["aset tetap", "properti investasi"],
    "liabilitas jangka pendek": ["jumlah liabilitas jangka pendek", "total liabilitas jangka pendek"],
    "liabilitas jangka panjan": ["jumlah liabilitas jangka panjang", "total liabilitas jangka panjang"],
    "total pendapatan": ["penjualan dan pendapatan usaha", "jumlah pendapatan usaha", "total pendapatan"],
    "laba kotor": ["jumlah laba bruto", "laba kotor", "laba bruto"],
    "total beban usaha": ["beban umum dan administrasi", "total beban usaha", "jumlah beban usaha"],
    "laba usaha": ["jumlah laba (rugi) usaha", "laba usaha", "laba (rugi) usaha"],
    "laba sebelum pajak": ["jumlah laba (rugi) sebelum pajak", "laba sebelum pajak"],
    "beban pajak penghasilan": ["pendapatan (beban) pajak", "beban pajak penghasilan"],
    "laba bersih tahun berjalan": ["jumlah laba (rugi)", "laba bersih", "jumlah laba (rugi) dari operasi yang dilanjutkan"],
    "arus kas dari aktivitas operasi": ["kas diperoleh dari (digunakan untuk) operasi", "arus kas bersih"],
}


def gi_xbrl(data: dict, *keywords) -> float:
    """Enhanced gi() that also checks XBRL aliases."""
    # First try standard gi()
    result = gi(data, *keywords)
    if result != 0.0:
        return result
    
    # Try XBRL aliases
    for kw in keywords:
        aliases = XBRL_ACCOUNT_ALIASES.get(kw, [])
        for alias in aliases:
            for k, v in data.items():
                if alias in k.lower():
                    return v
    return 0.0


def extract_raw_accounts_xbrl(quarters: dict) -> dict:
    """Like extract_raw_accounts but with XBRL-aware label matching."""
    out = {}
    for q in sorted_quarters(quarters):
        bs = quarters[q].get("neraca", {})
        pl = quarters[q].get("labarugi", {})
        cf = quarters[q].get("aruskas", {})
        row = {}
        for key, (section, kw) in ACCOUNT_KEYS.items():
            src = {"neraca": bs, "labarugi": pl, "aruskas": cf}[section]
            row[key] = gi_xbrl(src, kw)
        out[q] = row
    return out



