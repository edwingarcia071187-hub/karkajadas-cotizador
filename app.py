import json
from io import BytesIO
from html import escape as esc
from pathlib import Path
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import altair as alt
from urllib.parse import quote_plus
from datetime import date, datetime

# Requiere Streamlit >= 1.39 (usa las clases .st-key-<key> para estilizar botones)

# =============================================================================
# CONSTANTES
# =============================================================================
ESTADOS = ["Aprobada", "Enviada", "Borrador", "Cancelada"]
MENU_CLIENTES = "Directorio de clientes"
MENU_PROVEEDORES = "Directorio de proveedores"
COLORES = {   # paleta de datos sobria: distinta a los botones (verde = confirmar, azul = neutro)
    "Aprobada": "#2C8C84",   # verde azulado
    "Enviada": "#7A68B5",    # lavanda
    "Borrador": "#B8913F",   # arena
    "Cancelada": "#B85C78",  # rosa antiguo
}
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
CIUDADES_DEMO = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]   # solo para el catálogo de ejemplo
CIUDADES_BASE = ["Quito", "Guayaquil", "Cuenca", "Santo Domingo de los Tsáchilas", "Machala", "Manta", "Portoviejo", "Ambato",
                 "Riobamba", "Loja", "Ibarra", "Esmeraldas", "Latacunga"]
OTRA = "Otra..."
CIUDADES = CIUDADES_BASE + ["Varias ciudades"]
NUEVO_CLIENTE = "+ Registrar nuevo cliente..."
IVA_CLIENTE = 0.15
SIN_FILTRO = {"f_emp": "Todas", "f_mes": "Todos", "f_ciu": "Todas", "b_u": ""}

st.set_page_config(page_title="Karkajadas Group - ERP", layout="wide", initial_sidebar_state="expanded")

# =============================================================================
# ESTILOS
# =============================================================================
CSS_BASE = """
.block-container { padding-top: 3.2rem !important; padding-bottom: 2rem !important; max-width: 98% !important; }
.stApp, .main, header { background-color: #EEF2F7 !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }

/* Botón para ocultar el panel (dentro del panel azul): blanco y con borde */
[data-testid="stSidebarCollapseButton"] button { background: rgba(255,255,255,.16) !important; border: 1px solid rgba(255,255,255,.55) !important; border-radius: 8px !important; width: 2.2rem !important; height: 2.2rem !important; opacity: 1 !important; }
[data-testid="stSidebarCollapseButton"] button:hover { background: rgba(255,255,255,.30) !important; }
[data-testid="stSidebarCollapseButton"] button span, [data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"] { color: #FFFFFF !important; opacity: 1 !important; }
/* Botón para volver a mostrar el panel (cuando está oculto): azul oscuro con flecha blanca */
[data-testid="stExpandSidebarButton"] { background: #1E3A8A !important; border: 1px solid #1E3A8A !important; border-radius: 8px !important; width: 2.2rem !important; height: 2.2rem !important; opacity: 1 !important; }
[data-testid="stExpandSidebarButton"]:hover { background: #2563EB !important; }
[data-testid="stExpandSidebarButton"] span, [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] { color: #FFFFFF !important; opacity: 1 !important; }

/* Tarjetas: contenedores con borde, identificados por su clave (st-key-card_N) */
[class*="st-key-card_"] {
    background-color: #FFFFFF !important; border: 1px solid #C9D3E0 !important; border-radius: 12px !important;
    box-shadow: 0 1px 2px rgba(15,23,42,.06), 0 4px 14px rgba(15,23,42,.06) !important; padding: 18px 25px !important;
}

/* Encabezado de módulo: mismo borde y una sombra neutra un poco más marcada para que resalte */
[class*="st-key-card_h_"] { box-shadow: 0 2px 4px rgba(15,23,42,.08), 0 10px 26px rgba(15,23,42,.11) !important; border-color: #B8C4D4 !important; padding: 14px 25px !important; }
.sec-sub { font-size: 1rem; font-weight: 700; color: #1E3A8A; padding: 2px 0 6px; margin: 10px 0 8px; border-bottom: 1px solid #E2E8F0; }
.sec-sub:first-child { margin-top: 0; }
.hd-titulo { font-size: 1.55rem; font-weight: 800; color: #0F172A; line-height: 1.15; margin: 0; }
.hd-sub { font-size: .85rem; font-weight: 600; color: #64748B; margin-top: 3px; }

/* Botones globales: verde = avanzar, azul = neutro */
button[kind="primary"], button[data-testid="stBaseButton-primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primaryFormSubmit"] {
    background-color: #059669 !important; border: 1px solid #059669 !important; color: #FFFFFF !important;
    border-radius: 8px !important; font-weight: 600 !important; transition: all .2s ease !important; box-shadow: none !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover, button[kind="primaryFormSubmit"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover { background-color: #047857 !important; transform: translateY(-1px); }
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: #1E3A8A !important; border: 1px solid #1E3A8A !important; color: #FFFFFF !important;
    border-radius: 8px !important; font-weight: 600 !important; transition: all .2s ease !important; box-shadow: none !important;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover { background-color: #1E40AF !important; transform: translateY(-1px); }
a[data-testid="stBaseLinkButton-secondary"] { background-color: #1E3A8A !important; border: 1px solid #1E3A8A !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; box-shadow: none !important; }
a[data-testid="stBaseLinkButton-secondary"] p, a[data-testid="stBaseLinkButton-secondary"] span { color: #FFFFFF !important; }
a[data-testid="stBaseLinkButton-secondary"]:hover { background-color: #1E40AF !important; }

/* Botones de elección (Sí / No, Pendiente / Enviada): iguales a las píldoras */
button[data-variant="segmented_control"] { background: #E3E9F1 !important; border: 1px solid #B4C0D0 !important; color: #475569 !important; box-shadow: none !important; }
button[data-variant="segmented_control"] p { color: inherit !important; font-weight: 600 !important; }
button[data-variant="segmented_control"][aria-checked="true"], button[data-variant="segmented_control"][data-selected="true"] { background: #1E3A8A !important; border-color: #1E3A8A !important; color: #FFFFFF !important; }

/* Filtros de selección: botones tipo "píldora" y etiquetas, en gris azulado; lo elegido va en azul (igual que las pestañas) */
button[data-variant="pills"] { background: #E3E9F1 !important; border: 1px solid #B4C0D0 !important; color: #475569 !important; border-radius: 8px !important; box-shadow: none !important; }
button[data-variant="pills"] p { color: inherit !important; font-weight: 600 !important; }
button[data-variant="pills"]:hover { background: #D3DCE8 !important; color: #1E3A8A !important; }
button[data-variant="pills"][aria-pressed="true"], button[data-variant="pills"][data-selected="true"] { background: #1E3A8A !important; border-color: #1E3A8A !important; color: #FFFFFF !important; }
[data-testid="stMultiSelectTagsContainer"] [data-tag] { background: #475569 !important; color: #FFFFFF !important; border-radius: 6px !important; }
[data-testid="stMultiSelectTagsContainer"] [data-tag] * { color: #FFFFFF !important; }

/* Tarjetas KPI (el color de cada una, incluido hover/focus, se agrega por código según su estado) */
[class*="st-key-kpi_"] button {
    width: 100% !important; min-height: 85px !important; padding: 12px 10px !important; border-radius: 8px !important;
    justify-content: flex-start !important; text-align: left !important; box-shadow: 0 1px 2px rgba(15,23,42,.06) !important;
}
[class*="st-key-kpi_"] button * { color: #0F172A !important; }
[class*="st-key-kpi_"] button p { font-size: 15px !important; font-weight: 800 !important; white-space: pre-wrap !important; margin: 0 !important; line-height: 1.3 !important; }
[class*="st-key-kpi_"] button:hover { transform: translateY(-2px) !important; }

/* "Borrar filtros": enlace de texto discreto, sin aspecto de botón */
div.st-key-clear_btn button, div.st-key-clear_btn button:hover, div.st-key-clear_btn button:focus, div.st-key-clear_btn button:active {
    background: transparent !important; border: none !important; box-shadow: none !important; transform: none !important;
    color: #64748B !important; font-weight: 500 !important; font-size: 13px !important;
    min-height: 0 !important; padding: 2px 0 !important; justify-content: flex-end !important; width: 100%;
}
div.st-key-clear_btn button:hover { color: #1E3A8A !important; text-decoration: underline; }
.total-general { text-align: right; font-size: 13px; color: #64748B; font-weight: 500; }
.total-general b { color: #0F172A; }

/* Botones compactos de la tabla de costos */
[class*="st-key-mv_"] button, [class*="st-key-del_"] button, [class*="st-key-edit_"] button { padding: 0 !important; min-height: 26px !important; height: 26px !important; width: 100% !important; font-size: 13px !important; line-height: 1 !important; }
[class*="st-key-mv_"] button, [class*="st-key-edit_"] button { background: #E9EEF5 !important; border: 1px solid #CBD5E1 !important; color: #475569 !important; box-shadow: none !important; border-radius: 6px !important; }
[class*="st-key-mv_"] button:hover, [class*="st-key-edit_"] button:hover { background: #DCE5F0 !important; color: #1E3A8A !important; border-color: #94A3B8 !important; }
[class*="st-key-mv_"] button:disabled { opacity: .35; }
[class*="st-key-del_"] button { background: #EF4444 !important; border: 1px solid #EF4444 !important; color: #FFF !important; font-weight: 700 !important; border-radius: 6px !important; box-shadow: none !important; }
[class*="st-key-del_"] button:hover { background: #DC2626 !important; }

/* Tabla "Estructura de costos": cada servicio es una franja suave (fondo + sombra) separada de la siguiente, sin cuadrícula */
.st-key-tabla_costos, .st-key-tabla_det { gap: 6px !important; }
.st-key-tabla_costos [data-testid="stHorizontalBlock"], .st-key-tabla_det [data-testid="stHorizontalBlock"] {
    gap: .4rem !important; align-items: center !important; padding: 7px 12px;
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 10px; box-shadow: 0 1px 2px rgba(15,23,42,.06);
}
.st-key-costos_head [data-testid="stHorizontalBlock"], .st-key-det_head [data-testid="stHorizontalBlock"] { background: transparent; border: none; box-shadow: none; padding: 0 12px 2px; }
/* Streamlit resta 1rem al contenedor de markdown para compensar el margen del <p>; al quitar el margen hay que quitar también ese ajuste */
.st-key-tabla_costos [data-testid="stMarkdownContainer"], .st-key-tabla_det [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.st-key-tabla_costos [data-testid="stMarkdownContainer"] p, .st-key-tabla_costos [data-testid="stElementContainer"],
.st-key-tabla_det [data-testid="stMarkdownContainer"] p, .st-key-tabla_det [data-testid="stElementContainer"] { margin: 0 !important; }
.st-key-tabla_det button { min-height: 30px !important; padding: 2px 10px !important; }
.badge-estado { display: inline-block; font-size: 11px; font-weight: 800; letter-spacing: .3px; padding: 2px 10px; border-radius: 999px; line-height: 18px; }
.cell { font-size: 14px; color: #1E293B; line-height: 26px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell.num, .col-head.num { text-align: right; }
.cell .pos { color: #059669; font-weight: 600; }

/* Botón "Regresar al panel": neutro, gris azulado */
div.st-key-back_btn button, div.st-key-back_btn button:focus, div.st-key-back_btn button:active {
    background: #E3E9F1 !important; border: 1px solid #B4C0D0 !important; color: #334155 !important; box-shadow: none !important;
}
div.st-key-back_btn button:hover { background: #D3DCE8 !important; border-color: #94A3B8 !important; color: #1E3A8A !important; }
/* Confirmación de salida: "Salir sin guardar" en rojo, "Cancelar" queda azul */
div.st-key-exit_confirm button, div.st-key-exit_confirm button:focus, div.st-key-exit_confirm button:active { background: #EF4444 !important; border: 1px solid #EF4444 !important; color: #FFFFFF !important; }
div.st-key-exit_confirm button:hover { background: #DC2626 !important; border-color: #DC2626 !important; }
button:disabled { opacity: .45 !important; cursor: not-allowed !important; transform: none !important; }

/* Panel lateral */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important; }
.brand-logo { font-size: 22px; font-weight: 900; color: #FFFFFF; margin: 5px 0 12px; padding-left: 5px; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .3rem !important; }
[data-testid="stSidebar"] div[data-testid="stButton"] { width: 100% !important; margin: 0 !important; }
[data-testid="stSidebar"] p.side-sec { font-size: 10.5px; font-weight: 700; letter-spacing: .08em; line-height: 34px !important; margin: 0 !important; padding: 0 0 0 4px !important; }
[data-testid="stSidebar"] div[data-testid="stButton"] button {
    background-color: #1E293B !important; border: 1px solid #334155 !important; color: #CBD5E1 !important; border-radius: 8px !important;
    padding: 8px 14px !important; min-height: 0 !important; width: 100% !important; display: flex !important; justify-content: flex-start !important;
    box-shadow: none !important; transition: all .2s ease !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] button p { width: 100% !important; text-align: left !important; font-weight: 500 !important; margin: 0 !important; }
[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
    background-color: #334155 !important; color: #FFFFFF !important; border-color: #475569 !important;
    box-shadow: none !important; transform: translateX(3px) !important;
}

/* Campos: cada recuadro tiene fondo gris azulado, borde definido y sombra interior (se distingue del fondo blanco de la tarjeta) */
[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"], [data-testid="stDateInputField"], [data-testid="stSelectbox"] [role="group"], [data-testid="stTextAreaRootElement"], [data-testid="stTimeInputTimeDisplay"] {
    background-color: #EEF2F7 !important; border: 1px solid #B4C0D0 !important; border-radius: 8px !important;
    box-shadow: inset 0 1px 2px rgba(15,23,42,.08) !important; transition: border-color .15s, background-color .15s, box-shadow .15s;
}
[data-testid="stTextAreaRootElement"]:hover, [data-testid="stTimeInputTimeDisplay"]:hover, [data-testid="stTextInputRootElement"]:hover, [data-testid="stNumberInputContainer"]:hover, [data-testid="stDateInputField"]:hover, [data-testid="stSelectbox"] [role="group"]:hover { border-color: #7C8CA3 !important; }
[data-testid="stTextAreaRootElement"]:focus-within, [data-testid="stTimeInputTimeDisplay"]:focus-within, [data-testid="stTextInputRootElement"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within, [data-testid="stDateInputField"]:focus-within, [data-testid="stSelectbox"] [role="group"]:focus-within {
    background-color: #FFFFFF !important; border-color: #1E3A8A !important; box-shadow: 0 0 0 3px rgba(30,58,138,.15) !important;
}

/* Pestañas: cada una es un botón con fondo y borde propios; la activa va en azul (igual que los botones neutros) */
[data-testid="stTabs"] [role="tablist"] { gap: 8px !important; border-bottom: none !important; box-shadow: none !important; margin-bottom: 8px; }
[data-testid="stTabs"] [role="tablist"]::before, [data-testid="stTabs"] [role="tablist"]::after { display: none !important; }
[data-testid="stTab"] {
    height: 38px !important; padding: 0 18px !important; border-radius: 8px !important; justify-content: center;
    background: #E3E9F1 !important; border: 1px solid #B4C0D0 !important; color: #475569 !important; outline: none !important; box-shadow: none !important;
}
[data-testid="stTab"] p { color: inherit !important; font-weight: 600 !important; }
[data-testid="stTab"]:hover { background: #D3DCE8 !important; color: #1E3A8A !important; }
[data-testid="stTab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"]:hover { background: #1E3A8A !important; border-color: #1E3A8A !important; color: #FFFFFF !important; }
[data-testid="stTab"] .react-aria-SelectionIndicator, .react-aria-SelectionIndicator { display: none !important; }
.stSelectbox label, .stTextInput label, .stNumberInput label { font-size: 13px !important; color: #64748B !important; font-weight: 600 !important; margin-bottom: 4px !important; }
.section-title { color: #0F172A; font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 12px; letter-spacing: .5px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; }
.col-head { font-size: 11px; font-weight: 700; color: #64748B; }
.st-key-barra_total { position: sticky; bottom: 0; z-index: 20; background: #FFFFFF; border-top: 2px solid #E2E8F0; padding: 10px 0 4px; margin-top: 8px; }
.metric-tile { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #1E3A8A; border-radius: 10px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(15,23,42,.06); }
.metric-tile.ganancia { border-left-color: #059669; }
.internal-metrics { font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .4px; }
.internal-metrics-value { font-size: 22px; font-weight: 800; color: #0F172A; }
.metric-tile.ganancia .internal-metrics-value { color: #047857; }
.invoice-container { width: 100%; background-color: #F8FAFC; padding: 10px 16px; border-radius: 12px; border: 1px solid #CBD5E1; box-shadow: 0 1px 2px rgba(15,23,42,.06), 0 4px 12px rgba(15,23,42,.06); }

/* Monto estimado (encabezado de la cotización) */
.monto-badge { display: flex; flex-direction: column; align-items: flex-start; justify-content: center; line-height: 1; padding: 2px 0 2px 18px;
    border-left: 4px solid #1E3A8A; margin-left: auto; width: fit-content; }
.monto-label { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #64748B; margin-bottom: 6px; }
.monto-valor { font-size: 30px; font-weight: 800; letter-spacing: -.01em; color: #0F172A; font-variant-numeric: tabular-nums; }
.invoice-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; color: #475569; }
.invoice-total { display: flex; justify-content: space-between; border-top: 2px solid #CBD5E1; padding-top: 10px; margin-top: 10px; font-size: 20px; font-weight: 800; color: #1E3A8A; }
"""


def css_kpi():
    """Tarjetas sobrias: fondo blanco, borde fino y franja izquierda del color del estado.
    Se repite en :hover/:focus/:active para ganar en especificidad al estilo global de botones."""
    reglas = []
    for e in ESTADOS:
        c = COLORES[e]
        for p, fondo in (("", "#FFFFFF"), (":hover", c + "12"), (":focus", "#FFFFFF"), (":active", c + "12")):
            reglas.append(f"div.st-key-kpi_{e} button{p}{{background:{fondo} !important;border:1px solid #DCE3EC !important;"
                          f"border-left:10px solid {c} !important;color:#0F172A !important;}}")
    return "".join(reglas)


def css_pills_estado():
    """Botones de estado del reporte con el color de cada estado (el mismo de las tarjetas del panel de control)."""
    reglas = []
    for i, e in enumerate(ESTADOS, start=2):   # el botón 1 es "Todas"
        c = COLORES[e]
        base = f'div.st-key-rep_est button[data-variant="pills"]:nth-of-type({i})'
        reglas.append(f"{base}{{box-shadow: inset 5px 0 0 {c} !important; padding-left: 14px !important;}}")
        reglas.append(f'{base}[aria-pressed="true"], {base}[data-selected="true"]{{background:{c} !important; border-color:{c} !important; color:#FFFFFF !important;}}')
    return "".join(reglas)


def css_tarjeta_activa(estado):
    """Tarjeta seleccionada: fondo tenue del color del estado y borde más marcado."""
    if estado not in COLORES:
        return ""
    c = COLORES[estado]
    sel = ", ".join(f"div.st-key-kpi_{estado} button{p}" for p in ("", ":hover", ":focus", ":active"))
    return f"{sel}{{background:{c}1A !important;border:1px solid {c} !important;border-left:10px solid {c} !important;}}"


def css_pills_estado():
    """Botones del filtro de estado: lo elegido toma el color de ese estado (los mismos de las tarjetas y gráficos del panel)."""
    reglas = ['.st-key-rep_est button[data-variant="pills"][aria-pressed="true"]:nth-child(1){background:#334155 !important;border-color:#334155 !important;}']
    for i, e in enumerate(ESTADOS, start=2):
        c = COLORES[e]
        reglas.append(f'.st-key-rep_est button[data-variant="pills"][aria-pressed="true"]:nth-child({i}){{background:{c} !important;border-color:{c} !important;color:#FFFFFF !important;}}')
    return "".join(reglas)


st.markdown(f"<style>{CSS_BASE}{css_kpi()}{css_pills_estado()}</style>", unsafe_allow_html=True)

# =============================================================================
# ESTADO INICIAL
# =============================================================================
ss = st.session_state
ss.setdefault("ciudades_extra", [])   # ciudades que se escriben con la opción "Otra..."
CIUDADES[:] = CIUDADES_BASE + [c for c in ss.ciudades_extra if c not in CIUDADES_BASE] + ["Varias ciudades"]
ss.setdefault("nav_menu", "Panel de control")
ss.setdefault("items_cot", [])
ss.setdefault("cotizacion_activa", None)
ss.setdefault("filtro_estado_tabla", "Todas")
ss.setdefault("cot_sid", 0)       # se incrementa en cada navegación: así los campos de la cotización arrancan limpios
ss.setdefault("cot_base", None)   # "foto" del formulario al abrirlo / guardarlo, para detectar cambios sin guardar
for _k, _v in SIN_FILTRO.items():
    ss.setdefault(_k, _v)

