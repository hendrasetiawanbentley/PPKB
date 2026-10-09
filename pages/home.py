# -*- coding: utf-8 -*-
"""
pages/home.py
Beranda — Ringkasan Portofolio emiten Perbankan & Asuransi (DATA SIMULASI dari utils/portfolio_data.py).
Agregasi Portofolio per Modul & Direktori Filterable Perusahaan.
"""

import dash
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.portfolio_data import (
    ALL_COMPANIES, SEKTOR_LIST, SEKTOR_SHORT, ENTITAS_TYPES,
    CALK_THEME_DETAILS, DATA_LABEL, TAHUN_LAPORAN,
    SUMBER_LK, SUMBER_APOLO, KOMPARASI_TOLERANSI_PCT,
    get_portfolio_summary, get_kepatuhan_portfolio_data,
    get_komparasi_portfolio_data, get_rasio_portfolio_data,
    get_calk_portfolio_data, get_kesimpulan_portfolio_data
)

dash.register_page(__name__, path="/", name="Ringkasan Portofolio")

RED      = "#8B2E1F"
TAB_STYLE = {"fontSize": "13px", "fontWeight": "700", "padding": "10px 6px", "lineHeight": "1.3"}
RED_DARK = "#6B2017"
WHITE    = "#FFFFFF"

