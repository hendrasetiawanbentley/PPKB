# -*- coding: utf-8 -*-
"""
pages/perusahaan.py
Menu Analisis Per Perusahaan (1-by-1 Company Analysis with Upload & Deep Dive)
"""

import os
import json
import dash
from dash import html, dcc, Input, Output, State, callback

from utils.portfolio_data import (ALL_COMPANIES, get_mock_company_deep_dive, build_full_pipeline_store,
                                  DEFAULT_COMPANY_ID, ENTITAS_TYPES, DATA_LABEL)
from utils.pipeline import run_pdf_analysis, run_excel_analysis, save_upload

dash.register_page(__name__, path="/perusahaan", name="Analisis Per Perusahaan")

RED   = "#8B2E1F"
WHITE = "#FFFFFF"
ACCENT = "#2563EB"

COMPANY_BY_ID = {c["id"]: c for c in ALL_COMPANIES}

# Options for pre-analyzed portfolio dropdown
PORTFOLIO_OPTIONS = [
    {"label": f"{c['id']} — {c['nama']} ({c['sektor']})", "value": c["id"]}
    for c in ALL_COMPANIES if c["status_analisis"] == "Sudah Dianalisis"
]


def _pill(text, color, bg, border):
    return html.Span(text, style={
        "fontSize": "11px", "fontWeight": "700",
        "color": color, "background": bg,
        "border": f"1px solid {border}",
        "padding": "3px 10px", "borderRadius": "20px",
    })


def _badge(text, ftype="kepatuhan"):
    colors = {
        "PATUH": ("#16A34A", "#F0FDF4", "#BBF7D0"),
        "PERLU REVIU": ("#D97706", "#FFFBEB", "#FDE68A"),
        "TIDAK PATUH": ("#DC2626", "#FEF2F2", "#FCA5A5"),
        "Patuh": ("#16A34A", "#F0FDF4", "#BBF7D0"),
        "Perlu Reviu": ("#D97706", "#FFFBEB", "#FDE68A"),
        "Tidak Patuh": ("#DC2626", "#FEF2F2", "#FCA5A5"),
        "Risiko Rendah": ("#16A34A", "#F0FDF4", "#BBF7D0"),
        "Risiko Sedang": ("#D97706", "#FFFBEB", "#FDE68A"),
        "Terindikasi Anomali": ("#DC2626", "#FEF2F2", "#FCA5A5"),
    }
    c, bg, b = colors.get(text, ("#4B5563", "#F3F4F6", "#E5E7EB"))
    return _pill(text, c, bg, b)


def _card(title, content, icon="📌", accent="#8B2E1F"):
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "18px", "marginRight": "8px"}),
            html.Span(title, style={"fontSize": "15px", "fontWeight": "700", "color": "#111827"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "14px"}),
        content
    ], style={
        "background": WHITE, "borderRadius": "16px", "padding": "20px",
        "border": "1px solid #EBEBEA", "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
        "marginBottom": "20px"
    })