if "proveedores_catalogo" not in ss:
    servicios_base = [
        ("Cabina fotográfica 360", "Entretenimiento", 300.0, 0.0),
        ("Carpa estructural 6x6", "Estructuras", 50.0, 0.15),
        ("Animador corporativo", "Animación", 150.0, 0.15),
        ("Catering premium", "Alimentos", 25.0, 0.15),
        ("Sonido profesional", "Audiovisual", 180.0, 0.15),
    ]
    ss.proveedores_catalogo = [
        {"servicio": s, "proveedor": f"Pro{cat} {ciu[:3].upper()}", "categoria": cat, "ciudad": ciu,
         "precio_base": precio, "iva": iva, "descripcion": "Estándar"}
        for ciu in CIUDADES_DEMO for s, cat, precio, iva in servicios_base
    ]


def _item(servicio, fecha, cant, costo, iva, fee):
    return {"servicio": servicio, "proveedor": "Pro", "ciudad": "Quito", "fecha": fecha,
            "cantidad": cant, "costo": costo, "iva_prov": iva, "fee_pct": fee}


if "cotizaciones_guardadas" not in ss:
    ss.cotizaciones_guardadas = [
        {"codigo": "KG-20261215-001", "evento": "Fiesta corporativa", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 1414.00, "items": [_item("Cabina fotográfica", "2026-12-15", 1, 300.0, 0.0, 20.0)]},
        {"codigo": "KG-20261110-002", "evento": "Lanzamiento de marca", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-11-10", "estado": "Enviada", "total": 2248.40, "items": [_item("Sonido profesional", "2026-11-10", 1, 180.0, 0.15, 20.0)]},
        {"codigo": "KG-20261020-003", "evento": "Cena de directivos", "cliente": "Hilton Colón Quito", "fecha": "2026-10-20", "estado": "Borrador", "total": 834.50, "items": [_item("Catering premium", "2026-10-20", 1, 25.0, 0.15, 20.0)]},
        {"codigo": "KG-20260905-004", "evento": "Capacitación anual", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-09-05", "estado": "Aprobada", "total": 3150.00, "items": [_item("Logística", "2026-09-05", 1, 1000.0, 0.0, 15.0)]},
        {"codigo": "KG-20260812-005", "evento": "Activación BTL", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-08-12", "estado": "Aprobada", "total": 1850.00, "items": [_item("Animador corporativo", "2026-08-12", 5, 150.0, 0.15, 20.0)]},
        {"codigo": "KG-20261006-007", "evento": "Feria cultural", "cliente": "Hilton Colón Quito", "fecha": "2026-10-06", "estado": "Aprobada", "total": 545.10, "items": [
            {"servicio": "Carpa 6x6 con 4 paredes", "proveedor": "Mario Mora - Bizion", "ciudad": "Guayaquil", "fecha": "2026-10-06", "cantidad": 1, "costo": 300.0, "iva_prov": 0.15, "fee_pct": 20.0},
            {"servicio": "Jenga gigante de madera", "proveedor": "Karkajadas Group", "ciudad": "Guayaquil", "fecha": "2026-10-06", "cantidad": 2, "costo": 30.0, "iva_prov": 0.0, "fee_pct": 0.0}]},
        {"codigo": "KG-20261005-006", "evento": "Feria de exposición", "cliente": "Hilton Colón Quito", "fecha": "2026-10-05", "estado": "Aprobada", "total": 2200.00, "items": [_item("Carpa", "2026-10-05", 2, 50.0, 0.15, 20.0)]},
    ]

    def _cot(cod, evento, cliente, fecha, estado, lineas):
        """lineas: (servicio, categoría, ciudad, cantidad, costo, iva, margen %). El proveedor sale del catálogo de ejemplo."""
        items = [{"servicio": sv, "proveedor": f"Pro{cat} {ciu[:3].upper()}", "ciudad": ciu, "fecha": fecha,
                  "cantidad": cant, "costo": costo, "iva_prov": iva, "fee_pct": fee} for sv, cat, ciu, cant, costo, iva, fee in lineas]
        total = sum(c * k * (1 + v) * (1 + f / 100) for _, _, _, c, k, v, f in lineas) * (1 + IVA_CLIENTE)
        return {"codigo": cod, "evento": evento, "cliente": cliente, "fecha": fecha, "estado": estado, "total": round(total, 2), "items": items}

    ss.cotizaciones_guardadas += [
        _cot("KG-20260918-008", "Convención anual de ventas", "Importadora Austral S.A.", "2026-09-18", "Aprobada",
             [("Sonido profesional", "Audiovisual", "Cuenca", 1, 180.0, 0.15, 20.0), ("Catering premium", "Alimentos", "Cuenca", 120, 25.0, 0.15, 20.0)]),
        _cot("KG-20261003-009", "Fiesta de fin de año", "Hotel Costa Azul S.A.", "2026-10-03", "Enviada",
             [("Carpa estructural 6x6", "Estructuras", "Manta", 3, 220.0, 0.15, 20.0), ("Animador corporativo", "Animación", "Manta", 2, 150.0, 0.15, 20.0)]),
        _cot("KG-20261112-010", "Lanzamiento de producto", "Grupo Litoral Cía. Ltda.", "2026-11-12", "Aprobada",
             [("Cabina fotográfica 360", "Entretenimiento", "Guayaquil", 1, 300.0, 0.0, 20.0), ("Sonido profesional", "Audiovisual", "Guayaquil", 1, 180.0, 0.15, 20.0)]),
        _cot("KG-20260825-011", "Feria de emprendedores", "Importadora Austral S.A.", "2026-08-25", "Borrador",
             [("Carpa estructural 6x6", "Estructuras", "Ambato", 4, 220.0, 0.15, 15.0)]),
        _cot("KG-20261205-012", "Gala empresarial", "Hotel Costa Azul S.A.", "2026-12-05", "Cancelada",
             [("Catering premium", "Alimentos", "Manta", 200, 25.0, 0.15, 20.0), ("Animador corporativo", "Animación", "Manta", 1, 150.0, 0.15, 20.0)]),
        _cot("KG-20261022-013", "Activación de marca", "Grupo Litoral Cía. Ltda.", "2026-10-22", "Enviada",
             [("Cabina fotográfica 360", "Entretenimiento", "Guayaquil", 2, 300.0, 0.0, 20.0), ("Animador corporativo", "Animación", "Guayaquil", 3, 150.0, 0.15, 20.0)]),
    ]

if "clientes_catalogo" not in ss:
    ss.clientes_catalogo = [
        {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
        {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
        {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
        {"empresa": "Importadora Austral S.A.", "ruc": "0190123456001", "ciudad": "Cuenca", "direccion": "Av. Ordóñez Lasso", "web": "www.austral.ec", "contacto": "Marketing", "email": "eventos@austral.ec", "telefono": "07-410-2233", "dias_credito": 30},
        {"empresa": "Hotel Costa Azul S.A.", "ruc": "1391234567001", "ciudad": "Manta", "direccion": "Malecón de Manta", "web": "www.costaazul.ec", "contacto": "Eventos", "email": "eventos@costaazul.ec", "telefono": "05-262-1100", "dias_credito": 15},
        {"empresa": "Grupo Litoral Cía. Ltda.", "ruc": "0991234567001", "ciudad": "Guayaquil", "direccion": "Av. Francisco de Orellana", "web": "www.grupolitoral.ec", "contacto": "Gerencia", "email": "gerencia@grupolitoral.ec", "telefono": "04-268-5500", "dias_credito": 45},
    ]


def migrar_datos():
    """Pone al día los datos de la sesión (también los creados con versiones anteriores de la app)."""
    for c in ss.cotizaciones_guardadas:
        c.setdefault("invitados", 100)
    for n, c in enumerate(ss.clientes_catalogo, 1):
        c.setdefault("id", f"CLI-{n:03d}")
        c.setdefault("contactos", [{"nombre": c.get("contacto", ""), "cargo": "", "correo": c.get("email", ""), "telefono": c.get("telefono", "")}]
                     if any(c.get(k) for k in ("contacto", "email", "telefono")) else [])
        c.setdefault("direcciones", [{"etiqueta": "Principal", "direccion": c.get("direccion", ""), "ciudad": c.get("ciudad", "")}] if c.get("direccion") else [])
        c.setdefault("web", "")
        c.setdefault("dias_credito", 30)
    for r in ss.proveedores_catalogo:
        r.pop("banco", None)
        r.pop("cuenta", None)
        r.setdefault("categoria", "")
        r.setdefault("descripcion", "")
    if "proveedores" not in ss:
        vistos = {}
        for r in ss.proveedores_catalogo:
            vistos.setdefault(r["proveedor"], r)
        ss.proveedores = [{"id": f"PRV-{n:03d}", "proveedor": nom, "ruc": "", "categoria": r["categoria"], "ciudad": r["ciudad"],
                           "observaciones": "", "contactos": [], "direcciones": [], "cuentas": []}
                          for n, (nom, r) in enumerate(vistos.items(), 1)]
    for n, p in enumerate(ss.proveedores, 1):
        p.setdefault("id", f"PRV-{n:03d}")
        for k in ("contactos", "direcciones", "cuentas"):
            p.setdefault(k, [])
        for k in ("ruc", "categoria", "observaciones"):
            p.setdefault(k, "")


# --- Datos del módulo de órdenes de servicio: Karkajadas como proveedor propio, eventos, fichas y pedido a bodega
EMPRESA_PROPIA = "Karkajadas Group"
SERVICIOS_PROPIOS = [("Jenga gigante de madera", 60.0), ("Cuatro en raya gigante", 50.0), ("Rompecabezas gigante", 75.0)]
ss.setdefault("fichas", {})
ss.setdefault("eventos", {})
ss.setdefault("hojas", {})        # checklist del bodeguero: {cotización: {servicio: [piezas]}}
ss.setdefault("plantillas", {})   # piezas por servicio (por unidad), para no escribirlas otra vez

def asegurar_proveedor_propio():
    if not any(p["proveedor"] == EMPRESA_PROPIA for p in ss.proveedores):
        ss.proveedores.append({"id": f"PRV-{len(ss.proveedores) + 1:03d}", "proveedor": EMPRESA_PROPIA, "ruc": "", "categoria": "Propio",
                               "ciudad": "Quito", "observaciones": "Servicios propios (salen de bodega)", "contactos": [], "direcciones": [], "cuentas": []})
    for nombre, precio in SERVICIOS_PROPIOS:
        if not any(r["proveedor"] == EMPRESA_PROPIA and r["servicio"] == nombre for r in ss.proveedores_catalogo):
            ss.proveedores_catalogo.append({"servicio": nombre, "proveedor": EMPRESA_PROPIA, "categoria": "Propio", "ciudad": "Quito",
                                            "precio_base": precio, "iva": 0.15, "descripcion": "Servicio propio"})


migrar_datos()
asegurar_proveedor_propio()


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def ir(destino, **estado):
    """Callback de navegación: cambia de vista y, opcionalmente, fija otras variables de sesión."""
    ss.nav_menu = destino
    ss.update(estado)
    ss.cot_sid += 1
    ss.cot_base = None


def _k(nombre):
    """Clave de un campo del formulario de cotización (cambia con cada apertura del módulo)."""
    return f"cot_{nombre}_{ss.cot_sid}"


def estado_formulario():
    """Foto de lo que hay en el formulario (campos + servicios)."""
    return (ss.get(_k("cod")), ss.get(_k("ev")), ss.get(_k("cli")), str(ss.get(_k("fec"))), ss.get(_k("est")), ss.get(_k("inv")),
            json.dumps(ss.items_cot, sort_keys=True, default=str))


def hay_cambios():
    return ss.nav_menu == "Nueva cotización" and ss.cot_base is not None and estado_formulario() != ss.cot_base


def navegar(destino):
    """Callback de menú: si estás en una cotización con cambios sin guardar, pide confirmación antes de salir."""
    if hay_cambios():
        ss.confirmar_salida = True
        ss.destino_salida = destino
    else:
        ir(destino)


@st.dialog("¿Salir sin guardar los cambios?")
def dialogo_salida():
    st.write("Hiciste cambios en esta cotización que todavía no se guardaron. Si sales ahora, se perderán.")
    c1, c2 = st.columns(2)
    if c1.button("Salir sin guardar", key="exit_confirm", use_container_width=True):
        ir(ss.pop("destino_salida", "Panel de control"))
        st.rerun()
    if c2.button("Cancelar", key="exit_cancel", use_container_width=True):
        ss.pop("destino_salida", None)
        st.rerun()


@st.dialog("Editar servicio de la cotización", width="large")
def dialogo_editar(idx):
    it = ss.items_cot[idx]
    nombres = sorted({p["proveedor"] for p in ss.proveedores} | {it["proveedor"]})
    c1, c2 = st.columns(2)
    prov = c1.selectbox("Proveedor", nombres, index=nombres.index(it["proveedor"]), key=f"ed_prov_{idx}")
    serv = c2.text_input("Servicio", it["servicio"], key=f"ed_serv_{idx}")
    c3, c4, c5 = st.columns(3)
    ciudad = selector_ciudad(c3, "Ciudad", f"ed_ciu_{idx}", it["ciudad"])
    try:
        f0 = datetime.strptime(str(it["fecha"])[:10], "%Y-%m-%d")
    except ValueError:
        f0 = datetime.now()
    fecha = c4.date_input("Fecha de servicio", f0, key=f"ed_fec_{idx}")
    cant = c5.number_input("Cantidad", min_value=1, value=int(it["cantidad"]), step=1, key=f"ed_can_{idx}")
    c6, c7, c8 = st.columns(3)
    costo = c6.number_input("Costo unit. ($)", value=float(it["costo"]), format="%.2f", key=f"ed_cos_{idx}")
    ivas = [0.0, 0.15] if it["iva_prov"] in (0.0, 0.15) else [0.0, 0.15, it["iva_prov"]]
    iva = c7.selectbox("IVA prov.", ivas, index=ivas.index(it["iva_prov"]), format_func=lambda x: f"{int(x * 100)}%", key=f"ed_iva_{idx}")
    fee = c8.number_input("Margen (%)", value=float(it["fee_pct"]), step=5.0, format="%.2f", key=f"ed_fee_{idx}")
    base = cant * costo * (1 + iva)
    st.caption(f"Con estos valores: costo \\${base:,.2f} · margen \\${base * fee / 100:,.2f} · precio de venta \\${base * (1 + fee / 100):,.2f}")
    b1, b2 = st.columns(2)
    if b1.button("Guardar cambios", type="primary", use_container_width=True, key=f"ed_ok_{idx}"):
        if not serv.strip():
            st.error("El servicio no puede quedar vacío.")
        else:
            it.update({"proveedor": prov, "servicio": serv.strip(), "ciudad": ciudad, "fecha": fecha.strftime("%Y-%m-%d"),
                       "cantidad": int(cant), "costo": float(costo), "iva_prov": float(iva), "fee_pct": float(fee)})
            st.rerun()
    if b2.button("Cancelar", use_container_width=True, key=f"ed_no_{idx}"):
        st.rerun()


def encabezado_modulo(clave, html, unsafe_allow_html=True):
    """Encabezado de cada módulo: botón para volver al panel de control + el título."""
    c_vol, c_tit = st.columns([2.1, 8], vertical_alignment="center")
    c_vol.button("← Panel de control", key=f"volver_{clave}", on_click=navegar, args=("Panel de control",), help="Volver al panel de control")
    c_tit.markdown(html, unsafe_allow_html=True)


def encabezado_estandar(clave, titulo, subtitulo="", volver=True, derecha=None):
    """Encabezado igual en todos los módulos: [← Panel de control] título y subtítulo a la izquierda, acciones o dato a la derecha."""
    with st.container(border=True, key=f"card_h_{clave}"):
        if volver:
            c_vol, c_tit, c_der = st.columns([1.55, 3.6, 3], vertical_alignment="center")
            c_vol.button("← Panel de control", key=f"volver_{clave}", on_click=navegar, args=("Panel de control",), help="Volver al panel de control", use_container_width=True)
        else:
            c_tit, c_der = st.columns([1.6, 3.6], vertical_alignment="center")
        c_tit.markdown(f"<div class='hd-titulo'>{titulo}</div>" + (f"<div class='hd-sub'>{subtitulo}</div>" if subtitulo else ""), unsafe_allow_html=True)
        if derecha:
            with c_der:
                derecha()


def excel_cotizaciones(cots):
    """Libro de Excel con tres hojas: cotizaciones, detalle de ítems y resumen por estado."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    azul, gris = "1E3A8A", "F1F5F9"
    borde = Border(bottom=Side(style="thin", color="DCE3EC"))
    dinero_fmt = '"$"#,##0.00'

    def hoja(ws, titulos, filas, anchos, cols_dinero=(), cols_fecha=()):
        ws.append(titulos)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=azul)
            c.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        ws.row_dimensions[1].height = 26
        for f in filas:
            ws.append(f)
        for fila in ws.iter_rows(min_row=2):
            for c in fila:
                c.border = borde
                if c.column in cols_dinero:
                    c.number_format = dinero_fmt
                if c.column in cols_fecha:
                    c.number_format = "dd/mm/yyyy"
                    c.alignment = Alignment(horizontal="center")
        for i, a in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(i)].width = a
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    def f_(txt):
        try:
            return datetime.strptime(str(txt)[:10], "%Y-%m-%d")
        except ValueError:
            return str(txt)

    ws1 = wb.active
    ws1.title = "Cotizaciones"
    hoja(ws1, ["Código", "Evento", "Cliente", "Fecha", "Estado", "Servicios", "Total con IVA ($)"],
         [[c["codigo"], c["evento"], c["cliente"], f_(c["fecha"]), c["estado"], len(c["items"]), round(c["total"], 2)] for c in cots],
         [18, 30, 36, 13, 12, 11, 18], cols_dinero=(7,), cols_fecha=(4,))
    n = len(cots) + 1
    ws1.append([])
    ws1.append(["Total", "", "", "", "", sum(len(c["items"]) for c in cots), round(sum(c["total"] for c in cots), 2)])
    for c in ws1[n + 2]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor=gris)
    ws1.cell(n + 2, 7).number_format = dinero_fmt

    ws2 = wb.create_sheet("Detalle de ítems")
    filas = []
    for c in cots:
        for it in c["items"]:
            base, fee, venta = calcular_linea(it)
            filas.append([c["codigo"], c["evento"], c["cliente"], c["estado"], it["servicio"], it["proveedor"], it["ciudad"], f_(it["fecha"]),
                          it["cantidad"], it["costo"], it["iva_prov"], it["fee_pct"] / 100.0, round(base, 2), round(fee, 2), round(venta, 2)])
    hoja(ws2, ["Código", "Evento", "Cliente", "Estado", "Servicio", "Proveedor", "Ciudad", "Fecha", "Cantidad", "Costo unit. ($)",
               "IVA proveedor", "Margen", "Costo con IVA ($)", "Margen ($)", "Precio de venta ($)"],
         filas, [18, 26, 32, 12, 28, 28, 14, 13, 10, 14, 12, 10, 16, 13, 18], cols_dinero=(10, 13, 14, 15), cols_fecha=(8,))
    for fila in ws2.iter_rows(min_row=2):
        fila[10].number_format = "0%"
        fila[11].number_format = "0%"

    ws3 = wb.create_sheet("Resumen por estado")
    ws3.append(["Estado", "Cotizaciones", "Total con IVA ($)", "% del total"])
    gran = sum(c["total"] for c in cots)
    for e in ESTADOS:   # valores calculados aquí (no fórmulas): se ven también en la vista protegida de Excel
        de = [c for c in cots if c["estado"] == e]
        tot_e = round(sum(c["total"] for c in de), 2)
        ws3.append([e, len(de), tot_e, (tot_e / gran) if gran else 0])
    ws3.append(["Total", len(cots), round(gran, 2), 1 if gran else 0])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=azul)
        c.alignment = Alignment(horizontal="center", vertical="center")
    for fila in ws3.iter_rows(min_row=2):
        fila[2].number_format = dinero_fmt
        fila[3].number_format = "0%"
        for c in fila:
            c.border = borde
    for c in ws3[ws3.max_row]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor=gris)
    for i, a in enumerate([16, 15, 20, 12], 1):
        ws3.column_dimensions[get_column_letter(i)].width = a

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def normalizar_multi(clave, todo):
    """Filtro múltiple con una opción "todo": al elegirla se desmarcan las demás; al elegir otra, se desmarca "todo"; si queda vacío, vuelve a "todo"."""
    val = list(ss.get(clave, []))
    antes = ss.get(clave + "_antes", [todo])
    if not val:
        val = [todo]
    elif todo in val and len(val) > 1:
        val = [v for v in val if v != todo] if todo in antes else [todo]
    ss[clave] = val
    ss[clave + "_antes"] = val


def fijar_estado(estado):
    """Selecciona la tarjeta; si ya estaba seleccionada, vuelve a 'Todas'."""
    ss.filtro_estado_tabla = "Todas" if ss.filtro_estado_tabla == estado else estado


def limpiar_filtros():
    """Borra TODAS las selecciones: tarjeta activa, filtros globales y buscador."""
    ss.filtro_estado_tabla = "Todas"
    ss.update(SIN_FILTRO)


def calcular_linea(item):
    """Devuelve (costo con IVA proveedor, margen en $, precio de venta) de una línea."""
    base = item["cantidad"] * item["costo"] * (1 + item["iva_prov"])
    fee = base * item["fee_pct"] / 100.0
    return base, fee, base + fee


def total_cliente(items):
    return sum(calcular_linea(i)[2] for i in items) * (1 + IVA_CLIENTE)


def siguiente_codigo():
    n = max((int(c["codigo"][-3:]) for c in ss.cotizaciones_guardadas if c["codigo"][-3:].isdigit()), default=0) + 1
    return f"KG-{datetime.now():%Y%m%d}-{n:03d}"


def guardar_cotizacion(activa, codigo, evento, cliente, fecha, estado, total, invitados=0):
    """Valida y guarda (o reemplaza en su misma posición) la cotización. Devuelve la cotización guardada o None."""
    lista = ss.cotizaciones_guardadas
    if not evento.strip():
        st.error("Ingrese el nombre del evento.")
    elif cliente == NUEVO_CLIENTE:
        st.error("Registre el cliente.")
    elif not ss.items_cot:
        st.error("Agregue al menos un servicio.")
    elif any(c["codigo"] == codigo and not (activa and activa["codigo"] == codigo) for c in lista):
        st.error("Ya existe una cotización con esa referencia.")
    else:
        nueva = {"codigo": codigo, "evento": evento, "cliente": cliente, "fecha": str(fecha),
                 "estado": estado, "total": total, "invitados": int(invitados), "items": [dict(i) for i in ss.items_cot]}
        pos = next((i for i, c in enumerate(lista) if activa and c["codigo"] == activa["codigo"]), None)
        if pos is None:
            lista.append(nueva)
        else:
            lista[pos] = nueva
        ss.cotizacion_activa = nueva          # los siguientes guardados reemplazan esta misma cotización
        ss.cot_base = estado_formulario()     # formulario "limpio": ya no hay cambios pendientes
        return nueva
    return None


def fmt_fecha(iso):
    try:
        return datetime.strptime(str(iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(iso)


def generar_pdf(cot, cliente):
    """PDF de la cotización para el cliente. Incluye los datos del evento y del cliente y, por cada servicio,
    proveedor, servicio, fecha, ciudad, cantidad y subtotal. NO incluye costo unitario, IVA del proveedor,
    margen % ni margen $, ni los totales internos (costos operativos / rentabilidad). Requiere reportlab."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    AZUL, VERDE = colors.HexColor("#1E3A8A"), colors.HexColor("#059669")
    TINTA, GRIS = colors.HexColor("#0F172A"), colors.HexColor("#64748B")
    LINEA, FONDO = colors.HexColor("#CBD5E1"), colors.HexColor("#F1F5F9")

    def est(size, bold=False, color=TINTA, align=0, leading=None):
        return ParagraphStyle("x", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                              leading=leading or size * 1.3, textColor=color, alignment=align)

    def P(texto, **kw):
        return Paragraph(escape(str(texto)), est(**kw))

    cliente = cliente or {}
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2.2 * cm,
                            title=f"Cotización {cot['codigo']}", author="Karkajadas Group")
    ancho = doc.width
    historia = []

    # Encabezado
    cab = Table([[P("Karkajadas Group", size=22, bold=True, color=AZUL),
                  [P("COTIZACIÓN", size=9, bold=True, color=GRIS, align=TA_RIGHT),
                   P(cot["codigo"], size=15, bold=True, align=TA_RIGHT)]]], colWidths=[ancho * 0.55, ancho * 0.45])
    cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, 0), 2.5, VERDE),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    de = datos_empresa()
    linea_emp = " · ".join(x for x in (f"RUC {de['ruc']}" if de.get("ruc") else "", f"Tel. {de['telefono']}" if de.get("telefono") else "",
                                       de.get("correo", ""), de.get("web", ""), de.get("direccion", "")) if x)
    historia += [cab, Spacer(1, 4), P(linea_emp, size=8, color=GRIS), Spacer(1, 12)]

    # Datos del evento y del cliente
    def ficha(filas):
        filas = [(a, b) for a, b in filas if str(b).strip()]
        t = Table([[P(a.upper(), size=7, bold=True, color=GRIS), P(b, size=9.5)] for a, b in filas], colWidths=[3.0 * cm, None])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return t

    dias = cliente.get("dias_credito")
    evento = [("Referencia", cot["codigo"]), ("Evento", cot["evento"]), ("Fecha del evento", fmt_fecha(cot["fecha"])), ("Estado", cot["estado"])]
    datos_cli = [("Empresa", cot["cliente"]), ("RUC", cliente.get("ruc", "")), ("Ciudad", cliente.get("ciudad", "")),
                 ("Dirección", cliente.get("direccion", "")), ("Contacto", cliente.get("contacto", "")), ("Correo", cliente.get("email", "")),
                 ("Teléfono", cliente.get("telefono", "")), ("Sitio web", cliente.get("web", "")),
                 ("Pago", "Contado" if dias == 0 else f"{dias} días de crédito" if dias else "")]
    w = (ancho - 0.6 * cm) / 2
    info = Table([[P("DATOS DEL EVENTO", size=8.5, bold=True, color=AZUL), "", P("DATOS DEL CLIENTE", size=8.5, bold=True, color=AZUL)],
                  [ficha(evento), "", ficha(datos_cli)]], colWidths=[w, 0.6 * cm, w])
    info.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), FONDO), ("BACKGROUND", (2, 0), (2, -1), FONDO),
                              ("BOX", (0, 0), (0, -1), 0.6, LINEA), ("BOX", (2, 0), (2, -1), 0.6, LINEA),
                              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, -1), 10), ("LEFTPADDING", (2, 0), (2, -1), 10),
                              ("RIGHTPADDING", (0, 0), (0, -1), 8), ("RIGHTPADDING", (2, 0), (2, -1), 8),
                              ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, -1), (-1, -1), 8)]))
    historia += [info, Spacer(1, 16), P("SERVICIOS", size=10, bold=True, color=AZUL), Spacer(1, 5)]

    # Servicios (sin costo unitario, IVA del proveedor, margen % ni margen $)
    cols = [0.8, 5.6, 3.0, 2.6, 1.5, 3.5]
    filas = [[P(t, size=8, bold=True, color=colors.white, align=a) for t, a in
              [("#", TA_CENTER), ("SERVICIO", 0), ("FECHA", 0), ("CIUDAD", 0), ("CANT.", TA_RIGHT), ("SUBTOTAL", TA_RIGHT)]]]
    subtotal = 0.0
    for n, it in enumerate(cot["items"], 1):
        p_ven = calcular_linea(it)[2]
        subtotal += p_ven
        filas.append([P(n, size=9, align=TA_CENTER), P(it["servicio"], size=9, bold=True),
                      P(fmt_fecha(it["fecha"]), size=9), P(it["ciudad"], size=9), P(it["cantidad"], size=9, align=TA_RIGHT),
                      P(f"${p_ven:,.2f}", size=9, bold=True, align=TA_RIGHT)])
    tabla = Table(filas, colWidths=[c * cm for c in cols], repeatRows=1)
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
                               ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINEA), ("BOX", (0, 0), (-1, -1), 0.6, LINEA),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    historia += [tabla, Spacer(1, 12)]

    # Totales
    iva = subtotal * IVA_CLIENTE
    tot = Table([[P("Subtotal", size=9.5, color=GRIS), P(f"${subtotal:,.2f}", size=9.5, align=TA_RIGHT)],
                 [P(f"IVA {int(IVA_CLIENTE * 100)}%", size=9.5, color=GRIS), P(f"${iva:,.2f}", size=9.5, align=TA_RIGHT)],
                 [P("TOTAL INVERSIÓN", size=11, bold=True, color=AZUL), P(f"${subtotal + iva:,.2f}", size=13, bold=True, color=AZUL, align=TA_RIGHT)]],
                colWidths=[4.3 * cm, 3.2 * cm], hAlign="RIGHT")
    tot.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FONDO), ("BOX", (0, 0), (-1, -1), 0.6, LINEA), ("LINEABOVE", (0, 2), (-1, 2), 1, LINEA),
                             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                             ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    historia += [tot, Spacer(1, 14), P("Valores expresados en dólares americanos (USD).", size=8, color=GRIS)]
    cond = []
    if de.get("validez_dias"):
        cond.append(f"Validez de la oferta: {de['validez_dias']} días.")
    if str(de.get("forma_pago", "")).strip():
        cond.append(f"Forma de pago: {de['forma_pago'].strip()}")
    if str(de.get("notas_comerciales", "")).strip():
        cond.append(de["notas_comerciales"].strip())
    for c in de.get("cuentas", []):
        cond.append(f"Cuenta {c.get('tipo', '').lower()} {c.get('banco', '')} N.º {c.get('numero', '')} - {c.get('titular', '')}")
    if cond:
        historia += [Spacer(1, 10), P("CONDICIONES COMERCIALES", size=8.5, bold=True, color=AZUL), Spacer(1, 3)]
        historia += [P(x, size=8.5, color=GRIS) for x in cond]

    def pie(canvas, d):
        canvas.saveState()
        canvas.setStrokeColor(LINEA); canvas.setLineWidth(0.5)
        canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        canvas.setFont("Helvetica", 8); canvas.setFillColor(GRIS)
        canvas.drawString(2 * cm, 1.1 * cm, f"Karkajadas Group  ·  Cotización {cot['codigo']}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Página {d.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()


# =============================================================================
# ÓRDENES DE SERVICIO: datos de la empresa, formatos y documentos PDF
# =============================================================================
EMPRESA = "Karkajadas Group"
EMPRESA_DATOS = {"web": "www.karkajadasgroup.com", "ruc": "1713272845001", "telefono": "0998526514 / 02 3076303",
                 "correo": "edwin.garcia@karkajadasgroup.com", "direccion": "La Victoria Baja, Calle D, Lote 50 B"}
LOGO_B64 = "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"
ss.setdefault("empresa", {**EMPRESA_DATOS, "razon_social": "", "representante": "", "cargo_representante": "", "ciudad": "Quito",
                          "logo_b64": "", "cuentas": [], "validez_dias": 15, "forma_pago": "", "notas_comerciales": ""})


def datos_empresa():
    """Datos de la empresa que salen en el encabezado de los documentos (se editan en Perfil de la empresa)."""
    return ss.empresa


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(d):
    """'miércoles, 30 de septiembre de 2026' a partir de una fecha o un texto AAAA-MM-DD."""
    if not hasattr(d, "year"):
        try:
            d = datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except ValueError:
            return str(d)
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}"