# ── Helper Styles ─────────────────────────────────────────────────────────────
def _kpi_card(title, value, subtitle, color="#8B2E1F", icon="📊"):
    return html.Div([
        html.Div([
            html.Div(icon, style={
                "fontSize": "22px", "width": "44px", "height": "44px",
                "borderRadius": "12px", "background": f"{color}15",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "border": f"1px solid {color}30"
            }),
            html.Div([
                html.Div(title, style={"fontSize": "12px", "fontWeight": "700", "color": "#6B7280", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                html.Div(value, style={"fontSize": "26px", "fontWeight": "900", "color": "#111827", "marginTop": "2px"}),
                html.Div(subtitle, style={"fontSize": "12px", "fontWeight": "600", "color": color, "marginTop": "2px"}),
            ], style={"marginLeft": "14px"})
        ], style={"display": "flex", "alignItems": "center"})
    ], style={
        "background": WHITE, "borderRadius": "16px", "padding": "18px 20px",
        "border": "1px solid #EBEBEA", "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
        "flex": "1", "minWidth": "210px"
    })


def _pill(text, color, bg, border):
    return html.Span(text, style={
        "fontSize": "11px", "fontWeight": "700",
        "color": color, "background": bg,
        "border": f"1px solid {border}",
        "padding": "3px 10px", "borderRadius": "20px",
        "whiteSpace": "nowrap"
    })


def _badge(text):
    colors = {
        "Patuh": ("#16A34A", "#F0FDF4", "#BBF7D0"),
        "Perlu Reviu": ("#D97706", "#FFFBEB", "#FDE68A"),
        "Tidak Patuh": ("#DC2626", "#FEF2F2", "#FCA5A5"),
        "Sudah Dianalisis": ("#2563EB", "#EFF6FF", "#BFDBFE"),
        "Belum Dianalisis": ("#6B7280", "#F3F4F6", "#E5E7EB"),
        "Risiko Rendah": ("#16A34A", "#F0FDF4", "#BBF7D0"),
        "Risiko Sedang": ("#D97706", "#FFFBEB", "#FDE68A"),
        "Terindikasi Anomali": ("#DC2626", "#FEF2F2", "#FCA5A5"),
    }
    c, bg, b = colors.get(text, ("#4B5563", "#F3F4F6", "#E5E7EB"))
    return _pill(text, c, bg, b)


# Fetch data summary
SUMMARY = get_portfolio_summary()
KEPATUHAN_DATA = get_kepatuhan_portfolio_data()
KOMPARASI_DATA = get_komparasi_portfolio_data()
RASIO_DATA = get_rasio_portfolio_data()
CALK_DATA = get_calk_portfolio_data()
KESIMPULAN_DATA = get_kesimpulan_portfolio_data()


# ── Figure Generators ────────────────────────────────────────────────────────
def _create_kepatuhan_donut():
    labels = ["Patuh", "Perlu Reviu", "Tidak Patuh"]
    values = [SUMMARY["patuh_count"], SUMMARY["reviu_count"], SUMMARY["tidak_patuh_count"]]
    colors = ["#16A34A", "#D97706", "#DC2626"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=colors), textinfo="label+percent",
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        showlegend=True, margin=dict(t=20, b=20, l=20, r=20),
        height=260, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def _create_komparasi_bar():
    mismatch_by_sektor = KOMPARASI_DATA["mismatch_by_sektor"]
    
    # Label sektor dipersingkat agar muat di sumbu grafik
    x_labels = [SEKTOR_SHORT.get(k, k) for k in mismatch_by_sektor.keys()]
    
    fig = px.bar(
        x=x_labels,
        y=list(mismatch_by_sektor.values()),
        color=x_labels,
        color_discrete_sequence=["#2563EB", "#7C3AED", "#0D9488", "#EA580C", "#DC2626", "#16A34A", "#0891B2", "#B45309"],
        labels={"x": "Sektor", "y": "Akun Tidak Sesuai"}
    )
    fig.update_layout(
        showlegend=False, margin=dict(t=20, b=40, l=20, r=20),
        height=260, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(tickangle=-30, tickfont=dict(size=9.5, color="#4B5563"))
    return fig


# ── Page Layout ───────────────────────────────────────────────────────────────
layout = html.Div([

    # ── Top Hero Banner ────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Div("SIKULI — Dashboard Analisis Laporan Keuangan", style={
                    "fontSize": "24px", "fontWeight": "900", "color": WHITE, "letterSpacing": "-0.3px"
                }),
                html.Div(
                    f"Monitoring & Analisis Laporan Keuangan Tahunan {TAHUN_LAPORAN} — Emiten Perbankan & Asuransi ({DATA_LABEL})",
                    style={"fontSize": "13px", "color": "rgba(255,255,255,0.80)", "marginTop": "6px"}
                )
            ]),
            html.A("🔍 Analisis Per Perusahaan / Upload ➔", href="/perusahaan", style={
                "background": WHITE, "color": RED, "fontWeight": "800", "fontSize": "13px",
                "padding": "10px 20px", "borderRadius": "10px", "textDecoration": "none",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.15)"
            })
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"})
    ], style={
        "background": f"linear-gradient(135deg, {RED} 0%, {RED_DARK} 70%, #4A130C 100%)",
        "padding": "28px 36px", "boxShadow": "0 4px 20px rgba(139,46,31,0.25)"
    }),

    # ── KPI Hero Cards Row ─────────────────────────────────────────────────────
    html.Div([
        _kpi_card("Total Laporan Keuangan", f"{SUMMARY['total_lk']}", f"{SUMMARY['num_analyzed']} Dianalisis ({SUMMARY['pct_analyzed']}%)", RED, "📄"),
        _kpi_card("Tingkat Kepatuhan", f"{SUMMARY['pct_patuh']}%", f"{SUMMARY['patuh_count']} dari {SUMMARY['num_analyzed']} Patuh", "#16A34A", "✅"),
        _kpi_card("Anomali ML Flagged", f"{SUMMARY['anomali_ml_count']}", f"{SUMMARY['pct_anomali_ml']}% Terindikasi Anomali", "#DC2626", "🤖"),
        _kpi_card("Rata-Rata Skor Kepatuhan", f"{SUMMARY['avg_score']}%", "Skor Portofolio", "#2563EB", "📐"),
    ], style={
        "display": "flex", "gap": "16px", "flexWrap": "wrap", "padding": "24px 36px 0"
    }),

    # ── Main Portfolio Tabs (5 Modules Overview) ──────────────────────────────
    html.Div([
        dcc.Tabs(id="portfolio-module-tabs", value="tab-kepatuhan", children=[
            dcc.Tab(label="✅ 1. Pemeriksaan Kepatuhan", value="tab-kepatuhan", style=TAB_STYLE, selected_style=TAB_STYLE),
            dcc.Tab(label="📊 2. Analisis Komparasi", value="tab-komparasi", style=TAB_STYLE, selected_style=TAB_STYLE),
            dcc.Tab(label="📐 3. Analisis Rasio Keuangan", value="tab-rasio", style=TAB_STYLE, selected_style=TAB_STYLE),
            dcc.Tab(label="📝 4. Analisis CALK", value="tab-calk", style=TAB_STYLE, selected_style=TAB_STYLE),
            dcc.Tab(label="📋 5. Kesimpulan dan Rekomendasi", value="tab-kesimpulan", style=TAB_STYLE, selected_style=TAB_STYLE),
        ]),

        html.Div(id="portfolio-tab-content", style={"padding": "24px 0 0"})
    ], style={
        "background": WHITE, "borderRadius": "16px", "padding": "20px 24px",
        "border": "1px solid #EBEBEA", "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
        "margin": "24px 36px 0"
    }),

    # ── Directory Table Header & Filters ───────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Div("🏛️ Direktori Laporan Keuangan Tahunan", style={
                    "fontSize": "18px", "fontWeight": "800", "color": "#111827"
                }),
                html.Div("Filter dan temukan status analisis & kepatuhan per emiten", style={
                    "fontSize": "12.5px", "color": "#6B7280", "marginTop": "2px"
                })
            ]),
            html.Div([
                html.Span(f"⚠️ {DATA_LABEL} — bukan hasil analisis sebenarnya", style={
                    "fontSize": "12px", "fontWeight": "700", "color": "#92400E",
                    "background": "#FFFBEB", "border": "1px solid #FDE68A",
                    "padding": "6px 14px", "borderRadius": "20px"
                })
            ])
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px"}),

        # Filter Inputs Row
        html.Div([
            # Search Box
            html.Div([
                dcc.Input(
                    id="filter-search", type="text", placeholder="🔍 Cari nama perusahaan / ID...",
                    style={"width": "100%", "padding": "8px 12px", "borderRadius": "8px", "border": "1px solid #D1D5DB", "fontSize": "13px"}
                )
            ], style={"flex": "1", "minWidth": "220px"}),

            # Kategori Entitas Filter
            html.Div([
                dcc.Dropdown(
                    id="filter-entitas-type",
                    options=[
                        {"label": "Semua Kategori", "value": "ALL"}
                    ] + [{"label": f"{v} ({k})", "value": k} for k, v in ENTITAS_TYPES.items()],
                    value="ALL", clearable=False, style={"fontSize": "13px"}
                )
            ], style={"width": "190px"}),

            # Sektor Filter
            html.Div([
                dcc.Dropdown(
                    id="filter-sektor",
                    options=[{"label": "Semua Sektor", "value": "ALL"}] + [{"label": s, "value": s} for s in SEKTOR_LIST],
                    value="ALL", clearable=False, style={"fontSize": "13px"}
                )
            ], style={"width": "210px"}),

            # Status Analisis Filter
            html.Div([
                dcc.Dropdown(
                    id="filter-status-analisis",
                    options=[
                        {"label": "Semua Status Analisis", "value": "ALL"},
                        {"label": "Sudah Dianalisis", "value": "Sudah Dianalisis"},
                        {"label": "Belum Dianalisis", "value": "Belum Dianalisis"}
                    ],
                    value="ALL", clearable=False, style={"fontSize": "13px"}
                )
            ], style={"width": "200px"}),

            # Status Kepatuhan Filter
            html.Div([
                dcc.Dropdown(
                    id="filter-status-kepatuhan",
                    options=[
                        {"label": "Semua Status Kepatuhan", "value": "ALL"},
                        {"label": "Patuh", "value": "Patuh"},
                        {"label": "Perlu Reviu", "value": "Perlu Reviu"},
                        {"label": "Tidak Patuh", "value": "Tidak Patuh"}
                    ],
                    value="ALL", clearable=False, style={"fontSize": "13px"}
                )
            ], style={"width": "200px"}),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"}),

        # Table Output
        html.Div(id="directory-table-container"),
        dcc.Store(id="directory-active-page", data=1),
        html.Div(id="calk-modal-overlay", style={"display": "none"})
    ], style={
        "background": WHITE, "borderRadius": "16px", "padding": "24px",
        "border": "1px solid #EBEBEA", "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
        "margin": "24px 36px 36px"
    })
])


