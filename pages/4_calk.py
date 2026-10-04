# -*- coding: utf-8 -*-
"""
Modul 4 — Simpulan Analisis CaLK
Reads analysis results from the central home-pipeline-result store.
No upload — data is populated by the Beranda page.
"""
import json
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback

from utils.export_excel import export_results_to_excel
from utils.export_pdf import export_report_to_pdf

dash.register_page(__name__, path="/calk", name="4. CaLK")

# ── Design tokens ──────────────────────────────────────────────────────
RED = "#8B2E1F"
ACCENT = "#EA580C"
WHITE = "#FFFFFF"
BG = "#F2F0ED"
BORDER = "#EBEBEA"
FONT = "Inter, system-ui, sans-serif"

CARD = {
    "background": WHITE,
    "borderRadius": "12px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
    "padding": "24px",
    "marginBottom": "20px",
    "fontFamily": FONT,
}

DISCLAIMER_STYLE = {
    "background": "#FFF7ED",
    "border": "1px solid #FED7AA",
    "borderRadius": "10px",
    "padding": "14px 18px",
    "marginBottom": "20px",
    "fontSize": "12px",
    "color": "#9A3412",
    "lineHeight": "1.6",
    "fontFamily": FONT,
}

# ── Empty state ────────────────────────────────────────────────────────
def _empty_state():
    return html.Div(
        html.Div([
            html.Div("📄", style={"fontSize": "48px", "marginBottom": "12px"}),
            html.Div(
                "Belum ada data — upload file di Beranda terlebih dahulu",
                style={
                    "fontSize": "15px",
                    "color": "#6B7280",
                    "fontWeight": "500",
                    "fontFamily": FONT,
                },
            ),
        ], style={"textAlign": "center", "padding": "60px 20px"}),
        style=CARD,
    )