def dinero(x):
    try:
        v = float(str(x).replace("$", "").replace(" ", "").replace(",", "."))  if isinstance(x, str) else float(x)
    except ValueError:
        return str(x)
    return "$" + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def a_numero(x):
    try:
        return float(str(x).replace("$", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return 0.0


def _logo(ancho_cm):
    import base64
    from io import BytesIO
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Image
    datos = base64.b64decode(ss.empresa.get("logo_b64") or LOGO_B64)
    w, h = ImageReader(BytesIO(datos)).getSize()
    return Image(BytesIO(datos), width=ancho_cm * cm, height=ancho_cm * cm * h / w)


def pdf_documento(titulo, ref, subtitulo, bloques):
    """PDF con el estilo del ERP. bloques: ("info", [(etiqueta, valor)]) | ("seccion", texto) | ("nota", texto) |
    ("tabla", titulos, filas, anchos_relativos, columnas_casilla). En columnas de casilla, True = marcada."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    AZUL, VERDE = colors.HexColor("#1E3A8A"), colors.HexColor("#059669")
    TINTA, GRIS = colors.HexColor("#0F172A"), colors.HexColor("#64748B")
    LINEA, FONDO = colors.HexColor("#CBD5E1"), colors.HexColor("#F1F5F9")

    def P(texto, size=9.5, bold=False, color=TINTA, align=0):
        txt = escape(str(texto)).replace("\n", "<br/>")
        return Paragraph(txt, ParagraphStyle("x", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                                             leading=size * 1.3, textColor=color, alignment=align))

    def casilla(marcada):
        caja = Table([[P("X" if marcada else "", 8, True, colors.white, 1)]], colWidths=[0.5 * cm], rowHeights=[0.5 * cm])
        caja.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, VERDE if marcada else GRIS),
                                  ("BACKGROUND", (0, 0), (-1, -1), VERDE if marcada else colors.white),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                  ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        return caja

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.4 * cm,
                            bottomMargin=2.0 * cm, title=titulo, author=EMPRESA)
    ancho = doc.width
    d = datos_empresa()
    lineas_emp = [x for x in (f"RUC {d['ruc']}" if d.get("ruc") else "", f"Tel. {d['telefono']}" if d.get("telefono") else "",
                              d.get("correo", ""), d.get("web", ""), d.get("direccion", "")) if x]
    izq = [_logo(3.4), Spacer(1, 3)] + [P(x, 7.5, False, GRIS) for x in lineas_emp]
    cab = Table([[izq, [P(titulo.upper(), 9, True, GRIS, TA_RIGHT), P(ref, 15, True, TINTA, TA_RIGHT)]]], colWidths=[ancho * 0.55, ancho * 0.45])
    cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, 0), 2.5, VERDE),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    h = [cab]
    if subtitulo:
        h += [Spacer(1, 6), P(subtitulo, 10, False, GRIS)]
    h += [Spacer(1, 12)]

    for b in bloques:
        if b[0] == "info":
            filas = [(a, v) for a, v in b[1] if str(v).strip()]
            t = Table([[P(a.upper(), 7, True, GRIS), P(v, 9.5)] for a, v in filas], colWidths=[4.0 * cm, None])
            t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
            h += [t, Spacer(1, 12)]
        elif b[0] == "seccion":
            h += [Spacer(1, 4), P(b[1], 11, True, AZUL), Spacer(1, 4)]
        elif b[0] == "nota":
            h += [Spacer(1, 6), P(b[1], 8, False, GRIS)]
        elif b[0] == "tabla":
            _, titulos, filas, rel, cols_cas = b
            datos = [[P(x, 7.5, True, colors.white) for x in titulos]]
            for f in filas:
                datos.append([casilla(v) if i in cols_cas else P(v, 9) for i, v in enumerate(f)])
            tot = sum(rel)
            t = Table(datos, colWidths=[ancho * r / tot for r in rel], repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
                                   ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINEA),
                                   ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
            h += [t, Spacer(1, 10)]

    def pie(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(1.8 * cm, 1.0 * cm, f"{EMPRESA} · {ref}")
        canvas.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, f"Página {d.page}")
        canvas.restoreState()

    doc.build(h, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()


def agrupar_por_proveedor(cot):
    grupos = {}
    for it in cot["items"]:
        grupos.setdefault(it["proveedor"], []).append(it)
    return dict(sorted(grupos.items(), key=lambda kv: (kv[0] != EMPRESA, kv[0].lower())))   # Karkajadas primero


def cliente_de(cot):
    return next((c for c in ss.clientes_catalogo if c["empresa"] == cot["cliente"]), {})


def proveedor_de(nombre):
    return next((p for p in ss.proveedores if p["proveedor"] == nombre), {})


OBS_BASE = ("El equipo de Karkajadas Group estará en constante coordinación con el cliente y el proveedor.\n\n"
            "El personal debe llevar los implementos de seguridad industrial básicos para el montaje.")


def evento_inicial(cot):
    """Datos del evento: se llenan una sola vez y alimentan todas las fichas y el pedido a bodega."""
    cli = cliente_de(cot)
    dirs, con = cli.get("direcciones", []), cli.get("contactos", [])
    return {
        "fecha_entrega": min(i["fecha"] for i in cot["items"]), "invitados": str(cot.get("invitados", "") or ""), "lugar": "",
        "direccion": dirs[0]["direccion"] if dirs else "", "ubicacion": "Pendiente", "horario": "", "tematica": cot["evento"],
        "recibe": con[0]["nombre"] if con else "", "telefono_recibe": con[0]["telefono"] if con else "",
        "montaje": "Sí", "hora_montaje": "", "desmontaje": "", "documento": "Cédula de identidad", "otros": "No aplica",
        "observacion": OBS_BASE,
    }


def proveedor_inicial(cot, prov, items):
    """Datos propios de cada proveedor en su ficha: servicio requerido, valores y condiciones."""
    cli = cliente_de(cot)
    lineas = []
    for i in items:
        desc = next((r["descripcion"] for r in ss.proveedores_catalogo if r["proveedor"] == prov and r["servicio"] == i["servicio"]), "")
        desc = "" if desc in ("", "Estándar", "Manual") else f"\n{desc}"
        lineas.append(f"{i['servicio']} - {i['ciudad']} - {fecha_larga(i['fecha'])}:\n{i['cantidad']} x {i['servicio']}{desc}")
    return {"servicio": "\n\n".join(lineas), "total": dinero(sum(calcular_linea(i)[0] for i in items)), "abono": dinero(0),
            "garantia": dinero(0), "transporte": "Incluido",
            "pago": f"A {cli['dias_credito']} días crédito" if cli.get("dias_credito") else "", "factura": "Factura"}


def texto_inclusion(ev, alimentacion=True):
    """Resumen de inclusión del evento para los documentos (solo cantidades, sin nombres). La alimentación puede omitirse por proveedor."""
    inc = ev.get("inclusion") or {}

    def lista(campos):
        return [f"{inc[c]} {t}" for c, t in campos if inc.get(c)]
    acc = lista([("movilidad", "con movilidad reducida o en silla de ruedas"), ("visual", "con discapacidad visual"),
                 ("auditiva", "con discapacidad auditiva"), ("otra_acc", "con otra necesidad de accesibilidad")])
    if str(inc.get("nota_acc", "")).strip():
        acc.append(inc["nota_acc"].strip())
    ali = lista([("vegetarianos", "vegetariano(s)"), ("veganos", "vegano(s)"), ("sin_gluten", "sin gluten"), ("alergias", "con alergia alimentaria")])
    if str(inc.get("nota_ali", "")).strip():
        ali.append(inc["nota_ali"].strip())
    partes = []
    if acc:
        partes.append("Accesibilidad: " + "; ".join(acc) + ".")
    if ali and alimentacion:
        partes.append("Alimentación: " + "; ".join(ali) + ".")
    if partes:
        return "\n".join(partes)
    return "No aplica a este servicio." if ali else "Sin necesidades especiales reportadas."


def pdf_ficha(cot, prov, ev, fp):
    """Ficha de contratación con el formato de la empresa (rosado, como el Excel)."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    ROSA, ROSA_CLARO, NAVY = colors.HexColor("#D66BCB"), colors.HexColor("#F3D1EF"), colors.HexColor("#0F2740")

    def P(t, size=10, bold=False, color=colors.black, align=0):
        return Paragraph(escape(str(t)).replace("\n", "<br/>"), ParagraphStyle("x", fontName="Helvetica-Bold" if bold else "Helvetica",
                                                                              fontSize=size, leading=size * 1.3, textColor=color, alignment=align))
    saldo = a_numero(fp["total"]) - a_numero(fp["abono"])
    nombre_cli = f"{EMPRESA.upper()} - {cot['cliente'].upper()}"
    filas = [
        ("FECHA DE EMISIÓN", fecha_larga(datetime.now())), ("CLIENTE:", nombre_cli),
        ("FECHA DE ENTREGA DEL SERVICIO", fecha_larga(ev["fecha_entrega"])), ("CANTIDAD DE INVITADOS:", ev["invitados"]),
        ("LUGAR", ev["lugar"] or ev["direccion"]), ("HORARIO:", ev["horario"]), ("TEMÁTICA:", ev["tematica"]), ("PROVEEDOR:", prov),
        ("SERVICIO REQUERIDO:", fp["servicio"]), ("OBSERVACIÓN", ev["observacion"]), ("DIRECCIÓN:", ev["direccion"]),
        ("UBICACIÓN:", ev["ubicacion"]), ("REFERENCIA:", ev.get("referencia", "")), ("NOVEDADES:", ev.get("novedades", "")), ("MAPA:", ev.get("enlace", "")), ("TOTAL:", dinero(fp["total"])), ("ABONO:", dinero(fp["abono"])),
        ("SALDO PENDIENTE:", dinero(saldo)), ("GARANTÍA", dinero(fp["garantia"])), ("TRANSPORTE", fp["transporte"]),
        ("FORMA DE PAGO:", fp["pago"]), ("FACTURA:", fp["factura"]), ("PERSONA QUE RECIBE", ev["recibe"]),
        ("TELEFONO PERSONA QUE RECIBE", ev["telefono_recibe"]), ("MONTAJE", ev["montaje"]), ("HORA DEL MONTAJE", ev["hora_montaje"]),
        ("DESMONTAJE", ev["desmontaje"]), ("DOCUMENTO REQUERIDO PARA EL INGRESO", ev["documento"]), ("OTROS", ev["otros"]),
        ("INCLUSIÓN Y ACCESIBILIDAD:", texto_inclusion(ev, fp.get("alimentacion", True))),
    ]
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.0 * cm, bottomMargin=0.8 * cm,
                            title=f"Contratación {cot['codigo']} - {prov}", author=EMPRESA)
    w = doc.width
    d = datos_empresa()
    caja = Table([[[P(d["web"], 9.5), P(f"Ruc: {d['ruc']}", 9.5), P(f"Telf.: {d['telefono']}", 9.5),
                    P(f"Correo: {d['correo']}", 9.5), P(f"Dirección: {d['direccion']}", 9.5)]]], colWidths=[w * 0.58],
                 style=[("BACKGROUND", (0, 0), (-1, -1), ROSA), ("BOX", (0, 0), (-1, -1), 2, colors.black),
                        ("ROUNDEDCORNERS", [10, 10, 10, 10]), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])
    cab = Table([[_logo(4.6), caja]], colWidths=[w * 0.38, w * 0.62], style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (0, 0), 0)])
    titulo = Table([[P("CONTRATACIÓN DEL SERVICIO", 14, True, colors.white, 1)]], colWidths=[w],
                   style=[("BACKGROUND", (0, 0), (-1, -1), ROSA), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)])
    barra = Table([[""]], colWidths=[w], rowHeights=[0.45 * cm], style=[("BACKGROUND", (0, 0), (-1, -1), colors.black)])
    datos = [[P("INFORMACIÓN", 12, True, colors.white, 1), P("DETALLE", 12, True, colors.white, 1)]]
    for k, v in filas:
        if k in ("MAPA:", "REFERENCIA:", "NOVEDADES:") and not str(v).strip():
            continue
        txt = v if str(v).strip() else " "
        color = colors.red if k == "SALDO PENDIENTE:" and saldo < 0 else colors.black
        datos.append([P(k, 9), P(txt, 9, color=color)])
    tabla = Table(datos, colWidths=[w * 0.40, w * 0.60], repeatRows=1)
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), ROSA), ("BACKGROUND", (0, 1), (0, -1), ROSA), ("BACKGROUND", (1, 1), (1, -1), ROSA_CLARO),
                               ("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("TOPPADDING", (0, 0), (-1, -1), 1.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8)]))
    aviso = Table([[P("SU SERVICIO ES CONTRATADO POR KARKAJADAS GROUP, USTED NO ESTÁ AUTORIZADO A DAR NINGUNA INFORMACIÓN DE PRECIOS, "
                      "NÚMEROS DE TELÉFONO, CORREOS ELECTRÓNICOS, NINGUNA INFORMACIÓN REFERENTE A SU SERVICIO.", 10, False, colors.white)]],
                  colWidths=[w], style=[("BACKGROUND", (0, 0), (-1, -1), NAVY), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                                        ("LEFTPADDING", (0, 0), (-1, -1), 8)])
    doc.build([cab, Spacer(1, 6), titulo, barra, tabla, aviso])
    return buf.getvalue()


def pdf_orden(cot, prov, items):
    p = proveedor_de(prov)
    con = p.get("contactos", [])
    filas = [[False, i["servicio"], fecha_larga(i["fecha"]), i["ciudad"], str(i["cantidad"]), ""] for i in items]
    bloques = [("info", [("Proveedor", prov), ("Contacto", f"{con[0]['nombre']} - {con[0]['telefono']}" if con else ""),
                         ("Cotización aprobada", cot["codigo"]), ("Evento", cot["evento"]), ("Cliente", cot["cliente"]),
                         ("Fecha de emisión", fecha_larga(datetime.now()))]
                        + ([("Inclusión y accesibilidad", texto_inclusion(ss.eventos[cot["codigo"]]))] if cot["codigo"] in ss.eventos else [])),
               ("seccion", "Servicios a contratar"),
               ("tabla", ["", "SERVICIO", "FECHA", "CIUDAD", "CANT.", "OBSERVACIONES"], filas, [0.5, 3.6, 2.8, 1.5, 0.9, 2.4], {0}),
               ("nota", "Marque cada servicio al confirmarlo con el proveedor.")]
    return pdf_documento("Orden de servicios", cot["codigo"], None, bloques)


def _info_evento(cot, ev):
    return [("Cotización aprobada", cot["codigo"]), ("Evento", cot["evento"]), ("Cliente", cot["cliente"]),
            ("Fecha de entrega", fecha_larga(ev["fecha_entrega"])), ("Lugar", ev["lugar"]), ("Dirección", ev["direccion"]), ("Referencia", ev.get("referencia", "")), ("Mapa", ev.get("enlace", "")), ("Novedades", ev.get("novedades", "")),
            ("Horario", ev["horario"]), ("Montaje", f"{ev['montaje']} - {ev['hora_montaje']}".strip(" -")), ("Desmontaje", ev["desmontaje"]),
            ("Recibe", f"{ev['recibe']} - {ev['telefono_recibe']}".strip(" -")),
            ("Inclusión y accesibilidad", texto_inclusion(ev)), ("Observación", ev["observacion"])]


def pdf_pedido_bodega(cot, items, ev):
    """Pedido a bodega generado desde la cotización: solo servicios propios, sin proveedores ni precios."""
    filas = [[i["servicio"], str(i["cantidad"]), fmt_fecha(i["fecha"]), i["ciudad"], ""] for i in items]
    bloques = [("info", _info_evento(cot, ev)), ("seccion", "Servicios a despachar"),
               ("tabla", ["SERVICIO", "CANT.", "FECHA", "CIUDAD", "OBSERVACIONES"], filas, [4.2, 1.0, 1.8, 1.8, 2.8], set()),
               ("nota", "El bodeguero detalla las piezas de cada servicio en su checklist.")]
    return pdf_documento("Pedido a bodega", cot["codigo"], None, bloques)


def pdf_hoja_bodega(cot, items, ev):
    """Checklist detallado del bodeguero: piezas de cada servicio, con salida y retorno."""
    bloques = [("info", _info_evento(cot, ev))]
    for it in items:
        bloques.append(("seccion", f"{it['servicio']} - {it['cantidad']} unidad(es) - {fmt_fecha(it['fecha'])}"))
        hoja = ss.hojas.get(cot["codigo"], {}).get(it["servicio"], [])
        if not hoja:
            bloques.append(("nota", "El bodeguero aún no ha detallado las piezas de este servicio."))
            continue
        filas = [[p["pieza"], str(p["cantidad"]), bool(p["salio"]), bool(p["regreso"]), p.get("obs", "")] for p in hoja]
        bloques.append(("tabla", ["PIEZA", "CANT.", "SALIÓ", "REGRESÓ", "OBSERVACIONES"], filas, [3.8, 0.9, 1.0, 1.1, 3.2], {2, 3}))
    return pdf_documento("Checklist de bodega", cot["codigo"], "Revisión de piezas a la salida y al regreso", bloques)


def firma_items(items):
    """Huella de los servicios de una cotización: sirve para avisar si cambió después de guardar una ficha."""
    return [[i["servicio"], i["cantidad"], i["fecha"], i["costo"]] for i in items]


def aprobadas_con(propio):
    """Cotizaciones aprobadas que tienen servicios propios (bodega) o de proveedores externos."""
    return [c for c in ss.cotizaciones_guardadas if c["estado"] == "Aprobada"
            and any((i["proveedor"] == EMPRESA) == propio for i in c["items"])]


DOCUMENTOS_INGRESO = ["Cédula de identidad", "Cédula y RUC de la empresa", "Pasaporte", "Credencial del proveedor", "Ninguno"]


def _a_fecha(txt, defecto):
    try:
        return datetime.strptime(str(txt)[:10], "%Y-%m-%d").date()
    except ValueError:
        return defecto


def _a_hora(txt, defecto):
    try:
        return datetime.strptime(str(txt)[:5], "%H:%M").time()
    except ValueError:
        return defecto


def _hh(t):
    """05:00 -> 05h00"""
    return f"{t:%H}h{t:%M}"


def _coords_en_texto(t):
    """Busca latitud y longitud dentro de un enlace de Google Maps o Waze."""
    import re
    from urllib.parse import unquote
    t = unquote(t)
    for patron in (r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", r"@(-?\d+\.\d+),(-?\d+\.\d+)", r"[?&](?:q|ll|query|center|destination|daddr)=(-?\d+\.\d+)[ ,]\s*(-?\d+\.\d+)"):
        m = re.search(patron, t)
        if m:
            return float(m.group(1)), float(m.group(2))
    return None


def _nombre_en_enlace(url):
    import re
    from urllib.parse import unquote_plus
    m = re.search(r"/place/([^/@?]+)", url)
    if m:
        n = unquote_plus(m.group(1)).strip()
        return "" if _coords_en_texto(n) else n
    return ""


def _http(url, leer=0):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "KarkajadasERP/1.0 (sistema interno de gestion de eventos)", "Accept-Language": "es"})
    with urllib.request.urlopen(req, timeout=8) as r:
        cuerpo = r.read(leer).decode("utf-8", "ignore") if leer else ""
        return r.geturl(), cuerpo


