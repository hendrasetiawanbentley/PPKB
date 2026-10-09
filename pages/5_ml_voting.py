# -*- coding: utf-8 -*-
"""
Modul 5 — Analisis Machine Learning (ML Voting)
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

dash.register_page(__name__, path="/ml-voting", name="5. ML Voting")

# ── Design tokens ─────────────────────────────────────────────────────
RED = "#8B2E1F"
ACCENT = "#DC2626"
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
ACCENT_LIGHT = "#FEF2F2"


# ── Helpers ───────────────────────────────────────────────────────────
def _empty_state():
    return html.Div(
        [
            html.Div(
                "🤖",
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


def _anomali_badge(level):
    """Colored badge for anomaly level (HIGH / MEDIUM / LOW)."""
    colors = {
        "HIGH": ("#DC2626", "#FEF2F2"),
        "MEDIUM": ("#D97706", "#FFFBEB"),
        "LOW": ("#16A34A", "#F0FDF4"),
    }
    fg, bg = colors.get(level, ("#6B7280", "#F9FAFB"))
    return html.Span(
        [
            html.Span(
                style={
                    "height": "8px",
                    "width": "8px",
                    "backgroundColor": fg,
                    "borderRadius": "50%",
                    "display": "inline-block",
                    "marginRight": "7px",
                }
            ),
            level,
        ],
        style={
            "fontWeight": "700",
            "fontSize": "12px",
            "color": fg,
            "background": bg,
            "padding": "4px 12px",
            "borderRadius": "6px",
        },
    )


def _verdict_badge(verdict):
    """Large verdict badge — FRAUD or CLEAN."""
    is_fraud = verdict == "FRAUD"
    return html.Span(
        verdict,
        style={
            "fontWeight": "800",
            "fontSize": "13px",
            "color": "#DC2626" if is_fraud else "#16A34A",
            "background": "#FEF2F2" if is_fraud else "#F0FDF4",
            "padding": "6px 18px",
            "borderRadius": "8px",
            "letterSpacing": "0.5px",
        },
    )


def _build_company_card(company_name, comp_data):
    """Build a detailed result card for one company."""
    verdict = comp_data.get("verdict", "CLEAN")
    benford = comp_data.get("benford", {})
    beneish = comp_data.get("beneish", {})
    votes = comp_data.get("votes", "0/0")
    avg_prob = comp_data.get("avg_prob", 0)
    narrative = comp_data.get("narrative", "")

    benford_level = benford.get("verdict", "LOW")
    beneish_level = beneish.get("verdict", "LOW")
    bb_level = "HIGH" if verdict == "FRAUD" else "LOW"

    # Map verdict into Low/Medium/High for Voting
    if verdict == "FRAUD":
        voting_level = "HIGH"
    elif benford_level == "MEDIUM" or beneish_level == "MEDIUM":
        voting_level = "MEDIUM"
    else:
        voting_level = "LOW"

    benford_desc = benford.get("desc", "-")
    beneish_desc = beneish.get("desc", "-")

    # Header row with verdict
    card_header = html.Div(
        [
            html.Div(
                [
                    html.H3(
                        company_name,
                        style={
                            "margin": "0",
                            "fontSize": "17px",
                            "fontWeight": "800",
                            "color": "#1F2937",
                        },
                    ),
                    html.Div(
                        f"Votes: {votes} · Avg Prob: {avg_prob * 100:.1f}%",
                        style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"},
                    ),
                ],
                style={"flex": "1"},
            ),
            _verdict_badge(verdict),
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "marginBottom": "20px",
            "paddingBottom": "16px",
            "borderBottom": f"1px solid {BORDER}",
        },
    )

    # Sub-headers matching the photo
    sub_headers = html.Div(
        [
            html.Table(
                html.Tbody([
                    html.Tr([
                        html.Td("Nama Entitas", style={"padding": "2px 0", "fontWeight": "600", "color": "#4B5563", "fontSize": "13px", "width": "160px", "border": "none"}),
                        html.Td(f": {company_name}", style={"padding": "2px 0", "color": "#111827", "fontSize": "13px", "border": "none"}),
                    ]),
                    html.Tr([
                        html.Td("Periode", style={"padding": "2px 0", "fontWeight": "600", "color": "#4B5563", "fontSize": "13px", "border": "none"}),
                        html.Td(": 2024", style={"padding": "2px 0", "color": "#111827", "fontSize": "13px", "border": "none"}),
                    ]),
                    html.Tr([
                        html.Td("Tanggal Generate AI", style={"padding": "2px 0", "fontWeight": "600", "color": "#4B5563", "fontSize": "13px", "border": "none"}),
                        html.Td(f": {datetime.date.today().strftime('%d-%m-%Y')}", style={"padding": "2px 0", "color": "#111827", "fontSize": "13px", "border": "none"}),
                    ]),
                ]),
                style={"border": "none", "background": "none", "marginBottom": "20px", "width": "auto"}
            )
        ]
    )

    # ML model table
    ml_rows = [
        {"no": "1", "model": "Benford Law", "deviasi": f"{benford.get('mad', 0):.4f}", "kesimpulan": benford_desc, "anomali": benford_level},
        {"no": "2", "model": "M - Benish Score", "deviasi": f"{beneish.get('score', 0):.2f}", "kesimpulan": beneish_desc, "anomali": beneish_level},
        {"no": "Hasil Voting", "model": "", "deviasi": "", "kesimpulan": "*dapat ditambahkan terkait hal yang ingin di capture oleh AI", "anomali": voting_level},
    ]

    header_labels = ["No", "Model", "Deviasi Model", "Kesimpulan Model", "Tingkat Anomali"]
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

    cell_base = {"padding": "9px 12px", "fontSize": "13px", "verticalAlign": "top"}

    rows = []
    for row in ml_rows:
        is_voting = (row["no"] == "Hasil Voting")
        text_style = {
            **cell_base,
            "color": "#DC2626" if is_voting else "#4B5563",
            "maxWidth": "400px",
            "lineHeight": "1.5",
        }
        if is_voting:
            text_style["fontStyle"] = "italic"
            text_style["fontWeight"] = "600"

        rows.append(
            html.Tr(
                [
                    html.Td(str(row["no"]), style={**cell_base, "fontWeight": "700" if is_voting else "normal"}),
                    html.Td(row["model"], style={**cell_base, "fontWeight": "600"}),
                    html.Td(row["deviasi"], style={**cell_base, "fontVariantNumeric": "tabular-nums"}),
                    html.Td(
                        row["kesimpulan"],
                        style=text_style,
                    ),
                    html.Td(_anomali_badge(row["anomali"]), style=cell_base),
                ],
                style={
                    "borderBottom": f"1px solid {BORDER}",
                    "background": "#FDF8F7" if is_voting else "transparent"
                },
            )
        )

    table = html.Table(
        [thead, html.Tbody(rows)],
        className="result-table",
        style={"width": "100%", "borderCollapse": "collapse", "marginBottom": "25px"},
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
            "border": "1px solid #FECACA",
            "borderRadius": "10px",
            "padding": "18px 20px",
        },
    )

    return html.Div(
        [card_header, sub_headers, table, narrative_block],
        style=CARD,
    )


# ── Layout ────────────────────────────────────────────────────────────
layout = html.Div(
    [
        html.Div(id="ml-guard-banner"),
        # Header
        html.Div(
            [
                html.Div(
                    "🤖",
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
                            "Modul 05 — ML Voting",
                            style={
                                "margin": "0",
                                "fontSize": "22px",
                                "fontWeight": "800",
                                "color": RED,
                                "letterSpacing": "-0.3px",
                            },
                        ),
                        html.P(
                            "Deteksi kewajaran penyajian menggunakan Benford's Law, Beneish M-Score, dan Ensemble ML.",
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
            html.Div(id="ml-result-area"),
            type="dot",
            color=ACCENT,
        ),
        # Download buttons
        html.Div(
            [
                html.Button(
                    [html.Span("⬇  ", style={"marginRight": "4px"}), "Download Excel"],
                    id="ml-btn-excel",
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
                    id="ml-btn-pdf",
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
            id="ml-download-bar",
            style={"marginTop": "20px", "display": "none"},
        ),
        dcc.Download(id="ml-download-excel"),
        dcc.Download(id="ml-download-pdf"),
        dcc.Store(id="ml-raw-result", storage_type="session"),
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
    Output("ml-guard-banner", "children"),
    Input("confirmed-company-store", "data"),
    prevent_initial_call=True,
)
def ml_check_company_confirmed(confirmed_data):
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
    Output("ml-result-area", "children"),
    Output("ml-raw-result", "data"),
    Output("ml-download-bar", "style"),
    Input("home-pipeline-result", "data"),
    prevent_initial_call=False,
)
def render_ml_voting(pipeline_json):
    from utils.portfolio_data import build_full_pipeline_store
    if not pipeline_json:
        pipeline_json = build_full_pipeline_store()

    try:
        result = json.loads(pipeline_json) if isinstance(pipeline_json, str) else pipeline_json
        ml_data = result.get("excel", {}).get("ml", {}) or result.get("pdf", {}).get("ml_voting", {})
    except Exception:
        ml_data = build_full_pipeline_store()["excel"]["ml"]

    if not ml_data:
        ml_data = build_full_pipeline_store()["excel"]["ml"]

    # Overall summary
    n_total = len(ml_data)
    n_fraud = sum(1 for v in ml_data.values() if v.get("verdict") == "FRAUD")
    n_clean = n_total - n_fraud

    summary_card = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(str(n_total), style={"fontSize": "32px", "fontWeight": "800", "color": "#374151"}),
                            html.Div("Emiten Dianalisis", style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"}),
                        ],
                        style={"textAlign": "center", "flex": "1"},
                    ),
                    html.Div(style={"width": "1px", "background": BORDER, "alignSelf": "stretch"}),
                    html.Div(
                        [
                            html.Div(str(n_fraud), style={"fontSize": "32px", "fontWeight": "800", "color": "#DC2626"}),
                            html.Div("Anomali (FRAUD)", style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"}),
                        ],
                        style={"textAlign": "center", "flex": "1"},
                    ),
                    html.Div(style={"width": "1px", "background": BORDER, "alignSelf": "stretch"}),
                    html.Div(
                        [
                            html.Div(str(n_clean), style={"fontSize": "32px", "fontWeight": "800", "color": "#16A34A"}),
                            html.Div("Wajar (CLEAN)", style={"fontSize": "12px", "color": "#6B7280", "marginTop": "4px"}),
                        ],
                        style={"textAlign": "center", "flex": "1"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "24px"},
            ),
        ],
        style=CARD,
    )

    company_cards = [_build_company_card(name, data) for name, data in ml_data.items()]

    store_payload = json.dumps(ml_data)

    return (
        html.Div([summary_card] + company_cards),
        store_payload,
        {"marginTop": "20px", "display": "flex"},
    )


# ── Download Excel ────────────────────────────────────────────────────
@callback(
    Output("ml-download-excel", "data"),
    Input("ml-btn-excel", "n_clicks"),
    State("ml-raw-result", "data"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, raw_json):
    if not raw_json:
        return no_update
    data = json.loads(raw_json)

    excel_sheets = {}
    for comp, r in data.items():
        benford = r.get("benford", {})
        beneish = r.get("beneish", {})
        verdict = r.get("verdict", "CLEAN")
        
        benford_level = benford.get("verdict", "LOW")
        beneish_level = beneish.get("verdict", "LOW")
        if verdict == "FRAUD":
            voting_level = "HIGH"
        elif benford_level == "MEDIUM" or beneish_level == "MEDIUM":
            voting_level = "MEDIUM"
        else:
            voting_level = "LOW"

        rows = [
            {"No": "1", "Model": "Benford Law", "Deviasi Model": f"{benford.get('mad', 0):.4f}",
             "Kesimpulan Model": benford.get("desc", "-"), "Tingkat Anomali": benford_level},
            {"No": "2", "Model": "M - Benish Score", "Deviasi Model": f"{beneish.get('score', 0):.2f}",
             "Kesimpulan Model": beneish.get("desc", "-"), "Tingkat Anomali": beneish_level},
            {"No": "Hasil Voting", "Model": "", "Deviasi Model": "",
             "Kesimpulan Model": "*dapat ditambahkan terkait hal yang ingin di capture oleh AI", "Tingkat Anomali": voting_level},
        ]
        excel_sheets[f"ML_{comp}"] = pd.DataFrame(rows)

    content = export_results_to_excel(excel_sheets)
    return dcc.send_bytes(lambda buf: buf.write(content), "hasil_ml_voting.xlsx")


# ── Download PDF ──────────────────────────────────────────────────────
@callback(
    Output("ml-download-pdf", "data"),
    Input("ml-btn-pdf", "n_clicks"),
    State("ml-raw-result", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, raw_json):
    if not raw_json:
        return no_update
    data = json.loads(raw_json)

    sections = []
    for comp, r in data.items():
        benford = r.get("benford", {})
        beneish = r.get("beneish", {})
        verdict = r.get("verdict", "CLEAN")
        narrative = r.get("narrative", "")
        
        benford_level = benford.get("verdict", "LOW")
        beneish_level = beneish.get("verdict", "LOW")
        if verdict == "FRAUD":
            voting_level = "HIGH"
        elif benford_level == "MEDIUM" or beneish_level == "MEDIUM":
            voting_level = "MEDIUM"
        else:
            voting_level = "LOW"

        sections.extend([
            {
                "type": "keyval",
                "rows": [
                    ["Nama Entitas", f": {comp}"],
                    ["Periode", f": 2024"],
                    ["Tanggal Generate AI", f": {datetime.date.today().strftime('%d-%m-%Y')}"],
                ],
            },
            {
                "type": "disclaimer",
                "text": (
                    "Laporan ini dihasilkan oleh proses GenAI sehingga tidak dapat serta merta dijadikan dasar "
                    "pengambilan keputusan tanpa disertai dengan penelaahan dan penelitian lebih lanjut, seluruh "
                    "tanggung jawab hukum dan konsekuensi dari hasil laporan ini tetap melekat pada pengambil keputusan."
                ),
            },
            {"type": "heading", "text": "Analisis Machine Learning"},
            {
                "type": "table",
                "headers": ["No", "Model", "Deviasi Model", "Kesimpulan Model", "Tingkat Anomali"],
                "rows": [
                    ["1", "Benford Law", f"{benford.get('mad', 0):.4f}", benford.get("desc", "-"), benford_level],
                    ["2", "M - Benish Score", f"{beneish.get('score', 0):.2f}", beneish.get("desc", "-"), beneish_level],
                    ["Hasil Voting", "", "", "<i><font color=\"#DC2626\">*dapat ditambahkan terkait hal yang ingin di capture oleh AI</font></i>", voting_level],
                ],
                "colWidths": [2.3, 2.5, 2.2, 7.7, 2.3],
            },
            {"type": "paragraph", "text": narrative},
            {"type": "pagebreak"},
        ])

    if sections:
        sections.pop()  # remove trailing pagebreak

    content = export_report_to_pdf(sections, title="Analisis Machine Learning")
    return dcc.send_bytes(lambda buf: buf.write(content), "laporan_ml_voting.pdf")
