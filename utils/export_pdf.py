# -*- coding: utf-8 -*-
"""Export laporan naratif (hasil GenAI + tabel ringkas) ke PDF.
Pakai reportlab supaya tidak butuh dependency browser/wkhtmltopdf."""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

RED = colors.HexColor("#8B2E1F")


def export_report_to_pdf(sections: list, title: str = "Laporan Analisis Kewajaran Laporan Keuangan") -> bytes:
    """
    sections: list of dict, tiap dict salah satu bentuk:
        {"type": "heading", "text": "Simpulan Kepatuhan"}
        {"type": "paragraph", "text": "narasi GenAI di sini..."}
        {"type": "disclaimer", "text": "AI disclaimer text..."}
        {"type": "keyval", "rows": [["Nama", "Val"], ...]}
        {"type": "table", "headers": [...], "rows": [[...], ...], "colWidths": [...]}
        {"type": "pagebreak"}
    Return: bytes PDF siap dikirim lewat dcc.send_bytes
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=RED, fontSize=16)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#2C3E50"), fontSize=12, fontName="Helvetica-Bold", spaceBefore=10)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=15)

    story = [Paragraph(title, h1), Spacer(1, 12)]

    for sec in sections:
        t = sec.get("type")
        if t == "heading":
            story.append(Paragraph(sec["text"], h2))
            story.append(Spacer(1, 6))
        elif t == "paragraph":
            story.append(Paragraph(sec["text"], body))
            story.append(Spacer(1, 10))
        elif t == "disclaimer":
            p = Paragraph(sec["text"], ParagraphStyle("DisclaimerText", parent=body, fontSize=9, fontName="Helvetica-Oblique", leading=13, textColor=colors.HexColor("#7B241C")))
            tbl = Table([[p]], colWidths=[17*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FCE9E4")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6B0AA")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 12))
        elif t == "keyval":
            tbl_data = []
            key_style = ParagraphStyle("Key", parent=body, fontName="Helvetica-Bold", fontSize=9)
            val_style = ParagraphStyle("Val", parent=body, fontSize=9)
            for row in sec["rows"]:
                k = Paragraph(str(row[0]), key_style)
                v = Paragraph(str(row[1]), val_style)
                tbl_data.append([k, v])
            tbl = Table(tbl_data, colWidths=[4.5*cm, 12.5*cm])
            tbl.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 12))
        elif t == "table":
            header_p_style = ParagraphStyle("THeader", parent=styles["Normal"], textColor=colors.white, fontSize=9, fontName="Helvetica-Bold")
            body_p_style = ParagraphStyle("TBody", parent=body, fontSize=9, leading=12)
            
            headers = [Paragraph(str(h), header_p_style) for h in sec["headers"]]
            formatted_rows = []
            for r in sec["rows"]:
                formatted_row = []
                for val in r:
                    formatted_row.append(Paragraph(str(val), body_p_style))
                formatted_rows.append(formatted_row)
                
            data = [headers] + formatted_rows
            col_widths = sec.get("colWidths", None)
            
            # Map standard cm sizes if passed as floats/ints
            if col_widths:
                col_widths = [w * cm if isinstance(w, (int, float)) else w for w in col_widths]
                
            tbl = Table(data, colWidths=col_widths, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), RED),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D8DC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F8")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 14))
        elif t == "pagebreak":
            story.append(PageBreak())

    doc.build(story)
    buf.seek(0)
    return buf.read()