@st.cache_resource
def _memoria():
    return {}


_MEM = _memoria()   # respuestas buenas de los buscadores (las fallas no se guardan, para poder reintentar)


def _json_de(url):
    import json as _json
    _, cuerpo = _http(url, leer=400000)
    return _json.loads(cuerpo)


def _arma_calles(via, num, zona, ciudad, respaldo=""):
    via = " ".join(x for x in (via, num) if x)
    return ", ".join(x for x in (via, zona, ciudad) if x) or respaldo


def reverse_punto(lat, lng):
    """Nombre del lugar y dirección aproximada (calle, sector, ciudad) de un punto del mapa. OpenStreetMap, con respaldo en Photon."""
    clave = ("rev", round(lat, 5), round(lng, 5))
    if clave in _MEM:
        return _MEM[clave]
    try:
        d = _json_de(f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=18&addressdetails=1&accept-language=es&lat={lat}&lon={lng}")
        a = d.get("address", {})
        r = {"nombre": d.get("name", ""), "falla": False,
             "calles": _arma_calles(a.get("road") or a.get("pedestrian") or "", a.get("house_number", ""),
                                    a.get("suburb") or a.get("neighbourhood") or a.get("quarter") or "",
                                    a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or "", d.get("display_name", ""))}
        _MEM[clave] = r
        return r
    except Exception:
        pass
    try:
        d = _json_de(f"https://photon.komoot.io/reverse?lat={lat}&lon={lng}")
        p = d["features"][0]["properties"]
        r = {"nombre": p.get("name", ""), "falla": False,
             "calles": _arma_calles(p.get("street", ""), p.get("housenumber", ""), p.get("district") or p.get("locality") or "", p.get("city") or p.get("county") or "")}
        _MEM[clave] = r
        return r
    except Exception:
        return {"nombre": "", "calles": "", "falla": True}


def buscar_lugar(texto):
    """Busca un lugar por palabras (ej. «Rincón de Puembo») en Ecuador. Devuelve (lista de hasta 5 resultados, error)."""
    from urllib.parse import quote_plus as _q
    clave = ("bus", texto.lower())
    if clave in _MEM:
        return _MEM[clave], ""
    sal, errores = [], []
    try:
        for d in _json_de(f"https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&countrycodes=ec&addressdetails=1&accept-language=es&q={_q(texto)}"):
            a = d.get("address", {})
            dn = d.get("display_name", "")
            sal.append({"ok": True, "lat": float(d["lat"]), "lng": float(d["lon"]), "nombre": d.get("name") or dn.split(",")[0],
                        "calles": _arma_calles(a.get("road") or a.get("pedestrian") or "", a.get("house_number", ""),
                                               a.get("suburb") or a.get("neighbourhood") or a.get("quarter") or a.get("village") or "",
                                               a.get("city") or a.get("town") or a.get("municipality") or a.get("county") or "", dn),
                        "etiqueta": ", ".join(dn.split(",")[:3])})
    except Exception as e:
        errores.append(f"OpenStreetMap: {type(e).__name__} {e}")
    if not sal:
        try:   # respaldo: Photon, limitado a Ecuador
            for f in _json_de(f"https://photon.komoot.io/api/?limit=5&bbox=-81.1,-5.1,-75.1,1.5&q={_q(texto)}")["features"]:
                p, (lng, lat) = f["properties"], f["geometry"]["coordinates"]
                zona = p.get("district") or p.get("locality") or ""
                ciudad = p.get("city") or p.get("county") or ""
                sal.append({"ok": True, "lat": lat, "lng": lng, "nombre": p.get("name", ""),
                            "calles": _arma_calles(p.get("street", ""), p.get("housenumber", ""), zona, ciudad, p.get("name", "")),
                            "etiqueta": ", ".join(x for x in (p.get("name", ""), zona or ciudad, p.get("state", "")) if x)})
        except Exception as e:
            errores.append(f"Photon: {type(e).__name__} {e}")
    if sal:
        _MEM[clave] = sal
        return sal, ""
    return [], ("; ".join(errores) if errores else "")


def resolver_ubicacion(enlace):
    """Del enlace (Google Maps, Waze, acortado o largo) saca el punto, el nombre del lugar y la dirección aproximada."""
    from urllib.parse import quote_plus as _q
    try:
        url, cuerpo = _http(enlace, leer=300000)
    except Exception:
        return {"ok": False, "error": "No pude abrir el enlace. Revisa que esté completo o escribe el nombre del lugar."}
    punto = _coords_en_texto(url) or _coords_en_texto(cuerpo[:300000])
    nombre = _nombre_en_enlace(url)
    if not punto and nombre:   # el enlace solo trae el nombre: se busca el punto
        lista, _ = buscar_lugar(nombre)
        if lista:
            punto = (lista[0]["lat"], lista[0]["lng"])
    if not punto:
        return {"ok": False, "error": "No encontré el punto en ese enlace. Prueba con el enlace de «Compartir» de la ubicación o elige el punto en el mapa."}
    r = reverse_punto(punto[0], punto[1])
    return {"ok": True, "lat": punto[0], "lng": punto[1], "nombre": nombre or r["nombre"], "calles": r["calles"]}


def bloque_evento(cot, sufijo):
    """Datos del evento (se llenan una vez por cotización; los usan las fichas y bodega). Fechas con calendario y horas con reloj."""
    cod, cli = cot["codigo"], cliente_de(cot)
    ev = {**evento_inicial(cot), **ss.eventos.get(cod, {})}
    contactos = cli.get("contactos", [])
    k = f"{sufijo}_{cod}"
    ev["fecha_entrega"] = min(i["fecha"] for i in cot["items"])   # vienen de la cotización aprobada: no se editan aquí
    ev["tematica"] = cot["evento"]
    ev["invitados"] = str(cot.get("invitados", "") or "")
    f_base = _a_fecha(ev["fecha_entrega"], date.today())

    with st.container(border=True, key=f"card_ev_{k}"):
        st.markdown("<div class='sec-sub'>El evento</div>", unsafe_allow_html=True)
        a, b, c3 = st.columns([1.1, 1.3, 1])
        f_ent = a.date_input("Fecha de entrega del servicio", value=f_base, key=f"ev_f_{k}", disabled=True, help="Viene de la cotización aprobada")
        inv = c3.number_input("Invitados (aprox.)", min_value=0, value=int(cot.get("invitados", 0) or 0), key=f"ev_i_{k}", disabled=True,
                              help="Viene de la cotización aprobada")
        tema = b.text_input("Temática", ev["tematica"], key=f"ev_t_{k}", disabled=True, help="Viene de la cotización aprobada")
        pkey = f"pto_{k}"
        if pkey not in ss and ev.get("lat"):
            ss[pkey] = {"ok": True, "lat": ev["lat"], "lng": ev["lng"], "nombre": ev["lugar"], "calles": ev["direccion"], "aceptada": True}
        lugar = ss.get(f"lug_{k}", ev["lugar"])

        def _aceptar(k=k, pkey=pkey):
            u = ss.get(pkey)
            if u and u.get("ok"):
                ss[f"ev_d_{k}"] = u["calles"]
                ss[f"ev_e_{k}"] = f"https://www.google.com/maps?q={u['lat']:.6f},{u['lng']:.6f}"   # enlace del punto elegido
                ss[f"lug_{k}"] = u.get("nombre", "")
                ss[pkey] = {**u, "aceptada": True}

        st.markdown("<div class='sec-sub'>Ubicación</div>", unsafe_allow_html=True)
        def _buscar(k=k, pkey=pkey):
            texto = (ss.get(f"ev_q_{k}") or "").strip()
            ss.pop(f"err_{k}", None)
            ss.pop(f"res_{k}", None)
            ss.pop(f"sel_{k}", None)
            if not texto:
                return
            if texto.startswith("http"):
                r = resolver_ubicacion(texto)
                lista = [r] if r.get("ok") else None
                if not lista:
                    ss[f"err_{k}"] = r["error"]
            else:
                lista, falla = buscar_lugar(texto)
                if falla:
                    ss[f"err_{k}"] = f"No pude consultar el buscador de lugares ({falla}). Elige el punto en el mapa o inténtalo de nuevo en un momento."
                elif not lista:
                    ss[f"err_{k}"] = f"No encontré «{texto}». Prueba con otras palabras (por ejemplo, el sector y la ciudad) o haz clic en el mapa."
                    lista = None
            if lista:
                ss[pkey] = lista[0]
                ss[f"zm_{k}"] = 17
                if len(lista) > 1:
                    ss[f"res_{k}"] = lista

        def _elegir_resultado(k=k, pkey=pkey):
            lista = ss.get(f"res_{k}") or []
            i = ss.get(f"sel_{k}")
            if i is not None and 0 <= i < len(lista):
                ss[pkey] = lista[i]
                ss[f"zm_{k}"] = 17

        e1, e2 = st.columns([4, 1], vertical_alignment="bottom")
        e1.text_input("Buscar un lugar o pegar un enlace de Google Maps o Waze", key=f"ev_q_{k}", on_change=_buscar,
                      placeholder="Ej. Rincón de Puembo, o pega aquí el enlace que te compartieron")
        e2.button("Buscar", key=f"ev_bu_{k}", use_container_width=True, type="secondary", on_click=_buscar)
        if ss.get(f"err_{k}"):
            st.warning(ss[f"err_{k}"])
        if ss.get(f"res_{k}"):
            lista = ss[f"res_{k}"]
            st.selectbox("Se encontraron varios lugares: elige el correcto", range(len(lista)), format_func=lambda i: f"{lista[i]['nombre']} - {lista[i]['etiqueta']}",
                         key=f"sel_{k}", on_change=_elegir_resultado)
        u = ss.get(pkey)
        try:
            import folium
            from streamlit_folium import st_folium
        except ImportError:
            folium = None
        m1, m2 = st.columns([1.7, 1])
        with m1:
            if folium is None:
                st.warning("Falta instalar el componente del mapa para poder hacer clic en él: sube el archivo requirements.txt a GitHub y reinicia la app. Mientras tanto se muestra una vista previa.")
                st.iframe(f"https://maps.google.com/maps?q={u['lat']},{u['lng']}&z=17&output=embed&hl=es" if u else "https://maps.google.com/maps?q=Quito,Ecuador&z=12&output=embed&hl=es", height=300)
            else:
                centro = [u["lat"], u["lng"]] if u else [-0.1807, -78.4678]
                mapa = folium.Map(location=centro, zoom_start=ss.get(f"zm_{k}") or (17 if u else 12), tiles="OpenStreetMap", control_scale=True)
                if u:
                    folium.Marker(centro, icon=folium.Icon(color="darkblue", icon="map-marker", prefix="fa")).add_to(mapa)
                res = st_folium(mapa, height=330, use_container_width=True, key=f"mapa_{k}", returned_objects=["last_clicked", "zoom"])
                if res and res.get("zoom"):
                    ss[f"zm_{k}"] = res["zoom"]
                cl = res.get("last_clicked") if res else None
                if cl and (round(cl["lat"], 7), round(cl["lng"], 7)) != ss.get(f"clk_{k}"):
                    ss[f"clk_{k}"] = (round(cl["lat"], 7), round(cl["lng"], 7))
                    rr = reverse_punto(cl["lat"], cl["lng"])
                    ss[pkey] = {"ok": True, "lat": cl["lat"], "lng": cl["lng"], "nombre": rr["nombre"], "calles": rr["calles"]}
                    st.rerun()
        with m2:
            if not u:
                st.markdown("<div class='col-head'>Cómo elegir el punto</div><div style='color:#475569; line-height:1.6; margin-top:4px;'>"
                            "Escribe el nombre del lugar arriba, haz clic en el mapa donde será el evento, o pega el enlace que te compartieron.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='col-head'>Punto elegido</div>"
                            f"<div style='font-weight:700; margin:2px 0 10px;'>{esc(u.get('nombre') or '') or 'Sin nombre'}</div>"
                            "<div class='col-head'>Dirección aproximada</div>"
                            f"<div style='margin:2px 0 12px;'>{esc(u.get('calles') or '') or 'No se pudo obtener; escríbela abajo'}</div>", unsafe_allow_html=True)
                if u.get("aceptada"):
                    st.success("Dirección aceptada")
                else:
                    st.button("Aceptar dirección", type="primary", key=f"ev_ac_{k}", on_click=_aceptar, use_container_width=True)
                    st.caption("Al aceptar se completan la dirección y el enlace. Si no es el punto exacto, haz clic en otro lugar del mapa.")

        d1, d2, d3 = st.columns([1.4, 1.2, 1.2])
        direccion = d1.text_area("Dirección", ev["direccion"], height=96, key=f"ev_d_{k}")
        referencia = d2.text_area("Referencia (opcional)", ev.get("referencia", ""), height=96, key=f"ev_rf_{k}",
                                  placeholder="Ej. Portón azul, frente al parque, preguntar por Juan en recepción")
        enlace = d3.text_area("Enlace de la ubicación", ev.get("enlace", ""), height=96, key=f"ev_e_{k}",
                              placeholder="Se completa solo al aceptar la dirección")
        texto_mapa = " ".join(x for x in (lugar.strip(), direccion.strip()) if x)
        if texto_mapa:
            q = quote_plus(texto_mapa + ", Ecuador")
            b1, b2, b3 = st.columns([1, 1, 1])
            b1.link_button("Buscar en Google Maps", f"https://www.google.com/maps/search/?api=1&query={q}", use_container_width=True)
            if enlace.strip().startswith("http"):
                b2.link_button("Abrir el enlace de la ubicación", enlace.strip(), use_container_width=True)

        st.markdown("<div class='sec-sub'>Horarios</div>", unsafe_allow_html=True)
        # cuadrícula: el evento y, en una sola fila, el montaje y el desmontaje (se bloquean si no hay montaje)
        g = [1.0, 1.5, 1.0, 1.0, 1.3]
        hd = st.columns(g)
        for col, t in zip(hd, ["", "Fecha", "Desde", "Hasta", ""]):
            col.markdown(f"<span class='col-head'>{t}</span>", unsafe_allow_html=True)
        r = st.columns(g, vertical_alignment="center")
        r[0].markdown("<b>Evento</b>", unsafe_allow_html=True)
        f_eve = r[1].date_input("Fecha del evento", value=_a_fecha(ev.get("f_evento", ""), f_base), key=f"ev_fe_{k}", label_visibility="collapsed")
        h_ini = r[2].time_input("Evento desde", value=_a_hora(ev.get("h_ini", ""), datetime.strptime("09:00", "%H:%M").time()), step=900, key=f"ev_hi_{k}", label_visibility="collapsed")
        h_fin = r[3].time_input("Evento hasta", value=_a_hora(ev.get("h_fin", ""), datetime.strptime("12:00", "%H:%M").time()), step=900, key=f"ev_hf_{k}", label_visibility="collapsed")
        t1, t2 = st.columns([1.0, 4.8], vertical_alignment="center")
        t1.markdown("<b>Montaje y desmontaje</b>", unsafe_allow_html=True)
        mon = t2.segmented_control("¿Hay montaje?", ["Sí", "No"], default="Sí" if ev["montaje"] != "No" else "No", key=f"ev_m_{k}", label_visibility="collapsed") or "Sí"
        sin = mon == "No"
        g2 = [1.0, 1.5, 1.0, 1.5, 1.0]
        m = st.columns(g2)
        f_mon = m[1].date_input("Fecha del montaje", value=_a_fecha(ev.get("f_montaje", ""), f_base), key=f"ev_fm_{k}", disabled=sin)
        h_mon = m[2].time_input("Hora del montaje", value=_a_hora(ev.get("h_montaje", ""), datetime.strptime("06:00", "%H:%M").time()), step=900, key=f"ev_hm_{k}", disabled=sin)
        f_des = m[3].date_input("Fecha del desmontaje", value=_a_fecha(ev.get("f_desm", ""), f_base), key=f"ev_fd_{k}", disabled=sin)
        h_des = m[4].time_input("Hora del desmontaje", value=_a_hora(ev.get("h_desm", ""), datetime.strptime("13:00", "%H:%M").time()), step=900, key=f"ev_hd_{k}", disabled=sin)
        obs_h = st.text_input("Nota sobre los horarios (opcional)", ev.get("obs_horario", ""),
                              placeholder="Ej. El horario del desmontaje puede variar según el cierre del evento", key=f"ev_oh_{k}")
        if h_fin <= h_ini:
            st.warning("La hora de fin del evento debe ser posterior a la de inicio.")

        st.markdown("<div class='sec-sub'>Inclusión y necesidades especiales</div>", unsafe_allow_html=True)
        st.caption("Solo cantidades de personas, sin nombres. Sale en las fichas de los proveedores para que se preparen.")
        inc0 = ev.get("inclusion") or {}
        st.markdown("<span class='col-head'>Alimentación</span>", unsafe_allow_html=True)
        i1, i2, i3, i4 = st.columns(4)
        vegt = i1.number_input("Vegetarianos", min_value=0, step=1, value=int(inc0.get("vegetarianos", 0)), key=f"in_v_{k}")
        vega = i2.number_input("Veganos", min_value=0, step=1, value=int(inc0.get("veganos", 0)), key=f"in_vg_{k}")
        glut = i3.number_input("Sin gluten (celíacos)", min_value=0, step=1, value=int(inc0.get("sin_gluten", 0)), key=f"in_g_{k}")
        aler = i4.number_input("Con alergias alimentarias", min_value=0, step=1, value=int(inc0.get("alergias", 0)), key=f"in_a_{k}")
        nota_ali = st.text_input("Detalle de alergias u otras restricciones (opcional)", inc0.get("nota_ali", ""), key=f"in_na_{k}",
                                 placeholder="Ej. Alergia a mariscos y maní; una persona sin lactosa")
        st.markdown("<span class='col-head'>Accesibilidad</span>", unsafe_allow_html=True)
        j1, j2, j3, j4 = st.columns(4)
        movi = j1.number_input("Movilidad reducida o silla de ruedas", min_value=0, step=1, value=int(inc0.get("movilidad", 0)), key=f"in_m_{k}")
        visu = j2.number_input("Discapacidad visual", min_value=0, step=1, value=int(inc0.get("visual", 0)), key=f"in_vi_{k}")
        audi = j3.number_input("Discapacidad auditiva", min_value=0, step=1, value=int(inc0.get("auditiva", 0)), key=f"in_au_{k}")
        otra = j4.number_input("Otra necesidad", min_value=0, step=1, value=int(inc0.get("otra_acc", 0)), key=f"in_o_{k}")
        nota_acc = st.text_input("Qué se necesita (opcional)", inc0.get("nota_acc", ""), key=f"in_nc_{k}",
                                 placeholder="Ej. Rampa en el ingreso, espacio frente al escenario, intérprete de lengua de señas")

        st.markdown("<div class='sec-sub'>Quién recibe y requisitos</div>", unsafe_allow_html=True)
        c2, c3 = st.columns(2)
        recibe = c2.text_input("Persona que recibe", ev["recibe"], key=f"ev_n_{k}")
        tel = c3.text_input("Teléfono de quien recibe", ev["telefono_recibe"], key=f"ev_p_{k}")
        u1, u2 = st.columns([1, 2])
        ubic = u1.segmented_control("Ubicación enviada", ["Pendiente", "Enviada"], default="Enviada" if ev["ubicacion"] == "Enviada" else "Pendiente", key=f"ev_u_{k}") or "Pendiente"
        docs = DOCUMENTOS_INGRESO if ev["documento"] in DOCUMENTOS_INGRESO or not ev["documento"] else DOCUMENTOS_INGRESO + [ev["documento"]]
        doc_in = u2.selectbox("Documento requerido para el ingreso", docs, index=docs.index(ev["documento"]) if ev["documento"] in docs else 0,
                              accept_new_options=True, key=f"ev_di_{k}")
        otros = st.text_input("Otros", ev["otros"], key=f"ev_o_{k}")
        obs = st.text_area("Observaciones generales", ev["observacion"], height=110, key=f"ev_ob_{k}")
        novedades = st.text_area("Novedades después de la aprobación (opcional)", ev.get("novedades", ""), height=80, key=f"ev_nv_{k}",
                                 placeholder="Ej. El cliente pidió adelantar el montaje una hora. Lo aprobado en la cotización no cambia; aquí solo se anota lo nuevo.")

        if st.button("Guardar datos del evento", type="primary", key=f"ev_save_{k}"):
            fm = lambda d: d.strftime("%d/%m/%Y")
            lineas = []
            if mon == "Sí":
                lineas.append(f"Montaje {fm(f_mon)} - A partir de las {_hh(h_mon)}")
            lineas.append(f"Evento {fm(f_eve)} - {h_ini:%H:%M} a {h_fin:%H:%M}")
            if mon == "Sí":
                lineas.append(f"Desmontaje {fm(f_des)} - A partir de las {_hh(h_des)}")
            if obs_h.strip():
                lineas.append(f"Nota: {obs_h.strip()}")
            ss.eventos[cod] = {
                "fecha_entrega": f_ent.strftime("%Y-%m-%d"), "invitados": str(inv) if inv else "", "lugar": lugar, "direccion": direccion, "lat": (ss.get(pkey) or {}).get("lat"), "lng": (ss.get(pkey) or {}).get("lng"),
                "ubicacion": ubic, "horario": "\n".join(lineas), "tematica": tema, "recibe": recibe, "telefono_recibe": tel,
                "montaje": mon, "novedades": novedades.strip(),
                "inclusion": {"vegetarianos": int(vegt), "veganos": int(vega), "sin_gluten": int(glut), "alergias": int(aler), "nota_ali": nota_ali.strip(),
                              "movilidad": int(movi), "visual": int(visu), "auditiva": int(audi), "otra_acc": int(otra), "nota_acc": nota_acc.strip()}, "enlace": enlace.strip(), "referencia": referencia.strip(),
                "hora_montaje": f"{fecha_larga(f_mon)} a partir de las {_hh(h_mon)}" if mon == "Sí" else "No aplica",
                "desmontaje": f"{fecha_larga(f_des)} a partir de las {_hh(h_des)}" if mon == "Sí" else "No aplica", "documento": doc_in, "otros": otros, "observacion": obs,
                "f_montaje": f_mon.strftime("%Y-%m-%d"), "h_montaje": f"{h_mon:%H:%M}",
                "f_evento": f_eve.strftime("%Y-%m-%d"), "h_ini": f"{h_ini:%H:%M}", "h_fin": f"{h_fin:%H:%M}",
                "f_desm": f_des.strftime("%Y-%m-%d"), "h_desm": f"{h_des:%H:%M}", "obs_horario": obs_h.strip()}
            st.rerun()
    return {**evento_inicial(cot), **ss.eventos.get(cod, {})}


def _nom_contacto(c):
    return f"{c['nombre']} - {c['cargo']}" if c.get("cargo") else c["nombre"]


def encabezados(cols, titulos):
    for col, t in zip(cols, titulos):
        col.markdown(f"<span class='col-head'>{t}</span>", unsafe_allow_html=True)


def _vacio(v):
    return v is None or (isinstance(v, float) and pd.isna(v))


def limpiar_lista(df, columnas):
    """Convierte la tabla editable en lista de dicts y descarta las filas totalmente vacías."""
    filas = []
    for r in df.to_dict("records"):
        f = {c: "" if _vacio(r.get(c)) else str(r.get(c)).strip() for c in columnas}
        if any(f.values()):
            filas.append(f)
    return filas


def editor_lista(clave, filas, columnas, config):
    """Tabla editable donde se agregan (＋ al final), editan o borran filas: sirve para varios correos, teléfonos, sedes, cuentas..."""
    df = pd.DataFrame(filas, columns=columnas).astype(object)
    ed = st.data_editor(df, num_rows="dynamic", hide_index=True, use_container_width=True, column_config=config, key=clave)
    return limpiar_lista(ed, columnas)


COL_CONTACTOS = ["nombre", "cargo", "correo", "telefono"]
CFG_CONTACTOS = {"nombre": st.column_config.TextColumn("Nombre", width="medium"), "cargo": st.column_config.TextColumn("Cargo / área"),
                 "correo": st.column_config.TextColumn("Correo", width="medium"), "telefono": st.column_config.TextColumn("Teléfono")}
COL_DIRECCIONES = ["etiqueta", "direccion", "ciudad"]
CFG_DIRECCIONES = {"etiqueta": st.column_config.TextColumn("Etiqueta (matriz, bodega...)"),
                   "direccion": st.column_config.TextColumn("Dirección", width="large"),
                   "ciudad": st.column_config.SelectboxColumn("Ciudad", options=CIUDADES)}
COL_SERVICIOS = ["servicio", "categoria", "ciudad", "precio_base", "iva", "descripcion"]
CFG_SERVICIOS = {"servicio": st.column_config.TextColumn("Servicio", width="medium"), "categoria": st.column_config.TextColumn("Categoría"),
                 "ciudad": st.column_config.SelectboxColumn("Ciudad", options=CIUDADES),
                 "precio_base": st.column_config.NumberColumn("Costo ($)", min_value=0.0, format="$%.2f"),
                 "iva": st.column_config.SelectboxColumn("IVA", options=["0%", "15%"]), "descripcion": st.column_config.TextColumn("Descripción")}
COL_CUENTAS = ["banco", "tipo", "numero", "titular"]
CFG_CUENTAS = {"banco": st.column_config.TextColumn("Banco"), "tipo": st.column_config.SelectboxColumn("Tipo", options=["Ahorros", "Corriente"]),
               "numero": st.column_config.TextColumn("Número de cuenta"), "titular": st.column_config.TextColumn("Titular")}


def selector_ciudad(contenedor, etiqueta, clave, valor=None):
    """Lista de ciudades con la opción "Otra...": si se elige, aparece un campo para escribirla
    y queda guardada en la lista para todo el ERP."""
    if valor and valor not in CIUDADES:
        ss.ciudades_extra.append(valor)
        CIUDADES.insert(len(CIUDADES) - 1, valor)
    opciones = CIUDADES + [OTRA]
    pos = CIUDADES.index(valor) if valor in CIUDADES else 0
    elegida = contenedor.selectbox(etiqueta, opciones, index=pos, key=clave)
    if elegida != OTRA:
        return elegida
    nueva = contenedor.text_input("Escribe la ciudad", key=f"{clave}_otra").strip()
    if nueva:
        nueva = nueva[:1].upper() + nueva[1:]
        if nueva not in CIUDADES:
            ss.ciudades_extra.append(nueva)
        return nueva
    return valor if valor in CIUDADES else CIUDADES[0]


def indice(opciones, valor):
    return opciones.index(valor) if valor in opciones else 0


def correos_invalidos(contactos):
    return [c["correo"] for c in contactos if c["correo"] and ("@" not in c["correo"] or " " in c["correo"])]


def siguiente_id(prefijo, lista):
    nums = [int(r["id"].split("-")[1]) for r in lista if str(r.get("id", "")).startswith(prefijo + "-")]
    return f"{prefijo}-{max(nums, default=0) + 1:03d}"


def aplanar_cliente(c):
    """Copia el contacto y la dirección principales (primera fila) a los campos simples que usa el PDF y las tablas."""
    con = c["contactos"][0] if c.get("contactos") else {}
    c["contacto"], c["email"], c["telefono"] = con.get("nombre", ""), con.get("correo", ""), con.get("telefono", "")
    c["direccion"] = c["direcciones"][0]["direccion"] if c.get("direcciones") else ""


def botones_formulario(prefijo, texto_guardar, cancelar):
    b1, b2, _ = st.columns([1.4, 1, 4])
    guardar = b1.button(texto_guardar, type="primary", use_container_width=True, key=f"{prefijo}_guardar")
    return guardar, (cancelar and b2.button("Cancelar", use_container_width=True, key=f"{prefijo}_cancelar"))


def form_cliente(prefijo, titulo_html="", datos=None, cancelar=False):
    """Formulario de cliente (nuevo o edición). Devuelve dict con los datos, "cancelar" o None."""
    d = datos or {}
    if titulo_html:
        st.markdown(titulo_html, unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2.3, 1.4, 1.3, 1.8, 1])
    emp = c1.text_input("Razón social / empresa *", value=d.get("empresa", ""), key=f"{prefijo}_emp")
    ruc = c2.text_input("RUC *", value=d.get("ruc", ""), key=f"{prefijo}_ruc")
    ciu = selector_ciudad(c3, "Ciudad principal", f"{prefijo}_ciu", d.get("ciudad"))
    web = c4.text_input("Sitio web", value=d.get("web", ""), key=f"{prefijo}_web")
    dias = c5.number_input("Días crédito", min_value=0, value=int(d.get("dias_credito", 30)), step=15, key=f"{prefijo}_dias")
    t_con, t_dir = st.tabs(["Contactos (correos y teléfonos)", "Direcciones"])
    with t_con:
        st.caption("Una fila por persona o correo. La primera fila es el contacto principal y es la que sale en la cotización.")
        contactos = editor_lista(f"{prefijo}_con", d.get("contactos", []), COL_CONTACTOS, CFG_CONTACTOS)
    with t_dir:
        st.caption("Una fila por sede o dirección de entrega. La primera es la principal.")
        direcciones = editor_lista(f"{prefijo}_dirs", d.get("direcciones", []), COL_DIRECCIONES, CFG_DIRECCIONES)
    guardar, cancel = botones_formulario(prefijo, "Guardar cambios" if datos else "Guardar cuenta", cancelar)
    if cancel:
        return "cancelar"
    if guardar:
        if not (emp.strip() and ruc.strip()):
            st.error("Razón social y RUC son requeridos.")
        elif correos_invalidos(contactos):
            st.error(f"Revisa estos correos: {', '.join(correos_invalidos(contactos))}")
        else:
            return {"empresa": emp.strip(), "ruc": ruc.strip(), "ciudad": ciu, "web": web.strip(), "dias_credito": dias,
                    "contactos": contactos, "direcciones": direcciones}
    return None


