"""Menú lateral del ERP."""
import streamlit as st
from constantes import SECCIONES
from utilidades import navegar

ss = st.session_state


def dibujar_menu():
    """Dibuja el menú de la izquierda y devuelve la opción elegida."""
    st.sidebar.markdown("<div class='brand-logo'>Karkajadas Group</div>", unsafe_allow_html=True)
    _css_lat, _n = "", 0
    for _gid, _tit, _ops, _col in SECCIONES:
        if _tit:
            st.sidebar.markdown(f"<p class='side-sec' style='color:{_col};'>{_tit}</p>", unsafe_allow_html=True)
        with st.sidebar.container(key=f"sec_{_gid}"):
            for _op in _ops:
                st.button(_op, use_container_width=True, key=f"nav_{_n}", on_click=navegar, args=(_op,))
                if ss.nav_menu == _op:
                    _css_lat += f"[data-testid=\"stSidebar\"] .st-key-nav_{_n} div[data-testid=\"stButton\"] button{{background:{_col}33 !important; color:#FFFFFF !important; border-color:{_col}88 !important; border-left:4px solid {_col} !important;}}"
                _n += 1
        _css_lat += (f"[data-testid=\"stSidebar\"] .st-key-sec_{_gid} div[data-testid=\"stButton\"] button{{background:{_col}12 !important; border:1px solid {_col}30 !important; border-left:4px solid {_col}AA !important;}}"
                     f"[data-testid=\"stSidebar\"] .st-key-sec_{_gid} div[data-testid=\"stButton\"] button:hover{{background:{_col}26 !important; border-left-color:{_col} !important;}}")
    st.sidebar.markdown(f"<style>{_css_lat}</style>", unsafe_allow_html=True)
    return ss.nav_menu
