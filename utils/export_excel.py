# -*- coding: utf-8 -*-
"""Export hasil analisis (dict of DataFrame / dict biasa) ke satu file Excel
dengan tiap modul jadi 1 sheet, plus formatting header sederhana."""

import io
import pandas as pd


def export_results_to_excel(sheets: dict, filename: str = "hasil_analisis.xlsx") -> bytes:
    """
    sheets: dict {nama_sheet: pandas.DataFrame}
    Contoh:
        sheets = {
            "Kepatuhan": df_kepatuhan,
            "Komparasi": df_komparasi,
            "Rasio": df_rasio,
            "ML Voting": df_ml,
        }
    Return: bytes siap dikirim lewat dcc.send_bytes
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]  # batas nama sheet Excel
            df.to_excel(writer, sheet_name=safe_name, index=False)
            ws = writer.sheets[safe_name]
            for col_idx, col in enumerate(df.columns, start=1):
                max_len = max([len(str(col))] + [len(str(v)) for v in df[col].astype(str)])
                ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 2, 50)
    buf.seek(0)
    return buf.read()
