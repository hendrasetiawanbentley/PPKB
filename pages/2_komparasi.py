# -*- coding: utf-8 -*-
"""
Modul 2 — Simpulan Analisis Komparasi
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

dash.register_page(__name__, path="/komparasi", name="2. Komparasi")

# ── Design tokens ─────────────────────────────────────────────────────
RED = "#8B2E1F"
ACCENT = "#7C3AED"
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
ACCENT_LIGHT = "#F5F3FF"

# ── Layout ────────────────────────────────────────────────────────────
layout = html.Div(
    [
        html.Div(id="kmp-guard-banner"),
        # Header
        html.Div(
            [
                html.Div(
                    "📊",
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
                            "Modul 02 — Komparasi",
                            style={
                                "margin": "0",
                                "fontSize": "22px",
                                "fontWeight": "800",
                                "color": RED,
                                "letterSpacing": "-0.3px",
                            },
                        ),
                        html.P(
                            "Perbandingan akun laporan keuangan antar kuartal — mendeteksi mismatch melebihi ambang batas.",
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
        # Result area — filled by callback
        dcc.Loading(
            html.Div(id="kmp-result-area"),
            type="dot",
            color=ACCENT,
        ),
        # Download buttons + hidden components
        html.Div(
            [
                html.Button(
                    [html.Span("⬇  ", style={"marginRight": "4px"}), "Download Excel"],
                    id="kmp-btn-excel",
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
                    id="kmp-btn-pdf",
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
            id="kmp-download-bar",
            style={"marginTop": "20px", "display": "none"},
        ),
        dcc.Download(id="kmp-download-excel"),
        dcc.Download(id="kmp-download-pdf"),
        dcc.Store(id="kmp-raw-result", storage_type="session"),
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
    Output("kmp-guard-banner", "children"),
    Input("confirmed-company-store", "data"),
    prevent_initial_call=True,
)
def kmp_check_company_confirmed(confirmed_data):
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


# ── Helpers ───────────────────────────────────────────────────────────
def _empty_state():
    return html.Div(
        [
            html.Div(
                "📊",
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


def _status_badge(is_mismatch):
    if is_mismatch:
        return html.Span(
            "MISMATCH",
            style={
                "background": "#FEF2F2",
                "color": "#DC2626",
                "padding": "3px 10px",
                "borderRadius": "6px",
                "fontWeight": "700",
                "fontSize": "11px",
            },
        )
    return html.Span(
        "SESUAI",
        style={
            "background": "#F0FDF4",
            "color": "#16A34A",
            "padding": "3px 10px",
            "borderRadius": "6px",
            "fontWeight": "700",
            "fontSize": "11px",
        },
    )


def _build_sheet_card(sheet_name, sheet_data):
    """Build a result card for one sheet (emiten)."""
    mismatches = sheet_data.get("mismatches", [])
    q_curr = sheet_data.get("q_curr", "-")
    q_prev = sheet_data.get("q_prev", "-")
    narrative = sheet_data.get("narrative", "")
    total_akun = sheet_data.get("total_akun", 0)
    n_mismatch = len(mismatches)

    # Summary strip
    summary_strip = html.Div(
        [
            html.Div(
                [
                    html.Div(str(total_akun), style={"fontSize": "26px", "fontWeight": "800", "color": ACCENT}),
                    html.Div("Total Akun", style={"fontSize": "11px", "color": "#6B7280", "marginTop": "2px"}),
                ],
                style={"textAlign": "center", "flex": "1"},
            ),
            html.Div(
                [
                    html.Div(str(n_mismatch), style={"fontSize": "26px", "fontWeight": "800", "color": "#DC2626" if n_mismatch else "#16A34A"}),
                    html.Div("Mismatch", style={"fontSize": "11px", "color": "#6B7280", "marginTop": "2px"}),
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
    header_labels = ["Akun", f"Nilai Y-1", f"Nilai Y", "Selisih", "Selisih (%)", "Status"]
    thead = html.Thead(
        html.Tr(
            [html.Th(h, style={"padding": "10px 12px", "fontSize": "11px", "fontWeight": "700",
                                "color": "#6B7280", "textTransform": "uppercase", "letterSpacing": "0.5px",
                                "borderBottom": f"2px solid {BORDER}", "textAlign": "left"})
             for h in header_labels]
        )
    )

    rows = []
    for m in mismatches:
        pct = m.get("pct", 0)
        is_mis = abs(pct) >= 30
        rows.append(
            html.Tr(
                [
                    html.Td(m.get("akun", ""), style={"padding": "9px 12px", "fontSize": "13px", "fontWeight": "500"}),
                    html.Td(f"{m.get('nilai_y1', 0):,.0f}", style={"padding": "9px 12px", "fontSize": "13px", "fontVariantNumeric": "tabular-nums"}),
                    html.Td(f"{m.get('nilai_y', 0):,.0f}", style={"padding": "9px 12px", "fontSize": "13px", "fontVariantNumeric": "tabular-nums"}),
                    html.Td(f"{m.get('selisih', 0):,.0f}", style={"padding": "9px 12px", "fontSize": "13px", "fontVariantNumeric": "tabular-nums"}),
                    html.Td(
                        f"{pct:+.1f}%",
                        style={
                            "padding": "9px 12px",
                            "fontSize": "13px",
                            "fontWeight": "700",
                            "color": "#DC2626" if is_mis else "#16A34A",
                            "fontVariantNumeric": "tabular-nums",
                        },
                    ),
                    html.Td(_status_badge(is_mis), style={"padding": "9px 12px"}),
                ],
                style={"borderBottom": f"1px solid {BORDER}"},
            )
        )

    if not rows:
        rows.append(
            html.Tr(
                html.Td(
                    "Tidak ada mismatch ditemukan.",
                    colSpan=6,
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
            "border": f"1px solid #E9E5FF",
            "borderRadius": "10px",
            "padding": "18px 20px",
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
            summary_strip,
            table,
            narrative_block,
        ],
        style=CARD,
    )


# ── Main render callback ─────────────────────────────────────────────
@callback(
    Output("kmp-result-area", "children"),
    Output("kmp-raw-result", "data"),
    Output("kmp-download-bar", "style"),
    Input("home-pipeline-result", "data"),
    prevent_initial_call=False,
)
def render_komparasi(pipeline_json):
    from utils.portfolio_data import build_full_pipeline_store
    if not pipeline_json:
        pipeline_json = build_full_pipeline_store("IDX-PTBA")

    try:
        result = json.loads(pipeline_json) if isinstance(pipeline_json, str) else pipeline_json
        komparasi_data = result.get("excel", {}).get("komparasi", {}) or result.get("pdf", {}).get("komparasi", {})
    except Exception:
        komparasi_data = build_full_pipeline_store("IDX-PTBA")["excel"]["komparasi"]

    if not komparasi_data:
        komparasi_data = build_full_pipeline_store("IDX-PTBA")["excel"]["komparasi"]

    # Overall summary
    total_mismatch = sum(len(s.get("mismatches", [])) for s in komparasi_data.values())
    total_sheets = len(komparasi_data)

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
                            html.Div(str(total_mismatch), style={"fontSize": "32px", "fontWeight": "800", "color": "#DC2626" if total_mismatch else "#16A34A"}),
                            html.Div("Total Mismatch", style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"}),
                        ],
                        style={"textAlign": "center", "flex": "1"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "24px"},
            ),
        ],
        style=CARD,
    )

    # Per-sheet cards
    sheet_cards = [_build_sheet_card(name, data) for name, data in komparasi_data.items()]

    # Store the data for download callbacks
    store_payload = json.dumps(komparasi_data)

    return (
        html.Div([summary_card] + sheet_cards),
        store_payload,
        {"marginTop": "20px", "display": "flex"},
    )


# ── Download Excel ────────────────────────────────────────────────────
@callback(
    Output("kmp-download-excel", "data"),
    Input("kmp-btn-excel", "n_clicks"),
    State("kmp-raw-result", "data"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, raw_json):
    if not raw_json:
        return no_update
    data = json.loads(raw_json)
    sheets = {}
    for sheet_name, sheet_data in data.items():
        rows = sheet_data.get("mismatches", [])
        if rows:
            df = pd.DataFrame(rows)
            sheets[sheet_name] = df
    if not sheets:
        return no_update
    content = export_results_to_excel(sheets)
    return dcc.send_bytes(lambda buf: buf.write(content), "hasil_komparasi.xlsx")


# ── Download PDF ──────────────────────────────────────────────────────
@callback(
    Output("kmp-download-pdf", "data"),
    Input("kmp-btn-pdf", "n_clicks"),
    State("kmp-raw-result", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, raw_json):
    if not raw_json:
        return no_update
    data = json.loads(raw_json)

    sections = []
    for sheet_name, sheet_data in data.items():
        mismatches = sheet_data.get("mismatches", [])
        narrative = sheet_data.get("narrative", "")
        sections.append({"type": "heading", "text": f"2. Komparasi — {sheet_name}"})
        sections.append({"type": "paragraph", "text": f"{len(mismatches)} akun MISMATCH ditemukan."})
        if mismatches:
            sections.append({
                "type": "table",
                "headers": ["Akun", "Nilai Y-1", "Nilai Y", "Selisih", "Selisih (%)"],
                "rows": [
                    [r.get("akun", ""), r.get("nilai_y1", ""), r.get("nilai_y", ""), r.get("selisih", ""), f"{r.get('pct', 0):.1f}%"]
                    for r in mismatches
                ][:40],
            })
        if narrative:
            sections.append({"type": "paragraph", "text": narrative})

    content = export_report_to_pdf(sections)
    return dcc.send_bytes(lambda buf: buf.write(content), "laporan_komparasi.pdf")
