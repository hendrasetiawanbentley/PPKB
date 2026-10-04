# -*- coding: utf-8 -*-
"""
Modul 3 — Simpulan Analisis Rasio
Reads analysis results from the shared session store populated by the Beranda page.
No local file upload — all processing happens in the home pipeline.
"""
import json
import datetime

import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback, no_update

from utils.export_excel import export_results_to_excel
from utils.export_pdf import export_report_to_pdf

dash.register_page(__name__, path="/rasio", name="3. Rasio")

# ── Design tokens ─────────────────────────────────────────────────────
RED = "#8B2E1F"
ACCENT = "#0D9488"
WHITE = "#FFFFFF"
BG = "#F2F0ED"
BORDER = "#EBEBEA"
CARD = {
    "background": WHITE,
    "borderRadius": "12px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
    "padding": "28px 32px",
    "marginBottom": "24px",
    "fontFamily": "Inter, sans-serif",
}
ACCENT_LIGHT = "#F0FDFA"


# ── Helpers ───────────────────────────────────────────────────────────
def format_ratio_value(name, val):
    """Format a ratio value for display — percentages vs raw numbers."""
    if val is None or val == "-":
        return "-"
    if isinstance(val, str) and ("%" in val or "x" in val):
        return val
    try:
        fval = float(val)
        if fval == 0.0:
            return "0.00"
        pct_ratios = [
            "Return on Asset (ROA)", "Return on Equity (ROE)",
            "Net Profit Margin (NPM)", "Gross Profit Margin (GPM)",
            "Current Ratio", "Quick Ratio", "Cash Ratio", "Working Capital to Assets",
            "BOPO/Cost to Income Ratio", "Persentase Penghasilan Kena Pajak",
            "Expense Ratio",
        ]
        if name in pct_ratios:
            return f"{fval * 100:.2f}%" if fval <= 5.0 else f"{fval:.2f}%"
        return f"{fval:.2f}x" if fval <= 50.0 else f"{fval:.2f}"
    except Exception:
        return str(val)


def _empty_state():
    return html.Div(
        [
            html.Div(
                "📐",
                style={"fontSize": "48px", "marginBottom": "16px", "opacity": "0.45"},
            ),
            html.Div(
                "Belum ada data — upload file di Beranda terlebih dahulu",
                style={
                    "fontSize": "15px",
                    "color": "#6B7280",
                    "fontWeight": "500",
                },
            ),
        ],
        style={
            **CARD,
            "textAlign": "center",
            "padding": "60px 32px",
        },
    )


def _trend_indicator(y1, y):
    """Return a small up/down/neutral arrow based on change direction."""
    try:
        v1, v2 = float(y1), float(y)
    except (TypeError, ValueError):
        return html.Span("—", style={"color": "#9CA3AF"})
    if v2 > v1:
        return html.Span("▲", style={"color": "#16A34A", "fontSize": "11px", "fontWeight": "700"})
    elif v2 < v1:
        return html.Span("▼", style={"color": "#DC2626", "fontSize": "11px", "fontWeight": "700"})
    return html.Span("●", style={"color": "#9CA3AF", "fontSize": "9px"})


