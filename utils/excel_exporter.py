# -*- coding: utf-8 -*-
"""
utils/excel_exporter.py
Export hasil analisis ke format Kertas Kerja OJK resmi.
Membaca template Excel, mengisi data hasil analisis, dan return bytes.
"""
import io
import os
from datetime import datetime
from copy import copy

import openpyxl


# Path ke template
_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir,
    "Kertas Kerja - GenAI LK PMDK - edit hms_1205.xlsx"
)


def _fill_metadata(ws, entity_name: str, entity_type: str,
                   report_type: str, period: str,
                   meta_col: str = "E"):
    """Fill metadata cells (Nama Entitas, Jenis, Periode, Tanggal AI)."""
    # Find metadata rows by scanning column C
    for row in range(1, min(12, ws.max_row + 1)):
        cell_c = ws[f"C{row}"].value
        if not cell_c:
            continue
        label = str(cell_c).strip().lower()
        target_col = meta_col
        if "nama entitas" in label:
            ws[f"{target_col}{row}"] = f": {entity_name}"
        elif "jenis eni" in label or "jenis entitas" in label:
            ws[f"{target_col}{row}"] = f": {entity_type}"
        elif "jenis laporan" in label:
            ws[f"{target_col}{row}"] = f": {report_type}"
        elif "periode laporan" in label or "periode" == label:
            ws[f"{target_col}{row}"] = f": {period}"
        elif "tanggal generate" in label:
            ws[f"{target_col}{row}"] = f": {datetime.now().strftime('%d-%m-%Y')}"


def _fill_kepatuhan(ws, kepatuhan: dict):
    """Fill sheet Pengecekan Kepatuhan."""
    if not kepatuhan or "error" in kepatuhan:
        return

    rows = kepatuhan.get("rows", [])
    # Data starts at row 15, header at row 14
    # Columns: C=No, D=Komponen, E=Entitas, F=Kriteria, G=Status, H=Hasil AI, I=Halaman, J=Catatan AI
    row_idx = 15
    for r in rows:
        # Find the matching row by No
        found = False
        for scan_row in range(15, ws.max_row + 1):
            cell_no = ws[f"C{scan_row}"].value
            if cell_no is not None and str(cell_no).strip() == str(r.get("No", "")):
                found = True
                ws[f"G{scan_row}"] = r.get("Status", "NA")
                ws[f"H{scan_row}"] = r.get("Hasil AI", "")
                ws[f"I{scan_row}"] = str(r.get("Halaman", ""))
                ws[f"J{scan_row}"] = r.get("Catatan AI", "")
                break
        if not found and row_idx <= ws.max_row:
            ws[f"G{row_idx}"] = r.get("Status", "NA")
            ws[f"H{row_idx}"] = r.get("Hasil AI", "")
            ws[f"I{row_idx}"] = str(r.get("Halaman", ""))
            ws[f"J{row_idx}"] = r.get("Catatan AI", "")
            row_idx += 1


def _fill_komparasi(ws, komparasi: dict):
    """Fill sheet Analisis Komparasi."""
    if not komparasi:
        return

    # Get first (or only) entity's data
    entity_data = next(iter(komparasi.values()), {})
    mismatches = entity_data.get("mismatches", [])
    q_curr = entity_data.get("q_curr", "Y")
    q_prev = entity_data.get("q_prev", "Y-1")

    # Build lookup: akun_name_lower -> mismatch_data
    mismatch_lookup = {}
    for m in mismatches:
        mismatch_lookup[m["akun"].lower()] = m

    # Scan template rows and fill matching data
    # Columns: C=No, D=Bagian, E=Entitas, F=Akun, G=Data PDF, H=Data Terstruktur,
    #          I=Sumber, J=Selisih, K=Status, L=Halaman, M=Catatan AI
    for row in range(15, ws.max_row + 1):
        akun_cell = ws[f"F{row}"].value
        if not akun_cell:
            continue
        akun = str(akun_cell).strip().lower()

        # Try to match with extracted data
        matched = None
        for key, data in mismatch_lookup.items():
            if akun in key or key in akun:
                matched = data
                break

        if matched:
            ws[f"H{row}"] = matched.get("nilai_y", 0)
            ws[f"G{row}"] = matched.get("nilai_y1", 0)  # Prior year from PDF
            ws[f"J{row}"] = matched.get("selisih", 0)
            pct = matched.get("pct", 0)
            ws[f"K{row}"] = "TIDAK SESUAI" if abs(pct) >= 30 else "SESUAI"
            ws[f"M{row}"] = f"Deviasi {pct:.1f}%"
        else:
            ws[f"K{row}"] = "SESUAI"

    # Write narrative if available
    narrative = entity_data.get("narrative", "")
    if narrative:
        # Find last data row + 2
        last_row = ws.max_row + 2
        ws[f"C{last_row}"] = "Narasi AI"
        ws[f"D{last_row}"] = narrative