layout = html.Div([

    # ── Top Banner ─────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Div("🔍 Analisis Per Perusahaan", style={
                    "fontSize": "22px", "fontWeight": "800", "color": WHITE
                }),
                html.Div("Upload Laporan Keuangan (PDF/Excel) atau pilih Perusahaan dari Portofolio untuk Analisis Mendalam", style={
                    "fontSize": "13px", "color": "rgba(255,255,255,0.75)", "marginTop": "4px"
                })
            ]),
            html.A("← Kembali ke Ringkasan Portofolio", href="/", style={
                "color": WHITE, "fontSize": "12.5px", "fontWeight": "600",
                "textDecoration": "none", "background": "rgba(255,255,255,0.15)",
                "padding": "8px 16px", "borderRadius": "8px", "border": "1px solid rgba(255,255,255,0.2)"
            })
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"})
    ], style={
        "background": f"linear-gradient(135deg, {RED} 0%, #6B2017 100%)",
        "padding": "24px 36px", "boxShadow": "0 4px 16px rgba(139,46,31,0.2)"
    }),

    # ── Main Controls Row ──────────────────────────────────────────────────────
    html.Div([
        # Selection Card
        html.Div([
            html.Div([
                # Left: Portfolio Dropdown Selector
                html.Div([
                    html.Label("Option A: 1. Kategori Entitas", style={
                        "fontSize": "12px", "fontWeight": "700", "color": "#374151", "marginBottom": "6px", "display": "block"
                    }),
                    dcc.Dropdown(
                        id="perusahaan-entitas-filter",
                        options=[
                            {"label": "Semua Kategori (All)", "value": "ALL"}
                        ] + [{"label": f"{v} ({k})", "value": k} for k, v in ENTITAS_TYPES.items()],
                        value="ALL",
                        clearable=False,
                        style={"fontSize": "13px"}
                    )
                ], style={"width": "180px"}),

                html.Div([
                    html.Label("2. Pilih Perusahaan", style={
                        "fontSize": "12px", "fontWeight": "700", "color": "#374151", "marginBottom": "6px", "display": "block"
                    }),
                    dcc.Dropdown(
                        id="perusahaan-portfolio-select",
                        options=PORTFOLIO_OPTIONS,
                        value=DEFAULT_COMPANY_ID,
                        clearable=False,
                        placeholder="Pilih Perusahaan...",
                        style={"fontSize": "13px"}
                    )
                ], style={"flex": "1", "minWidth": "240px"}),

                html.Div("ATAU", style={
                    "fontSize": "12px", "fontWeight": "800", "color": "#9CA3AF",
                    "padding": "0 10px", "alignSelf": "center"
                }),

                # Right: Upload Button Zone
                html.Div([
                    html.Label("Option B: Upload File Baru (PDF / Excel)", style={
                        "fontSize": "12px", "fontWeight": "700", "color": "#374151", "marginBottom": "6px", "display": "block"
                    }),
                    dcc.Upload(
                        id="perusahaan-file-upload",
                        children=html.Div([
                            html.Span("📁 Drag & Drop atau Klik Upload File (PDF / Excel)", style={
                                "fontSize": "12.5px", "fontWeight": "700", "color": RED
                            })
                        ]),
                        style={
                            "minHeight": "42px", "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "borderWidth": "1px", "borderStyle": "dashed", "borderColor": RED, "borderRadius": "8px",
                            "padding": "6px 16px", "background": "#FDF8F7", "cursor": "pointer", "textAlign": "center"
                        },
                        multiple=False
                    )
                ], style={"flex": "1", "minWidth": "280px"})
            ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "alignItems": "flex-end"}),
        ], style={
            "background": WHITE, "borderRadius": "16px", "padding": "20px",
            "border": "1px solid #EBEBEA", "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
            "margin": "24px 36px 0"
        })
    ]),

    # Location component to read URL query params like ?id=IDX-BBCA
    dcc.Location(id="perusahaan-url-location", refresh=False),

    # Store pending company metadata (before confirmation)
    dcc.Store(id="perusahaan-pending-meta", storage_type="session"),

    # ── Step 1: Company Profile Card (shown immediately after selection) ──────
    dcc.Loading(
        id="perusahaan-loading",
        type="circle",
        color=RED,
        children=html.Div(id="perusahaan-deep-dive-container", style={"padding": "24px 36px 0"}),
        style={"marginTop": "80px"}
    ),

    # ── Step 2 & 3: Confirm button + Module Grid (after confirmation) ─────────
    html.Div(id="perusahaan-confirm-section", style={"padding": "16px 36px 36px"}),
])


@callback(
    Output("perusahaan-portfolio-select", "options"),
    Input("perusahaan-entitas-filter", "value")
)
def update_portfolio_options(entitas_val):
    if not entitas_val or entitas_val == "ALL":
        filtered = ALL_COMPANIES
    else:
        filtered = [c for c in ALL_COMPANIES if c.get("entitas_type") == entitas_val]
    
    return [
        {"label": f"{c['id']} — {c['nama']} ({c['sektor']})", "value": c["id"]}
        for c in filtered if c["status_analisis"] == "Sudah Dianalisis"
    ]


