# -*- coding: utf-8 -*-
"""Ekstraksi teks dokumen (PDF) per halaman, dengan penanda halaman,
supaya GenAI bisa merujuk 'ditemukan di halaman berapa'."""

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from PIL import Image
    import pytesseract
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False


def extract_pdf_text_by_page(path: str, ocr_if_empty: bool = True) -> list:
    """Return: [{'halaman': 1, 'text': '...'}, ...]"""
    if not PDF_SUPPORT:
        raise RuntimeError("pdfplumber belum terinstall. Jalankan: pip install pdfplumber")

    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = ""
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if not text.strip() and ocr_if_empty and OCR_SUPPORT:
                try:
                    im = page.to_image(resolution=200).original
                    text = pytesseract.image_to_string(im, lang="ind+eng") or ""
                except Exception:
                    text = ""
            pages.append({"halaman": i, "text": text or ""})
    return pages


def build_document_context(pages: list) -> str:
    parts = []
    for p in pages:
        txt = p.get('text') or ""
        h = p.get('halaman', 1)
        parts.append(f"--- Halaman {h} ---\n{txt}")
    return "\n".join(parts)


def extract_financial_statement_context(pages: list) -> str:
    """Filter dan pilih halaman-halaman yang paling relevan dengan Laporan Keuangan (Neraca, Laba Rugi, Arus Kas)."""
    import re
    keywords = [
        "laporan posisi keuangan", "neraca", "balance sheet",
        "laporan laba rugi", "income statement", "laba (rugi)",
        "laporan arus kas", "cash flows", "aset lancar",
        "total aset", "total liabilitas", "total ekuitas",
        "kas dan setara kas", "piutang usaha", "laba kotor"
    ]
    scored_pages = []
    for p in pages:
        txt = p.get('text') or ""
        txt_lower = txt.lower()
        score = 0
        for kw in keywords:
            if kw in txt_lower:
                score += txt_lower.count(kw) * 5
        num_count = len(re.findall(r'\b\d+[\.,]\d+\b|\b\d{3,}\b', txt))
        score += min(num_count, 30)
        if score > 5:
            scored_pages.append((score, p.get('halaman', 1), txt))
    
    scored_pages.sort(key=lambda x: x[0], reverse=True)
    top_pages = scored_pages[:20]
    top_pages.sort(key=lambda x: x[1])

    if not top_pages:
        return build_document_context(pages[:25])
    
    parts = []
    for score, page_num, text in top_pages:
        parts.append(f"--- Halaman {page_num} ---\n{text}")
    return "\n".join(parts)


