"""Cotizador de catálogos (regular y navideño)."""
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from constantes import CATALOGOS
from utilidades import encabezado_modulo


def mostrar(menu):
    _nav = CATALOGOS[menu] == "navidad"
    _fondo = "#7F1D1D" if _nav else "#14305E"
    _acento = "#FCA5A5" if _nav else "#93C5FD"
    _titulo = "Catálogo navideño" if _nav else "Catálogo regular"
    _lema = "Shows, inflables y experiencias para la temporada" if _nav else "Atracciones y servicios para tus eventos corporativos"
    _icono = "🎄" if _nav else "🎪"
    encabezado_modulo("cat",
        "<style>.block-container{padding-top:3.4rem !important; padding-bottom:0 !important; min-height:0 !important;}</style>"
        f"<div style='display:flex; align-items:center; justify-content:space-between; gap:18px; background:{_fondo}; border-radius:14px; padding:12px 24px; margin:0 0 10px 0; box-shadow:0 1px 2px rgba(15,23,42,.10);'>"
        f"<div style='display:flex; align-items:center; gap:16px;'>"
        f"<span style='font-size:2rem; line-height:1;'>{_icono}</span>"
        f"<div><div style='font-size:0.78rem; font-weight:600; color:{_acento}; letter-spacing:0.02em;'>Cotizador Karkajadas Group</div>"
        f"<div style='font-size:1.9rem; font-weight:900; color:#FFFFFF; line-height:1.05; letter-spacing:-0.02em;'>{_titulo}</div></div></div>"
        f"<div style='font-size:0.92rem; font-weight:600; color:{_acento}; text-align:right;'>{_lema}</div>"
        "</div>",
        unsafe_allow_html=True)
    ruta_html = Path(__file__).parent / "cotizador_catalogos.html"
    if not ruta_html.exists():
        st.error("Falta el archivo cotizador_catalogos.html en el repositorio, junto a app.py. Súbelo en GitHub (Add file → Upload files).")
    else:
        pagina = ruta_html.read_text(encoding="utf-8").replace("</body>", f"<script>iniciarEmbebido('{CATALOGOS[menu]}');</script></body>")
        components.html(pagina, height=700, scrolling=False)