@callback(
    Output("perusahaan-entitas-filter", "value"),
    Input("perusahaan-url-location", "search"),
    State("perusahaan-entitas-filter", "value"),
    prevent_initial_call=True
)
def update_filter_from_url(search, current_filter):
    if search and "id=" in search:
        try:
            comp_id = search.split("id=")[1].split("&")[0]
            for c in ALL_COMPANIES:
                if c["id"] == comp_id:
                    return c.get("entitas_type", "ALL")
        except Exception:
            pass
    return current_filter


@callback(
    Output("perusahaan-portfolio-select", "value"),
    Input("perusahaan-url-location", "search"),
    prevent_initial_call=True
)
def update_select_from_url(search):
    if search and "id=" in search:
        try:
            comp_id = search.split("id=")[1].split("&")[0]
            if any(c["id"] == comp_id for c in ALL_COMPANIES):
                return comp_id
        except Exception:
            pass
    return DEFAULT_COMPANY_ID


@callback(
    Output("perusahaan-deep-dive-container", "children"),
    Output("home-pipeline-result", "data"),
    Output("perusahaan-file-upload", "children"),
    Output("perusahaan-pending-meta", "data"),
    Input("perusahaan-portfolio-select", "value"),
    Input("perusahaan-file-upload", "contents"),
    State("perusahaan-file-upload", "filename")
)
def render_deep_dive(selected_id, upload_contents, upload_filename):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    # ── Case 1: Custom File Uploaded ─────────────────────────────────────────
    if triggered_id == "perusahaan-file-upload" and upload_contents:
        try:
            saved_path = save_upload(upload_contents, upload_filename)
            ext = os.path.splitext(upload_filename)[1].lower()
            if ext == ".pdf":
                res = run_pdf_analysis(saved_path)
                pipeline_store = {"pdf": res, "excel": {}}
            else:
                res = run_excel_analysis(saved_path)
                pipeline_store = {"excel": res, "pdf": {}}

            komparasi_raw = res.get("komparasi", {})
            komparasi_dict = list(komparasi_raw.values())[0] if komparasi_raw else {}
            rasio_raw = res.get("rasio", {})
            rasio_dict = list(rasio_raw.values())[0] if rasio_raw else {}
            ml_raw = res.get("ml", {}) or res.get("ml_voting", {})
            ml_dict = list(ml_raw.values())[0] if ml_raw else {}

            data = {
                "file_name": upload_filename,
                "doc_meta": res.get("meta", {}),
                "kepatuhan": {
                    "skor": 92.0 if res.get("kepatuhan", {}).get("ya", 0) > 15 else 75.0,
                    "status": "PATUH" if res.get("kepatuhan", {}).get("ya", 0) > 15 else "PERLU REVIU",
                    "penjelasan": res.get("kepatuhan", {}).get("narrative", "Hasil evaluasi kepatuhan."),
                    "checklist": [
                        {
                            "no": r.get("No"), "komponen": r.get("Komponen"),
                            "kriteria": r.get("Kriteria Pemeriksaan"), "status": r.get("Status"),
                            "catatan": (
                                "Tanda tangan direksi tidak lengkap / tidak ditemukan"
                                if r.get("Status") == "TIDAK" and r.get("No") == 5
                                   and (r.get("Catatan AI") == "Tercantum tanda tangan direksi lengkap" or not r.get("Catatan AI"))
                                else ("Tanda tangan Komisaris Utama tidak ditemukan"
                                      if r.get("Status") == "TIDAK" and r.get("No") == 6
                                         and (r.get("Catatan AI") == "Tercantum tanda tangan komite/komisaris" or not r.get("Catatan AI"))
                                      else r.get("Catatan AI", "-"))
                            )
                        }
                        for r in res.get("kepatuhan", {}).get("rows", [])
                    ]
                },
                "komparasi": {
                    "mismatch_count": len(komparasi_dict.get("mismatches", [])),
                    "summary": komparasi_dict.get("narrative", "Hasil komparasi."),
                    "items": [
                        {"akun": m.get("akun"), "val_y": str(m.get("nilai_y")),
                         "val_y1": str(m.get("nilai_y1")),
                         "perubahan_pct": f"{m.get('pct', 0):.1f}%", "mismatch": True}
                        for m in komparasi_dict.get("mismatches", [])
                    ]
                },
                "rasio": {
                    "items": [
                        {"nama": r.get("rasio"), "nilai_y": f"{r.get('y', 0):.2f}",
                         "nilai_y1": f"{r.get('y1', 0):.2f}", "benchmark": "OJK Standard", "status": "Sehat"}
                        for r in rasio_dict.get("rasio_rows", [])
                    ]
                },
                "calk": {
                    "narrative": res.get("calk", {}).get("narrative", "Catatan CaLK."),
                    "findings": [
                        {"topik": f.get("kategori", "Temuan"),
                         "temuan": f.get("temuan_ai", f.get("ringkasan", "-")), "kategori_risiko": "Sedang"}
                        for f in res.get("calk", {}).get("catatan_signifikan", [])
                    ]
                },
                "ml_voting": {
                    "ensemble_pred": 1 if ml_dict.get("verdict") == "FRAUD" else 0,
                    "risk_label": "Terindikasi Anomali" if ml_dict.get("verdict") == "FRAUD" else "Risiko Rendah",
                    "probabilitas": 0.88 if ml_dict.get("verdict") == "FRAUD" else 0.12,
                    "votes": {
                        "benford": 1 if ml_dict.get("benford", {}).get("verdict") == "HIGH" else 0,
                        "beneish": 1 if ml_dict.get("beneish", {}).get("verdict") == "HIGH" else 0,
                        "iforest": 0
                    }
                },
                "kesimpulan": {
                    "ringkasan": "Analisis file yang diunggah selesai diproses oleh AI pipeline.",
                    "rekomendasi": ["Verifikasi ulang data hasil analisis AI.", "Pastikan kelengkapan dokumen pendukung."]
                }
            }
            company_id = f"UPLOAD-{upload_filename}"
            is_dummy = False
            meta = data.get("doc_meta", {})
            nama_entity = meta.get("nama_entitas", upload_filename)
            sektor = meta.get("sektor", "-")
            periode = meta.get("periode", "-")
            entitas_type = "EPP"
            kep_status = data.get("kepatuhan", {}).get("status", "PERLU REVIU")

            short_name = upload_filename[:25] + "..." if len(upload_filename) > 28 else upload_filename
            upload_btn_content = html.Div([
                html.Span(f"✅ Selesai: {short_name}",
                          style={"fontSize": "12px", "fontWeight": "700", "color": "#16A34A"})
            ])

        except Exception as e:
            error_btn = html.Div([
                html.Span("⚠️ Gagal Menganalisis Dokumen. Klik untuk coba lagi.",
                          style={"fontSize": "12.5px", "fontWeight": "600", "color": RED})
            ])
            return (html.Div(f"Error memproses file upload: {str(e)}", style={"color": "red"}),
                    dash.no_update, error_btn, dash.no_update)

    else:
        # ── Case 2: Selected from Portfolio ──────────────────────────────────
        company_id = selected_id or DEFAULT_COMPANY_ID
        is_dummy = True
        data = get_mock_company_deep_dive(company_id)
        pipeline_store = build_full_pipeline_store(company_id)
        meta = data.get("doc_meta", {})
        nama_entity = meta.get("nama_entitas", company_id)
        sektor = meta.get("sektor", "-")
        periode = meta.get("periode", "-")
        kep_status = data.get("kepatuhan", {}).get("status", "PERLU REVIU")
        ml_label = data.get("ml_voting", {}).get("risk_label", "Risiko Rendah")
        entitas_type = COMPANY_BY_ID.get(company_id, {}).get("entitas_type", "-")
        upload_btn_content = html.Div([
            html.Span("📁 Drag & Drop atau Klik Upload File (PDF / Excel)",
                      style={"fontSize": "12.5px", "fontWeight": "700", "color": RED})
        ])

    # ── Build pending meta to store ───────────────────────────────────────────
    pending_meta = {
        "company_id": company_id,
        "nama": nama_entity,
        "sektor": sektor,
        "periode": periode,
        "entitas_type": entitas_type,
        "kepatuhan_status": kep_status,
        "ml_label": data.get("ml_voting", {}).get("risk_label", "Risiko Rendah"),
    }

    # ── Build Profile Card (Step 1 view) ──────────────────────────────────────
    kep_color = "#16A34A" if kep_status == "PATUH" else ("#D97706" if kep_status == "PERLU REVIU" else "#DC2626")
    kep_bg = "#F0FDF4" if kep_status == "PATUH" else ("#FFFBEB" if kep_status == "PERLU REVIU" else "#FEF2F2")
    ml_label = pending_meta["ml_label"]
    ml_color = "#DC2626" if "Anomali" in ml_label else "#16A34A"
    ml_bg = "#FEF2F2" if "Anomali" in ml_label else "#F0FDF4"

    def _info_row(label, value):
        return html.Div([
            html.Span(label, style={
                "fontSize": "11px", "fontWeight": "700", "color": "#9CA3AF",
                "textTransform": "uppercase", "letterSpacing": "0.5px",
                "display": "block", "marginBottom": "2px"
            }),
            html.Span(value, style={"fontSize": "13.5px", "fontWeight": "600", "color": "#1E293B"}),
        ], style={"flex": "1", "minWidth": "140px"})

    profile_card = html.Div([
        # Top: name + badges
        html.Div([
            html.Div([
                html.Div(nama_entity, style={
                    "fontSize": "20px", "fontWeight": "800", "color": "#111827", "marginBottom": "6px"
                }),
                html.Div([
                    html.Span(entitas_type, style={
                        "fontSize": "11px", "fontWeight": "700", "color": "#6B7280",
                        "background": "#F3F4F6", "border": "1px solid #E5E7EB",
                        "padding": "3px 10px", "borderRadius": "20px", "marginRight": "8px"
                    }),
                    html.Span(kep_status, style={
                        "fontSize": "11px", "fontWeight": "700", "color": kep_color,
                        "background": kep_bg, "border": f"1px solid {kep_color}40",
                        "padding": "3px 10px", "borderRadius": "20px", "marginRight": "8px"
                    }),
                    html.Span(ml_label, style={
                        "fontSize": "11px", "fontWeight": "700", "color": ml_color,
                        "background": ml_bg, "border": f"1px solid {ml_color}40",
                        "padding": "3px 10px", "borderRadius": "20px", "marginRight": "8px"
                    }),
                    html.Span(f"⚠️ {DATA_LABEL}", style={
                        "fontSize": "11px", "fontWeight": "700", "color": "#92400E",
                        "background": "#FFFBEB", "border": "1px solid #FDE68A",
                        "padding": "3px 10px", "borderRadius": "20px"
                    }) if is_dummy else html.Span(),
                ])
            ], style={"flex": "1"}),
            html.Div("📋 Profil Perusahaan", style={
                "fontSize": "11px", "fontWeight": "700", "color": "#9CA3AF",
                "textTransform": "uppercase", "letterSpacing": "1px"
            })
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start",
                  "marginBottom": "20px"}),

        # Divider
        html.Hr(style={"border": "none", "borderTop": "1px solid #F3F4F6", "margin": "0 0 18px"}),

        # Info grid
        html.Div([
            _info_row("Sektor / Industri", sektor),
            _info_row("Periode Laporan", periode),
            _info_row("Jenis Entitas", ENTITAS_TYPES.get(entitas_type, entitas_type)),
            _info_row("Status Kepatuhan", kep_status),
            _info_row("Risiko ML", ml_label),
        ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap"}),

    ], style={
        "background": WHITE, "borderRadius": "16px", "padding": "24px",
        "border": "1px solid #EBEBEA", "boxShadow": "0 2px 8px rgba(0,0,0,0.05)",
    })

    return profile_card, json.dumps(pipeline_store), upload_btn_content, pending_meta


# ── Confirm Section Renderer (Step 2 & 3) ─────────────────────────────────────
@callback(
    Output("perusahaan-confirm-section", "children"),
    Input("perusahaan-pending-meta", "data"),
    Input("confirmed-company-store", "data"),
)
def render_confirm_section(pending_meta, confirmed_data):
    if not pending_meta:
        return html.Div()

    pending_id = pending_meta.get("company_id")
    confirmed_id = confirmed_data.get("company_id") if confirmed_data else None
    nama = pending_meta.get("nama", pending_id)

    MODULE_GRID = [
        {"icon": "✅", "label": "1. Kepatuhan", "desc": "Pengecekan Kepatuhan Komponen LK",
         "color": "#2563EB", "bg": "#EFF6FF", "href": "/kepatuhan"},
        {"icon": "📊", "label": "2. Komparasi", "desc": "Pergeseran Material Lintas Periode",
         "color": "#7C3AED", "bg": "#F5F3FF", "href": "/komparasi"},
        {"icon": "📐", "label": "3. Rasio", "desc": "Evaluasi Rasio Keuangan",
         "color": "#0D9488", "bg": "#F0FDFA", "href": "/rasio"},
        {"icon": "📝", "label": "4. CaLK", "desc": "Ekstraksi Temuan CaLK (GenAI)",
         "color": "#EA580C", "bg": "#FFF7ED", "href": "/calk"},
        {"icon": "🤖", "label": "5. ML Voting", "desc": "Deteksi Anomali Penyajian",
         "color": "#DC2626", "bg": "#FEF2F2", "href": "/ml-voting"},
        {"icon": "📋", "label": "6. Kesimpulan", "desc": "Kesimpulan & Rekomendasi Eksekutif",
         "color": "#16A34A", "bg": "#F0FDF4", "href": "/kesimpulan"},
    ]

    def _module_card(m):
        return html.A([
            html.Div([
                html.Span(m["icon"], style={"fontSize": "22px", "marginBottom": "8px", "display": "block"}),
                html.Div(m["label"], style={
                    "fontWeight": "800", "fontSize": "13px", "color": m["color"], "marginBottom": "4px"
                }),
                html.Div(m["desc"], style={
                    "fontSize": "11.5px", "color": "#6B7280", "lineHeight": "1.4"
                }),
            ], style={
                "background": m["bg"], "borderRadius": "12px", "padding": "18px 16px",
                "border": f"1px solid {m['color']}25",
                "transition": "transform 0.15s, box-shadow 0.15s",
                "cursor": "pointer",
            }),
        ], href=m["href"], style={"textDecoration": "none"}, className="module-card")

    if confirmed_id == pending_id:
        # ── Already confirmed: show green banner + module grid
        return html.Div([
            # Confirmed banner
            html.Div([
                html.Div([
                    html.Span("✅", style={"fontSize": "18px", "marginRight": "10px"}),
                    html.Div([
                        html.Div(f"Perusahaan dikonfirmasi: {nama}", style={
                            "fontWeight": "700", "fontSize": "14px", "color": "#15803D"
                        }),
                        html.Div("6 Modul Analisis siap dijalankan. Pilih modul di bawah atau gunakan sidebar.",
                                 style={"fontSize": "12.5px", "color": "#166534", "marginTop": "2px"}),
                    ]),
                ], style={"display": "flex", "alignItems": "center", "flex": "1"}),
                html.Button("🔄 Ganti Perusahaan", id="perusahaan-reset-btn", n_clicks=0, style={
                    "fontSize": "12px", "fontWeight": "600", "color": "#374151",
                    "background": WHITE, "border": "1px solid #D1D5DB",
                    "borderRadius": "8px", "padding": "8px 16px", "cursor": "pointer",
                }),
            ], style={
                "display": "flex", "alignItems": "center", "justifyContent": "space-between",
                "background": "#F0FDF4", "border": "1px solid #86EFAC",
                "borderRadius": "12px", "padding": "16px 20px", "marginBottom": "20px"
            }),

            # Section label
            html.Div([
                html.Div("MODUL ANALISIS", style={
                    "fontSize": "10px", "fontWeight": "800", "color": "#9CA3AF",
                    "letterSpacing": "1.5px", "marginBottom": "4px"
                }),
                html.Div("Pilih Modul untuk Memulai Analisis", style={
                    "fontSize": "16px", "fontWeight": "800", "color": "#1E293B", "marginBottom": "16px"
                }),
            ]),

            # 3×2 module grid
            html.Div([_module_card(m) for m in MODULE_GRID], style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "14px",
            }),
        ])
    else:
        # ── Not yet confirmed: show confirm button
        return html.Div([
            html.Div([
                html.Div([
                    html.Span("🔒", style={"fontSize": "18px", "marginRight": "10px"}),
                    html.Div([
                        html.Div(f"Konfirmasi untuk mengakses 6 Modul Analisis", style={
                            "fontWeight": "700", "fontSize": "14px", "color": "#1E293B"
                        }),
                        html.Div(
                            f"Data {nama} telah dimuat. Klik konfirmasi untuk mengaktifkan modul analisis.",
                            style={"fontSize": "12.5px", "color": "#6B7280", "marginTop": "2px"}
                        ),
                    ]),
                ], style={"display": "flex", "alignItems": "center", "flex": "1"}),
                html.Button([
                    html.Span("✅", style={"marginRight": "8px"}),
                    "Konfirmasi & Mulai Analisis",
                ], id="perusahaan-confirm-btn", n_clicks=0, style={
                    "fontSize": "13px", "fontWeight": "700", "color": WHITE,
                    "background": f"linear-gradient(135deg, #16A34A 0%, #15803D 100%)",
                    "border": "none", "borderRadius": "10px",
                    "padding": "12px 24px", "cursor": "pointer",
                    "boxShadow": "0 4px 12px rgba(21,128,61,0.3)",
                    "whiteSpace": "nowrap",
                }),
            ], style={
                "display": "flex", "alignItems": "center", "justifyContent": "space-between",
                "background": "#FFFBEB", "border": "1px solid #FDE68A",
                "borderRadius": "12px", "padding": "16px 20px",
            }),
        ])


# ── Confirmation Handler ───────────────────────────────────────────────────────
@callback(
    Output("confirmed-company-store", "data"),
    Input("perusahaan-confirm-btn", "n_clicks"),
    State("perusahaan-pending-meta", "data"),
    prevent_initial_call=True
)
def handle_confirmation(n_clicks, pending_meta):
    if n_clicks and n_clicks > 0 and pending_meta:
        return pending_meta
    return dash.no_update


# ── Reset / Change Company ─────────────────────────────────────────────────────
@callback(
    Output("confirmed-company-store", "data", allow_duplicate=True),
    Input("perusahaan-reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_reset(n_clicks):
    if n_clicks and n_clicks > 0:
        return None
    return dash.no_update


# ── Clientside Callback for Instant Upload Status Visual Feedback ─────────────
dash.clientside_callback(
    """
    function(contents, filename) {
        if (contents) {
            var shortName = filename.length > 25 ? filename.substring(0, 22) + "..." : filename;
            return "⏳ AI sedang menganalisis: " + shortName;
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("perusahaan-file-upload", "children", allow_duplicate=True),
    Input("perusahaan-file-upload", "contents"),
    State("perusahaan-file-upload", "filename"),
    prevent_initial_call=True
)