def form_proveedor(prefijo, titulo_html="", datos=None, cancelar=False):
    d = datos or {}
    if titulo_html:
        st.markdown(titulo_html, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2.3, 1.4, 1.6, 1.3])
    nom = c1.text_input("Proveedor *", value=d.get("proveedor", ""), key=f"{prefijo}_nom")
    ruc = c2.text_input("RUC", value=d.get("ruc", ""), key=f"{prefijo}_ruc")
    cat = c3.text_input("Categoría general", value=d.get("categoria", ""), key=f"{prefijo}_cat")
    ciu = selector_ciudad(c4, "Ciudad base", f"{prefijo}_ciu", d.get("ciudad"))
    obs = st.text_input("Observaciones", value=d.get("observaciones", ""), key=f"{prefijo}_obs")
    t_srv, t_con, t_dir, t_cta = st.tabs(["Servicios y costos", "Contactos (correos y teléfonos)", "Direcciones", "Cuentas bancarias"])
    with t_con:
        st.caption("Una fila por persona o correo. La primera fila es el contacto principal.")
        contactos = editor_lista(f"{prefijo}_con", d.get("contactos", []), COL_CONTACTOS, CFG_CONTACTOS)
    with t_dir:
        direcciones = editor_lista(f"{prefijo}_dirs", d.get("direcciones", []), COL_DIRECCIONES, CFG_DIRECCIONES)
    with t_cta:
        st.caption("Puede tener varias cuentas. La primera es la que se usa por defecto para pagos.")
        cuentas = editor_lista(f"{prefijo}_cta", d.get("cuentas", []), COL_CUENTAS, CFG_CUENTAS)
    with t_srv:
        st.caption("Todo lo que ofrece este proveedor: una fila por servicio (sonido, pantallas, TVs...). Estos servicios aparecen al cotizar.")
        srv_ini = [dict(r) for r in ss.proveedores_catalogo if d and r["proveedor"] == d.get("proveedor")]
        df_srv = pd.DataFrame(srv_ini, columns=COL_SERVICIOS)
        df_srv["iva"] = df_srv["iva"].map(lambda x: f"{int(x * 100)}%")
        ed_srv = st.data_editor(df_srv, num_rows="dynamic", hide_index=True, use_container_width=True, column_config=CFG_SERVICIOS, key=f"{prefijo}_srv")
    guardar, cancel = botones_formulario(prefijo, "Guardar cambios" if datos else "Registrar proveedor", cancelar)
    if cancel:
        return "cancelar"
    if guardar:
        if not nom.strip():
            st.error("El nombre del proveedor es obligatorio.")
        elif correos_invalidos(contactos):
            st.error(f"Revisa estos correos: {', '.join(correos_invalidos(contactos))}")
        elif any(_vacio(r["servicio"]) or not str(r["servicio"]).strip() for r in ed_srv.to_dict("records") if any(not _vacio(v) and str(v).strip() for v in r.values())):
            st.error("Cada servicio necesita su nombre.")
        else:
            servicios = []
            for r in ed_srv.to_dict("records"):
                if _vacio(r["servicio"]) or not str(r["servicio"]).strip():
                    continue
                servicios.append({"servicio": str(r["servicio"]).strip(), "categoria": "" if _vacio(r["categoria"]) else str(r["categoria"]).strip(),
                                  "ciudad": ciu if _vacio(r["ciudad"]) else r["ciudad"], "precio_base": 0.0 if _vacio(r["precio_base"]) else float(r["precio_base"]),
                                  "iva": 0.15 if r["iva"] == "15%" else 0.0, "descripcion": "" if _vacio(r["descripcion"]) else str(r["descripcion"]).strip()})
            return {"servicios": servicios, "proveedor": nom.strip(), "ruc": ruc.strip(), "categoria": cat.strip(), "ciudad": ciu, "observaciones": obs.strip(),
                    "contactos": contactos, "direcciones": direcciones, "cuentas": cuentas}
    return None


# --- Altas, cambios y validaciones de clientes y proveedores
def validar_cliente(d, cid=None):
    for c in ss.clientes_catalogo:
        if c["id"] != cid and c["ruc"] == d["ruc"]:
            return f"Ya existe una cuenta con ese RUC ({c['empresa']})."
        if c["id"] != cid and c["empresa"].lower() == d["empresa"].lower():
            return "Ya existe una cuenta con ese nombre."
    return None


def crear_cliente(d):
    d["id"] = siguiente_id("CLI", ss.clientes_catalogo)
    aplanar_cliente(d)
    ss.clientes_catalogo.append(d)


def actualizar_cliente(cid, nuevo):
    c = next(x for x in ss.clientes_catalogo if x["id"] == cid)
    viejo = c["empresa"]
    c.update(nuevo)
    aplanar_cliente(c)
    if viejo != c["empresa"]:   # las cotizaciones ya guardadas siguen apuntando a la misma cuenta
        for q in ss.cotizaciones_guardadas:
            if q["cliente"] == viejo:
                q["cliente"] = c["empresa"]