def _build_sheet_card(sheet_name, sheet_data):
    """Build a result card for one sheet (emiten)."""
    rasio_rows = sheet_data.get("rasio_rows", [])
    q_curr = sheet_data.get("q_curr", "-")
    q_prev = sheet_data.get("q_prev", "-")
    narrative = sheet_data.get("narrative", "")

    # Metadata strip
    meta_strip = html.Div(
        [
            html.Div(
                [
                    html.Div(str(len(rasio_rows)), style={"fontSize": "26px", "fontWeight": "800", "color": ACCENT}),
                    html.Div("Rasio Dihitung", style={"fontSize": "11px", "color": "#6B7280", "marginTop": "2px"}),
                ],
                style={"textAlign": "center", "flex": "1"},
            ),
            html.Div(
                [
                    html.Div(q_prev, style={"fontSize": "14px", "fontWeight": "700", "color": "#374151"}),
                    html.Div("Periode Y-1", style={"fontSize": "11px", "color": "#6B7280", "marginTop": "2px"}),
                ],
                style={"textAlign": "center", "flex": "1"},
            ),
            html.Div(
                [
                    html.Div(q_curr, style={"fontSize": "14px", "fontWeight": "700", "color": "#374151"}),
                    html.Div("Periode Y", style={"fontSize": "11px", "color": "#6B7280", "marginTop": "2px"}),
                ],
                style={"textAlign": "center", "flex": "1"},
            ),
        ],
        style={
            "display": "flex",
            "gap": "12px",
            "background": "#FAFAF9",
            "borderRadius": "10px",
            "padding": "18px 12px",
            "marginBottom": "20px",
            "border": f"1px solid {BORDER}",
        },
    )

    # Table
    header_labels = ["No", "Kategori", "Rasio", f"Y-1 ({q_prev})", f"Y ({q_curr})", "Tren", "Analisis AI"]
    thead = html.Thead(
        html.Tr(
            [html.Th(
                h,
                style={
                    "padding": "10px 12px",
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "color": "#6B7280",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                    "borderBottom": f"2px solid {BORDER}",
                    "textAlign": "left",
                },
            ) for h in header_labels]
        )
    )

    cell_base = {
        "padding": "9px 12px",
        "fontSize": "13px",
        "verticalAlign": "top",
    }

    rows = []
    for r in rasio_rows:
        ai_text = r.get("analisis_ai", "")
        rows.append(
            html.Tr(
                [
                    html.Td(str(r.get("no", "")), style=cell_base),
                    html.Td(
                        r.get("kategori", ""),
                        style={**cell_base, "color": "#6B7280", "fontSize": "12px"},
                    ),
                    html.Td(r.get("rasio", ""), style={**cell_base, "fontWeight": "600"}),
                    html.Td(
                        format_ratio_value(r.get("rasio", ""), r.get("y1")),
                        style={**cell_base, "fontVariantNumeric": "tabular-nums"},
                    ),
                    html.Td(
                        format_ratio_value(r.get("rasio", ""), r.get("y")),
                        style={**cell_base, "fontVariantNumeric": "tabular-nums", "fontWeight": "600"},
                    ),
                    html.Td(_trend_indicator(r.get("y1"), r.get("y")), style={**cell_base, "textAlign": "center"}),
                    html.Td(
                        ai_text,
                        style={
                            **cell_base,
                            "fontSize": "12px",
                            "color": "#4B5563",
                            "maxWidth": "320px",
                            "lineHeight": "1.5",
                        },
                    ),
                ],
                style={"borderBottom": f"1px solid {BORDER}"},
            )
        )

    if not rows:
        rows.append(
            html.Tr(
                html.Td(
                    "Tidak ada data rasio.",
                    colSpan=7,
                    style={"padding": "24px", "textAlign": "center", "color": "#9CA3AF", "fontSize": "13px"},
                )
            )
        )

    table = html.Table(
        [thead, html.Tbody(rows)],
        className="result-table",
        style={"width": "100%", "borderCollapse": "collapse", "marginBottom": "20px"},
    )

    # Narrative
    narrative_block = html.Div(
        [
            html.Div(
                [
                    html.Span("🤖", style={"marginRight": "8px"}),
                    html.Span("Narasi AI", style={"fontWeight": "700", "fontSize": "13px", "color": "#374151"}),
                ],
                style={"marginBottom": "8px"},
            ),
            html.Div(
                narrative,
                style={
                    "fontSize": "13px",
                    "lineHeight": "1.7",
                    "color": "#4B5563",
                },
            ),
        ],
        style={
            "background": ACCENT_LIGHT,
            "border": "1px solid #CCFBF1",
            "borderRadius": "10px",
            "padding": "18px 20px",
        },
    )

    # Disclaimer
    disclaimer = html.Div(
        [
            html.Div("AI Disclaimer", style={"fontWeight": "700", "fontSize": "12px", "marginBottom": "4px"}),
            html.Div(
                "Laporan ini dihasilkan oleh proses GenAI sehingga tidak dapat serta merta dijadikan dasar "
                "pengambilan keputusan tanpa disertai dengan penelaahan dan penelitian lebih lanjut, seluruh "
                "tanggung jawab hukum dan konsekuensi dari hasil laporan ini tetap melekat pada pengambil keputusan.",
                style={"fontSize": "12px", "fontStyle": "italic", "lineHeight": "1.6"},
            ),
        ],
        style={
            "background": "#FFF7ED",
            "border": "1px solid #FED7AA",
            "padding": "12px 16px",
            "borderRadius": "8px",
            "marginTop": "16px",
            "color": "#92400E",
        },
    )

    return html.Div(
        [
            html.H3(
                sheet_name,
                style={
                    "fontSize": "16px",
                    "fontWeight": "700",
                    "color": ACCENT,
                    "marginBottom": "16px",
                    "marginTop": "0",
                },
            ),
            meta_strip,
            table,
            narrative_block,
            disclaimer,
        ],
        style=CARD,
    )


