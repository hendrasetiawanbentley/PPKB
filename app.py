# -*- coding: utf-8 -*-
"""
OJK - Sistem Analisis AI Kewajaran & Kepatuhan Laporan Keuangan
Entry point utama. Jalankan: python3 app.py
Buka: http://localhost:8050
"""
import dash
from dash import Dash, html, dcc, Input, Output

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="SIKULI — Dashboard Analisis Kepatuhan Keuangan",
)
server = app.server

# ── Design tokens ─────────────────────────────────────────────────────────────
RED      = "#8B2E1F"
RED_DARK = "#6B2017"
RED_MID  = "#A3392A"
WHITE    = "#FFFFFF"
BG       = "#F2F0ED"

# ── Sidebar Navigation Items ──────────────────────────────────────────────────
MAIN_NAV_ITEMS = [
    {"id": "portofolio", "icon": "🏢", "color": "#FFFFFF", "label": "Ringkasan Portofolio", "href": "/"},
    {"id": "perusahaan", "icon": "🔍", "color": "#F59E0B", "label": "Analisis Per Perusahaan", "href": "/perusahaan"},
]

MODULE_NAV_ITEMS = [
    {"id": "modul-1",    "icon": "✅", "color": "#2563EB", "label": "1. Kepatuhan",  "href": "/kepatuhan"},
    {"id": "modul-2",    "icon": "📊", "color": "#7C3AED", "label": "2. Komparasi",  "href": "/komparasi"},
    {"id": "modul-3",    "icon": "📐", "color": "#0D9488", "label": "3. Rasio",      "href": "/rasio"},
    {"id": "modul-4",    "icon": "📝", "color": "#EA580C", "label": "4. CaLK",       "href": "/calk"},
    {"id": "modul-5",    "icon": "🤖", "color": "#DC2626", "label": "5. ML Voting",  "href": "/ml-voting"},
    {"id": "kesimpulan", "icon": "📋", "color": "#16A34A", "label": "Kesimpulan",    "href": "/kesimpulan"},
]

def _sidebar_btn(item):
    return html.A(
        html.Div([
            html.Div(item["icon"], style={
                "width": "32px", "height": "32px",
                "borderRadius": "8px",
                "background": f"{item['color']}30",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "15px", "flexShrink": "0",
            }),
            html.Span(item["label"], style={
                "fontSize": "13.5px", "fontWeight": "600",
                "color": "rgba(255,255,255,0.92)",
                "whiteSpace": "nowrap",
            }),
        ], className="nav-item-inner", style={
            "display": "flex", "alignItems": "center",
            "gap": "12px", "padding": "10px 16px",
            "borderRadius": "10px",
            "transition": "background 0.15s",
        }),
        href=item["href"],
        className="sidebar-link",
        style={
            "display": "block", "textDecoration": "none",
            "margin": "2px 12px",
            "borderRadius": "10px",
            "cursor": "pointer",
        },
    )


def _sidebar_btn_disabled(item):
    """Render a sidebar module button in locked/disabled state."""
    return html.Div(
        html.Div([
            html.Div(item["icon"], style={
                "width": "32px", "height": "32px",
                "borderRadius": "8px",
                "background": "rgba(255,255,255,0.08)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "15px", "flexShrink": "0",
                "filter": "grayscale(1)", "opacity": "0.45",
            }),
            html.Span(item["label"], style={
                "fontSize": "13.5px", "fontWeight": "600",
                "color": "rgba(255,255,255,0.30)",
                "whiteSpace": "nowrap",
            }),
        ], style={
            "display": "flex", "alignItems": "center",
            "gap": "12px", "padding": "10px 16px",
            "borderRadius": "10px",
        }),
        style={
            "display": "block",
            "margin": "2px 12px",
            "borderRadius": "10px",
            "cursor": "not-allowed",
            "pointerEvents": "none",
        },
    )

sidebar = html.Div([
    # ── Brand Header ───────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Span("SIKULI", style={
                    "fontSize": "24px", "fontWeight": "900",
                    "color": WHITE, "letterSpacing": "2px",
                }),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div("Sistem Informasi Ulasan", style={
                "fontSize": "11px", "color": "rgba(255,255,255,0.55)",
                "marginTop": "8px", "lineHeight": "1.6",
            }),
            html.Div("Laporan Keuangan Berbasis AI", style={
                "fontSize": "11px", "color": "rgba(255,255,255,0.55)",
            }),
        ]),
    ], style={
        "padding": "24px 20px 20px",
        "borderBottom": "1px solid rgba(255,255,255,0.10)",
        "marginBottom": "6px",
    }),

    # ── Main Modes Navigation ──────────────────────────────────────────────
    html.Div([
        html.Div("MODE UTAMA", style={
            "fontSize": "10px", "fontWeight": "800", "color": "rgba(255,255,255,0.45)",
            "padding": "6px 20px 4px", "letterSpacing": "1px"
        }),
    ] + [_sidebar_btn(item) for item in MAIN_NAV_ITEMS], style={"padding": "4px 0"}),

    # ── Modul Deep-Dive Navigation (dynamic — active only after company confirmed) ──
    html.Div(id="sidebar-module-nav"),

], style={
    "width": "240px",
    "minHeight": "100vh",
    "background": f"linear-gradient(170deg, {RED} 0%, {RED_DARK} 60%, #4A130C 100%)",
    "position": "fixed",
    "left": 0, "top": 0,
    "boxShadow": "6px 0 24px rgba(0,0,0,0.22)",
    "zIndex": "100",
    "overflowY": "auto",
})

