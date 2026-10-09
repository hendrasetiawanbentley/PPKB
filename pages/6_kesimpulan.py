# -*- coding: utf-8 -*-
"""
Modul 6 — Kesimpulan Keseluruhan
Reads all module results from the central home-pipeline-result store,
synthesises a final conclusion and actionable recommendations.
"""
import json
import datetime
import dash
import pandas as pd
from dash import html, dcc, Input, Output, State, callback

from utils.genai_narrator import narrate_kesimpulan_keseluruhan, generate_rekomendasi_tindak_lanjut
from utils.export_excel import export_results_to_excel
from utils.export_pdf import export_report_to_pdf

dash.register_page(__name__, path="/kesimpulan", name="Kesimpulan Keseluruhan")

# ── Design tokens ──────────────────────────────────────────────────────
RED = "#8B2E1F"
ACCENT = "#7C3AED"          # purple for conclusion module
WHITE = "#FFFFFF"
BG = "#F2F0ED"
BORDER = "#EBEBEA"
FONT = "Inter, system-ui, sans-serif"

# Module accent colors for section badges
MODULE_COLORS = {
    "kepatuhan": "#2563EB",
    "komparasi": "#0891B2",
    "rasio": "#7C3AED",
    "calk": "#EA580C",
    "ml_voting": "#059669",
}

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
    html.Div(id="ks-guard-banner"),
    # Header
    html.Div([
        html.Div([
            html.Span("📊", style={"fontSize": "28px", "marginRight": "14px"}),
            html.Div([
                html.Div("Modul 06", style={
                    "fontSize": "11px", "fontWeight": "700", "color": ACCENT,
                    "textTransform": "uppercase", "letterSpacing": "1.2px",
                    "marginBottom": "2px", "fontFamily": FONT,
                }),
                html.Div("Kesimpulan & Rekomendasi", style={
                    "fontSize": "22px", "fontWeight": "800", "color": "#1E293B",
                    "fontFamily": FONT,
                }),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={
        **CARD,
        "background": f"linear-gradient(135deg, {WHITE} 0%, #F5F3FF 100%)",
        "borderLeft": f"4px solid {ACCENT}",
    }),

    # Result area
    dcc.Loading(
        html.Div(id="ks-result-area", style={"marginTop": "4px"}),
        type="dot",
        color=ACCENT,
    ),

    # Download buttons
    html.Div([
        html.Button([
            html.Span("📥", style={"marginRight": "6px"}),
            "Download Excel Lengkap",
        ], id="ks-btn-excel", style={
            "marginRight": "10px", "padding": "10px 20px", "borderRadius": "8px",
            "border": f"1px solid {BORDER}", "background": WHITE, "cursor": "pointer",
            "fontFamily": FONT, "fontWeight": "600", "fontSize": "13px", "color": "#374151",
        }),
        html.Button([
            html.Span("📄", style={"marginRight": "6px"}),
            "Download PDF Lengkap",
        ], id="ks-btn-pdf", style={
            "padding": "10px 20px", "borderRadius": "8px",
            "border": f"1px solid {BORDER}", "background": WHITE, "cursor": "pointer",
            "fontFamily": FONT, "fontWeight": "600", "fontSize": "13px", "color": "#374151",
        }),
    ], style={"marginTop": "16px", "marginBottom": "24px"}),

    dcc.Download(id="ks-download-excel"),
    dcc.Download(id="ks-download-pdf"),
    dcc.Store(id="ks-raw-result"),
], style={"fontFamily": FONT})


# ── Guard banner callback ─────────────────────────────────────────────
@callback(
    Output("ks-guard-banner", "children"),
    Input("confirmed-company-store", "data"),
    prevent_initial_call=True,
)
def ks_check_company_confirmed(confirmed_data):
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


# ── Helpers ────────────────────────────────────────────────────────────
def _section_card(number, title, narrative_text, color):
    """Render one module summary section with a colored left border."""
    return html.Div([
        html.Div([
            html.Span(f"{number}.", style={
                "display": "inline-flex", "alignItems": "center",
                "justifyContent": "center", "width": "24px", "height": "24px",
                "borderRadius": "50%", "background": color, "color": WHITE,
                "fontSize": "12px", "fontWeight": "700", "marginRight": "10px",
            }),
            html.Span(title, style={
                "fontWeight": "700", "fontSize": "14px", "color": "#1E293B",
            }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"}),
        dcc.Markdown(narrative_text, style={
            "fontSize": "13px", "lineHeight": "1.7", "color": "#374151",
            "paddingLeft": "34px",
        }),
    ], style={
        **CARD,
        "borderLeft": f"3px solid {color}",
        "paddingTop": "18px", "paddingBottom": "18px",
    })


# ── Main render callback ──────────────────────────────────────────────
@callback(
    Output("ks-result-area", "children"),
    Output("ks-raw-result", "data"),
    Input("home-pipeline-result", "data"),
    prevent_initial_call=False,
)
def render_kesimpulan(store_data):
    from utils.portfolio_data import build_full_pipeline_store
    if not store_data:
        store_data = build_full_pipeline_store()

    data = store_data if isinstance(store_data, dict) else json.loads(store_data)
    pdf_data = data.get("pdf", {})
    excel_data = data.get("excel", {})

    # Collect per-module narratives
    kp_d = pdf_data.get("kepatuhan", {}) or excel_data.get("kepatuhan", {})
    kmp_d = pdf_data.get("komparasi", {}) or excel_data.get("komparasi", {})
    rs_d = pdf_data.get("rasio", {}) or excel_data.get("rasio", {})
    clk_d = pdf_data.get("calk", {}) or excel_data.get("calk", {})
    ml_d = pdf_data.get("ml_voting", {}) or excel_data.get("ml_voting", {}) or excel_data.get("ml", {})

    # Check completeness
    missing = [name for name, val in [
        ("Kepatuhan", kp_d), ("Komparasi", kmp_d), ("Rasio", rs_d),
        ("CaLK", clk_d), ("ML Voting", ml_d),
    ] if not val]

    if len(missing) == 5:
        return _empty_state(), None

    # Extract metadata
    meta = kp_d.get("meta", {}) or clk_d.get("meta", {})
    nama_entitas = meta.get("nama_entitas", "-")
    jenis_laporan = meta.get("jenis_laporan", "Laporan Keuangan")
    periode_laporan = meta.get("periode_laporan", "2024")
    tanggal_generate = datetime.date.today().strftime("%d-%m-%Y")
    tentang_entitas = kp_d.get("tentang_entitas", clk_d.get("tentang_entitas", ""))

    # Build ML voting narrative
    ml_voting_narrative = ""
    if ml_d:
        if isinstance(ml_d, dict) and "narrative" in ml_d:
            ml_voting_narrative = ml_d.get("narrative", "")
        else:
            ml_summaries = []
            for k, v in ml_d.items():
                if isinstance(v, dict) and "verdict" in v:
                    ml_summaries.append(
                        f"{k} — Verdict: {v['verdict']} "
                        f"(probabilitas: {v.get('avg_prob', 0)*100:.1f}%) | "
                        f"Vote: {v.get('votes_fraud', 0)}/{v.get('n_models', 0)} model. "
                        f"{v.get('narrative', '')}"
                    )
            ml_voting_narrative = "\n".join(ml_summaries)

    all_narratives = {
        "kepatuhan": kp_d.get("narrative", "-"),
        "komparasi": kmp_d.get("narrative", "-"),
        "rasio": rs_d.get("narrative", "-"),
        "calk": clk_d.get("narrative", "-"),
        "ml_voting": ml_voting_narrative or "-",
    }

    final_narrative = narrate_kesimpulan_keseluruhan(all_narratives)
    rekomendasi = generate_rekomendasi_tindak_lanjut(all_narratives)

    # ── Metadata card
    meta_card = html.Div([
        html.Div([
            html.Span(label, style={
                "fontWeight": "600", "width": "180px", "display": "inline-block",
                "color": "#6B7280", "fontSize": "13px",
            }),
            html.Span(f": {value}", style={"color": "#1E293B", "fontSize": "13px"}),
        ]) for label, value in [
            ("Nama Entitas", nama_entitas),
            ("Jenis Entitas", "Emiten"),
            ("Jenis Laporan", jenis_laporan),
            ("Periode Laporan", periode_laporan),
            ("Tanggal Generate AI", tanggal_generate),
        ]
    ], style={**CARD, "lineHeight": "2.0"})

    # ── Tentang Entitas
    tentang_card = html.Div([
        html.Div("Tentang Entitas", style={
            "fontWeight": "700", "fontSize": "14px", "color": "#1E293B",
            "marginBottom": "8px",
        }),
        html.P(tentang_entitas, style={
            "fontSize": "13px", "lineHeight": "1.7", "color": "#374151", "margin": 0,
        }),
    ], style=CARD) if tentang_entitas else html.Div()

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

    # ── Missing modules warning
    if missing:
        missing_card = html.Div([
            html.Div([
                html.Span("⚠️", style={"marginRight": "8px"}),
                html.Span(
                    f"Modul belum tersedia: {', '.join(missing)}",
                    style={"fontWeight": "600", "color": "#92400E"},
                ),
            ]),
        ], style={
            "background": "#FFFBEB", "border": "1px solid #FDE68A",
            "borderRadius": "10px", "padding": "14px 18px",
            "marginBottom": "20px", "fontSize": "13px",
        })
    else:
        missing_card = html.Div()

    # ── BAGIAN 1 — KESIMPULAN
    section_header_1 = html.Div([
        html.Div("BAGIAN 1", style={
            "fontSize": "10px", "fontWeight": "700", "color": ACCENT,
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "marginBottom": "2px",
        }),
        html.Div("Kesimpulan Per Modul", style={
            "fontSize": "18px", "fontWeight": "800", "color": "#1E293B",
        }),
    ], style={"marginBottom": "16px", "marginTop": "8px"})

    module_sections = [
        ("1", "Kesimpulan Pengecekan Kepatuhan", all_narratives["kepatuhan"], MODULE_COLORS["kepatuhan"]),
        ("2", "Kesimpulan Analisis Komparasi", all_narratives["komparasi"], MODULE_COLORS["komparasi"]),
        ("3", "Kesimpulan Analisis Rasio", all_narratives["rasio"], MODULE_COLORS["rasio"]),
        ("4", "Kesimpulan Analisis CaLK", all_narratives["calk"], MODULE_COLORS["calk"]),
        ("5", "Analisis Machine Learning — Deteksi Kewajaran", all_narratives["ml_voting"], MODULE_COLORS["ml_voting"]),
    ]

    module_cards = [_section_card(n, t, narr, clr) for n, t, narr, clr in module_sections]

    # ── Final conclusion — render with section-aware layout
    def _render_conclusion_narrative(text: str):
        """
        Splits narrative on **Bold Heading** markers and renders each
        section as a visually distinct block with header + paragraph.
        """
        import re
        if not text:
            return html.Div("Kesimpulan tidak tersedia.", style={"color": "#6B7280"})

        # Split on **...** heading markers
        parts = re.split(r'\*\*(.+?)\*\*', text)
        # parts alternates: [plain_text, heading, plain_text, heading, plain_text, ...]

        blocks = []
        i = 0
        while i < len(parts):
            chunk = parts[i].strip()
            is_heading = (i % 2 == 1)

            if is_heading:
                # This is a bold heading — render as section header
                blocks.append(html.Div(chunk, style={
                    "fontWeight": "700",
                    "fontSize": "14px",
                    "color": "#1E293B",
                    "marginTop": "20px",
                    "marginBottom": "8px",
                    "paddingTop": "16px",
                    "borderTop": "1px solid #E5E7EB",
                }))
            else:
                # Plain text — split into paragraphs by newline
                if chunk:
                    for para in chunk.split("\n"):
                        para = para.strip()
                        if para:
                            blocks.append(html.P(para, style={
                                "fontSize": "13px",
                                "lineHeight": "1.9",
                                "color": "#374151",
                                "margin": "0 0 12px 0",
                            }))
            i += 1

        return html.Div(blocks)

    final_card = html.Div([
        html.Div([
            html.Span("🎯", style={"marginRight": "8px", "fontSize": "18px"}),
            html.Span("Kesimpulan Keseluruhan", style={
                "fontWeight": "800", "fontSize": "16px", "color": "#1E293B",
            }),
        ], style={"marginBottom": "18px"}),
        _render_conclusion_narrative(final_narrative),
    ], style={
        **CARD,
        "background": "linear-gradient(135deg, #FAFAFA 0%, #F5F3FF 100%)",
        "borderLeft": f"4px solid {ACCENT}",
    })

    # ── BAGIAN 2 — REKOMENDASI
    section_header_2 = html.Div([
        html.Div("BAGIAN 2", style={
            "fontSize": "10px", "fontWeight": "700", "color": "#DC2626",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "marginBottom": "2px",
        }),
        html.Div("Rekomendasi Tindak Lanjut", style={
            "fontSize": "18px", "fontWeight": "800", "color": "#1E293B",
        }),
    ], style={"marginBottom": "16px", "marginTop": "12px"})

    if rekomendasi:
        rekom_table = html.Table([
            html.Thead(html.Tr([
                html.Th("No"),
                html.Th("Poin Utama"),
                html.Th("Usulan Rencana Tindak Lanjut"),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(r["no"]),
                    html.Td(
                        html.Span(r["poin_utama"], style={"fontWeight": "600"}),
                    ),
                    html.Td(r["usulan_rencana"]),
                ]) for r in rekomendasi
            ]),
        ], className="result-table")

        rekom_card = html.Div([
            html.Div(rekom_table, style={"overflowX": "auto"}),
        ], style=CARD)
    else:
        rekom_card = html.Div(
            html.Div("Belum ada rekomendasi.", style={
                "textAlign": "center", "color": "#6B7280", "padding": "20px",
            }),
            style=CARD,
        )

    result_block = html.Div([
        meta_card,
        tentang_card,
        disclaimer,
        missing_card,
        section_header_1,
        *module_cards,
        final_card,
        section_header_2,
        rekom_card,
    ])

    raw_result_data = {
        "final_narrative": final_narrative,
        "modules": all_narratives,
        "meta": {
            "nama_entitas": nama_entitas,
            "jenis_entitas": "Emiten",
            "jenis_laporan": jenis_laporan,
            "periode_laporan": periode_laporan,
            "tanggal_generate": tanggal_generate,
        },
        "tentang_entitas": tentang_entitas,
        "rekomendasi": rekomendasi,
    }
    return result_block, json.dumps(raw_result_data)


# ── Download Excel ─────────────────────────────────────────────────────
@callback(
    Output("ks-download-excel", "data"),
    Input("ks-btn-excel", "n_clicks"),
    State("ks-raw-result", "data"),
    prevent_initial_call=True,
)
def download_excel(n_clicks, raw_json):
    if not raw_json:
        return dash.no_update
    data = json.loads(raw_json)
    df = pd.DataFrame([{"Modul": k, "Kesimpulan": v} for k, v in data["modules"].items()])
    df_final = pd.DataFrame([{"Kesimpulan Keseluruhan": data["final_narrative"]}])
    df_rekomendasi = pd.DataFrame(data.get("rekomendasi", []))
    content = export_results_to_excel({
        "Per Modul": df,
        "Kesimpulan": df_final,
        "Rencana Tindak Lanjut": df_rekomendasi,
    })
    return dcc.send_bytes(lambda buf: buf.write(content), "kesimpulan_keseluruhan.xlsx")


# ── Download PDF ───────────────────────────────────────────────────────
@callback(
    Output("ks-download-pdf", "data"),
    Input("ks-btn-pdf", "n_clicks"),
    State("ks-raw-result", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, raw_json):
    if not raw_json:
        return dash.no_update
    data = json.loads(raw_json)
    m = data["meta"]

    sections = [
        # Metadata
        {
            "type": "keyval",
            "rows": [
                ["Nama Entitas", f": {m.get('nama_entitas', '-')}"],
                ["Jenis Entitas", ": Emiten"],
                ["Jenis Laporan", f": {m.get('jenis_laporan', '-')}"],
                ["Periode Laporan", f": {m.get('periode_laporan', '-')}"],
                ["Tanggal Generate AI", f": {m.get('tanggal_generate', '-')}"],
            ],
        },
        # Disclaimer
        {
            "type": "disclaimer",
            "text": "Laporan ini dihasilkan oleh proses GenAI sehingga tidak dapat serta merta dijadikan dasar "
                    "pengambilan keputusan tanpa disertai dengan penelaahan dan penelitian lebih lanjut, seluruh "
                    "tanggung jawab hukum dan konsekuensi dari hasil laporan ini tetap melekat pada pengambil keputusan.",
        },
        # Tentang Entitas
        {"type": "heading", "text": "Tentang Entitas"},
        {"type": "paragraph", "text": data.get("tentang_entitas", "")},

        # BAGIAN 1 — KESIMPULAN
        {"type": "heading", "text": "BAGIAN 1 - KESIMPULAN"},
        {"type": "heading", "text": "1. Kesimpulan Pengecekan Kepatuhan"},
        {"type": "paragraph", "text": data["modules"].get("kepatuhan", "")},

        {"type": "heading", "text": "2. Kesimpulan Analisis Komparasi"},
        {"type": "paragraph", "text": data["modules"].get("komparasi", "")},

        {"type": "heading", "text": "3. Kesimpulan Analisis Rasio"},
        {"type": "paragraph", "text": data["modules"].get("rasio", "")},

        {"type": "heading", "text": "4. Kesimpulan Analisis CaLK"},
        {"type": "paragraph", "text": data["modules"].get("calk", "")},

        {"type": "heading", "text": "5. Analisis Machine Learning Untuk Deteksi Kewajaran Penyajian"},
        {"type": "paragraph", "text": data["modules"].get("ml_voting", "")},

        {"type": "heading", "text": "Kesimpulan Keseluruhan"},
        {"type": "paragraph", "text": data.get("final_narrative", "")},

        {"type": "pagebreak"},

        # BAGIAN 2 — REKOMENDASI
        {"type": "heading", "text": "BAGIAN 2 - REKOMENDASI TINDAK LANJUT"},
        {
            "type": "table",
            "headers": ["No", "Poin Utama", "Usulan Rencana Tindak Lanjut"],
            "rows": [
                [str(r["no"]), r["poin_utama"], r["usulan_rencana"]]
                for r in data.get("rekomendasi", [])
            ],
            "colWidths": [1.0, 5.0, 11.0],
        },
    ]

    content = export_report_to_pdf(sections, title="Kesimpulan & Rekomendasi")
    return dcc.send_bytes(
        lambda buf: buf.write(content),
        f"laporan_kesimpulan_{m.get('nama_entitas', 'emiten')}.pdf",
    )