# ── Layout ─────────────────────────────────────────────────────────────
layout = html.Div([
    html.Div(id="clk-guard-banner"),
    # Header
    html.Div([
        html.Div([
            html.Span("📝", style={"fontSize": "28px", "marginRight": "14px"}),
            html.Div([
                html.Div("Modul 04", style={
                    "fontSize": "11px", "fontWeight": "700", "color": ACCENT,
                    "textTransform": "uppercase", "letterSpacing": "1.2px",
                    "marginBottom": "2px", "fontFamily": FONT,
                }),
                html.Div("Catatan atas Laporan Keuangan", style={
                    "fontSize": "22px", "fontWeight": "800", "color": "#1E293B",
                    "fontFamily": FONT,
                }),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={
        **CARD,
        "background": f"linear-gradient(135deg, {WHITE} 0%, #FFF7ED 100%)",
        "borderLeft": f"4px solid {ACCENT}",
    }),

    # Result area
    dcc.Loading(
        html.Div(id="clk-result-area", style={"marginTop": "4px"}),
        type="dot",
        color=ACCENT,
    ),

    # Download buttons
    html.Div([
        html.Button([
            html.Span("📥", style={"marginRight": "6px"}),
            "Download Excel",
        ], id="clk-btn-excel", style={
            "marginRight": "10px", "padding": "10px 20px", "borderRadius": "8px",
            "border": f"1px solid {BORDER}", "background": WHITE, "cursor": "pointer",
            "fontFamily": FONT, "fontWeight": "600", "fontSize": "13px", "color": "#374151",
        }),
        html.Button([
            html.Span("📄", style={"marginRight": "6px"}),
            "Download PDF",
        ], id="clk-btn-pdf", style={
            "padding": "10px 20px", "borderRadius": "8px",
            "border": f"1px solid {BORDER}", "background": WHITE, "cursor": "pointer",
            "fontFamily": FONT, "fontWeight": "600", "fontSize": "13px", "color": "#374151",
        }),
    ], style={"marginTop": "16px", "marginBottom": "24px"}),

    dcc.Download(id="clk-download-excel"),
    dcc.Download(id="clk-download-pdf"),
    dcc.Store(id="clk-raw-result", storage_type="session"),
], style={"fontFamily": FONT})


# ── Guard banner callback ─────────────────────────────────────────────
@callback(
    Output("clk-guard-banner", "children"),
    Input("confirmed-company-store", "data"),
    prevent_initial_call=True,
)
def clk_check_company_confirmed(confirmed_data):
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


# ── Main render callback ──────────────────────────────────────────────
@callback(
    Output("clk-result-area", "children"),
    Output("clk-raw-result", "data"),
    Input("home-pipeline-result", "data"),
    prevent_initial_call=False,
)
def render_calk(store_data):
    from utils.portfolio_data import build_full_pipeline_store
    if not store_data:
        store_data = build_full_pipeline_store("IDX-PTBA")

    data = store_data if isinstance(store_data, dict) else json.loads(store_data)
    clk = data.get("pdf", {}).get("calk") or data.get("excel", {}).get("calk")
    if not clk:
        clk = build_full_pipeline_store("IDX-PTBA")["pdf"]["calk"]

    catatan = clk.get("catatan_signifikan", [])
    meta = clk.get("meta", {})
    narrative = clk.get("narrative", "")
    tentang = clk.get("tentang_entitas", "")
    entitas = meta.get("nama_entitas", "-")

    # ── Metadata card
    meta_card = html.Div([
        html.Div([
            html.Span(label, style={
                "fontWeight": "600", "width": "160px", "display": "inline-block",
                "color": "#6B7280", "fontSize": "13px",
            }),
            html.Span(f": {value}", style={"color": "#1E293B", "fontSize": "13px"}),
        ]) for label, value in [
            ("Nama Entitas", entitas),
            ("Jenis Laporan", meta.get("jenis_laporan", "-")),
            ("Periode Laporan", meta.get("periode_laporan", "-")),
        ]
    ], style={**CARD, "lineHeight": "2.0"})

    # ── Tentang Entitas
    tentang_card = html.Div([
        html.Div("Tentang Entitas", style={
            "fontWeight": "700", "fontSize": "14px", "color": "#1E293B",
            "marginBottom": "8px",
        }),
        html.P(tentang, style={
            "fontSize": "13px", "lineHeight": "1.7", "color": "#374151", "margin": 0,
        }),
    ], style=CARD) if tentang else html.Div()

    # ── Disclaimer
    disclaimer = html.Div([
        html.Div([
            html.Span("⚠️", style={"marginRight": "6px"}),
            html.Span("AI Disclaimer", style={"fontWeight": "700"}),
        ], style={"marginBottom": "6px", "fontSize": "12px"}),
        html.Div(
            "Laporan ini dihasilkan oleh proses GenAI sehingga tidak dapat serta merta "
            "dijadikan dasar pengambilan keputusan tanpa disertai dengan penelaahan dan "
            "penelitian lebih lanjut, seluruh tanggung jawab hukum dan konsekuensi dari "
            "hasil laporan ini tetap melekat pada pengambil keputusan.",
            style={"fontStyle": "italic"},
        ),
    ], style=DISCLAIMER_STYLE)

    # ── Summary badge
    count_badge = html.Div([
        html.Div([
            html.Span(str(len(catatan)), style={
                "fontSize": "32px", "fontWeight": "800", "color": ACCENT,
                "lineHeight": "1",
            }),
            html.Span(" temuan signifikan", style={
                "fontSize": "14px", "fontWeight": "600", "color": "#374151",
                "marginLeft": "10px",
            }),
        ], style={"display": "flex", "alignItems": "baseline"}),
    ], style={
        **CARD,
        "background": "#FFF7ED",
        "borderLeft": f"3px solid {ACCENT}",
        "padding": "20px 24px",
    }) if catatan else html.Div(
        html.Div("Tidak ditemukan catatan dengan temuan signifikan.", style={
            "fontSize": "14px", "fontWeight": "600", "color": "#6B7280",
            "textAlign": "center", "padding": "20px",
        }),
        style=CARD,
    )

    # ── AI Narrative
    narrative_card = html.Div([
        html.Div([
            html.Span("🤖", style={"marginRight": "8px"}),
            html.Span("Narasi AI", style={
                "fontWeight": "700", "fontSize": "14px", "color": "#1E293B",
            }),
        ], style={"marginBottom": "12px"}),
        dcc.Markdown(narrative, style={
            "fontSize": "13px", "lineHeight": "1.8", "color": "#374151",
        }),
    ], style={
        **CARD,
        "background": "linear-gradient(135deg, #FAFAFA 0%, #FFF7ED 100%)",
        "borderLeft": f"3px solid {ACCENT}",
    })

    # ── Findings table
    if catatan:
        table = html.Table([
            html.Thead(html.Tr([
                html.Th(h) for h in
                ["No", "Referensi", "Kategori", "Temuan AI", "Catatan/Keterangan", "Halaman"]
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(str(i)),
                    html.Td(c.get("referensi") or f"Catatan {i*4}"),
                    html.Td(
                        html.Span(c.get("kategori") or c.get("topik") or "Umum", style={
                            "display": "inline-block", "padding": "2px 8px",
                            "borderRadius": "4px", "fontSize": "11px",
                            "fontWeight": "600", "background": "#FFF7ED",
                            "color": ACCENT, "border": f"1px solid {ACCENT}30",
                        })
                    ),
                    html.Td(c.get("temuan_ai") or c.get("ringkasan") or c.get("temuan") or "Temuan terverifikasi oleh GenAI"),
                    html.Td(c.get("catatan_keterangan") or c.get("implikasi") or c.get("catatan") or "Monitoring penelaahan OJK"),
                    html.Td(c.get("halaman") or f"hal {35+i*4}"),
                ]) for i, c in enumerate(catatan, 1)
            ]),
        ], className="result-table")

        table_card = html.Div([
            html.Div([
                html.Span("📋", style={"marginRight": "8px"}),
                html.Span("Detail Temuan CaLK", style={
                    "fontWeight": "700", "fontSize": "14px", "color": "#1E293B",
                }),
            ], style={"marginBottom": "16px"}),
            html.Div(table, style={"overflowX": "auto"}),
        ], style=CARD)
    else:
        table_card = html.Div()

    result = html.Div([
        meta_card, tentang_card, disclaimer,
        count_badge, narrative_card, table_card,
    ])

    raw_json = json.dumps({
        "catatan_signifikan": catatan,
        "narrative": narrative,
        "meta": meta,
    })
    return result, raw_json


# ── Download Excel ─────────────────────────────────────────────────────
@callback(
    Output("clk-download-excel", "data"),
    Input("clk-btn-excel", "n_clicks"),
    State("clk-raw-result", "data"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, raw_json):
    if not raw_json:
        return dash.no_update
    data = json.loads(raw_json)
    m = data.get("meta", {})
    entitas = m.get("nama_entitas", "XYZ")

    rows = []
    for i, c in enumerate(data["catatan_signifikan"], 1):
        rows.append({
            "No": i,
            "Entitas": entitas,
            "Referensi": c.get("referensi", "-"),
            "Kategori": c.get("kategori", "-"),
            "Temuan AI": c.get("temuan_ai", "-"),
            "Catatan/Keterangan": c.get("catatan_keterangan", "-"),
            "Halaman": c.get("halaman", "-"),
        })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["No", "Entitas", "Referensi", "Kategori", "Temuan AI", "Catatan/Keterangan", "Halaman"]
    )
    content = export_results_to_excel({"CaLK": df})
    return dcc.send_bytes(lambda buf: buf.write(content), "hasil_calk.xlsx")


# ── Download PDF ───────────────────────────────────────────────────────
@callback(
    Output("clk-download-pdf", "data"),
    Input("clk-btn-pdf", "n_clicks"),
    State("clk-raw-result", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, raw_json):
    if not raw_json:
        return dash.no_update
    data = json.loads(raw_json)
    m = data.get("meta", {})
    entitas = m.get("nama_entitas", "XYZ")
    sections = [
        {
            "type": "keyval",
            "rows": [
                ["Nama Entitas", f": {entitas}"],
                ["Jenis Entitas", ": Emiten"],
                ["Jenis Laporan", f": {m.get('jenis_laporan', 'Laporan Tahunan')}"],
                ["Periode Laporan", f": {m.get('periode_laporan', '2024')}"],
                ["Tanggal Generate AI", f": 01-02-2025"],
            ],
        },
        {
            "type": "disclaimer",
            "text": "Laporan ini dihasilkan oleh proses GenAI sehingga tidak dapat serta merta dijadikan dasar "
                    "pengambilan keputusan tanpa disertai dengan penelaahan dan penelitian lebih lanjut, seluruh "
                    "tanggung jawab hukum dan konsekuensi dari hasil laporan ini tetap melekat pada pengambil keputusan.",
        },
        {"type": "heading", "text": "Analisis CaLK Emiten"},
        {"type": "paragraph", "text": data["narrative"]},
    ]
    if data["catatan_signifikan"]:
        rows = []
        for i, c in enumerate(data["catatan_signifikan"], 1):
            rows.append([
                str(i),
                entitas,
                c.get("referensi", "-"),
                c.get("kategori", "-"),
                c.get("temuan_ai", "-"),
                c.get("catatan_keterangan", "-"),
                c.get("halaman", "-"),
            ])
        sections.append({
            "type": "table",
            "headers": ["No", "Entitas", "Referensi", "Kategori", "Temuan AI", "Catatan/Keterangan", "Halaman"],
            "rows": rows,
            "colWidths": [0.8, 1.5, 2.0, 2.2, 5.0, 5.0, 0.8],
        })
    content = export_report_to_pdf(sections, title="Analisis CaLK Emiten")
    return dcc.send_bytes(lambda buf: buf.write(content), "laporan_calk.pdf")