def _fill_rasio(ws, rasio: dict):
    """Fill sheet Analisis Rasio."""
    if not rasio:
        return

    entity_data = next(iter(rasio.values()), {})
    rasio_rows = entity_data.get("rasio_rows", [])
    q_curr = entity_data.get("q_curr", "Y")
    q_prev = entity_data.get("q_prev", "Y-1")

    # Build lookup by rasio name
    rasio_lookup = {}
    for r in rasio_rows:
        rasio_lookup[r["rasio"].lower()] = r

    # Columns: C=No, D=Kategori, E=Entitas, F=Rasio, G=Nilai Y-1, H=Nilai Y, I=Analisis AI
    for row in range(15, ws.max_row + 1):
        rasio_cell = ws[f"F{row}"].value
        if not rasio_cell:
            continue
        rasio_name = str(rasio_cell).strip().lower()

        matched = None
        for key, data in rasio_lookup.items():
            if rasio_name in key or key in rasio_name:
                matched = data
                break

        if matched:
            y1 = matched.get("y1", 0)
            y = matched.get("y", 0)
            ws[f"G{row}"] = round(y1, 4) if isinstance(y1, float) else y1
            ws[f"H{row}"] = round(y, 4) if isinstance(y, float) else y
            ws[f"I{row}"] = matched.get("analisis_ai", "")


def _fill_calk(ws, calk: dict):
    """Fill sheet Analisis CaLK."""
    if not calk or "error" in calk:
        return

    findings = calk.get("catatan_signifikan", [])
    # Columns: C=No, D=Entitas, E=Referensi, F=Kategori, G=Temuan AI, H=Catatan, I=Halaman
    for i, f in enumerate(findings):
        row = 15 + i
        ws[f"C{row}"] = i + 1
        ws[f"E{row}"] = f.get("referensi", "")
        ws[f"F{row}"] = f.get("kategori", "")
        ws[f"G{row}"] = f.get("temuan_ai", "")
        ws[f"H{row}"] = f.get("catatan_keterangan", "")
        ws[f"I{row}"] = str(f.get("halaman", ""))


def _fill_ml(ws, ml: dict):
    """Fill sheet Analisis Kewajaran Penyajian (ML Voting)."""
    if not ml or "error" in ml:
        return

    entity_data = next(iter(ml.values()), {}) if isinstance(ml, dict) else {}
    if not entity_data or "error" in entity_data:
        return

    # Row 9 = Benford, Row 10 = Beneish, Row 11 = Blackbox, Row 12 = Voting
    benford = entity_data.get("benford", {})
    beneish = entity_data.get("beneish", {})
    verdict = entity_data.get("verdict", "")
    avg_prob = entity_data.get("avg_prob", 0)

    _anomaly_icon = lambda v: "🟢 LOW" if v == "CLEAN" else "🔴 HIGH" if v == "FRAUD" else "🟡 MEDIUM"

    # Benford
    ws["E9"] = benford.get("detail", "")
    ws["F9"] = f"Verdict: {benford.get('verdict', 'N/A')}"
    ws["H9"] = _anomaly_icon(benford.get("verdict", ""))

    # Beneish
    ws["E10"] = beneish.get("detail", "")
    ws["F10"] = f"Verdict: {beneish.get('verdict', 'N/A')}"
    ws["H10"] = _anomaly_icon(beneish.get("verdict", ""))

    # Blackbox (row 11)
    ws["F11"] = f"Avg Probability: {avg_prob:.2%}" if avg_prob else ""
    ws["H11"] = _anomaly_icon(verdict)

    # Voting result (row 12)
    ws["F12"] = f"Final Verdict: {verdict}"
    ws["H12"] = _anomaly_icon(verdict)


