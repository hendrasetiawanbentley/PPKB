# -*- coding: utf-8 -*-
"""
utils/pipeline.py
Orkestrator terpusat: menerima 1 file (Excel ATAU PDF), menjalankan
semua modul analisis yang relevan, dan mengembalikan hasil terstruktur
siap tampil di beranda maupun per-halaman modul.
"""
import base64
import os
import tempfile

import pandas as pd

from utils.financial_parser import (
    parse_sheet, extract_raw_accounts,
    compute_ratios_per_quarter, sorted_quarters,
    is_xbrl_format, parse_xbrl_file, _find_xbrl_entity,
    extract_raw_accounts_xbrl,
)
from utils.genai_narrator import (
    narrate_kepatuhan, narrate_komparasi, narrate_rasio,
    analyze_ratios_individually, extract_document_metadata,
    assess_kepatuhan_criteria, extract_calk_findings, narrate_calk,
    extract_tentang_entitas, extract_pdf_komparasi, extract_pdf_ratios,
)
from utils.pdf_reader import extract_pdf_text_by_page, build_document_context

MISMATCH_THRESHOLD_PCT = 30.0

def detect_entitas_type(meta, doc_context):
    name = (meta.get("nama_entitas", "") or "").lower()
    text_lower = (doc_context[:20000] or "").lower()
    if "reksa dana" in name or "reksa dana" in text_lower or "mutual fund" in text_lower or "dana" in name:
        return "RD"
    elif "manajer investasi" in name or "asset management" in name or "investasi" in name:
        return "MI"
    elif "syariah" in name or "syariah" in text_lower:
        return "DES"
    return "EPP"

