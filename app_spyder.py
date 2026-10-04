# -*- coding: utf-8 -*-
"""
SIKULI — Dashboard Analisis Kepatuhan Keuangan (OJK)
VERSI SPYDER

Cara pakai di Spyder (Anaconda):
  1. Buka file ini di Spyder (File > Open > app_spyder.py).
  2. Tekan F5 (Run file). Browser otomatis membuka http://127.0.0.1:8050
  3. Konsol tetap bisa dipakai selama dashboard jalan.
     - Hentikan server  : ketik  hentikan_dashboard()  di konsol
     - Jalankan ulang   : tekan F5 lagi (server lama otomatis dimatikan dulu)

Kenapa perlu file terpisah dari app.py?
  - app.run(debug=True) memakai "reloader" Flask yang membuat proses baru;
    di konsol IPython Spyder ini memicu error / konsol macet.
  - Saat F5 ditekan berkali-kali, Dash mendaftarkan ulang halaman & callback
    dan port 8050 masih dipakai server lama -> error "Address already in use"
    atau "Duplicate callback outputs".
  - Spyder belum tentu menjalankan file dengan working directory = folder
    proyek, sehingga folder `pages/`, `utils/`, `ml/` bisa tidak ditemukan.
File ini mengatasi ketiganya tanpa mengubah app.py — logika dashboard tetap
satu sumber (app.py + pages/ + utils/ + ml/).

File ini juga dibagi per sel (# %%), jadi bisa dijalankan per bagian dengan
Ctrl+Enter bila perlu.
"""

# %% 0. Konfigurasi — ubah sesuai kebutuhan
HOST = "127.0.0.1"
PORT = 8050
BUKA_BROWSER = True     # buka browser otomatis setelah server siap
DEBUG_UI = True         # tampilkan panel error Dash di pojok kanan bawah browser
MODE_BLOKIR = False     # True  = server jalan di depan (konsol "sibuk", stop pakai
                        #         tombol stop merah / Ctrl+C di konsol)
                        # False = server jalan di background, konsol tetap bisa dipakai


# %% 1. Siapkan path proyek
import os
import sys
import builtins
import socket
import threading
import webbrowser
from pathlib import Path

try:
    PROJECT_DIR = Path(__file__).resolve().parent
except NameError:  # dijalankan per sel tanpa __file__
    PROJECT_DIR = Path.cwd()

if not (PROJECT_DIR / "app.py").exists() or not (PROJECT_DIR / "pages").is_dir():
    raise FileNotFoundError(
        f"app.py / folder pages tidak ditemukan di {PROJECT_DIR}.\n"
        "Pastikan app_spyder.py berada di folder ojk_dashboard, atau set working "
        "directory Spyder ke folder tersebut (ikon folder di kanan atas Spyder)."
    )

os.chdir(PROJECT_DIR)
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# %% 1b. Cek paket yang dibutuhkan (semua yang kurang ditampilkan sekaligus)
import importlib.util


def _ada(modul):
    try:
        return importlib.util.find_spec(modul) is not None
    except (ImportError, ValueError):
        return False


# nama import -> nama paket pip
_WAJIB = {
    "dash": "dash", "plotly": "plotly", "pandas": "pandas", "numpy": "numpy",
    "sklearn": "scikit-learn", "openpyxl": "openpyxl",
    "reportlab": "reportlab", "pdfplumber": "pdfplumber",
}
_OPSIONAL = {  # dashboard tetap jalan tanpa ini, fiturnya saja yang nonaktif
    "google.genai": "google-genai",   # narasi GenAI via Gemini
    "pytesseract": "pytesseract",     # OCR PDF hasil scan
    "PIL": "Pillow",                  # OCR PDF hasil scan
}

_kurang = [pip for mod, pip in _WAJIB.items() if not _ada(mod)]
_kurang_ops = [pip for mod, pip in _OPSIONAL.items() if not _ada(mod)]

if _kurang_ops:
    print("Info: paket opsional belum terinstal -> " + " ".join(_kurang_ops))