# ── Global CSS via index_string ────────────────────────────────────────────────
app.index_string = """<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Plus Jakarta Sans', 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: #F2F0ED;
    color: #1A1A2E;
    -webkit-font-smoothing: antialiased;
  }

  /* Sidebar nav hover */
  .sidebar-link .nav-item-inner {
    transition: background 0.15s ease;
  }
  .sidebar-link:hover .nav-item-inner {
    background: rgba(255,255,255,0.12) !important;
  }
  .sidebar-link:active .nav-item-inner {
    background: rgba(255,255,255,0.18) !important;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #D0C8BF; border-radius: 10px; }

  /* Card hover lift */
  .module-card {
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    cursor: default;
  }
  .module-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
  }

  .calk-clickable-card:hover {
    border-color: #2563EB !important;
    background: #F0F9FF !important;
    transform: translateX(4px);
  }

  /* Upload zone */
  .upload-zone {
    transition: border-color 0.2s, background 0.2s;
  }
  .upload-zone:hover {
    border-color: #8B2E1F !important;
    background: #FDF8F7 !important;
  }

  /* Toggle chevron */
  .chevron { transition: transform 0.25s ease; }
  .chevron.open { transform: rotate(90deg); }

  /* Table */
  .result-table th {
    background: #8B2E1F;
    color: white;
    padding: 8px 11px;
    font-size: 11.5px;
    font-weight: 600;
    text-align: left;
  }
  .result-table td {
    padding: 8px 11px;
    font-size: 12px;
    border-bottom: 1px solid #F0EDE8;
    vertical-align: top;
    color: #374151;
  }
  .result-table tr:last-child td { border-bottom: none; }
  .result-table tr:hover td { background: #FAFAF9; }
  .result-table { width: 100%; border-collapse: collapse; }

  /* Status pills */
  .pill {
    display: inline-flex; align-items: center;
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700;
    margin-right: 6px;
  }

  /* Loading spinner override */
  ._dash-loading-callback { opacity: 0.6; }
</style>
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>"""

# ── Content wrapper ────────────────────────────────────────────────────────────
content = html.Div(
    dash.page_container,
    style={
        "marginLeft": "240px",
        "padding": "0",
        "background": BG,
        "minHeight": "100vh",
        "overflowX": "hidden",
    },
)

# ── Global stores ──────────────────────────────────────────────────────────────
app.layout = html.Div([
    sidebar,
    content,
    dcc.Store(id="global-data-store",        storage_type="session"),
    dcc.Store(id="results-store",            storage_type="session"),
    dcc.Store(id="home-pipeline-result",     storage_type="session"),
    dcc.Store(id="home-file-meta",           storage_type="session"),
    dcc.Store(id="confirmed-company-store",  storage_type="session"),
    dcc.Location(id="url-location", refresh=False),
])


# ── Sidebar Module Nav: active/disabled based on confirmed company ─────────────
@app.callback(
    Output("sidebar-module-nav", "children"),
    Input("confirmed-company-store", "data"),
)
def render_sidebar_module_nav(confirmed_data):
    label = html.Div("MODUL DETIL", style={
        "fontSize": "10px", "fontWeight": "800", "color": "rgba(255,255,255,0.45)",
        "padding": "12px 20px 4px", "letterSpacing": "1px"
    })

    if confirmed_data:
        nama = confirmed_data.get("nama", "")
        short_nama = (nama[:20] + "…") if len(nama) > 20 else nama
        company_tag = html.Div(short_nama, style={
            "fontSize": "11px", "color": "rgba(255,255,255,0.55)",
            "padding": "2px 20px 8px", "fontStyle": "italic",
            "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap",
        }) if short_nama else html.Div()
        module_items = [_sidebar_btn(item) for item in MODULE_NAV_ITEMS]
        return html.Div([label, company_tag] + module_items, style={"padding": "4px 0"})
    else:
        return html.Div()

if __name__ == "__main__":
    print("\nMembuka dashboard di http://localhost:8050")
    app.run(debug=True, port=8050)