def _fill_kesimpulan(ws, result: dict):
    """Fill sheet Kesimpulan Rekomendasi."""
    pdf_data = result.get("pdf", {})
    excel_data = result.get("excel", {})

    # Tentang Entitas (row 15)
    kepatuhan = pdf_data.get("kepatuhan", {})
    tentang = kepatuhan.get("tentang", "")
    if tentang:
        ws["C15"] = tentang

    # Bagian 1 - Kesimpulan Kepatuhan (row 18)
    kp_narrative = kepatuhan.get("narrative", "")
    if kp_narrative:
        ws["C19"] = kp_narrative

    # Bagian Komparasi
    kmp = excel_data.get("komparasi", {})
    if kmp:
        entity_data = next(iter(kmp.values()), {})
        ws["C22"] = entity_data.get("narrative", "")

    # Bagian Rasio
    rs = excel_data.get("rasio", {})
    if rs:
        entity_data = next(iter(rs.values()), {})
        ws["C25"] = entity_data.get("narrative", "")

    # Bagian CaLK
    calk = pdf_data.get("calk", {})
    if calk:
        ws["C28"] = calk.get("narrative", "")


def generate_kertas_kerja(result: dict, entity_name: str = "",
                          entity_type: str = "Emiten",
                          report_type: str = "Laporan Keuangan",
                          period: str = "2026") -> bytes:
    """
    Generate Kertas Kerja OJK Excel dari template + hasil analisis.
    
    Args:
        result: Dict hasil pipeline {pdf: {...}, excel: {...}}
        entity_name: Nama entitas
        entity_type: Jenis entitas (Emiten/MI/RD)
        report_type: Jenis laporan
        period: Periode laporan
    
    Returns:
        bytes: Excel file content
    """
    # Load template
    template_path = os.path.normpath(_TEMPLATE_PATH)
    wb = openpyxl.load_workbook(template_path)

    pdf_data = result.get("pdf", {})
    excel_data = result.get("excel", {})

    # Auto-detect entity name from data
    if not entity_name:
        kp_meta = pdf_data.get("kepatuhan", {}).get("meta", {})
        entity_name = kp_meta.get("nama_entitas", "")
        if not entity_name and excel_data:
            # Try from komparasi keys
            kmp = excel_data.get("komparasi", {})
            if kmp:
                entity_name = next(iter(kmp.keys()), "")

    # Fill metadata in all sheets
    for sheet_name in wb.sheetnames:
        if sheet_name in ("Information", "Kompilasi Kriteria"):
            continue
        ws = wb[sheet_name]
        # Detect metadata column (E or F depending on sheet)
        meta_col = "E"
        for row in range(4, 10):
            for col in ["E", "F"]:
                cell = ws[f"{col}{row}"].value
                if cell and str(cell).strip().startswith(":"):
                    meta_col = col
                    break
        _fill_metadata(ws, entity_name, entity_type, report_type, period, meta_col)

    # Fill each analysis sheet
    if "Pengecekan Kepatuhan" in wb.sheetnames and pdf_data.get("kepatuhan"):
        _fill_kepatuhan(wb["Pengecekan Kepatuhan"], pdf_data["kepatuhan"])

    if "Analisis Komparasi" in wb.sheetnames and excel_data.get("komparasi"):
        _fill_komparasi(wb["Analisis Komparasi"], excel_data["komparasi"])

    if "Analisis Rasio" in wb.sheetnames and excel_data.get("rasio"):
        _fill_rasio(wb["Analisis Rasio"], excel_data["rasio"])

    if "Analisis CaLK" in wb.sheetnames and pdf_data.get("calk"):
        _fill_calk(wb["Analisis CaLK"], pdf_data["calk"])

    if "Analisis Kewajaran Penyajian" in wb.sheetnames and excel_data.get("ml"):
        _fill_ml(wb["Analisis Kewajaran Penyajian"], excel_data["ml"])

    if "Kesimpulan Rekomendasi" in wb.sheetnames:
        _fill_kesimpulan(wb["Kesimpulan Rekomendasi"], result)

    # Save to bytes
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()