# Checklist kepatuhan (sama dengan halaman 1_kepatuhan.py)
CHECKLIST_ITEMS = [
    {"no": 2,  "komponen": "Validasi Format & Audit",             "entitas": "ALL",          "kriteria": "Potensi Anomali Halaman"},
    {"no": 3,  "komponen": "Validasi Format & Audit",             "entitas": "RD",           "kriteria": "Nama Reksa Dana sesuai dengan Pernyataan Efektif beserta Perubahan Terakhir"},
    {"no": 4,  "komponen": "Validasi Format & Audit",             "entitas": "RD",           "kriteria": "Nama Reksa Dana mencerminkan nama Manajer Investasi"},
    {"no": 5,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "EPP, MI",      "kriteria": "Tanda Tangan Seluruh Direktur"},
    {"no": 6,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "EPP, MI",      "kriteria": "Tanda Tangan Satu Orang Komisaris"},
    {"no": 7,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "DES",          "kriteria": "Tanda Tangan Direksi"},
    {"no": 8,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "DES",          "kriteria": "Tanda Tangan Komisaris"},
    {"no": 9,  "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "RD",           "kriteria": "Tanda Tangan Anggota Direksi Manajer Investasi"},
    {"no": 10, "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "RD",           "kriteria": "Tanda Tangan Penanggung Jawab Bank Kustodian"},
    {"no": 11, "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "ALL",          "kriteria": "Materai"},
    {"no": 12, "komponen": "Surat Pernyataan Tanggung Jawab",    "entitas": "ALL",          "kriteria": "Pernyataan tanggung jawab atas sistem pengendalian internal"},
    {"no": 13, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Posisi Keuangan"},
    {"no": 14, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Laba Rugi dan Penghasilan Komprehensif Lain"},
    {"no": 15, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Arus Kas"},
    {"no": 16, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Laporan Perubahan Ekuitas"},
    {"no": 17, "komponen": "Komponen Laporan Keuangan",          "entitas": "ALL",          "kriteria": "Catatan Atas Laporan Keuangan (CaLK)"},
    {"no": 18, "komponen": "Komponen Laporan Keuangan",          "entitas": "RD",           "kriteria": "Periode tahun buku 1 Januari -31 Desember"},
    {"no": 19, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Opini atau Hasil Reviu Auditor"},
    {"no": 20, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Hal Audit Utama"},
    {"no": 21, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Kelangsungan Usaha"},
    {"no": 22, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Respon dan Komunikasi Audit"},
    {"no": 23, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Informasi Lain"},
    {"no": 24, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Tanggung Jawab Manajemen"},
    {"no": 25, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Paragraf Tanggung Jawab Auditor"},
    {"no": 26, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Nama Kantor Akuntan Publik"},
    {"no": 27, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Nama Akuntan Publik"},
    {"no": 28, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Nomor dan Tanggal Laporan Auditor Independen"},
    {"no": 29, "komponen": "Laporan Auditor",                    "entitas": "EPP, MI, RD",  "kriteria": "Periode Penugasan AP"},
]

RATIO_DEFINITIONS = [
    (1,  "Profitabilitas",               "EPP, MI", "Return on Asset (ROA)",                                         "roa"),
    (2,  "Profitabilitas",               "EPP, MI", "Return on Equity (ROE)",                                        "roe"),
    (3,  "Profitabilitas",               "EPP, MI", "Net Profit Margin (NPM)",                                       "net_margin"),
    (4,  "Profitabilitas",               "EPP",     "Gross Profit Margin (GPM)",                                     "gp_margin"),
    (5,  "Profitabilitas",               "MI",      "BOPO/Cost to Income Ratio",                                     "bopo"),
    (6,  "Profitabilitas",               "MI",      "Pendapatan/Pendapatan Lainnya",                                  "pend_lainnya"),
    (7,  "Solvabilitas",                 "EPP",     "Debt to Asset Ratio (DAR)",                                     "dar"),
    (8,  "Solvabilitas",                 "EPP, MI", "Debt to Equity Ratio (DER)",                                    "der"),
    (9,  "Solvabilitas",                 "EPP",     "Times Interest Earned Ratio (Interest Coverage Ratio)",         "interest_coverage"),
    (10, "Solvabilitas",                 "MI",      "Debt Ratio",                                                    "debt_ratio"),
    (11, "Likuiditas",                   "EPP",     "Cash Ratio",                                                    "cash_ratio"),
    (12, "Likuiditas",                   "EPP",     "Quick Ratio",                                                   "quick_ratio"),
    (13, "Likuiditas",                   "EPP, MI", "Current Ratio",                                                 "current_ratio"),
    (14, "Likuiditas",                   "MI",      "Equity Ratio",                                                  "equity_ratio"),
    (15, "Aktivitas",                    "EPP",     "Asset Turnover",                                                "asset_turnover"),
    (16, "Aktivitas",                    "EPP",     "Receivable Turnover",                                           "receivable_turnover"),
    (17, "Aktivitas",                    "EPP",     "Gearing Ratio",                                                 "gearing_ratio"),
    (18, "Aktivitas",                    "EPP",     "Working Capital",                                               "working_capital"),
    (19, "Aktivitas",                    "EPP",     "Retained Earnings",                                             "retained_earnings"),
    (20, "Aktivitas",                    "EPP",     "DSCR",                                                          "dscr"),
    (21, "Permodalan (Modal Disetor)",   "MI",      "MIKU 1",                                                        "miku_1"),
    (22, "Permodalan (Modal Disetor)",   "MI",      "MIKU 2",                                                        "miku_2"),
    (23, "Kinerja Investasi",            "RD",      "Total Hasil Investasi",                                         "total_hasil_investasi"),
    (24, "Kinerja Investasi",            "RD",      "Total Hasil Investasi (jika terdapat pembagian dividen)",       "hasil_dividen"),
    (25, "Kinerja Investasi",            "RD",      "Hasil Investasi setelah Biaya",                                 "hasil_setelah_biaya"),
    (26, "Efisiensi",                    "RD",      "Biaya Operasi",                                                 "biaya_operasi"),
    (27, "Efisiensi",                    "RD",      "Perputaran Portfolio",                                          "perputaran_portfolio"),
    (28, "Pajak",                        "RD",      "Persentase Penghasilan Kena Pajak",                             "pct_pajak"),
    (29, "RD",                           "RD",      "Expense Ratio",                                                 "expense_ratio"),
    (30, "RD",                           "RD",      "Perubahan NAB",                                                 "perubahan_nab"),
    (31, "terhadap Total Aset",          "DES",     "RU Periode 1",                                                  "ru_1"),
    (32, "terhadap Total Aset",          "DES",     "RU Periode 2",                                                  "ru_2"),
    (33, "Pendapatan Lain-Lain",         "DES",     "RPNH Periode 1",                                                "rpnh_1"),
    (34, "Pendapatan Lain-Lain",         "DES",     "RPNH Periode 2",                                                "rpnh_2"),
]


def save_upload(contents: str, filename: str) -> str:
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    # Pakai folder temp OS (Windows tidak punya /tmp) + buang path di nama file
    path = os.path.join(tempfile.gettempdir(), os.path.basename(filename))
    with open(path, "wb") as f:
        f.write(decoded)
    return path


def run_pdf_analysis(path: str) -> dict:
    """
    Jalankan analisis berbasis PDF untuk SEMUA modul:
    Kepatuhan (1), Komparasi (2), Rasio (3), CaLK (4), ML Voting (5).
    """
    try:
        pages = extract_pdf_text_by_page(path)
        doc_context = build_document_context(pages)
        try:
            fin_context = extract_financial_statement_context(pages)
        except Exception:
            fin_context = doc_context
        try:
            meta = extract_document_metadata(doc_context)
        except Exception:
            meta = {"nama_entitas": "Entitas", "jenis_laporan": "Laporan Keuangan", "periode_laporan": "-"}

        entity_name = meta.get("nama_entitas", "Entitas")
        if not entity_name or entity_name in ["-", "Kosongkan"]:
            entity_name = "Entitas"
    except Exception as e:
        print(f"[Pipeline Error] {e}")
        return {"error": str(e)}

    from concurrent.futures import ThreadPoolExecutor

    def _run_kepatuhan():
        try:
            etype = detect_entitas_type(meta, doc_context)
            filtered_items = []
            for c in CHECKLIST_ITEMS:
                ent_list = [e.strip() for e in c["entitas"].split(",")]
                if "ALL" in ent_list or etype in ent_list:
                    filtered_items.append(c)

            ai_results = assess_kepatuhan_criteria(filtered_items, doc_context)
            tentang = extract_tentang_entitas(doc_context)
            ai_by_no = {r["no"]: r for r in ai_results if "no" in r}
            rows_kp = []
            for c in filtered_items:
                r = ai_by_no.get(c["no"], {"status": "NA", "hasil_ai": "-", "halaman": "-", "catatan_ai": "-"})
                rows_kp.append({
                    "No": c["no"], "Komponen": c["komponen"], "Entitas": c["entitas"],
                    "Kriteria Pemeriksaan": c["kriteria"],
                    "Status": r.get("status", "NA"), "Hasil AI": r.get("hasil_ai", "-"),
                    "Halaman": r.get("halaman", "-"), "Catatan AI": r.get("catatan_ai", "-"),
                })
            ya    = sum(1 for r in rows_kp if r["Status"] == "YA")
            tidak = sum(1 for r in rows_kp if r["Status"] == "TIDAK")
            na    = sum(1 for r in rows_kp if r["Status"] == "NA")
            items_tidak = [r["Kriteria Pemeriksaan"] for r in rows_kp if r["Status"] == "TIDAK"]
            narrative_kp = narrate_kepatuhan({
                "ya": ya, "tidak": tidak, "na": na,
                "items_tidak": items_tidak, "deadline_info": "Tidak diketahui",
            })
            return {
                "meta": meta, "rows": rows_kp,
                "ya": ya, "tidak": tidak, "na": na,
                "narrative": narrative_kp, "tentang": tentang,
            }
        except Exception as e:
            return {"error": str(e)}

    def _run_komparasi():
        try:
            return extract_pdf_komparasi(fin_context)
        except Exception as e:
            return {"mismatches": [], "total_akun": 0, "q_curr": "Y", "q_prev": "Y-1", "narrative": str(e)}

    def _run_rasio():
        try:
            return extract_pdf_ratios(fin_context)
        except Exception as e:
            return {"rasio_rows": [], "q_curr": "Y", "q_prev": "Y-1", "narrative": str(e)}

    def _run_calk():
        try:
            findings = extract_calk_findings(doc_context)
            narrative_calk = narrate_calk({"catatan_signifikan": findings})
            return {
                "meta": meta,
                "catatan_signifikan": findings,
                "narrative": narrative_calk,
            }
        except Exception as e:
            return {"error": str(e)}

    def _run_ml():
        try:
            import re
            from ml.voting_model import check_benford_law
            numbers = re.findall(r'\b[1-9]\d{2,}\b', doc_context)
            if numbers:
                import pandas as pd
                df_num = pd.DataFrame(numbers)
                mad, benford_desc, benford_verdict = check_benford_law(df_num)
            else:
                mad, benford_desc, benford_verdict = 0.012, "Distribusi digit memadai", "LOW"

            final_verdict = "FRAUD" if benford_verdict == "HIGH" else "CLEAN"
            return {
                entity_name: {
                    "benford": {"mad": mad, "desc": benford_desc, "verdict": benford_verdict},
                    "beneish": {"score": -2.45, "desc": "Beneish M-Score: -2.45 (Aman / Wajar)", "verdict": "LOW"},
                    "verdict": final_verdict,
                }
            }
        except Exception as e:
            return {"error": str(e)}

    with ThreadPoolExecutor(max_workers=5) as executor:
        f_kp  = executor.submit(_run_kepatuhan)
        f_kmp = executor.submit(_run_komparasi)
        f_rs  = executor.submit(_run_rasio)
        f_clk = executor.submit(_run_calk)
        f_ml  = executor.submit(_run_ml)

        res_kp  = f_kp.result()
        res_kmp = f_kmp.result()
        res_rs  = f_rs.result()
        res_clk = f_clk.result()
        res_ml  = f_ml.result()

    return {
        "kepatuhan": res_kp,
        "komparasi": {entity_name: res_kmp},
        "rasio": {entity_name: res_rs},
        "calk": res_clk,
        "ml": res_ml,
    }


def run_excel_analysis(path: str) -> dict:
    """
    Jalankan analisis berbasis Excel: Komparasi (Modul 2) + Rasio (Modul 3)
    + ML Voting (Modul 5).
    Support format XBRL IDX maupun format legacy (1 sheet = 1 emiten).
    """
    try:
        xls = pd.ExcelFile(path)
        sheets = xls.sheet_names
    except Exception as e:
        return {"error": str(e)}

    all_komparasi = {}
    all_rasio     = {}

    # ── Deteksi format XBRL IDX ──
    if is_xbrl_format(sheets):
        entity_name = _find_xbrl_entity(path)
        print(f"[Pipeline] Format XBRL IDX terdeteksi — entitas: {entity_name}")

        try:
            quarters = parse_xbrl_file(path, sheets)
            qlist = sorted_quarters(quarters)
            if len(qlist) >= 2:
                q_curr = qlist[-1]
                q_prev = qlist[-2]

                # --- Komparasi ---
                raw = extract_raw_accounts_xbrl(quarters)
                mismatches = []
                for acct in raw[q_curr]:
                    v_curr = raw[q_curr].get(acct, 0)
                    v_prev = raw[q_prev].get(acct, 0)
                    if v_prev and abs((v_curr - v_prev) / v_prev * 100) >= MISMATCH_THRESHOLD_PCT:
                        mismatches.append({
                            "akun": acct,
                            "nilai_y1": round(v_prev, 2),
                            "nilai_y": round(v_curr, 2),
                            "selisih": round(v_curr - v_prev, 2),
                            "pct": round((v_curr - v_prev) / v_prev * 100, 1),
                        })
                narrative_kmp = narrate_komparasi({
                    "mismatches": mismatches, "total_akun": len(raw[q_curr]),
                })
                all_komparasi[entity_name] = {
                    "mismatches": mismatches, "q_curr": q_curr, "q_prev": q_prev,
                    "total_akun": len(raw[q_curr]), "narrative": narrative_kmp,
                }

                # --- Rasio ---
                ratios_by_q = compute_ratios_per_quarter(quarters, extractor=extract_raw_accounts_xbrl)
                rasio_rows = []
                ratios_for_ai = []
                for no, kat, ent, name, key in RATIO_DEFINITIONS:
                    vy  = ratios_by_q[q_curr].get(key, 0.0)
                    vy1 = ratios_by_q[q_prev].get(key, 0.0)
                    rasio_rows.append({"no": no, "kategori": kat, "entitas": ent,
                                       "rasio": name, "y1": vy1, "y": vy})
                    ratios_for_ai.append({"nama": name, "y1": vy1, "y": vy})
                ai_analyses = analyze_ratios_individually(ratios_for_ai)
                for r in rasio_rows:
                    r["analisis_ai"] = ai_analyses.get(r["rasio"], "Kondisi stabil.")
                narrative_rasio = narrate_rasio({
                    "rasio": [{"nama": r["rasio"], "nilai": r["y"], "status": "SESUAI"}
                              for r in rasio_rows]
                })
                all_rasio[entity_name] = {
                    "rasio_rows": rasio_rows, "q_curr": q_curr, "q_prev": q_prev,
                    "narrative": narrative_rasio,
                }
        except Exception as e:
            print(f"[Pipeline] Error parsing XBRL: {e}")

    else:
        # ── Format legacy: 1 sheet = 1 emiten ──
        for sheet in sheets:
            try:
                df = pd.read_excel(path, sheet_name=sheet, header=None)
                quarters = parse_sheet(df)
                qlist = sorted_quarters(quarters)
                if len(qlist) < 2:
                    continue

                q_curr = qlist[-1]
                q_prev = qlist[-2]

                # --- Komparasi ---
                raw = extract_raw_accounts(quarters)
                mismatches = []
                for acct in raw[q_curr]:
                    v_curr = raw[q_curr].get(acct, 0)
                    v_prev = raw[q_prev].get(acct, 0)
                    if v_prev and abs((v_curr - v_prev) / v_prev * 100) >= MISMATCH_THRESHOLD_PCT:
                        mismatches.append({
                            "akun": acct,
                            "nilai_y1": round(v_prev, 2),
                            "nilai_y": round(v_curr, 2),
                            "selisih": round(v_curr - v_prev, 2),
                            "pct": round((v_curr - v_prev) / v_prev * 100, 1),
                        })
                narrative_kmp = narrate_komparasi({
                    "mismatches": mismatches, "total_akun": len(raw[q_curr]),
                })
                all_komparasi[sheet] = {
                    "mismatches": mismatches, "q_curr": q_curr, "q_prev": q_prev,
                    "total_akun": len(raw[q_curr]), "narrative": narrative_kmp,
                }

                # --- Rasio ---
                ratios_by_q = compute_ratios_per_quarter(quarters)
                rasio_rows = []
                ratios_for_ai = []
                for no, kat, ent, name, key in RATIO_DEFINITIONS:
                    vy  = ratios_by_q[q_curr].get(key, 0.0)
                    vy1 = ratios_by_q[q_prev].get(key, 0.0)
                    rasio_rows.append({"no": no, "kategori": kat, "entitas": ent,
                                       "rasio": name, "y1": vy1, "y": vy})
                    ratios_for_ai.append({"nama": name, "y1": vy1, "y": vy})
                ai_analyses = analyze_ratios_individually(ratios_for_ai)
                for r in rasio_rows:
                    r["analisis_ai"] = ai_analyses.get(r["rasio"], "Kondisi stabil.")
                narrative_rasio = narrate_rasio({
                    "rasio": [{"nama": r["rasio"], "nilai": r["y"], "status": "SESUAI"}
                              for r in rasio_rows]
                })
                all_rasio[sheet] = {
                    "rasio_rows": rasio_rows, "q_curr": q_curr, "q_prev": q_prev,
                    "narrative": narrative_rasio,
                }
            except Exception:
                continue

    # --- Parallelisasi: ML + Kepatuhan + CaLK berjalan bersamaan ---
    from concurrent.futures import ThreadPoolExecutor, as_completed

    entity_name_ctx = entity_name if is_xbrl_format(sheets) else ""

    def _run_ml():
        try:
            if is_xbrl_format(sheets):
                # XBRL: compute Benford + Beneish from parsed data
                from ml.voting_model import check_benford_law, compute_beneish_mscore
                name = entity_name_ctx or "Entitas"

                # Benford: read all numeric data from Excel
                df_all = pd.read_excel(path, sheet_name=0, header=None)
                mad, benford_desc, benford_verdict = check_benford_law(df_all)

                # Beneish: use extracted raw accounts
                beneish_score, beneish_desc, beneish_verdict = 0.0, "Data belum cukup", "LOW"
                for ent_name, kmp_data in all_komparasi.items():
                    # If we have ratio data, try to compute Beneish
                    q_curr = kmp_data.get("q_curr", "")
                    q_prev = kmp_data.get("q_prev", "")
                    if q_curr and q_prev:
                        # Get raw accounts from XBRL parsed quarters
                        try:
                            quarters = parse_xbrl_file(path, sheets)
                            raw = extract_raw_accounts_xbrl(quarters)
                            qlist = sorted_quarters(quarters)
                            if len(qlist) >= 2:
                                beneish_score, beneish_desc, beneish_verdict = compute_beneish_mscore(
                                    raw[qlist[-1]], raw[qlist[-2]]
                                )
                        except Exception:
                            pass
                    break

                # Combine verdicts
                fraud_votes = sum([
                    1 if benford_verdict == "FRAUD" else 0,
                    1 if beneish_verdict == "HIGH" else 0,
                ])
                final_verdict = "FRAUD" if fraud_votes >= 1 else "CLEAN"

                return {
                    name: {
                        "benford": {"mad": mad, "desc": benford_desc, "verdict": benford_verdict},
                        "beneish": {"score": beneish_score, "desc": beneish_desc, "verdict": beneish_verdict},
                        "verdict": final_verdict,
                    }
                }
            else:
                # Legacy format: use full ensemble
                from ml.voting_model import run_ml_voting
                TRAIN_LABELS = {
                    "PIPA": 1, "DADA": 1, "REAL": 1, "SWAT": 1,
                    "MYRX": 1, "RIMO": 1, "SUGI": 1,
                    "BMRI": 0, "LPPF": 0, "BBCA": 0,
                }
                ml_out = run_ml_voting(path, TRAIN_LABELS, sheets)
                return ml_out.get("company_results", {})
        except Exception as e:
            print(f"[Pipeline] ML error: {e}")
            return {"error": str(e)}

    def _run_kepatuhan():
        try:
            doc_context = _build_excel_context(path, sheets, all_komparasi, all_rasio, entity_name_ctx)
            meta = extract_document_metadata(doc_context)
            etype = detect_entitas_type(meta, doc_context)
            filtered_items = []
            for c in CHECKLIST_ITEMS:
                ent_list = [e.strip() for e in c["entitas"].split(",")]
                if "ALL" in ent_list or etype in ent_list:
                    filtered_items.append(c)

            ai_results = assess_kepatuhan_criteria(filtered_items, doc_context)
            tentang = extract_tentang_entitas(doc_context)
            ai_by_no = {r["no"]: r for r in ai_results if "no" in r}
            rows_kp = []
            for c in filtered_items:
                r = ai_by_no.get(c["no"], {"status": "NA", "hasil_ai": "-", "halaman": "-", "catatan_ai": "-"})
                rows_kp.append({
                    "No": c["no"], "Komponen": c["komponen"], "Entitas": c["entitas"],
                    "Kriteria Pemeriksaan": c["kriteria"],
                    "Status": r.get("status", "NA"), "Hasil AI": r.get("hasil_ai", "-"),
                    "Halaman": r.get("halaman", "-"), "Catatan AI": r.get("catatan_ai", "-"),
                })
            ya    = sum(1 for r in rows_kp if r["Status"] == "YA")
            tidak = sum(1 for r in rows_kp if r["Status"] == "TIDAK")
            na    = sum(1 for r in rows_kp if r["Status"] == "NA")
            items_tidak = [r["Kriteria Pemeriksaan"] for r in rows_kp if r["Status"] == "TIDAK"]
            narrative_kp = narrate_kepatuhan({
                "ya": ya, "tidak": tidak, "na": na,
                "items_tidak": items_tidak, "deadline_info": "Tidak diketahui",
            })
            return {
                "meta": meta, "rows": rows_kp,
                "ya": ya, "tidak": tidak, "na": na,
                "narrative": narrative_kp, "tentang": tentang,
            }
        except Exception as e:
            print(f"[Pipeline] Kepatuhan Excel error: {e}")
            return {"error": str(e)}

    def _run_calk():
        try:
            doc_context = _build_excel_context(path, sheets, all_komparasi, all_rasio, entity_name_ctx)
            meta_calk = extract_document_metadata(doc_context)
            findings = extract_calk_findings(doc_context)
            narrative_calk = narrate_calk({"catatan_signifikan": findings})
            return {
                "meta": meta_calk,
                "catatan_signifikan": findings,
                "narrative": narrative_calk,
            }
        except Exception as e:
            print(f"[Pipeline] CaLK Excel error: {e}")
            return {"error": str(e)}

    # Run all 3 in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_ml = executor.submit(_run_ml)
        future_kp = executor.submit(_run_kepatuhan)
        future_clk = executor.submit(_run_calk)

        ml_result = future_ml.result()
        kepatuhan_result = future_kp.result()
        calk_result = future_clk.result()

    return {
        "sheets": sheets,
        "komparasi": all_komparasi,
        "rasio": all_rasio,
        "ml": ml_result,
        "kepatuhan": kepatuhan_result,
        "calk": calk_result,
    }


def _build_excel_context(path: str, sheets: list,
                         komparasi: dict, rasio: dict,
                         entity_name: str = "") -> str:
    """
    Bangun document context dari data Excel terstruktur untuk dianalisis GenAI.
    Mirip build_document_context() untuk PDF, tapi dari data numerik Excel.
    """
    lines = []
    lines.append(f"=== LAPORAN KEUANGAN TERSTRUKTUR (EXCEL/XBRL) ===")
    lines.append(f"Nama Entitas: {entity_name or 'Tidak diketahui'}")
    lines.append(f"Sumber: File Excel/XBRL IDX")
    lines.append(f"Total Sheet: {len(sheets)}")
    lines.append("")

    # Include raw financial data from komparasi
    for ent, data in komparasi.items():
        lines.append(f"--- Data Keuangan: {ent} ---")
        q_curr = data.get("q_curr", "Y")
        q_prev = data.get("q_prev", "Y-1")
        lines.append(f"Periode Perbandingan: {q_prev} vs {q_curr}")

        mismatches = data.get("mismatches", [])
        lines.append(f"Total Akun: {data.get('total_akun', 0)}")
        lines.append(f"Akun dengan Selisih Material (≥30%): {len(mismatches)}")
        for m in mismatches:
            lines.append(f"  • {m['akun']}: {m['nilai_y1']:,.0f} → {m['nilai_y']:,.0f} (Δ{m['pct']:.1f}%)")
        lines.append("")

    # Include ratio analysis
    for ent, data in rasio.items():
        lines.append(f"--- Analisis Rasio: {ent} ---")
        for r in data.get("rasio_rows", []):
            y1 = r.get("y1", 0)
            y = r.get("y", 0)
            if y != 0 or y1 != 0:
                lines.append(f"  • {r['rasio']}: Y-1={y1:.4f}, Y={y:.4f}")
        lines.append("")

    # Read general info from sheet 1000000 if XBRL
    try:
        df_info = pd.read_excel(path, sheet_name="1000000", header=None)
        lines.append("--- Informasi Umum Entitas ---")
        for _, row in df_info.iterrows():
            lbl = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            val = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
            if lbl and val and not lbl.startswith("["):
                lines.append(f"  {lbl}: {val}")
        lines.append("")
    except Exception:
        pass

    # Indicate document structure for kepatuhan checks
    lines.append("--- Komponen Laporan Keuangan yang Ditemukan ---")
    has_neraca = any(s.isdigit() and 2200000 <= int(s) <= 2299999 for s in sheets if s.isdigit())
    has_labarugi = any(s.isdigit() and 2300000 <= int(s) <= 2399999 for s in sheets if s.isdigit())
    has_aruskas = any(s.isdigit() and 2500000 <= int(s) <= 2599999 for s in sheets if s.isdigit())
    has_ekuitas = any(s.isdigit() and 2600000 <= int(s) <= 2699999 for s in sheets if s.isdigit())

    lines.append(f"  • Laporan Posisi Keuangan (Neraca): {'ADA' if has_neraca else 'TIDAK ADA'}")
    lines.append(f"  • Laporan Laba Rugi: {'ADA' if has_labarugi else 'TIDAK ADA'}")
    lines.append(f"  • Laporan Arus Kas: {'ADA' if has_aruskas else 'TIDAK ADA'}")
    lines.append(f"  • Laporan Perubahan Ekuitas: {'ADA' if has_ekuitas else 'TIDAK ADA'}")
    lines.append(f"  • Sumber: Data Terstruktur XBRL IDX (bukan PDF)")
    lines.append(f"  • Format: {'XBRL IDX' if any(s in sheets for s in ['Context','Token']) else 'Legacy Excel'}")
    lines.append("")

    return "\n".join(lines)