# ── Callbacks for Module Tabs ─────────────────────────────────────────────────
@callback(
    Output("portfolio-tab-content", "children"),
    Input("portfolio-module-tabs", "value")
)
def render_tab_content(tab):
    if tab == "tab-kepatuhan":
        return html.Div([
            html.Div([
                # Left Donut
                html.Div([
                    html.Div("Distribusi Status Kepatuhan Portofolio", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "8px"}),
                    dcc.Graph(figure=_create_kepatuhan_donut(), config={"displayModeBar": False})
                ], style={"flex": "1", "minWidth": "300px"}),

                # Right List of Common Issues
                html.Div([
                    html.Div("⚠️ Top 6 Temuan Ketidakpatuhan Terbanyak pada Portofolio LK", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "12px"}),
                    html.Table([
                        html.Thead(html.Tr([html.Th("Kriteria Check"), html.Th("Komponen"), html.Th("Frekuensi (LK)"), html.Th("Persentase")])),
                        html.Tbody([
                            html.Tr([
                                html.Td(issue["kriteria"]),
                                html.Td(issue["komponen"]),
                                html.Td(f"{issue['non_compliant_count']} LK"),
                                html.Td(f"{issue['pct']}%")
                            ]) for issue in KEPATUHAN_DATA["frequent_checklist_issues"]
                        ])
                    ], className="result-table")
                ], style={"flex": "1.5", "minWidth": "380px"})
            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "alignItems": "center"})
        ])

    elif tab == "tab-komparasi":
        return html.Div([
            html.Div([
                # Left Bar Chart
                html.Div([
                    html.Div("Akun Tidak Sesuai (LK vs APOLO) per Sektor", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "8px"}),
                    dcc.Graph(figure=_create_komparasi_bar(), config={"displayModeBar": False})
                ], style={"flex": "1", "minWidth": "300px"}),

                # Right Table
                html.Div([
                    html.Div("Akun Paling Sering Tidak Sesuai dengan APOLO", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "4px"}),
                    html.Div(f"Membandingkan {SUMBER_LK} dengan {SUMBER_APOLO}; ditandai bila selisih > {KOMPARASI_TOLERANSI_PCT:g}%.",
                             style={"fontSize": "12px", "color": "#6B7280", "marginBottom": "12px"}),
                    html.Table([
                        html.Thead(html.Tr([html.Th("Akun Keuangan"), html.Th("Jumlah LK Tidak Sesuai"), html.Th("Persentase LK"), html.Th("Tingkat Keparahan")])),
                        html.Tbody([
                            html.Tr([
                                html.Td(item["akun"]),
                                html.Td(f"{item['flags']} LK"),
                                html.Td(f"{item['pct']}%"),
                                html.Td(_badge(item["severity"] if item["severity"] != "Tinggi" else "Terindikasi Anomali"))
                            ]) for item in KOMPARASI_DATA["mismatch_categories"]
                        ])
                    ], className="result-table")
                ], style={"flex": "1.2", "minWidth": "360px"})
            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "alignItems": "center"})
        ])

    elif tab == "tab-rasio":
        return html.Div([
            html.Div("Ringkasan Sebaran Rasio Utama Perbankan & Asuransi terhadap Acuan", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "16px"}),
            html.Div([
                html.Div([
                    html.Div(r["rasio"], style={"fontSize": "13.5px", "fontWeight": "800", "color": RED, "lineHeight": "1.3"}),
                    html.Div(f"Kategori: {r['kategori']}", style={"fontSize": "11px", "color": "#6B7280", "marginTop": "2px"}),
                    html.Div([
                        html.Div([
                            html.Span("Rata-rata: ", style={"fontSize": "11.5px", "color": "#6B7280"}),
                            html.Span(r['mean'], style={"fontSize": "13px", "fontWeight": "800", "color": "#111827"}),
                        ]),
                        html.Div([
                            html.Span("Rentang: ", style={"fontSize": "11.5px", "color": "#6B7280"}),
                            html.Span(f"{r['min']} s/d {r['max']}", style={"fontSize": "11.5px", "fontWeight": "600", "color": "#4B5563"}),
                        ]),
                    ], style={"marginTop": "10px", "display": "flex", "flexDirection": "column", "gap": "2px"}),
                    html.Div([
                        _pill(f"Sehat: {r['healthy_pct']}%", "#16A34A", "#F0FDF4", "#BBF7D0"),
                        _pill(f"Perhatian: {r['warning_pct']}%", "#D97706", "#FFFBEB", "#FDE68A")
                    ], style={"marginTop": "12px", "display": "flex", "gap": "6px", "flexWrap": "wrap"})
                ], style={
                    "background": "#FAFAF9", "borderRadius": "12px", "padding": "16px",
                    "border": "1px solid #EBEBEA", "boxShadow": "0 1px 3px rgba(0,0,0,0.02)"
                }) for r in RASIO_DATA["ratios_summary"]
            ], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(260px, 1fr))",
                "gap": "16px"
            })
        ])

    elif tab == "tab-calk":
        return html.Div([
            html.Div("Topik CaLK Berisiko Paling Sering Ditemukan via GenAI (Klik pada kartu untuk melihat detail temuan)", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "14px"}),
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(theme["topik"], style={"fontSize": "13.5px", "fontWeight": "800", "color": "#111827"}),
                        _badge("Terindikasi Anomali" if theme["risk"] == "Tinggi" else "Perlu Reviu")
                    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
                    html.P(theme["desc"], style={"fontSize": "12.5px", "color": "#4B5563", "margin": "8px 0"}),
                    html.Div([
                        html.Span(f"Ditemukan pada {theme['count']} Laporan Keuangan Tahunan", style={"fontSize": "11.5px", "fontWeight": "600", "color": RED}),
                        html.Span("Lihat Daftar Perusahaan ➔", style={"fontSize": "11.5px", "fontWeight": "700", "color": "#2563EB", "marginLeft": "auto"})
                    ], style={"display": "flex", "alignItems": "center"})
                ], id={"type": "calk-card", "index": theme["topik"]}, n_clicks=0,
                   className="calk-clickable-card",
                   style={
                       "background": "#FAFAF9", "borderRadius": "12px", "padding": "14px 16px",
                       "border": "1px solid #EBEBEA", "marginBottom": "12px", "cursor": "pointer",
                       "transition": "transform 0.15s ease, border-color 0.15s ease"
                   }) for theme in CALK_DATA["calk_risk_themes"]
            ])
        ])

    elif tab == "tab-kesimpulan":
        k = KESIMPULAN_DATA
        temuan_cards = [
            html.Div([
                html.Div([
                    html.Span(t["icon"], style={"fontSize": "16px", "marginRight": "8px"}),
                    html.Span(t["modul"], style={"fontSize": "13px", "fontWeight": "800", "color": RED}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                html.Div(t["teks"], style={"fontSize": "12.5px", "color": "#374151", "lineHeight": "1.55"}),
            ], style={
                "background": "#FAFAF9", "borderRadius": "12px", "padding": "14px 16px",
                "border": "1px solid #EBEBEA",
            }) for t in k["temuan"]
        ]
        prioritas_rows = [
            html.Tr([
                html.Td(html.Div([
                    html.Span(c["ticker"], style={"fontWeight": "800", "marginRight": "6px"}),
                    html.Span(c["nama"], style={"color": "#4B5563"}),
                ])),
                html.Td(f"{c['skor_kepatuhan']:.1f}%", style={"whiteSpace": "nowrap"}),
                html.Td(_badge(c["status_kepatuhan"])),
                html.Td(_badge(c["ml_risk"])),
                html.Td(html.A("Ulas ➔", href=f"/perusahaan?id={c['id']}", style={
                    "color": "#2563EB", "fontWeight": "700", "fontSize": "12px", "textDecoration": "none",
                    "background": "#EFF6FF", "padding": "4px 10px", "borderRadius": "6px", "whiteSpace": "nowrap",
                })),
            ]) for c in k["prioritas"]
        ]
        return html.Div([
            # Ringkasan umum
            html.Div(k["ringkasan"], style={
                "fontSize": "13.5px", "fontWeight": "600", "color": "#111827", "lineHeight": "1.6",
                "background": "#FDF8F7", "border": f"1px solid {RED}30", "borderLeft": f"4px solid {RED}",
                "borderRadius": "10px", "padding": "12px 16px", "marginBottom": "18px",
            }),
            # Temuan utama per modul
            html.Div("Temuan Utama per Modul", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "10px"}),
            html.Div(temuan_cards, style={
                "display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(190px, 1fr))",
                "gap": "12px", "marginBottom": "22px",
            }),
            html.Div([
                # Rekomendasi
                html.Div([
                    html.Div("📌 Rekomendasi Tindak Lanjut", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "10px"}),
                    html.Ol([
                        html.Li(r, style={"fontSize": "12.5px", "color": "#374151", "lineHeight": "1.55", "marginBottom": "8px"})
                        for r in k["rekomendasi"]
                    ], style={"paddingLeft": "20px", "margin": 0}),
                ], style={"flex": "1", "minWidth": "320px"}),
                # Emiten prioritas
                html.Div([
                    html.Div("🎯 Emiten Prioritas Tindak Lanjut", style={"fontSize": "14px", "fontWeight": "700", "color": "#111827", "marginBottom": "10px"}),
                    html.Table([
                        html.Thead(html.Tr([html.Th("Emiten"), html.Th("Skor"), html.Th("Kepatuhan"), html.Th("Risiko ML"), html.Th("Aksi")])),
                        html.Tbody(prioritas_rows),
                    ], className="result-table"),
                ], style={"flex": "1.3", "minWidth": "420px"}),
            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "alignItems": "flex-start"}),
        ])

    return html.Div()


# ── Callbacks for Directory Table Pagination ──────────────────────────────────
@callback(
    Output("directory-active-page", "data"),
    Input("filter-search", "value"),
    Input("filter-sektor", "value"),
    Input("filter-entitas-type", "value"),
    Input("filter-status-analisis", "value"),
    Input("filter-status-kepatuhan", "value"),
    Input("dir-page-prev", "n_clicks"),
    Input("dir-page-next", "n_clicks"),
    dash.State("directory-active-page", "data"),
    prevent_initial_call=False
)
def manage_page_state(search, sektor, entitas_type, status_anal, status_kepat, prev_clicks, next_clicks, current_page):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 1
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Reset to page 1 on filter changes
    if trigger_id in ["filter-search", "filter-sektor", "filter-entitas-type", "filter-status-analisis", "filter-status-kepatuhan"]:
        return 1
        
    if trigger_id == "dir-page-prev" and prev_clicks:
        return max(1, (current_page or 1) - 1)
    if trigger_id == "dir-page-next" and next_clicks:
        return (current_page or 1) + 1
        
    return current_page or 1


@callback(
    Output("directory-table-container", "children"),
    Input("filter-search", "value"),
    Input("filter-sektor", "value"),
    Input("filter-entitas-type", "value"),
    Input("filter-status-analisis", "value"),
    Input("filter-status-kepatuhan", "value"),
    Input("directory-active-page", "data")
)
def update_directory_table(search_val, sektor_val, entitas_type_val, status_analisis_val, status_kepatuhan_val, page_val):
    filtered = ALL_COMPANIES

    if search_val:
        s = search_val.lower().strip()
        filtered = [c for c in filtered if s in c["nama"].lower() or s in c["id"].lower()]

    if sektor_val and sektor_val != "ALL":
        filtered = [c for c in filtered if c["sektor"] == sektor_val]

    if entitas_type_val and entitas_type_val != "ALL":
        filtered = [c for c in filtered if c.get("entitas_type") == entitas_type_val]

    if status_analisis_val and status_analisis_val != "ALL":
        filtered = [c for c in filtered if c["status_analisis"] == status_analisis_val]

    if status_kepatuhan_val and status_kepatuhan_val != "ALL":
        filtered = [c for c in filtered if c["status_kepatuhan"] == status_kepatuhan_val]

    if not filtered:
        return html.Div("Tidak ada perusahaan yang sesuai filter.", style={"padding": "20px", "color": "#6B7280", "textAlign": "center"})

    # Pagination Slicing
    page_size = 15
    total_items = len(filtered)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = min(page_val or 1, total_pages)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = filtered[start_idx:end_idx]

    rows = []
    for c in paginated_items:
        skor_str = f"{c['skor_kepatuhan']:.1f}%" if c["skor_kepatuhan"] is not None else "—"
        
        # Color mapping for Entity Type pills
        etype_colors = {
            "BANK": ("#2563EB", "rgba(37,99,235,0.06)", "rgba(37,99,235,0.2)"),
            "BUS": ("#16A34A", "rgba(22,163,74,0.06)", "rgba(22,163,74,0.2)"),
            "ASR": ("#7C3AED", "rgba(124,58,237,0.06)", "rgba(124,58,237,0.2)"),
        }
        et_c, et_bg, et_b = etype_colors.get(c.get("entitas_type", "EPP"), ("#4B5563", "#F3F4F6", "#E5E7EB"))
        
        if c["status_analisis"] == "Sudah Dianalisis":
            action_btn = html.A(
                "Analisis Detail ➔",
                href=f"/perusahaan?id={c['id']}",
                style={
                    "color": RED, "fontWeight": "700", "fontSize": "12px",
                    "textDecoration": "none", "background": "#FDF8F7",
                    "padding": "4px 10px", "borderRadius": "6px", "border": f"1px solid {RED}40",
                    "whiteSpace": "nowrap", "display": "inline-block"
                }
            )
        else:
            action_btn = html.A(
                "Upload & Analisis ➔",
                href="/perusahaan",
                style={
                    "color": "#4B5563", "fontWeight": "600", "fontSize": "12px",
                    "textDecoration": "none", "background": "#F3F4F6",
                    "padding": "4px 10px", "borderRadius": "6px", "border": "1px solid #E5E7EB",
                    "whiteSpace": "nowrap", "display": "inline-block"
                }
            )

        rows.append(html.Tr([
            html.Td(html.Div([
                html.Span(c["id"], style={"fontSize": "11px", "fontWeight": "700", "color": "#6B7280", "marginRight": "6px"}),
                html.Span(c["nama"], style={"fontWeight": "700", "color": "#111827"})
            ])),
            html.Td(_pill(c.get("entitas_type", "EPP"), et_c, et_bg, et_b)),
            html.Td(c["sektor"]),
            html.Td(_badge(c["status_analisis"])),
            html.Td(html.Div([
                html.Span(skor_str, style={"fontWeight": "700", "color": RED if c["skor_kepatuhan"] and c["skor_kepatuhan"] < 80 else "#111827"}),
                html.Span(" "),
                _badge(c["status_kepatuhan"]) if c["status_kepatuhan"] != "Belum Dianalisis" else html.Span()
            ])),
            html.Td(_badge(c["ml_risk"])),
            html.Td(f"{c['mismatch_count']} Mismatch" if c["status_analisis"] == "Sudah Dianalisis" else "—", style={"whiteSpace": "nowrap"}),
            html.Td(action_btn)
        ]))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Kode & Nama Perusahaan"),
            html.Th("Tipe Entitas"),
            html.Th("Sektor"),
            html.Th("Status Analisis"),
            html.Th("Skor Kepatuhan"),
            html.Th("Risk Flag ML"),
            html.Th("Mismatch APOLO"),
            html.Th("Aksi Analisis")
        ])),
        html.Tbody(rows)
    ], className="result-table")

    # Pagination controls layout
    pagination_controls = html.Div([
        html.Button("◀ Sebelumnya", id="dir-page-prev", n_clicks=0, disabled=(page == 1), style={
            "padding": "6px 14px", "borderRadius": "8px", "border": "1px solid #D1D5DB",
            "background": WHITE if page > 1 else "#F3F4F6", "cursor": "pointer" if page > 1 else "not-allowed",
            "fontSize": "12.5px", "fontWeight": "600", "color": "#374151" if page > 1 else "#9CA3AF"
        }),
        html.Span(f"Halaman {page} dari {total_pages} (Total: {total_items} Emiten)", style={
            "fontSize": "13px", "fontWeight": "600", "color": "#4B5563"
        }),
        html.Button("Berikutnya ▶", id="dir-page-next", n_clicks=0, disabled=(page == total_pages), style={
            "padding": "6px 14px", "borderRadius": "8px", "border": "1px solid #D1D5DB",
            "background": WHITE if page < total_pages else "#F3F4F6", "cursor": "pointer" if page < total_pages else "not-allowed",
            "fontSize": "12.5px", "fontWeight": "600", "color": "#374151" if page < total_pages else "#9CA3AF"
        })
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "marginTop": "16px", "paddingTop": "12px", "borderTop": "1px solid #F0EDE8"
    })

    return html.Div([
        html.Div(table, style={"overflowX": "auto"}),
        pagination_controls
    ])