def validar_proveedor(d, pid=None):
    actual = next((x for x in ss.proveedores if x["id"] == pid), None)
    if actual and actual["proveedor"] == EMPRESA and d["proveedor"].strip() != EMPRESA:
        return f"«{EMPRESA}» es la empresa propia (sus servicios salen de bodega); no se puede cambiar su nombre."
    if any(p["id"] != pid and p["proveedor"].lower() == d["proveedor"].lower() for p in ss.proveedores):
        return "Ya existe un proveedor con ese nombre."
    return None


def crear_proveedor(d):
    servicios = d.pop("servicios", [])
    d["id"] = siguiente_id("PRV", ss.proveedores)
    ss.proveedores.append(d)
    ss.proveedores_catalogo.extend({**sv, "proveedor": d["proveedor"]} for sv in servicios)


def actualizar_proveedor(pid, nuevo):
    p = next(x for x in ss.proveedores if x["id"] == pid)
    viejo = p["proveedor"]
    servicios = nuevo.pop("servicios", None)
    p.update(nuevo)
    if p["proveedor"] != viejo:   # el cambio de nombre llega a las cotizaciones, a las fichas guardadas y a los servicios
        for lista in [c["items"] for c in ss.cotizaciones_guardadas] + [ss.items_cot]:
            for it in lista:
                if it["proveedor"] == viejo:
                    it["proveedor"] = p["proveedor"]
        ss.fichas = {(k.rsplit("|", 1)[0] + "|" + p["proveedor"] if k.endswith("|" + viejo) else k): v for k, v in ss.fichas.items()}
    if servicios is not None:   # los servicios del formulario reemplazan a los anteriores de este proveedor
        ss.proveedores_catalogo = [r for r in ss.proveedores_catalogo if r["proveedor"] != viejo] + [{**sv, "proveedor": p["proveedor"]} for sv in servicios]


def asegurar_proveedor(nombre, ciudad, categoria):
    """Si se registra un servicio de un proveedor que no está en el directorio, se crea el proveedor."""
    if not any(p["proveedor"].lower() == nombre.lower() for p in ss.proveedores):
        crear_proveedor({"proveedor": nombre, "ruc": "", "categoria": categoria, "ciudad": ciudad, "observaciones": "",
                         "contactos": [], "direcciones": [], "cuentas": []})
        return True
    return False


def faltantes_proveedor(p):
    """Qué le falta a un proveedor para considerarse completo: RUC y un contacto con teléfono (la empresa propia no se revisa)."""
    if not p:
        return ["estar en el directorio"]
    if p.get("proveedor") == "Karkajadas Group":
        return []
    falta = []
    if not str(p.get("ruc", "")).strip():
        falta.append("RUC")
    if not any(str(c.get("telefono", "")).strip() for c in p.get("contactos", [])):
        falta.append("contacto con teléfono")
    return falta


def completar_proveedor(nombre, ciudad):
    """Lleva al directorio; si el proveedor no existe todavía, lo crea para poder completarlo."""
    asegurar_proveedor(nombre, ciudad, "General")
    ss.dir_prv_solo = True
    navegar(MENU_PROVEEDORES)


def resumen_contactos(r):
    """Contacto principal + cuántos más hay."""
    con = r.get("contactos", [])
    extra = f" (+{len(con) - 1})" if len(con) > 1 else ""
    return (con[0]["nombre"] if con else "", (con[0]["correo"] if con else "") + extra, con[0]["telefono"] if con else "")


def abrir_nuevo(k):
    ss[f"dir_{k}_nuevo"] = True
    ss[f"dir_{k}_ver"] += 1   # deselecciona la fila de la tabla


def panel_directorio(k, registros, fila_tabla, texto_busqueda, form, validar, crear, actualizar, nombre, etiqueta_nuevo, filtro=None):
    """Tabla con búsqueda; al seleccionar una fila se edita; el botón de nuevo abre el formulario vacío."""
    ss.setdefault(f"dir_{k}_ver", 0)
    ss.setdefault(f"dir_{k}_nuevo", False)
    ver = ss[f"dir_{k}_ver"]
    c_b, c_n = st.columns([3, 1], vertical_alignment="center")
    busq = c_b.text_input("Buscar", key=f"dir_{k}_b", label_visibility="collapsed", placeholder="Buscar...").lower()
    c_n.button(f"＋ {etiqueta_nuevo}", key=f"dir_{k}_btn_nuevo", on_click=abrir_nuevo, args=(k,), use_container_width=True, type="primary")
    vis = [r for r in registros if (not busq or busq in texto_busqueda(r).lower()) and (filtro is None or filtro(r))]
    sel = []
    if vis:
        ev = st.dataframe(pd.DataFrame([fila_tabla(r) for r in vis]), hide_index=True, use_container_width=True, on_select="rerun",
                          selection_mode="single-row", key=f"dir_{k}_t{ver}", height=min(35 * (len(vis) + 1) + 3, 340))
        sel = ev.selection.rows
        if not sel:
            st.caption("Haz clic en el recuadro a la izquierda de una fila para editarla.")
    else:
        st.info("No hay registros que coincidan.")

    def cerrar():
        ss[f"dir_{k}_nuevo"] = False
        ss[f"dir_{k}_ver"] += 1
        st.rerun()

    if sel and sel[0] < len(vis):
        reg = vis[sel[0]]
        ss[f"dir_{k}_nuevo"] = False
        with st.container(border=True, key=f"card_dir_{k}_e"):
            res = form(f"e{k}_{reg['id']}_{ver}", f"<div class='section-title'>Editar: {esc(nombre(reg))}</div>", reg, True)
            if res == "cancelar":
                cerrar()
            elif res:
                err = validar(res, reg["id"])
                if err:
                    st.error(err)
                else:
                    actualizar(reg["id"], res)
                    st.toast("Cambios guardados")
                    cerrar()
    elif ss[f"dir_{k}_nuevo"]:
        with st.container(border=True, key=f"card_dir_{k}_n"):
            res = form(f"n{k}_{ver}", f"<div class='section-title' style='color:#059669; border-color:#059669;'>{etiqueta_nuevo}</div>", None, True)
            if res == "cancelar":
                cerrar()
            elif res:
                err = validar(res, None)
                if err:
                    st.error(err)
                else:
                    crear(res)
                    st.toast("Registrado")
                    cerrar()


# =============================================================================
# MENÚ LATERAL
# =============================================================================
st.sidebar.markdown("<div class='brand-logo'>Karkajadas Group</div>", unsafe_allow_html=True)
MENU_PRINCIPAL = ["Panel de control", "Reportes financieros", "Proyecciones de ventas", "Noticias corporativas"]
MENU_SOPORTE = ["Centro de ayuda"]
MENU_PERFIL = "Perfil de la empresa"
CATALOGOS = {"Catálogo regular": "regular", "Catálogo navideño": "navidad"}   # menú -> catálogo del cotizador
MENU_PROV = "Órdenes a proveedores"
MENU_BODEGA = "Bodega"
MENU_REPORTES = "Reportes financieros"

# Cada sección tiene un tono propio y apagado (franja izquierda, etiqueta y fondo muy tenue); la opción activa se resalta
SECCIONES = [
    ("pri", None, MENU_PRINCIPAL, "#94A3B8"),
    ("cat", "COTIZADOR DE CATÁLOGOS", list(CATALOGOS), "#5FA8A0"),
    ("dir", "DIRECTORIOS", [MENU_CLIENTES, MENU_PROVEEDORES], "#9B8EC9"),
    ("ope", "OPERACIONES", [MENU_PROV, MENU_BODEGA], "#C9A961"),
    ("emp", "MI EMPRESA", [MENU_PERFIL], "#7C9CBF"),
    ("sop", "SOPORTE Y PROCESOS", MENU_SOPORTE, "#C28A9B"),
]
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

menu = ss.nav_menu
if ss.get("aviso_pendiente"):
    st.toast(ss.pop("aviso_pendiente"), icon="ℹ️")

# =============================================================================
# MÓDULOS EN CONSTRUCCIÓN
# =============================================================================
if menu in [m for m in MENU_PRINCIPAL[1:] + MENU_SOPORTE if m != MENU_REPORTES]:
    encabezado_estandar("obra", menu, "Módulo en construcción")
    st.info("Módulo en construcción.")