if _kurang:
    _perintah = "%pip install " + " ".join(_kurang + _kurang_ops)
    print("\n" + "=" * 70)
    print("Paket wajib belum terinstal di Python yang dipakai Spyder:")
    print("   " + ", ".join(_kurang))
    print("\nKetik perintah ini di konsol Spyder (kanan bawah), tekan Enter:")
    print("\n   " + _perintah + "\n")
    print("Setelah selesai: Consoles > Restart kernel, lalu tekan F5 lagi.")
    print("Python yang dipakai sekarang: " + sys.executable)
    print("=" * 70)
    raise ModuleNotFoundError("Paket belum lengkap: " + ", ".join(_kurang))


# %% 2. Bersihkan sisa run sebelumnya (supaya F5 berulang tidak error)
def hentikan_dashboard():
    """Matikan server dashboard yang sedang jalan di background."""
    srv = getattr(builtins, "_SIKULI_SERVER", None)
    if srv is None:
        print("Tidak ada server dashboard yang sedang jalan.")
        return
    srv.shutdown()
    srv.server_close()
    builtins._SIKULI_SERVER = None
    print("Server dashboard dihentikan.")


if getattr(builtins, "_SIKULI_SERVER", None) is not None:
    print("Menghentikan server dari run sebelumnya...")
    hentikan_dashboard()


def _bersihkan_modul_proyek():
    """Hapus modul proyek dari cache Python + registry global Dash, supaya
    perubahan kode terbaca dan halaman/callback tidak terdaftar dua kali."""
    root = str(PROJECT_DIR)
    for name, mod in list(sys.modules.items()):
        top = name.split(".")[0]
        if top not in ("app", "pages", "utils", "ml"):
            continue
        f = getattr(mod, "__file__", None) or ""
        paths = list(getattr(mod, "__path__", []) or [])
        if f.startswith(root) or any(str(p).startswith(root) for p in paths) or not f:
            del sys.modules[name]

    try:
        import dash._pages as _dp
        _dp.PAGE_REGISTRY.clear()
    except Exception:
        pass
    try:
        import dash._callback as _dc
        _dc.GLOBAL_CALLBACK_LIST.clear()
        _dc.GLOBAL_CALLBACK_MAP.clear()
        if hasattr(_dc, "GLOBAL_INLINE_SCRIPTS"):
            _dc.GLOBAL_INLINE_SCRIPTS.clear()
    except Exception:
        pass


_bersihkan_modul_proyek()


# %% 3. Muat aplikasi dari app.py (tanpa menjalankan blok __main__-nya)
import app as _sikuli          # noqa: E402  -> app.py, pages/, utils/, ml/

app = _sikuli.app
server = app.server
URL = f"http://{HOST}:{PORT}"

if DEBUG_UI:
    # Panel error Dash aktif, tapi hot-reload & reloader dimatikan (aman di Spyder)
    app.enable_dev_tools(
        debug=True,
        dev_tools_hot_reload=False,
        dev_tools_serve_dev_bundles=False,
    )


def _port_terpakai(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def _buka_browser():
    if BUKA_BROWSER:
        threading.Timer(1.0, lambda: webbrowser.open(URL)).start()


# %% 4. Jalankan server
if _port_terpakai(HOST, PORT):
    raise OSError(
        f"Port {PORT} masih dipakai program lain (mungkin `python app.py` di "
        "terminal, atau kernel Spyder lain). Tutup program itu, restart kernel "
        "(Consoles > Restart kernel), atau ganti nilai PORT di sel 0."
    )

if MODE_BLOKIR:
    print(f"\nDashboard jalan di {URL}  (tekan tombol stop / Ctrl+C di konsol untuk berhenti)")
    _buka_browser()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
else:
    from werkzeug.serving import make_server

    _srv = make_server(HOST, PORT, server, threaded=True)
    builtins._SIKULI_SERVER = _srv
    threading.Thread(target=_srv.serve_forever, name="sikuli-dash", daemon=True).start()

    print(f"\nDashboard jalan di background: {URL}")
    print("  - Hentikan          : hentikan_dashboard()")
    print("  - Jalankan ulang    : tekan F5 lagi")
    print("  - Variabel tersedia : app (objek Dash), server (Flask)")
    _buka_browser()