# ── Layout ────────────────────────────────────────────────────────────
layout = html.Div(
    [
        html.Div(id="rs-guard-banner"),
        # Header
        html.Div(
            [
                html.Div(
                    "📐",
                    style={
                        "fontSize": "28px",
                        "width": "52px",
                        "height": "52px",
                        "borderRadius": "14px",
                        "background": ACCENT_LIGHT,
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "marginRight": "18px",
                        "flexShrink": "0",
                    },
                ),
                html.Div(
                    [
                        html.H2(
                            "Modul 03 — Analisis Rasio",
                            style={
                                "margin": "0",
                                "fontSize": "22px",
                                "fontWeight": "800",
                                "color": RED,
                                "letterSpacing": "-0.3px",
                            },
                        ),
                        html.P(
                            "Perhitungan 34 rasio keuangan dengan perbandingan Y vs Y-1 dan analisis AI per rasio.",
                            style={
                                "margin": "4px 0 0",
                                "fontSize": "13px",
                                "color": "#6B7280",
                                "lineHeight": "1.5",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "marginBottom": "28px",
            },
        ),
        # Result area
        dcc.Loading(
            html.Div(id="rs-result-area"),
            type="dot",
            color=ACCENT,
        ),
        # Download buttons
        html.Div(
            [
                html.Button(
                    [html.Span("⬇  ", style={"marginRight": "4px"}), "Download Excel"],
                    id="rs-btn-excel",
                    style={
                        "marginRight": "10px",
                        "padding": "10px 22px",
                        "borderRadius": "8px",
                        "border": f"1px solid {BORDER}",
                        "background": WHITE,
                        "fontFamily": "Inter, sans-serif",
                        "fontWeight": "600",
                        "fontSize": "13px",
                        "cursor": "pointer",
                        "color": "#374151",
                    },
                ),
                html.Button(
                    [html.Span("⬇  ", style={"marginRight": "4px"}), "Download PDF"],
                    id="rs-btn-pdf",
                    style={
                        "padding": "10px 22px",
                        "borderRadius": "8px",
                        "border": f"1px solid {BORDER}",
                        "background": WHITE,
                        "fontFamily": "Inter, sans-serif",
                        "fontWeight": "600",
                        "fontSize": "13px",
                        "cursor": "pointer",
                        "color": "#374151",
                    },
                ),
            ],
            id="rs-download-bar",
            style={"marginTop": "20px", "display": "none"},
        ),
        dcc.Download(id="rs-download-excel"),
        dcc.Download(id="rs-download-pdf"),
        dcc.Store(id="rs-raw-result", storage_type="session"),
    ],
    style={
        "fontFamily": "Inter, sans-serif",
        "padding": "32px 36px",
        "background": BG,
        "minHeight": "100vh",
    },
)


# ── Guard banner callback ─────────────────────────────────────────────
@callback(
    Output("rs-guard-banner", "children"),
    Input("confirmed-company-store", "data"),
    prevent_initial_call=True,
)
def rs_check_company_confirmed(confirmed_data):
    if not confirmed_data:
        return html.Div([
            html.Div([
                html.Span("⚠️", style={"fontSize": "24px", "marginRight": "12px"}),
                html.Div([
                    html.Div("Belum ada perusahaan yang dikonfirmasi", style={
                        "fontWeight": "700", "fontSize": "15px", "color": "#92400E"
                    }),
                    html.Div([
                        html.Span("Silakan ", style={"fontSize": "13px", "color": "#78350F"}),
                        html.A("pilih dan konfirmasi perusahaan terlebih dahulu",
                               href="/perusahaan", style={
                                   "fontSize": "13px", "color": "#D97706",
                                   "fontWeight": "600", "textDecoration": "underline"
                               }),
                        html.Span(" sebelum menjalankan modul ini.",
                                  style={"fontSize": "13px", "color": "#78350F"}),
                    ], style={"marginTop": "2px"}),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={
            "background": "#FFFBEB", "border": "1px solid #FDE68A",
            "borderRadius": "12px", "padding": "16px 20px",
            "marginBottom": "20px",
        })
    return html.Div()


# ── Main render callback ─────────────────────────────────────────────
@callback(
    Output("rs-result-area", "children"),
    Output("rs-raw-result", "data"),
    Output("rs-download-bar", "style"),
    Input("home-pipeline-result", "data"),
    prevent_initial_call=False,
)
def render_rasio(pipeline_json):
    from utils.portfolio_data import build_full_pipeline_store
    if not pipeline_json:
        pipeline_json = build_full_pipeline_store("IDX-PTBA")

    try:
        result = json.loads(pipeline_json) if isinstance(pipeline_json, str) else pipeline_json
        rasio_data = result.get("excel", {}).get("rasio", {}) or result.get("pdf", {}).get("rasio", {})
    except Exception:
        rasio_data = build_full_pipeline_store("IDX-PTBA")["excel"]["rasio"]

    if not rasio_data:
        rasio_data = build_full_pipeline_store("IDX-PTBA")["excel"]["rasio"]

    # Overall summary
    total_rasio = sum(len(s.get("rasio_rows", [])) for s in rasio_data.values())
    total_sheets = len(rasio_data)

    summary_card = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(str(total_sheets), style={"fontSize": "32px", "fontWeight": "800", "color": ACCENT}),
                            html.Div("Emiten Dianalisis", style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"}),
                        ],
                        style={"textAlign": "center", "flex": "1"},
                    ),
                    html.Div(
                        style={"width": "1px", "background": BORDER, "alignSelf": "stretch"},
                    ),
                    html.Div(
                        [
                            html.Div(str(total_rasio), style={"fontSize": "32px", "fontWeight": "800", "color": ACCENT}),
                            html.Div("Total Rasio Dihitung", style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"}),
                        ],
                        style={"textAlign": "center", "flex": "1"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "24px"},
            ),
        ],
        style=CARD,
    )

    sheet_cards = [_build_sheet_card(name, data) for name, data in rasio_data.items()]

    store_payload = json.dumps(rasio_data)

    return (
        html.Div([summary_card] + sheet_cards),
        store_payload,
        {"marginTop": "20px", "display": "flex"},
    )


# ── Download Excel ────────────────────────────────────────────────────
@callback(
    Output("rs-download-excel", "data"),
    Input("rs-btn-excel", "n_clicks"),
    State("rs-raw-result", "data"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, raw_json):
    if not raw_json:
        return no_update
    data = json.loads(raw_json)

    sheets = {}
    for sheet_name, sheet_data in data.items():
        rasio_rows = sheet_data.get("rasio_rows", [])
        q_curr = sheet_data.get("q_curr", "-")
        q_prev = sheet_data.get("q_prev", "-")
        rows = []
        for r in rasio_rows:
            rows.append({
                "No": r.get("no", ""),
                "Kategori": r.get("kategori", ""),
                "Rasio": r.get("rasio", ""),
                f"Nilai Y-1 ({q_prev})": format_ratio_value(r.get("rasio", ""), r.get("y1")),
                f"Nilai Y ({q_curr})": format_ratio_value(r.get("rasio", ""), r.get("y")),
                "Analisis AI": r.get("analisis_ai", ""),
            })
        if rows:
            sheets[sheet_name] = pd.DataFrame(rows)

    if not sheets:
        return no_update
    content = export_results_to_excel(sheets)
    return dcc.send_bytes(lambda buf: buf.write(content), "hasil_rasio.xlsx")


# ── Download PDF ──────────────────────────────────────────────────────
@callback(
    Output("rs-download-pdf", "data"),
    Input("rs-btn-pdf", "n_clicks"),
    State("rs-raw-result", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, raw_json):
    if not raw_json:
        return no_update
    data = json.loads(raw_json)

    sections = []
    for sheet_name, sheet_data in data.items():
        rasio_rows = sheet_data.get("rasio_rows", [])
        narrative = sheet_data.get("narrative", "")
        q_curr = sheet_data.get("q_curr", "-")
        q_prev = sheet_data.get("q_prev", "-")

        sections.append({
            "type": "keyval",
            "rows": [
                ["Nama Entitas", f": {sheet_name}"],
                ["Jenis Laporan", ": Laporan Keuangan"],
                ["Periode Laporan", f": {q_curr}"],
                ["Tanggal Generate AI", f": {datetime.date.today().strftime('%d-%m-%Y')}"],
            ],
        })
        sections.append({
            "type": "disclaimer",
            "text": (
                "Laporan ini dihasilkan oleh proses GenAI sehingga tidak dapat serta merta dijadikan dasar "
                "pengambilan keputusan tanpa disertai dengan penelaahan dan penelitian lebih lanjut, seluruh "
                "tanggung jawab hukum dan konsekuensi dari hasil laporan ini tetap melekat pada pengambil keputusan."
            ),
        })
        sections.append({"type": "heading", "text": f"Analisis Rasio — {sheet_name}"})
        if narrative:
            sections.append({"type": "paragraph", "text": narrative})

        tbl_rows = []
        for r in rasio_rows:
            tbl_rows.append([
                str(r.get("no", "")),
                r.get("kategori", ""),
                r.get("rasio", ""),
                format_ratio_value(r.get("rasio", ""), r.get("y1")),
                format_ratio_value(r.get("rasio", ""), r.get("y")),
                r.get("analisis_ai", ""),
            ])
        if tbl_rows:
            sections.append({
                "type": "table",
                "headers": ["No", "Kategori", "Rasio", "Nilai Y-1", "Nilai Y", "Analisis AI"],
                "rows": tbl_rows,
                "colWidths": [0.8, 2.5, 3.5, 1.8, 1.8, 5.7],
            })

    content = export_report_to_pdf(sections, title="Analisis Rasio Emiten")
    return dcc.send_bytes(lambda buf: buf.write(content), "laporan_rasio.pdf")