# =============================================================================
# REPORTES FINANCIEROS
# =============================================================================
elif menu == MENU_REPORTES:
    encabezado_estandar("rep", "Reportes financieros", "Listado de cotizaciones y exportación a Excel")
    cots_all = ss.cotizaciones_guardadas
    with st.container(border=True, key="card_rep1"):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:0;'>Filtros del reporte</div>", unsafe_allow_html=True)
        ss.setdefault("rep_est", ["Todas"])
        ss.setdefault("rep_cli", ["Todos"])
        st.pills("Estado", ["Todas"] + ESTADOS, selection_mode="multi", key="rep_est", on_change=normalizar_multi, args=("rep_est", "Todas"))
        r2, r3, r4, r5 = st.columns([2.6, 1.6, 1.2, 1.2])
        r2.multiselect("Cliente", ["Todos"] + sorted({c["cliente"] for c in cots_all}), key="rep_cli", on_change=normalizar_multi, args=("rep_cli", "Todos"))
        f_ciu = r3.selectbox("Ciudad del servicio", ["Todas"] + CIUDADES, key="rep_ciu")
        fechas = sorted(c["fecha"] for c in cots_all) or [str(date.today())]
        f_des = r4.date_input("Desde", value=date.fromisoformat(fechas[0]), key="rep_des")
        f_has = r5.date_input("Hasta", value=date.fromisoformat(fechas[-1]), key="rep_has")
        f_est = ESTADOS if ("Todas" in ss.rep_est or not ss.rep_est) else ss.rep_est
        f_cli = ss.rep_cli
    sel = [c for c in cots_all
           if c["estado"] in f_est and ("Todos" in f_cli or not f_cli or c["cliente"] in f_cli)
           and (f_ciu == "Todas" or any(i["ciudad"] == f_ciu for i in c["items"]))
           and f_des.isoformat() <= c["fecha"] <= f_has.isoformat()]
    sel.sort(key=lambda c: c["fecha"], reverse=True)

    with st.container(border=True, key="card_rep2"):
        k1, k2, k3 = st.columns([1.2, 1.2, 1.6], vertical_alignment="center")
        k1.markdown(f"<div class='monto-badge' style='margin-left:0;'><div class='monto-label'>Cotizaciones</div><div class='monto-valor'>{len(sel)}</div></div>", unsafe_allow_html=True)
        k2.markdown(f"<div class='monto-badge' style='margin-left:0;'><div class='monto-label'>Total con IVA</div><div class='monto-valor'>${sum(c['total'] for c in sel):,.2f}</div></div>", unsafe_allow_html=True)
        with k3:
            if sel:
                st.download_button("Descargar Excel", data=excel_cotizaciones(sel), key="rep_xlsx", use_container_width=True, type="secondary",
                                   file_name=f"cotizaciones_{date.today():%Y%m%d}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   help="Incluye tres hojas: cotizaciones, detalle de ítems y resumen por estado")
            else:
                st.button("Descargar Excel", disabled=True, use_container_width=True, key="rep_xlsx_off")
        if sel:
            st.dataframe(pd.DataFrame([{"Código": c["codigo"], "Evento": c["evento"], "Cliente": c["cliente"], "Fecha": fmt_fecha(c["fecha"]),
                                        "Estado": c["estado"], "Servicios": len(c["items"]), "Total ($)": c["total"]} for c in sel]),
                         hide_index=True, use_container_width=True, height=min(35 * (len(sel) + 1) + 3, 340),
                         column_config={"Total ($)": st.column_config.NumberColumn(format="$%.2f")})
        else:
            st.info("No hay cotizaciones con esos filtros.")


elif menu == MENU_PERFIL:
    encabezado_estandar("perfil", "Perfil de la empresa", "Se escribe una vez y sale en todos los documentos")
    emp = ss.empresa
    import base64 as _b64

    def _vista_encabezado():
        logo = emp.get("logo_b64") or LOGO_B64
        lineas = [x for x in (f"RUC {emp['ruc']}" if emp.get("ruc") else "", f"Tel. {emp['telefono']}" if emp.get("telefono") else "",
                              emp.get("correo", ""), emp.get("web", ""), emp.get("direccion", "")) if x]
        st.markdown(
            "<div style='display:flex; gap:22px; align-items:center; padding:6px 4px;'>"
            f"<img src='data:image/png;base64,{logo}' style='height:62px; max-width:190px; object-fit:contain;'/>"
            f"<div style='font-size:0.85rem; color:#475569; line-height:1.5;'><b style='color:#0F172A;'>{esc(emp.get('razon_social') or EMPRESA)}</b><br>"
            + " · ".join(esc(x) for x in lineas) + "</div></div>", unsafe_allow_html=True)

    t_dat, t_logo, t_cta, t_con, t_doc = st.tabs(["Datos generales", "Logo", "Cuentas bancarias", "Condiciones comerciales", "Documentación operativa"])

    with t_dat:
        with st.container(border=True, key="card_emp_prev"):
            st.markdown("<div class='sec-sub'>Así sale en los documentos</div>", unsafe_allow_html=True)
            _vista_encabezado()
        with st.container(border=True, key="card_emp_dat"):
            st.markdown("<div class='sec-sub'>Identificación</div>", unsafe_allow_html=True)
            a, b = st.columns(2)
            razon = a.text_input("Razón social", emp["razon_social"], key="emp_razon", placeholder="Nombre legal registrado en el SRI")
            ruc = b.text_input("RUC", emp["ruc"], key="emp_ruc", max_chars=13)
            a, b = st.columns(2)
            rep_n = a.text_input("Representante legal", emp["representante"], key="emp_rep")
            rep_c = b.text_input("Cargo", emp["cargo_representante"], key="emp_rep_c", placeholder="Gerente general")
            st.markdown("<div class='sec-sub'>Contacto y ubicación</div>", unsafe_allow_html=True)
            a, b = st.columns(2)
            tel = a.text_input("Teléfonos", emp["telefono"], key="emp_tel")
            correo = b.text_input("Correo", emp["correo"], key="emp_correo")
            a, b = st.columns(2)
            web = a.text_input("Sitio web", emp["web"], key="emp_web")
            ciudad_e = b.text_input("Ciudad", emp["ciudad"], key="emp_ciu")
            dire = st.text_input("Dirección", emp["direccion"], key="emp_dir")
            if st.button("Guardar datos", type="primary", key="emp_guardar"):
                if ruc.strip() and not (ruc.strip().isdigit() and len(ruc.strip()) == 13):
                    st.error("El RUC debe tener 13 números.")
                elif correo.strip() and "@" not in correo:
                    st.error("Revisa el correo: falta el @.")
                else:
                    emp.update({"razon_social": razon.strip(), "ruc": ruc.strip(), "representante": rep_n.strip(), "cargo_representante": rep_c.strip(),
                                "telefono": tel.strip(), "correo": correo.strip(), "web": web.strip(), "ciudad": ciudad_e.strip(), "direccion": dire.strip()})
                    st.toast("Datos de la empresa guardados", icon="✅")
                    st.rerun()

    with t_logo:
        with st.container(border=True, key="card_emp_logo"):
            st.markdown("<div class='sec-sub'>Logo de la empresa</div>", unsafe_allow_html=True)
            logo_actual = emp.get("logo_b64") or LOGO_B64
            st.markdown(f"<img src='data:image/png;base64,{logo_actual}' style='height:90px; max-width:300px; object-fit:contain; margin:4px 0 10px;'/>", unsafe_allow_html=True)
            arch = st.file_uploader("Subir un logo nuevo (PNG o JPG, de preferencia con fondo transparente)", type=["png", "jpg", "jpeg"], key="emp_logo_up")
            c1, c2 = st.columns([1, 1])
            if arch is not None and c1.button("Usar este logo", type="primary", key="emp_logo_ok"):
                emp["logo_b64"] = _b64.b64encode(arch.getvalue()).decode()
                st.rerun()
            if emp.get("logo_b64") and c2.button("Volver al logo original", key="emp_logo_reset"):
                emp["logo_b64"] = ""
                st.rerun()

    with t_cta:
        with st.container(border=True, key="card_emp_cta"):
            st.markdown("<div class='sec-sub'>Cuentas para recibir pagos</div>", unsafe_allow_html=True)
            st.caption("Salen al final de la cotización, en «Condiciones comerciales».")
            cuentas = editor_lista("emp_cuentas", emp["cuentas"], COL_CUENTAS, CFG_CUENTAS)
            if st.button("Guardar cuentas", type="primary", key="emp_cta_ok"):
                emp["cuentas"] = cuentas
                st.toast("Cuentas guardadas", icon="✅")
                st.rerun()

    with t_con:
        with st.container(border=True, key="card_emp_con"):
            st.markdown("<div class='sec-sub'>Condiciones que salen en la cotización</div>", unsafe_allow_html=True)
            a, b = st.columns([1, 3])
            validez = a.number_input("Validez de la oferta (días)", min_value=0, step=5, value=int(emp.get("validez_dias") or 0), key="emp_val")
            fpago = b.text_input("Forma de pago", emp.get("forma_pago", ""), key="emp_fpago", placeholder="Ej. 50% de anticipo y el saldo contra entrega")
            notas = st.text_area("Otras condiciones o notas", emp.get("notas_comerciales", ""), height=110, key="emp_notas",
                                 placeholder="Ej. Los precios no incluyen permisos municipales ni transporte fuera de la ciudad.")
            if st.button("Guardar condiciones", type="primary", key="emp_con_ok"):
                emp.update({"validez_dias": int(validez), "forma_pago": fpago.strip(), "notas_comerciales": notas.strip()})
                st.toast("Condiciones guardadas", icon="✅")
                st.rerun()

    with t_doc:
        with st.container(border=True, key="card_emp_doc"):
            st.markdown("<div class='sec-sub'>Documentación operativa</div>", unsafe_allow_html=True)
            st.info("Submódulo en construcción.")
            st.markdown("<div style='color:#475569; line-height:1.9;'>Lo que irá aquí:<br>"
                        "· Procedimientos paso a paso (montaje, bodega, atención al cliente)<br>"
                        "· Formatos y plantillas de la empresa<br>"
                        "· Normas de seguridad y checklists<br>"
                        "· Políticas internas y manual de funciones</div>", unsafe_allow_html=True)


# =============================================================================
# VISTA 1: PANEL DE INICIO
# =============================================================================
elif menu == "Panel de control":

    # 1. Título + accesos rápidos
    def _accesos():
        b1, b2, b3 = st.columns(3)
        b1.button("Crear cotización", use_container_width=True, type="primary", key="go_new",
                  on_click=ir, args=("Nueva cotización",), kwargs={"cotizacion_activa": None, "items_cot": []})
        b2.button("Directorio de clientes", use_container_width=True, type="secondary", key="go_cli", on_click=navegar, args=(MENU_CLIENTES,))
        b3.button("Directorio de proveedores", use_container_width=True, type="secondary", key="go_pro", on_click=navegar, args=(MENU_PROVEEDORES,))
    encabezado_estandar("panel", "Panel de control", "Resumen ejecutivo", volver=False, derecha=_accesos)

    # 2. Filtros globales (con key para poder borrarlos desde el botón "Borrar selección")
    cotizaciones = ss.cotizaciones_guardadas
    ciudad_cliente = {c["empresa"]: c["ciudad"] for c in ss.clientes_catalogo}
    with st.container(border=True, key="card_2"):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:0;'>Filtros operativos globales</div>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.selectbox("Filtrar por empresa / cuenta", ["Todas"] + sorted({c["cliente"] for c in cotizaciones}), key="f_emp")
        col_f2.selectbox("Filtrar por mes operativo", ["Todos"] + sorted({c["fecha"][:7] for c in cotizaciones}), key="f_mes")
        col_f3.selectbox("Filtrar por ciudad", ["Todas"] + CIUDADES, key="f_ciu")

    cots_dash = [
        c for c in cotizaciones
        if (ss.f_emp == "Todas" or c["cliente"] == ss.f_emp)
        and (ss.f_mes == "Todos" or c["fecha"][:7] == ss.f_mes)
        and (ss.f_ciu == "Todas" or ciudad_cliente.get(c["cliente"], "Desconocida") == ss.f_ciu)
    ]

    tot = {e: sum(c["total"] for c in cots_dash if c["estado"] == e) for e in ESTADOS}
    # Total general: todas las cotizaciones, sin filtros y de todos los tiempos (las canceladas no cuentan como ingreso)
    total_general = sum(c["total"] for c in cotizaciones if c["estado"] != "Cancelada")
    estado_actual = ss.filtro_estado_tabla
    hay_filtros = estado_actual != "Todas" or any(ss[k] != v for k, v in SIN_FILTRO.items())

    # 3. Tarjetas + gráficos
    with st.container(border=True, key="card_3"):
        c_tit, c_clear = st.columns([3, 2], vertical_alignment="center")
        c_tit.markdown("<div class='section-title'>Análisis financiero interactivo</div>", unsafe_allow_html=True)
        with c_clear:
            if hay_filtros:   # enlace discreto: borra tarjeta, filtros globales y buscador
                st.button(f"↺ Borrar filtros · Total general ${total_general:,.2f}", key="clear_btn", on_click=limpiar_filtros)
            else:
                st.markdown(f"<div class='total-general'>Total general: <b>${total_general:,.2f}</b></div>", unsafe_allow_html=True)

        etiquetas = {"Aprobada": "APROBADAS", "Enviada": "ENVIADAS", "Borrador": "BORRADORES", "Cancelada": "CANCELADAS"}
        for col, e in zip(st.columns(4), ESTADOS):
            col.button(f"{etiquetas[e]}\n${tot[e]:,.2f}", use_container_width=True, key=f"kpi_{e}", on_click=fijar_estado, args=(e,))

        st.markdown(f"<style>{css_tarjeta_activa(estado_actual)}</style>", unsafe_allow_html=True)  # anillo en la tarjeta activa

        st.markdown("<br>", unsafe_allow_html=True)
        col_donut, col_ley, col_trend = st.columns([0.95, 1.25, 2.45], gap="medium")

        with col_donut:
            if estado_actual == "Todas":   # distribución por estado
                df_donut = pd.DataFrame({"Segmento": ESTADOS, "Monto": [tot[e] for e in ESTADOS]})
                dominio, paleta, titulo_leyenda = ESTADOS, [COLORES[e] for e in ESTADOS], "Distribución por estado"
            else:                          # una tarjeta elegida: reparte ese estado por cliente (tonos del color de la tarjeta)
                por_cli = {}
                for c in cots_dash:
                    if c["estado"] == estado_actual:
                        por_cli[c["cliente"]] = por_cli.get(c["cliente"], 0.0) + c["total"]
                df_donut = pd.DataFrame({"Segmento": list(por_cli), "Monto": list(por_cli.values())})
                dominio = list(por_cli)
                base_rgb = tuple(int(COLORES[estado_actual][i:i + 2], 16) for i in (1, 3, 5))
                n = max(len(dominio), 1)
                paleta = ["#%02X%02X%02X" % tuple(int(v + (255 - v) * (0.55 * i / max(n - 1, 1))) for v in base_rgb) for i in range(n)]
                titulo_leyenda = f"{estado_actual}s por cliente"
            df_donut = df_donut[df_donut["Monto"] > 0]
            if df_donut.empty:
                st.info("Sin datos para distribución.")
            else:
                donut = alt.Chart(df_donut).mark_arc(innerRadius={"expr": "min(width, height) / 2 * 0.56"}, outerRadius={"expr": "min(width, height) / 2"}, cornerRadius=4, padAngle=0.03).encode(
                    theta=alt.Theta("Monto:Q"),
                    color=alt.Color("Segmento:N", scale=alt.Scale(domain=dominio, range=paleta), legend=None),
                    tooltip=[alt.Tooltip("Segmento", title="Detalle"), alt.Tooltip("Monto", format="$,.2f")],
                ).properties(height=176, padding={"left": 6, "right": 6, "top": 6, "bottom": 6})
                st.altair_chart(donut, use_container_width=True)
                # leyenda propia en su recuadro de alto fijo: si hay muchas empresas, solo ese recuadro se desplaza
                col_de = dict(zip(dominio, paleta))
                total_d = float(df_donut["Monto"].sum())
                filas_ley = "".join(
                    f"<div style='display:flex; align-items:center; gap:8px; padding:4px 0; font-size:0.82rem; color:#334155;'>"
                    f"<span style='width:10px; height:10px; border-radius:50%; background:{col_de[r.Segmento]}; flex:none;'></span>"
                    f"<span style='flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;' title='{r.Segmento}'>{r.Segmento}</span>"
                    f"<span style='flex:none; font-weight:700; color:#0F172A;'>{r.Monto / total_d:.0%}</span></div>"
                    for r in df_donut.itertuples())
                with col_ley:
                    st.markdown(f"<div style='height:176px; margin-top:8px; overflow-y:auto; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:8px 14px;'>"
                                f"<div style='font-size:0.74rem; font-weight:700; color:#64748B; letter-spacing:.04em; padding-bottom:4px; border-bottom:1px solid #E2E8F0; margin-bottom:2px;'>{titulo_leyenda}</div>{filas_ley}</div>",
                                unsafe_allow_html=True)

        with col_trend:
            # "Todas" = una serie por estado (incluye canceladas); una tarjeta = solo esa serie
            estados_graf = ESTADOS if estado_actual == "Todas" else [estado_actual]
            y_title = "Volumen ($)" if estado_actual == "Todas" else f"Volumen {estado_actual.upper()} ($)"
            filas = [c for c in cots_dash if c["estado"] in estados_graf]

            if filas:
                # Eje completo de meses (los meses sin movimiento valen 0, así la línea no une puntos lejanos)
                meses = pd.period_range(min(c["fecha"][:7] for c in cots_dash), max(c["fecha"][:7] for c in cots_dash), freq="M")
                orden = [f"{MESES_ES[p.month - 1]} {p.year}" for p in meses]
                df = pd.DataFrame({"Periodo": [pd.Period(c["fecha"][:7], "M") for c in filas],
                                   "Estado": [c["estado"] for c in filas], "Monto": [c["total"] for c in filas]})
                df = (df.pivot_table(index="Periodo", columns="Estado", values="Monto", aggfunc="sum")
                        .reindex(index=meses, columns=estados_graf).fillna(0.0))
                df.index = orden
                df = df.rename_axis(index="Mes", columns="Estado").stack().rename("Monto").reset_index()

                # symbolOpacity=1: la leyenda no hereda la transparencia del área
                color = alt.Color("Estado:N", scale=alt.Scale(domain=estados_graf, range=[COLORES[e] for e in estados_graf]),
                                  legend=alt.Legend(title=None, orient="top", symbolOpacity=1, symbolType="circle", labelFontSize=11, padding=2) if len(estados_graf) > 1 else None)
                base = alt.Chart(df).encode(
                    x=alt.X("Mes:O", sort=orden, title="Mes operativo", axis=alt.Axis(labelAngle=0, grid=False, labelColor="#64748B")),
                    y=alt.Y("Monto:Q", stack=None, title=y_title, axis=alt.Axis(format="$,.0f", gridColor="#E2E8F0", labelColor="#64748B")),
                    color=color,
                )
                grafico = (
                    base.mark_area(opacity=0.14, interpolate="monotone")                       # área sutil del color de la tarjeta
                    + base.mark_line(strokeWidth=2.5, interpolate="monotone")
                    + base.mark_point(filled=True, size=70, opacity=1).encode(
                        tooltip=["Estado:N", alt.Tooltip("Mes:O", title="Periodo"), alt.Tooltip("Monto:Q", format="$,.2f", title="Total")])
                ).properties(height=225, padding={"left": 4, "right": 8, "top": 4, "bottom": 4})
                st.altair_chart(grafico, use_container_width=True)
            else:
                st.markdown(f"<div style='padding-top:100px; text-align:center; color:#64748B;'>No hay ingresos registrados en la categoría <b>{estado_actual}</b> para el periodo seleccionado.</div>", unsafe_allow_html=True)

    # 4. Tabla detallada
    with st.container(border=True, key="card_4"):
        col_tit, col_bus = st.columns([2, 1])
        col_tit.markdown(f"<div class='section-title'>Detalle operativo: {estado_actual.upper()}</div>", unsafe_allow_html=True)
        busqueda = col_bus.text_input("Buscador...", key="b_u", label_visibility="collapsed", placeholder="Buscar código, evento o cliente...").lower()

        ev_filt = [c for c in cots_dash
                   if (estado_actual == "Todas" or c["estado"] == estado_actual)
                   and (not busqueda or busqueda in f"{c['codigo']} {c['evento']} {c['cliente']}".lower())]

        if ev_filt:
            ANCHOS = [1.3, 0.95, 1.9, 1.05, 2.5, 1.0, 0.8]
            TIT = ["CÓDIGO", "FECHA", "EVENTO", "ESTADO", "CLIENTE CORPORATIVO", "MONTO", ""]
            with st.container(key="tabla_det"):
                with st.container(key="det_head"):
                    hx = st.columns(ANCHOS, vertical_alignment="center")
                    for i, t in enumerate(TIT):
                        hx[i].markdown(f"<div class='col-head{' num' if i == 5 else ''}'>{t}</div>", unsafe_allow_html=True)
                for cot in ev_filt:
                    col_e = COLORES[cot["estado"]]
                    cx = st.columns(ANCHOS, vertical_alignment="center")
                    cx[0].markdown(f"<div class='cell'><b>{cot['codigo']}</b></div>", unsafe_allow_html=True)
                    cx[1].markdown(f"<div class='cell' style='color:#475569;'>{cot['fecha']}</div>", unsafe_allow_html=True)
                    cx[2].markdown(f"<div class='cell'>{cot['evento']}</div>", unsafe_allow_html=True)
                    cx[3].markdown(f"<div class='cell'><span class='badge-estado' style='color:{col_e}; background:{col_e}1F;'>{cot['estado'].upper()}</span></div>", unsafe_allow_html=True)
                    cx[4].markdown(f"<div class='cell'>{cot['cliente']}</div>", unsafe_allow_html=True)
                    cx[5].markdown(f"<div class='cell num'><b>${cot['total']:,.2f}</b></div>", unsafe_allow_html=True)
                    cx[6].button("Abrir", key=f"ab_{cot['codigo']}", type="secondary", use_container_width=True,
                                 on_click=ir, args=("Nueva cotización",),
                                 kwargs={"cotizacion_activa": cot, "items_cot": [dict(i) for i in cot.get("items", [])]})
        else:
            st.info("No hay cotizaciones para mostrar.")

# =============================================================================
# VISTA 2: NUEVA COTIZACIÓN
# =============================================================================
elif menu == "Nueva cotización":
    items = ss.items_cot
    tot_head = total_cliente(items)

    if ss.pop("confirmar_salida", False):
        dialogo_salida()
    def _monto():
        st.markdown(f"<div class='monto-badge'><div class='monto-label'>Monto estimado</div><div class='monto-valor'>${tot_head:,.2f}</div></div>", unsafe_allow_html=True)
    encabezado_estandar("cot", "Gestión de cotizaciones", "Datos del evento, servicios y totales", derecha=_monto)

    activa = ss.cotizacion_activa
    lista_cli = [c["empresa"] for c in ss.clientes_catalogo] + [NUEVO_CLIENTE]
    ESTADOS_COT = ["Borrador", "Enviada", "Aprobada", "Cancelada"]
    if "cliente_pendiente" in ss:   # cliente recién creado: queda seleccionado
        ss[_k("cli")] = ss.pop("cliente_pendiente")
    # el valor inicial solo se pasa la primera vez (después manda lo que el usuario haya elegido)
    ini_cli = {} if _k("cli") in ss else {"index": lista_cli.index(activa["cliente"]) if activa and activa["cliente"] in lista_cli else 0}
    ini_est = {} if _k("est") in ss else {"index": ESTADOS_COT.index(activa["estado"]) if activa else 0}
    fecha_def = date.fromisoformat(activa["fecha"]) if activa else date.today()

    with st.container(border=True, key="card_5"):
        st.markdown("<div class='section-title'>Información del evento</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c6, c5 = st.columns([1.4, 1.8, 2.3, 1.4, 1.1, 1.4])
        cod_cotizacion = c1.text_input("Referencia", value=activa["codigo"] if activa else siguiente_codigo(), key=_k("cod"))
        nombre_evento = c2.text_input("Nombre del evento", value=activa["evento"] if activa else "", key=_k("ev"))
        cliente_sel = c3.selectbox("Cuenta de cliente", lista_cli, key=_k("cli"), **ini_cli)
        fecha_gral = c4.date_input("Fecha", fecha_def, key=_k("fec"))
        invitados_cot = c6.number_input("Invitados", min_value=0, step=10, value=int(activa.get("invitados", 0)) if activa else 0, key=_k("inv"),
                                        help="Cantidad aproximada de invitados; pasa a las fichas de proveedores")
        estado_cot = c5.selectbox("Estado", ESTADOS_COT, key=_k("est"), **ini_est)

    if ss.cot_base is None:   # primera vez que se pinta el formulario: esto es "sin cambios"
        ss.cot_base = estado_formulario()

    if cliente_sel == NUEVO_CLIENTE:
        with st.container(border=True, key="card_6"):
            nuevo = form_cliente("nc", "<div class='section-title' style='color:#059669; border-color:#059669;'>Apertura de cuenta corporativa</div>")
            if nuevo:
                err = validar_cliente(nuevo)
                if err:
                    st.error(err)
                else:
                    crear_cliente(nuevo)
                    ss.cliente_pendiente = nuevo["empresa"]
                    st.rerun()

    with st.container(border=True, key="card_7"), st.expander(f"AÑADIR SERVICIOS  ·  {len(items)} en la cotización", expanded=True):
        tab_cat, tab_man = st.tabs(["Seleccionar del catálogo", "Ingreso manual"])

        with tab_cat:
            f1, f2, f3 = st.columns([1.1, 1.1, 1.8])
            ciu_f = f1.selectbox("Ciudad", CIUDADES, index=0, key="cat_ciu")
            en_ciudad = [p for p in ss.proveedores_catalogo if p["ciudad"] == ciu_f]
            cat_f = f2.selectbox("Categoría", ["Todas"] + sorted({p.get("categoria", "") for p in en_ciudad if p.get("categoria")}), key="cat_cat")
            pal_b = f3.text_input("Buscar", placeholder="Proveedor o servicio...", key="cat_bus").strip().lower()

            res = [p for p in en_ciudad
                   if (cat_f == "Todas" or p.get("categoria") == cat_f)
                   and (not pal_b or pal_b in f"{p['servicio']} {p['proveedor']}".lower())]
            res.sort(key=lambda p: (p["servicio"].lower(), p["precio_base"]))   # mismo servicio junto y de menor a mayor costo
            if not res:
                st.info(f"No hay servicios en {ciu_f} con ese filtro. Puedes registrarlos en la pestaña «Ingreso manual».")
            else:
                t_izq, t_der = st.columns([2.05, 1], gap="medium")
                df_cat = pd.DataFrame([{
                    "Servicio": r["servicio"], "Proveedor": r["proveedor"],
                    "Costo ($)": float(r["precio_base"]), "IVA": f"{int(r['iva'] * 100)}%"} for r in res])
                with t_izq:
                    ev_cat = st.dataframe(
                        df_cat, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row",
                        key=f"cat_tbl_{ciu_f}_{cat_f}_{pal_b}", height=min(35 * (len(df_cat) + 1) + 3, 215),
                        column_config={"Servicio": st.column_config.TextColumn(width=165), "Proveedor": st.column_config.TextColumn(width=150),
                                       "Costo ($)": st.column_config.NumberColumn(format="$%.2f", width=75),
                                       "IVA": st.column_config.TextColumn(width=50)})
                    st.caption(f"{len(res)} servicio(s) en {ciu_f}. Del mismo servicio, primero el más económico.")
                item_sel = res[ev_cat.selection.rows[0]] if ev_cat.selection.rows else None
                with t_der:
                    if not item_sel:
                        st.markdown("<div style='padding:14px; border:1px dashed #C9D3E0; border-radius:8px; color:#64748B; font-size:0.9rem; margin-top:4px;'>Elige un servicio de la tabla (recuadro de la izquierda) para completar los datos.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding:8px 12px; background:#EEF2F7; border-left:5px solid #1E3A8A; border-radius:6px; font-size:0.88rem; color:#0F172A; line-height:1.35;'>"
                                    f"<b>{item_sel['servicio']}</b><br>{item_sel['proveedor']} · {ciu_f}"
                                    + ("<br><span style='color:#B45309;'>Ficha del proveedor pendiente</span>" if faltantes_proveedor(proveedor_de(item_sel["proveedor"])) else "") + "</div>", unsafe_allow_html=True)
                        d1, d2 = st.columns([1.5, 1])
                        f_it = d1.date_input("Fecha", value=fecha_gral)
                        can_it = d2.number_input("Cantidad", min_value=1, value=1)
                        d3, d4, d5 = st.columns([1.05, 1.2, 1])
                        cos_it = d3.number_input("Costo ($)", value=float(item_sel["precio_base"]))
                        iva_it = d4.selectbox("IVA", [0.0, 0.15], index=1 if item_sel["iva"] > 0 else 0, format_func=lambda x: f"{int(x*100)}%")
                        fee_it = d5.number_input("Margen", value=20.00, step=5.00, format="%.2f")
                        if st.button("Agregar a la cotización", type="primary", use_container_width=True, key="add_cat"):
                            items.append({"servicio": item_sel["servicio"], "proveedor": item_sel["proveedor"], "ciudad": ciu_f, "fecha": str(f_it),
                                          "cantidad": can_it, "costo": cos_it, "iva_prov": iva_it, "fee_pct": fee_it})
                            st.rerun()

        with tab_man:
            nc1, nc2, nc3, nc4 = st.columns(4)
            n_pro = nc1.text_input("Proveedor *")
            n_ser = nc2.text_input("Servicio *")
            n_ciu = selector_ciudad(nc3, "Ciudad op.", "mc_c")
            n_cat = nc4.text_input("Categoría")
            ca, cb, cc, cd, ce, cf = st.columns([1.3, 0.8, 1.1, 0.9, 1.0, 1.4], vertical_alignment="bottom")
            f_it_m = ca.date_input("Fecha de servicio", value=fecha_gral, key="mc_f")
            can_it_m = cb.number_input("Cantidad", min_value=1, value=1, key="mc_ca")
            cos_it_m = cc.number_input("Costo unit. ($)", value=0.00, format="%.2f", key="mc_co")
            iva_it_m = cd.selectbox("IVA prov.", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x*100)}%", key="mc_i")
            fee_it_m = ce.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f", key="mc_ma")
            g_bd = st.checkbox("Guardar en directorio", value=True)
            if cf.button("Agregar", type="primary", use_container_width=True, key="add_man"):
                if n_pro.strip() and n_ser.strip():
                    items.append({"servicio": n_ser, "proveedor": n_pro, "ciudad": n_ciu, "fecha": str(f_it_m),
                                  "cantidad": can_it_m, "costo": cos_it_m, "iva_prov": iva_it_m, "fee_pct": fee_it_m})
                    if g_bd:
                        if asegurar_proveedor(n_pro.strip(), n_ciu, n_cat or "General"):
                            ss.aviso_pendiente = f"Proveedor «{n_pro.strip()}» creado. Complétalo luego en Directorios."
                        ss.proveedores_catalogo.append({"servicio": n_ser, "proveedor": n_pro.strip(), "categoria": n_cat or "General", "ciudad": n_ciu,
                                                        "precio_base": cos_it_m, "iva": iva_it_m, "descripcion": "Manual"})
                    st.rerun()
                else:
                    st.error("Proveedor y servicio requeridos.")

    if items:
        with st.container(border=True, key="card_8"):
            st.markdown("<div class='section-title'>Estructura de costos</div>", unsafe_allow_html=True)
            # Una línea por servicio, una columna por dato. Los 4 últimos anchos son ✎ ↑ ↓ ✕ (botones compactos)
            ANCHOS = [2.0, 2.2, 1.15, 0.95, 0.6, 1.0, 0.6, 0.8, 1.0, 1.1, 0.38, 0.38, 0.38, 0.38]
            TITULOS = ["PROVEEDOR", "SERVICIO", "FECHA", "CIUDAD", "CANT.", "COSTO U.", "IVA", "MARGEN %", "MARGEN $", "SUBTOTAL", "", "", "", ""]
            NUM = {4, 5, 6, 7, 8, 9}   # columnas numéricas: alineadas a la derecha

            s_prov = t_fee = s_com = 0.0
            accion = None  # (tipo, idx): se ejecuta una sola vez al final, fuera del bucle
            with st.container(key="tabla_costos"):
                with st.container(key="costos_head"):
                    hx = st.columns(ANCHOS, vertical_alignment="center")
                    for i, t in enumerate(TITULOS):
                        hx[i].markdown(f"<div class='col-head{' num' if i in NUM else ''}'>{t}</div>", unsafe_allow_html=True)

                for idx, item in enumerate(items):
                    c_iva, f_val, p_ven = calcular_linea(item)
                    s_prov += c_iva; t_fee += f_val; s_com += p_ven

                    valores = [
                        f"<b>{item['proveedor']}</b>", item["servicio"], item["fecha"], item["ciudad"],
                        f"{item['cantidad']}", f"${item['costo']:,.2f}", f"{int(item['iva_prov'] * 100)}%",
                        f"{item['fee_pct']:.0f}%", f"<span class='pos'>+${f_val:,.2f}</span>", f"<b>${p_ven:,.2f}</b>",
                    ]
                    cx = st.columns(ANCHOS, vertical_alignment="center")
                    for i, v in enumerate(valores):
                        cx[i].markdown(f"<div class='cell{' num' if i in NUM else ''}'>{v}</div>", unsafe_allow_html=True)
                    if cx[10].button("✎", key=f"edit_{idx}", help="Editar este servicio"):
                        accion = ("edit", idx)
                    if cx[11].button("↑", key=f"mv_up_{idx}", disabled=idx == 0, help="Subir"):
                        accion = ("up", idx)
                    if cx[12].button("↓", key=f"mv_dn_{idx}", disabled=idx == len(items) - 1, help="Bajar"):
                        accion = ("dn", idx)
                    if cx[13].button("✕", key=f"del_{idx}", help="Eliminar"):
                        accion = ("del", idx)

            if accion and accion[0] == "edit":
                dialogo_editar(accion[1])
            elif accion:
                tipo, i = accion
                if tipo == "del":
                    items.pop(i)
                else:
                    j = i - 1 if tipo == "up" else i + 1
                    items[i], items[j] = items[j], items[i]
                st.rerun()

            iva_cli = s_com * IVA_CLIENTE
            t_cli = s_com + iva_cli
            # Barra inferior fija: totales y acciones siempre a la vista aunque la cotización sea larga
            with st.container(key="barra_total"):
                cm1, cm2, ci, c_acc = st.columns([1.1, 1.1, 1.7, 1.15], vertical_alignment="center")
                cm1.markdown(f"<div class='metric-tile'><div class='internal-metrics'>Costos operativos</div><div class='internal-metrics-value'>${s_prov:,.2f}</div></div>", unsafe_allow_html=True)
                cm2.markdown(f"<div class='metric-tile ganancia'><div class='internal-metrics'>Rentabilidad</div><div class='internal-metrics-value'>${t_fee:,.2f}</div></div>", unsafe_allow_html=True)
                ci.markdown(f"<div class='invoice-container'><div class='invoice-row'><span>Subtotal</span><span>${s_com:,.2f}</span></div><div class='invoice-row'><span>IVA 15%</span><span>${iva_cli:,.2f}</span></div><div class='invoice-total'><span>TOTAL INVERSIÓN</span><span>${t_cli:,.2f}</span></div></div>", unsafe_allow_html=True)
                c_save = c_pdf = c_acc
                if c_save.button("Guardar cotización", use_container_width=True, type="primary", key="btn_save"):
                    if guardar_cotizacion(activa, cod_cotizacion, nombre_evento, cliente_sel, fecha_gral, estado_cot, t_cli, invitados_cot):
                        st.toast("Cotización guardada. Ya puedes generar el PDF.")

                # El PDF se habilita cuando la cotización está guardada y sin cambios pendientes (así siempre refleja lo guardado)
                guardada = ss.cotizacion_activa
                pdf, ayuda = None, "Guarda la cotización para generar el PDF."
                if guardada and estado_formulario() == ss.cot_base:
                    try:
                        cli_pdf = next((c for c in ss.clientes_catalogo if c["empresa"] == guardada["cliente"]), None)
                        pdf, ayuda = generar_pdf(guardada, cli_pdf), "Descargar la cotización en PDF."
                    except ImportError:
                        ayuda = "Falta instalar reportlab (agrégalo a requirements.txt)."
                elif guardada:
                    ayuda = "Hay cambios sin guardar: guarda la cotización para actualizar el PDF."
                c_pdf.download_button("Generar PDF", data=pdf or b"", file_name=f"{(guardada or {}).get('codigo', 'cotizacion')}.pdf",
                                      mime="application/pdf", disabled=pdf is None, use_container_width=True, key="btn_pdf", help=ayuda)

# =============================================================================
# COTIZADOR DE CATÁLOGOS (regular y navideño): página HTML incrustada
# =============================================================================
elif menu in CATALOGOS:
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

# =============================================================================
# ÓRDENES A PROVEEDORES (cotización aprobada -> datos del evento -> una ficha de contratación por proveedor)
# =============================================================================
elif menu == MENU_PROV:
    encabezado_modulo("prov",
        "<style>.block-container{padding-top:2.4rem !important;}</style>"
        "<div style='background:#134E4A; border-radius:14px; padding:12px 24px; margin:0 0 12px 0;'>"
        "<div style='font-size:0.78rem; font-weight:600; color:#99F6E4;'>Operaciones</div>"
        "<div style='font-size:1.9rem; font-weight:900; color:#FFFFFF; line-height:1.05; letter-spacing:-0.02em;'>Órdenes a proveedores</div></div>",
        unsafe_allow_html=True)
    lista = aprobadas_con(propio=False)
    if not lista:
        st.info("No hay cotizaciones aprobadas con servicios de proveedores externos. Cuando apruebes una, aparecerá aquí.")
    else:
        etiquetas = {f"{c['codigo']} · {c['evento']} · {c['cliente']}": c for c in lista}
        cot = etiquetas[st.selectbox("Cotización aprobada", list(etiquetas), key="prov_cot")]
        cod = cot["codigo"]
        externos = {p: its for p, its in agrupar_por_proveedor(cot).items() if p != EMPRESA}
        listo_evento = cod in ss.eventos
        n_fichas = sum(1 for p in externos if f"{cod}|{p}" in ss.fichas)
        st.caption(f"{len(externos)} proveedor(es) en esta cotización · {n_fichas} ficha(s) guardada(s) · "
                   + ("datos del evento listos" if listo_evento else "faltan los datos del evento"))
        tab_ev, tab_fi = st.tabs(["1. Datos del evento", "2. Fichas de proveedores"])

        with tab_ev:
            st.caption("Fecha, lugar, horario, quién recibe, montaje... Se escriben una sola vez y salen en cada ficha y en el pedido a bodega.")
            ev = bloque_evento(cot, "prov")
        with tab_fi:
            ev = {**evento_inicial(cot), **ss.eventos.get(cod, {})}
            if not listo_evento:
                st.warning("Primero guarda los datos del evento (pestaña 1). Sin ellos no se pueden descargar las fichas.")
            for n, (prov, items) in enumerate(externos.items()):
                clave = f"{cod}|{prov}"
                guardada = ss.fichas.get(clave)
                with st.container(border=True, key=f"orden_{n}"):
                    cab1, cab2 = st.columns([4, 1.6], vertical_alignment="center")
                    estado = ("<span class='badge-estado' style='color:#047857; background:#D1FAE5;'>FICHA GUARDADA</span>" if guardada
                              else "<span class='badge-estado' style='color:#B45309; background:#FEF3C7;'>PENDIENTE</span>")
                    cab1.markdown(f"<div style='font-size:1.15rem; font-weight:800; color:#0F172A;'>{prov} &nbsp;{estado}</div>", unsafe_allow_html=True)
                    if guardada and guardada.get("firma") != firma_items(items):
                        w1, w2 = st.columns([4, 1.4], vertical_alignment="center")
                        w1.warning("La cotización cambió después de guardar esta ficha. Actualízala para que coincida.")
                        if w2.button("Actualizar desde la cotización", key=f"act_{n}_{cod}", type="primary", use_container_width=True):
                            ss.fichas.pop(clave, None)
                            st.rerun()
                    falta = faltantes_proveedor(proveedor_de(prov))
                    if falta:
                        q1, q2 = st.columns([4, 1.6], vertical_alignment="center")
                        q1.warning(f"A este proveedor le falta: {', '.join(falta)}.")
                        q2.button("Completar proveedor", key=f"comp_{n}_{cod}", type="primary", use_container_width=True,
                                  on_click=completar_proveedor, args=(prov, items[0]["ciudad"]))
                    fp = {**proveedor_inicial(cot, prov, items), **{k: v for k, v in (guardada or {}).items() if k != "firma"}}
                    st.dataframe(pd.DataFrame([{"Servicio": i["servicio"], "Fecha": fmt_fecha(i["fecha"]), "Ciudad": i["ciudad"], "Cantidad": i["cantidad"]} for i in items]),
                                 hide_index=True, use_container_width=True, height=min(35 * (len(items) + 1) + 3, 240))
                    con = proveedor_de(prov).get("contactos", [])
                    if con:
                        st.caption("Contacto en el directorio: " + " · ".join(f"{x['nombre']} {x['telefono']}".strip() for x in con))
                    with st.expander("Completar ficha de contratación"):
                        with st.form(f"form_ficha_{n}_{cod}"):
                            serv = st.text_area("Servicio requerido", fp["servicio"], height=150, key=f"fp_s_{n}_{cod}")
                            g1, g2, g3, g4 = st.columns(4)
                            tot = g1.text_input("Total", fp["total"], key=f"fp_t_{n}_{cod}")
                            abo = g2.text_input("Abono", fp["abono"], key=f"fp_a_{n}_{cod}")
                            gar = g3.text_input("Garantía", fp["garantia"], key=f"fp_g_{n}_{cod}")
                            tra = g4.text_input("Transporte", fp["transporte"], key=f"fp_tr_{n}_{cod}")
                            h1, h2 = st.columns(2)
                            pago = h1.text_input("Forma de pago", fp["pago"], key=f"fp_p_{n}_{cod}")
                            fac = h2.text_input("Factura", fp["factura"], key=f"fp_f_{n}_{cod}")
                            ali_fi = st.segmented_control("¿Esta ficha lleva las necesidades de alimentación (vegetarianos, alergias)?", ["Sí", "No"],
                                                          default="Sí" if fp.get("alimentacion", True) else "No", key=f"fp_al_{n}_{cod}") or "Sí"
                            st.caption("La accesibilidad siempre se incluye. Apaga la alimentación solo si el servicio no tiene relación con comida.")
                            if st.form_submit_button("Guardar ficha", type="primary"):
                                ss.fichas[clave] = {"servicio": serv, "total": tot, "abono": abo, "garantia": gar, "transporte": tra,
                                                    "pago": pago, "factura": fac, "alimentacion": ali_fi == "Sí", "firma": firma_items(items)}
                                st.rerun()
                    d1, d2 = st.columns(2)
                    d1.download_button("Ficha de contratación (PDF)", data=pdf_ficha(cot, prov, ev, fp) if listo_evento else b"", disabled=not listo_evento,
                                       file_name=f"Ficha_{cod}_{prov.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True, key=f"dlf_{n}_{cod}")
                    d2.download_button("Orden de servicios - checklist (PDF)", data=pdf_orden(cot, prov, items),
                                       file_name=f"Orden_{cod}_{prov.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True, key=f"dl_{n}_{cod}")

# =============================================================================
# BODEGA (pedido generado desde la cotización + checklist detallado del bodeguero)
# =============================================================================
elif menu == MENU_BODEGA:
    encabezado_modulo("bod",
        "<style>.block-container{padding-top:2.4rem !important;}</style>"
        "<div style='background:#134E4A; border-radius:14px; padding:12px 24px; margin:0 0 12px 0;'>"
        "<div style='font-size:0.78rem; font-weight:600; color:#99F6E4;'>Operaciones</div>"
        "<div style='font-size:1.9rem; font-weight:900; color:#FFFFFF; line-height:1.05; letter-spacing:-0.02em;'>Bodega</div></div>",
        unsafe_allow_html=True)
    lista = aprobadas_con(propio=True)
    if not lista:
        st.info(f"No hay cotizaciones aprobadas con servicios de {EMPRESA}. Cuando apruebes una, aparecerá aquí.")
    else:
        etiquetas = {f"{c['codigo']} · {c['evento']} · {c['cliente']}": c for c in lista}
        cot = etiquetas[st.selectbox("Cotización aprobada", list(etiquetas), key="bod_cot")]
        cod = cot["codigo"]
        items = [i for i in cot["items"] if i["proveedor"] == EMPRESA]
        hojas = ss.hojas.setdefault(cod, {})
        if cod not in ss.eventos:
            st.warning("Faltan los datos del evento (fecha, lugar, horario, quién recibe...). Complétalos aquí para generar el pedido.")
            with st.expander("Datos del evento", expanded=True):
                bloque_evento(cot, "bod")
        else:
            ev = {**evento_inicial(cot), **ss.eventos[cod]}
            with st.expander("Datos del evento"):
                ev = bloque_evento(cot, "bod")
            tab_ped, tab_chk = st.tabs(["Pedido a bodega", "Checklist del bodeguero"])

            with tab_ped:
                st.caption("Pedido generado desde la cotización aprobada: los servicios de Karkajadas Group que deben salir de bodega.")
                filas = []
                for i in items:
                    hoja = hojas.get(i["servicio"], [])
                    if not hoja:
                        est = "Sin checklist"
                    else:
                        est = f"Salió {sum(p['salio'] for p in hoja)}/{len(hoja)} · Regresó {sum(p['regreso'] for p in hoja)}/{len(hoja)}"
                    filas.append({"Servicio": i["servicio"], "Cantidad": i["cantidad"], "Fecha": fmt_fecha(i["fecha"]), "Ciudad": i["ciudad"], "Estado en bodega": est})
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True, height=min(35 * (len(filas) + 1) + 3, 300))
                st.download_button("Pedido a bodega (PDF)", data=pdf_pedido_bodega(cot, items, ev), file_name=f"Pedido_bodega_{cod}.pdf", mime="application/pdf", key=f"dlp_{cod}")

            with tab_chk:
                st.caption("El bodeguero detalla las piezas de cada servicio y marca cuando salen y cuando regresan. Lo que guardas aquí queda como plantilla para la próxima vez.")
                for j, it in enumerate(items):
                    s_ = it["servicio"]
                    with st.container(border=True, key=f"chk_{j}"):
                        st.markdown(f"<div style='font-size:1.05rem; font-weight:800; color:#0F172A;'>{s_} <span style='font-weight:600; color:#64748B;'>· {it['cantidad']} unidad(es) · {fmt_fecha(it['fecha'])} · {it['ciudad']}</span></div>", unsafe_allow_html=True)
                        actual = hojas.get(s_)
                        if actual is None and ss.plantillas.get(s_):
                            if st.button("Usar las piezas de la última vez", key=f"plt_{j}_{cod}", type="primary"):
                                hojas[s_] = [{"pieza": p["pieza"], "cantidad": p["cantidad"] * int(it["cantidad"]), "salio": False, "regreso": False, "obs": ""} for p in ss.plantillas[s_]]
                                st.rerun()
                        df = pd.DataFrame(actual or [], columns=["pieza", "cantidad", "salio", "regreso", "obs"])
                        if df.empty:
                            df = pd.DataFrame([{"pieza": "", "cantidad": 1, "salio": False, "regreso": False, "obs": ""}])
                        ver = ss.get(f"hoja_ver_{cod}_{j}", 0)
                        with st.form(f"form_hoja_{cod}_{j}_{ver}"):
                            ed = st.data_editor(df, num_rows="dynamic", hide_index=True, use_container_width=True, key=f"hoja_{cod}_{j}_{ver}",
                                                column_config={"pieza": st.column_config.TextColumn("Pieza", required=True),
                                                               "cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1, default=1),
                                                               "salio": st.column_config.CheckboxColumn("Salió", default=False),
                                                               "regreso": st.column_config.CheckboxColumn("Regresó", default=False),
                                                               "obs": st.column_config.TextColumn("Observación")})
                            if st.form_submit_button("Guardar checklist", type="primary"):
                                filas = [{"pieza": str(r["pieza"]).strip(), "cantidad": int(r["cantidad"] or 1), "salio": bool(r["salio"]),
                                          "regreso": bool(r["regreso"]), "obs": "" if str(r["obs"]) == "nan" else str(r["obs"])}
                                         for _, r in ed.iterrows() if str(r["pieza"]).strip() and str(r["pieza"]) != "nan"]
                                hojas[s_] = filas
                                q = max(int(it["cantidad"]), 1)
                                ss.plantillas[s_] = [{"pieza": p["pieza"], "cantidad": max(round(p["cantidad"] / q), 1)} for p in filas]
                                st.rerun()
                        hoja = hojas.get(s_, [])
                        if hoja:
                            st.caption(f"Salió {sum(p['salio'] for p in hoja)} de {len(hoja)} · Regresó {sum(p['regreso'] for p in hoja)} de {len(hoja)}")
                st.download_button("Checklist de bodega (PDF)", data=pdf_hoja_bodega(cot, items, ev), file_name=f"Checklist_bodega_{cod}.pdf", mime="application/pdf", key=f"dlh_{cod}")

# =============================================================================
# VISTA 3: DIRECTORIOS
# =============================================================================
elif menu in (MENU_CLIENTES, MENU_PROVEEDORES):
    encabezado_estandar("dir", menu, "Cuentas, contactos y datos de facturación" if menu == MENU_CLIENTES else "Contactos, servicios y costos")

    with st.container(border=True, key="card_9"):
        if menu == MENU_CLIENTES:
            def fila_cliente(c):
                con, mail, tel = resumen_contactos(c)
                return {"Empresa": c["empresa"], "RUC": c["ruc"], "Ciudad": c["ciudad"], "Contacto": con, "Correo": mail, "Teléfono": tel,
                        "Direcciones": len(c.get("direcciones", [])), "Días crédito": c["dias_credito"]}
            panel_directorio(
                "cli", ss.clientes_catalogo, fila_cliente,
                lambda c: " ".join([c["empresa"], c["ruc"], c["ciudad"]] + [f"{x['nombre']} {x['correo']} {x['telefono']}" for x in c.get("contactos", [])]),
                form_cliente, validar_cliente, crear_cliente, actualizar_cliente, lambda c: c["empresa"], "Nueva cuenta")

        if menu == MENU_PROVEEDORES:
            sub_prov, sub_serv = st.tabs(["Proveedores (datos de contacto)", "Servicios y costos"])

            with sub_prov:
                def fila_proveedor(p):
                    con, mail, tel = resumen_contactos(p)
                    cta = p["cuentas"][0] if p.get("cuentas") else {}
                    return {"Proveedor": p["proveedor"], "Estado": "Incompleto" if faltantes_proveedor(p) else "Completo",
                            "Categoría": p["categoria"], "Ciudad": p["ciudad"], "Contacto": con, "Correo": mail, "Teléfono": tel,
                            "Banco": f"{cta.get('banco', '')} {cta.get('numero', '')}".strip(),
                            "Servicios": sum(1 for r in ss.proveedores_catalogo if r["proveedor"] == p["proveedor"])}
                n_inc = sum(1 for p in ss.proveedores if faltantes_proveedor(p))
                ss.setdefault("dir_prv_solo", False)
                if n_inc:
                    a1, a2 = st.columns([4, 1.6], vertical_alignment="center")
                    a1.warning(f"{n_inc} proveedor(es) por completar (falta RUC o un contacto con teléfono).")
                    a2.checkbox("Ver solo los incompletos", key="dir_prv_solo")
                else:
                    ss.dir_prv_solo = False
                    st.caption("Todos los proveedores tienen su información básica completa.")
                panel_directorio(
                    "prv", ss.proveedores, fila_proveedor,
                    lambda p: " ".join([p["proveedor"], p["categoria"], p["ciudad"], p.get("ruc", "")] + [f"{x['nombre']} {x['correo']} {x['telefono']}" for x in p.get("contactos", [])]),
                    form_proveedor, validar_proveedor, crear_proveedor, actualizar_proveedor, lambda p: p["proveedor"], "Nuevo proveedor",
                    filtro=(lambda p: bool(faltantes_proveedor(p))) if ss.dir_prv_solo else None)

            with sub_serv:
                st.caption("Edita directamente en la tabla: cambia un valor con doble clic, agrega una fila con ＋ al final, o borra una fila seleccionándola y pulsando la papelera.")
                ver_s = ss.setdefault("serv_ver", 0)
                nombres = [p["proveedor"] for p in ss.proveedores]
                df_s = pd.DataFrame([{"proveedor": r["proveedor"], "servicio": r["servicio"], "categoria": r.get("categoria", ""), "ciudad": r["ciudad"],
                                      "precio_base": float(r["precio_base"]), "iva": f"{int(r['iva'] * 100)}%", "descripcion": r.get("descripcion", "")}
                                     for r in ss.proveedores_catalogo],
                                    columns=["proveedor", "servicio", "categoria", "ciudad", "precio_base", "iva", "descripcion"])
                ed_s = st.data_editor(
                    df_s, num_rows="dynamic", hide_index=True, use_container_width=True, key=f"serv_ed_{ver_s}",
                    column_config={"proveedor": st.column_config.SelectboxColumn("Proveedor", options=nombres, required=True),
                                   "servicio": st.column_config.TextColumn("Servicio", required=True),
                                   "categoria": st.column_config.TextColumn("Categoría"),
                                   "ciudad": st.column_config.SelectboxColumn("Ciudad", options=CIUDADES),
                                   "precio_base": st.column_config.NumberColumn("Costo ($)", min_value=0.0, format="$%.2f"),
                                   "iva": st.column_config.SelectboxColumn("IVA", options=["0%", "15%"]),
                                   "descripcion": st.column_config.TextColumn("Descripción")})
                if st.button("Guardar cambios en servicios", type="primary", key="serv_save"):
                    nuevos, error = [], None
                    for r in ed_s.to_dict("records"):
                        f = {k: ("" if _vacio(v) else v) for k, v in r.items()}
                        if not any(str(v).strip() for v in f.values()):
                            continue
                        if not (str(f["proveedor"]).strip() and str(f["servicio"]).strip()):
                            error = "Cada servicio necesita proveedor y nombre del servicio."
                            break
                        nuevos.append({"proveedor": f["proveedor"], "servicio": str(f["servicio"]).strip(), "categoria": str(f["categoria"]).strip(),
                                       "ciudad": f["ciudad"] or CIUDADES[0], "precio_base": float(f["precio_base"] or 0),
                                       "iva": 0.15 if f["iva"] == "15%" else 0.0, "descripcion": str(f["descripcion"]).strip()})
                    if error:
                        st.error(error)
                    else:
                        ss.proveedores_catalogo = nuevos
                        ss.serv_ver += 1
                        st.toast("Servicios guardados")
                        st.rerun()