# ── Callback for CaLK Interactive Modal Popup ────────────────────────────────
@callback(
    Output("calk-modal-overlay", "style"),
    Output("calk-modal-overlay", "children"),
    Input({"type": "calk-card", "index": dash.ALL}, "n_clicks"),
    Input("calk-modal-close", "n_clicks"),
    dash.State("calk-modal-overlay", "style"),
    prevent_initial_call=True
)
def handle_calk_modal_click(card_clicks, close_clicks, current_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "none"}, html.Div()
        
    trigger_id = ctx.triggered[0]["prop_id"]
    
    # Close button click
    if "calk-modal-close" in trigger_id:
        return {"display": "none"}, html.Div()
        
    # Card click
    if "calk-card" in trigger_id:
        try:
            import json as _json
            triggered_prop = _json.loads(trigger_id.split(".")[0])
            topic = triggered_prop["index"]
        except Exception:
            return {"display": "none"}, html.Div()
            
        # Get details for this topic
        details_list = CALK_THEME_DETAILS.get(topic, [])
        if not details_list:
            return {"display": "none"}, html.Div()
            
        modal_content = html.Div([
            html.Div([
                # Header
                html.Div([
                    html.Div([
                        html.Span("📝", style={"fontSize": "20px", "marginRight": "8px"}),
                        html.Span(topic, style={"fontSize": "16px", "fontWeight": "800", "color": "#111827"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                    html.Button("✕ Tutup", id="calk-modal-close", n_clicks=0, style={
                        "background": "none", "border": "none", "color": "#6B7280",
                        "fontSize": "14px", "fontWeight": "600", "cursor": "pointer"
                    })
                ], style={
                    "display": "flex", "justifyContent": "space-between", "alignItems": "center",
                    "paddingBottom": "16px", "borderBottom": "1px solid #E5E7EB", "marginBottom": "16px"
                }),
                
                # Scrollable Table Container
                html.Div([
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Kode Emiten"),
                            html.Th("Nama Emiten"),
                            html.Th("Temuan AI (CaLK Excerpt)"),
                            html.Th("Halaman"),
                            html.Th("Risk Level"),
                            html.Th("Aksi")
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(c["ticker"], style={"fontWeight": "700"}),
                                html.Td(c["nama"]),
                                html.Td(c["temuan"], style={"fontSize": "12.5px", "lineHeight": "1.5"}),
                                html.Td(c["halaman"]),
                                html.Td(_badge(c["status"])),
                                html.Td(html.A("Ulas Emiten ➔", href=f"/perusahaan?id=IDX-{c['ticker']}", style={
                                    "color": "#2563EB", "fontWeight": "700", "fontSize": "12px",
                                    "textDecoration": "none", "background": "#EFF6FF", "padding": "4px 10px", "borderRadius": "6px"
                                }))
                            ]) for c in details_list
                        ])
                    ], className="result-table")
                ], style={"maxHeight": "400px", "overflowY": "auto"}),
                
            ], style={
                "background": WHITE, "width": "90%", "maxWidth": "850px",
                "borderRadius": "16px", "padding": "24px", "boxShadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                "fontFamily": "Plus Jakarta Sans, sans-serif"
            })
        ], style={
            "display": "flex", "position": "fixed", "top": 0, "left": 0,
            "width": "100%", "height": "100%", "backgroundColor": "rgba(0,0,0,0.5)",
            "zIndex": 9999, "justifyContent": "center", "alignItems": "center"
        })
        
        return {"display": "block"}, modal_content

    return {"display": "none"}, html.Div()

