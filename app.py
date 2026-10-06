import json
from html import escape as esc
from pathlib import Path
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, datetime

# Requiere Streamlit >= 1.39 (usa las clases .st-key-<key> para estilizar botones)

# =============================================================================
# CONSTANTES
# =============================================================================
ESTADOS = ["Aprobada", "Enviada", "Borrador", "Cancelada"]
COLORES = {
    "Aprobada": "#059669",   # verde
    "Enviada": "#1E3A8A",    # azul
    "Borrador": "#64748B",   # gris
    "Cancelada": "#EF4444",  # rojo
}
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
CIUDADES = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]
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

/* Botones globales: verde = avanzar, azul = neutro */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: #059669 !important; border: 1px solid #059669 !important; color: #FFFFFF !important;
    border-radius: 8px !important; font-weight: 600 !important; transition: all .2s ease !important; box-shadow: none !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { background-color: #047857 !important; transform: translateY(-1px); }
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: #1E3A8A !important; border: 1px solid #1E3A8A !important; color: #FFFFFF !important;
    border-radius: 8px !important; font-weight: 600 !important; transition: all .2s ease !important; box-shadow: none !important;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover { background-color: #1E40AF !important; transform: translateY(-1px); }

/* Tarjetas KPI (el color de cada una, incluido hover/focus, se agrega por código según su estado) */
[class*="st-key-kpi_"] button {
    width: 100% !important; min-height: 85px !important; padding: 12px 10px !important; border-radius: 8px !important;
    justify-content: flex-start !important; text-align: left !important; box-shadow: 0 3px 5px rgba(0,0,0,.15) !important;
}
[class*="st-key-kpi_"] button * { color: #FFFFFF !important; }
[class*="st-key-kpi_"] button p { font-size: 15px !important; font-weight: 800 !important; white-space: pre-wrap !important; margin: 0 !important; line-height: 1.3 !important; }
[class*="st-key-kpi_"] button:hover { filter: brightness(.9); transform: translateY(-3px) !important; }

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
[class*="st-key-mv_"] button, [class*="st-key-del_"] button { padding: 0 !important; min-height: 26px !important; height: 26px !important; width: 100% !important; font-size: 13px !important; line-height: 1 !important; }
[class*="st-key-mv_"] button { background: #E9EEF5 !important; border: 1px solid #CBD5E1 !important; color: #475569 !important; box-shadow: none !important; border-radius: 6px !important; }
[class*="st-key-mv_"] button:hover { background: #DCE5F0 !important; color: #1E3A8A !important; border-color: #94A3B8 !important; }
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
.brand-logo { font-size: 22px; font-weight: 900; color: #FFFFFF; margin: 5px 0 20px; padding-left: 5px; }
[data-testid="stSidebar"] div[data-testid="stButton"] { width: 100% !important; margin-bottom: 2px !important; }
[data-testid="stSidebar"] div[data-testid="stButton"] button {
    background-color: #1E293B !important; border: 1px solid #334155 !important; color: #CBD5E1 !important; border-radius: 8px !important;
    padding: 12px 15px !important; width: 100% !important; display: flex !important; justify-content: flex-start !important;
    box-shadow: 0 2px 4px rgba(0,0,0,.1) !important; transition: all .3s ease !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] button p { width: 100% !important; text-align: left !important; font-weight: 500 !important; margin: 0 !important; }
[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
    background-color: #334155 !important; color: #FFFFFF !important; border-color: #475569 !important;
    box-shadow: 0 8px 15px rgba(0,0,0,.4) !important; transform: translateX(4px) !important;
}

/* Campos: cada recuadro tiene fondo gris azulado, borde definido y sombra interior (se distingue del fondo blanco de la tarjeta) */
[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"], [data-testid="stDateInputField"], [data-testid="stSelectbox"] [role="group"] {
    background-color: #EEF2F7 !important; border: 1px solid #B4C0D0 !important; border-radius: 8px !important;
    box-shadow: inset 0 1px 2px rgba(15,23,42,.08) !important; transition: border-color .15s, background-color .15s, box-shadow .15s;
}
[data-testid="stTextInputRootElement"]:hover, [data-testid="stNumberInputContainer"]:hover, [data-testid="stDateInputField"]:hover, [data-testid="stSelectbox"] [role="group"]:hover { border-color: #7C8CA3 !important; }
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within, [data-testid="stDateInputField"]:focus-within, [data-testid="stSelectbox"] [role="group"]:focus-within {
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
.monto-badge { text-align: right; line-height: 1; margin-bottom: 8px; }
.monto-label { font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #64748B; margin-bottom: 6px; }
.monto-valor { font-size: 46px; font-weight: 900; letter-spacing: -.02em; color: #1E3A8A; font-variant-numeric: tabular-nums; }
.monto-valor .mon { font-size: 26px; font-weight: 800; color: #059669; margin-right: 4px; vertical-align: top; position: relative; top: 4px; }
.monto-badge::after { content: ""; display: block; width: 56px; height: 4px; border-radius: 2px; background: #059669; margin: 8px 0 0 auto; }
.invoice-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; color: #475569; }
.invoice-total { display: flex; justify-content: space-between; border-top: 2px solid #CBD5E1; padding-top: 10px; margin-top: 10px; font-size: 20px; font-weight: 800; color: #1E3A8A; }
"""


def css_kpi():
    """Un color por tarjeta, tomado de COLORES. Se fija también en :hover/:focus/:active
    (con mayor especificidad que el estilo global de botones) para que el hover no la pinte de azul."""
    reglas = []
    for e in ESTADOS:
        c = COLORES[e]
        sel = ", ".join(f"div.st-key-kpi_{e} button{p}" for p in ("", ":hover", ":focus", ":active"))
        reglas.append(f"{sel}{{background:{c} !important;border:1px solid {c} !important;color:#FFFFFF !important;}}")
    return "".join(reglas)


def css_tarjeta_activa(estado):
    """Anillo del color de la tarjeta seleccionada (se mantiene también con hover/focus)."""
    if estado not in COLORES:
        return ""
    sel = ", ".join(f"div.st-key-kpi_{estado} button{p}" for p in ("", ":hover", ":focus", ":active"))
    return f"{sel}{{box-shadow:0 0 0 2px #FFFFFF, 0 0 0 5px {COLORES[estado]} !important;}}"


st.markdown(f"<style>{CSS_BASE}{css_kpi()}</style>", unsafe_allow_html=True)

# =============================================================================
# ESTADO INICIAL
# =============================================================================
ss = st.session_state
ss.setdefault("nav_menu", "Panel de inicio")
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
        for ciu in CIUDADES for s, cat, precio, iva in servicios_base
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
        {"codigo": "KG-20261005-006", "evento": "Feria de exposición", "cliente": "Hilton Colón Quito", "fecha": "2026-10-05", "estado": "Aprobada", "total": 2200.00, "items": [_item("Carpa", "2026-10-05", 2, 50.0, 0.15, 20.0)]},
    ]

if "clientes_catalogo" not in ss:
    ss.clientes_catalogo = [
        {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
        {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
        {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
    ]


def migrar_datos():
    """Pone al día los datos de la sesión (también los creados con versiones anteriores de la app)."""
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


migrar_datos()


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
    return (ss.get(_k("cod")), ss.get(_k("ev")), ss.get(_k("cli")), str(ss.get(_k("fec"))), ss.get(_k("est")),
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
        ir(ss.pop("destino_salida", "Panel de inicio"))
        st.rerun()
    if c2.button("Cancelar", key="exit_cancel", use_container_width=True):
        ss.pop("destino_salida", None)
        st.rerun()


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


def guardar_cotizacion(activa, codigo, evento, cliente, fecha, estado, total):
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
                 "estado": estado, "total": total, "items": [dict(i) for i in ss.items_cot]}
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
    historia += [cab, Spacer(1, 14)]

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
CFG_CONTACTOS = {"nombre": st.column_config.TextColumn("Nombre", width="medium"), "cargo": st.column_config.TextColumn("Cargo / Área"),
                 "correo": st.column_config.TextColumn("Correo", width="medium"), "telefono": st.column_config.TextColumn("Teléfono")}
COL_DIRECCIONES = ["etiqueta", "direccion", "ciudad"]
CFG_DIRECCIONES = {"etiqueta": st.column_config.TextColumn("Etiqueta (Matriz, Bodega...)"),
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
    emp = c1.text_input("Razón social / Empresa *", value=d.get("empresa", ""), key=f"{prefijo}_emp")
    ruc = c2.text_input("RUC *", value=d.get("ruc", ""), key=f"{prefijo}_ruc")
    ciu = c3.selectbox("Ciudad principal", CIUDADES, index=indice(CIUDADES, d.get("ciudad")), key=f"{prefijo}_ciu")
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
    ciu = c4.selectbox("Ciudad base", CIUDADES, index=indice(CIUDADES, d.get("ciudad")), key=f"{prefijo}_ciu")
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
    if servicios is not None:   # los servicios del formulario reemplazan a los anteriores de este proveedor
        ss.proveedores_catalogo = [r for r in ss.proveedores_catalogo if r["proveedor"] != viejo] + [{**sv, "proveedor": p["proveedor"]} for sv in servicios]


def asegurar_proveedor(nombre, ciudad, categoria):
    """Si se registra un servicio de un proveedor que no está en el directorio, se crea el proveedor."""
    if not any(p["proveedor"].lower() == nombre.lower() for p in ss.proveedores):
        crear_proveedor({"proveedor": nombre, "ruc": "", "categoria": categoria, "ciudad": ciudad, "observaciones": "",
                         "contactos": [], "direcciones": [], "cuentas": []})


def resumen_contactos(r):
    """Contacto principal + cuántos más hay."""
    con = r.get("contactos", [])
    extra = f" (+{len(con) - 1})" if len(con) > 1 else ""
    return (con[0]["nombre"] if con else "", (con[0]["correo"] if con else "") + extra, con[0]["telefono"] if con else "")


def abrir_nuevo(k):
    ss[f"dir_{k}_nuevo"] = True
    ss[f"dir_{k}_ver"] += 1   # deselecciona la fila de la tabla


def panel_directorio(k, registros, fila_tabla, texto_busqueda, form, validar, crear, actualizar, nombre, etiqueta_nuevo):
    """Tabla con búsqueda; al seleccionar una fila se edita; el botón de nuevo abre el formulario vacío."""
    ss.setdefault(f"dir_{k}_ver", 0)
    ss.setdefault(f"dir_{k}_nuevo", False)
    ver = ss[f"dir_{k}_ver"]
    c_b, c_n = st.columns([3, 1], vertical_alignment="center")
    busq = c_b.text_input("Buscar", key=f"dir_{k}_b", label_visibility="collapsed", placeholder="Buscar...").lower()
    c_n.button(f"＋ {etiqueta_nuevo}", key=f"dir_{k}_btn_nuevo", on_click=abrir_nuevo, args=(k,), use_container_width=True, type="primary")
    vis = [r for r in registros if not busq or busq in texto_busqueda(r).lower()]
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
MENU_PRINCIPAL = ["Panel de inicio", "Reportes financieros", "Proyecciones de ventas", "Noticias corporativas"]
MENU_SOPORTE = ["Centro de ayuda", "Documentación operativa"]
CATALOGOS = {"Catálogo regular": "regular", "Catálogo navideño": "navidad"}   # menú -> catálogo del cotizador

for opcion in MENU_PRINCIPAL:
    st.sidebar.button(opcion, use_container_width=True, key=f"nav_{opcion}", on_click=navegar, args=(opcion,))
st.sidebar.markdown("<p style='font-size:11px; color:#64748B; font-weight:700; margin-top:20px; padding-left:10px;'>COTIZADOR DE CATÁLOGOS</p>", unsafe_allow_html=True)
for opcion in CATALOGOS:
    st.sidebar.button(opcion, use_container_width=True, key=f"nav_{opcion}", on_click=navegar, args=(opcion,))
st.sidebar.markdown("<p style='font-size:11px; color:#64748B; font-weight:700; margin-top:20px; padding-left:10px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
for opcion in MENU_SOPORTE:
    st.sidebar.button(opcion, use_container_width=True, key=f"nav_{opcion}", on_click=navegar, args=(opcion,))

menu = ss.nav_menu

# =============================================================================
# MÓDULOS EN CONSTRUCCIÓN
# =============================================================================
if menu in MENU_PRINCIPAL[1:] + MENU_SOPORTE:
    st.markdown(f"<h2 style='color:#0F172A; font-weight:800;'>{menu}</h2>", unsafe_allow_html=True)
    st.info("Módulo en construcción.")

# =============================================================================
# VISTA 1: PANEL DE INICIO
# =============================================================================
elif menu == "Panel de inicio":

    # 1. Título + accesos rápidos
    with st.container(border=True, key="card_1"):
        col_tit, col_btns = st.columns([1, 2.5])
        with col_tit:
            st.markdown("<h3 style='color:#0F172A; font-weight:800; margin:0; padding-top:5px;'>Panel de Control</h3>", unsafe_allow_html=True)
            st.markdown("<span style='color:#64748B; font-size:13px; font-weight:600;'>Resumen Ejecutivo</span>", unsafe_allow_html=True)
        with col_btns:
            b1, b2, b3 = st.columns(3)
            b1.button("Crear cotización", use_container_width=True, type="primary", key="go_new",
                      on_click=ir, args=("Nueva cotización",), kwargs={"cotizacion_activa": None, "items_cot": []})
            b2.button("Directorio Clientes", use_container_width=True, type="secondary", key="go_cli", on_click=ir, args=("Directorios",))
            b3.button("Directorio Proveedores", use_container_width=True, type="secondary", key="go_pro", on_click=ir, args=("Directorios",))

    # 2. Filtros globales (con key para poder borrarlos desde el botón "Borrar selección")
    cotizaciones = ss.cotizaciones_guardadas
    ciudad_cliente = {c["empresa"]: c["ciudad"] for c in ss.clientes_catalogo}
    with st.container(border=True, key="card_2"):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:0;'>Filtros Operativos Globales</div>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.selectbox("Filtrar por Empresa / Cuenta", ["Todas"] + sorted({c["cliente"] for c in cotizaciones}), key="f_emp")
        col_f2.selectbox("Filtrar por Mes Operativo", ["Todos"] + sorted({c["fecha"][:7] for c in cotizaciones}), key="f_mes")
        col_f3.selectbox("Filtrar por Ciudad", ["Todas"] + CIUDADES, key="f_ciu")

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
        c_tit.markdown("<div class='section-title'>Análisis Financiero Interactivo</div>", unsafe_allow_html=True)
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
        col_donut, col_trend = st.columns([1, 2.5])

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
                donut = alt.Chart(df_donut).mark_arc(innerRadius=45, outerRadius=90, cornerRadius=4, padAngle=0.03).encode(
                    theta=alt.Theta("Monto:Q"),
                    color=alt.Color("Segmento:N", scale=alt.Scale(domain=dominio, range=paleta),
                                    legend=alt.Legend(title=titulo_leyenda, orient="bottom", offset=18, titlePadding=8, columns=1 if estado_actual != "Todas" else 2)),
                    tooltip=[alt.Tooltip("Segmento", title="Detalle"), alt.Tooltip("Monto", format="$,.2f")],
                    # CORRECCIÓN del TypeError 'bottom': el padding debe ser un dict, no un número
                ).properties(height=260, padding={"left": 10, "right": 10, "top": 10, "bottom": 10})
                st.altair_chart(donut, use_container_width=True)

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
                                  legend=alt.Legend(title=None, orient="bottom", symbolOpacity=1, symbolType="circle") if len(estados_graf) > 1 else None)
                base = alt.Chart(df).encode(
                    x=alt.X("Mes:O", sort=orden, title="Mes Operativo", axis=alt.Axis(labelAngle=0, grid=False, labelColor="#64748B")),
                    y=alt.Y("Monto:Q", stack=None, title=y_title, axis=alt.Axis(format="$,.0f", gridColor="#E2E8F0", labelColor="#64748B")),
                    color=color,
                )
                grafico = (
                    base.mark_area(opacity=0.14, interpolate="monotone")                       # área sutil del color de la tarjeta
                    + base.mark_line(strokeWidth=2.5, interpolate="monotone")
                    + base.mark_point(filled=True, size=70, opacity=1).encode(
                        tooltip=["Estado:N", alt.Tooltip("Mes:O", title="Periodo"), alt.Tooltip("Monto:Q", format="$,.2f", title="Total")])
                ).properties(height=260)
                st.altair_chart(grafico, use_container_width=True)
            else:
                st.markdown(f"<div style='padding-top:100px; text-align:center; color:#64748B;'>No hay ingresos registrados en la categoría <b>{estado_actual}</b> para el periodo seleccionado.</div>", unsafe_allow_html=True)

    # 4. Tabla detallada
    with st.container(border=True, key="card_4"):
        col_tit, col_bus = st.columns([2, 1])
        col_tit.markdown(f"<div class='section-title'>Detalle Operativo: {estado_actual.upper()}</div>", unsafe_allow_html=True)
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
    h_back, h_tit, h_monto = st.columns([1.15, 4, 2.2], vertical_alignment="center")
    h_back.button("← Panel de inicio", key="back_btn", on_click=navegar, args=("Panel de inicio",), help="Volver al panel de inicio")
    h_tit.markdown("<h2 style='font-weight:800; color:#0F172A; margin:0;'>Gestión de cotizaciones</h2>", unsafe_allow_html=True)
    h_monto.markdown(f"""<div class='monto-badge'><div class='monto-label'>Monto estimado</div>
        <div class='monto-valor'><span class='mon'>$</span>{tot_head:,.2f}</div></div>""", unsafe_allow_html=True)

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
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
        cod_cotizacion = c1.text_input("Referencia", value=activa["codigo"] if activa else siguiente_codigo(), key=_k("cod"))
        nombre_evento = c2.text_input("Nombre del evento", value=activa["evento"] if activa else "", key=_k("ev"))
        cliente_sel = c3.selectbox("Cuenta de cliente", lista_cli, key=_k("cli"), **ini_cli)
        fecha_gral = c4.date_input("Fecha", fecha_def, key=_k("fec"))
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
            f1, f2 = st.columns([1, 2])
            ciu_f = f1.selectbox("Filtrar ciudad", CIUDADES, index=0)
            pal_b = f2.text_input("Buscar proveedor/servicio...").lower()

            res = [p for p in ss.proveedores_catalogo
                   if p["ciudad"] == ciu_f and (pal_b in p["servicio"].lower() or pal_b in p["proveedor"].lower())]
            if not res:
                st.warning("No hay registros.")
            else:
                opc = [f"{r['proveedor']} ➔ {r['servicio']} | IVA {int(r['iva']*100)}% | {r.get('descripcion', '')}" for r in res]
                item_sel = res[opc.index(st.selectbox("Proveedor:", opc))]
                ca, cb, cc, cd, ce, cf = st.columns([1.3, 0.8, 1.1, 0.9, 1.0, 1.4], vertical_alignment="bottom")
                f_it = ca.date_input("Fecha de servicio", value=fecha_gral)
                can_it = cb.number_input("Cantidad", min_value=1, value=1)
                cos_it = cc.number_input("Costo unit. ($)", value=float(item_sel["precio_base"]))
                iva_it = cd.selectbox("IVA prov.", [0.0, 0.15], index=1 if item_sel["iva"] > 0 else 0, format_func=lambda x: f"{int(x*100)}%")
                fee_it = ce.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f")
                if cf.button("Agregar", type="primary", use_container_width=True, key="add_cat"):
                    items.append({"servicio": item_sel["servicio"], "proveedor": item_sel["proveedor"], "ciudad": ciu_f, "fecha": str(f_it),
                                  "cantidad": can_it, "costo": cos_it, "iva_prov": iva_it, "fee_pct": fee_it})
                    st.rerun()

        with tab_man:
            nc1, nc2, nc3, nc4 = st.columns(4)
            n_pro = nc1.text_input("Proveedor *")
            n_ser = nc2.text_input("Servicio *")
            n_ciu = nc3.selectbox("Ciudad op.", CIUDADES, key="mc_c")
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
                        asegurar_proveedor(n_pro.strip(), n_ciu, n_cat or "General")
                        ss.proveedores_catalogo.append({"servicio": n_ser, "proveedor": n_pro.strip(), "categoria": n_cat or "General", "ciudad": n_ciu,
                                                        "precio_base": cos_it_m, "iva": iva_it_m, "descripcion": "Manual"})
                    st.rerun()
                else:
                    st.error("Proveedor y servicio requeridos.")

    if items:
        with st.container(border=True, key="card_8"):
            st.markdown("<div class='section-title'>Estructura de costos</div>", unsafe_allow_html=True)
            # Una línea por servicio, una columna por dato. Los 3 últimos anchos son ↑ ↓ ✕ (botones compactos)
            ANCHOS = [2.0, 2.2, 1.15, 0.95, 0.6, 1.0, 0.6, 0.8, 1.0, 1.1, 0.38, 0.38, 0.38]
            TITULOS = ["PROVEEDOR", "SERVICIO", "FECHA", "CIUDAD", "CANT.", "COSTO U.", "IVA", "MARGEN %", "MARGEN $", "SUBTOTAL", "", "", ""]
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
                    if cx[10].button("↑", key=f"mv_up_{idx}", disabled=idx == 0, help="Subir"):
                        accion = ("up", idx)
                    if cx[11].button("↓", key=f"mv_dn_{idx}", disabled=idx == len(items) - 1, help="Bajar"):
                        accion = ("dn", idx)
                    if cx[12].button("✕", key=f"del_{idx}", help="Eliminar"):
                        accion = ("del", idx)

            if accion:
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
                    if guardar_cotizacion(activa, cod_cotizacion, nombre_evento, cliente_sel, fecha_gral, estado_cot, t_cli):
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
    _color = "#B91C1C" if _nav else "#1E3A8A"
    _fondo = "#FEE2E2" if _nav else "#E3E9F1"
    _tipo = "navideño" if _nav else "regular"
    st.markdown(
        "<style>.block-container{padding-top:2.2rem !important; padding-bottom:0 !important;}</style>"
        "<div style='display:flex; align-items:center; gap:14px; margin:0 0 8px 0;'>"
        "<span style='font-size:1.55rem; font-weight:800; color:#0F172A; letter-spacing:-0.01em;'>Cotizador de catálogos</span>"
        f"<span style='font-size:0.82rem; font-weight:700; color:{_color}; background:{_fondo}; border:1px solid {_color}33; padding:4px 14px; border-radius:999px;'>Catálogo {_tipo}</span>"
        "</div>",
        unsafe_allow_html=True)
    ruta_html = Path(__file__).parent / "cotizador_catalogos.html"
    if not ruta_html.exists():
        st.error("Falta el archivo cotizador_catalogos.html en el repositorio, junto a app.py. Súbelo en GitHub (Add file → Upload files).")
    else:
        pagina = ruta_html.read_text(encoding="utf-8").replace("</body>", f"<script>iniciarEmbebido('{CATALOGOS[menu]}');</script></body>")
        components.html(pagina, height=700, scrolling=False)

# =============================================================================
# VISTA 3: DIRECTORIOS
# =============================================================================
elif menu == "Directorios":
    st.markdown("<h2 style='color:#0F172A; font-weight:800; margin-bottom:20px;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)

    with st.container(border=True, key="card_9"):
        t_cli, t_pro = st.tabs(["Directorio de clientes", "Red de proveedores"])

        with t_cli:
            def fila_cliente(c):
                con, mail, tel = resumen_contactos(c)
                return {"Empresa": c["empresa"], "RUC": c["ruc"], "Ciudad": c["ciudad"], "Contacto": con, "Correo": mail, "Teléfono": tel,
                        "Direcciones": len(c.get("direcciones", [])), "Días crédito": c["dias_credito"]}
            panel_directorio(
                "cli", ss.clientes_catalogo, fila_cliente,
                lambda c: " ".join([c["empresa"], c["ruc"], c["ciudad"]] + [f"{x['nombre']} {x['correo']} {x['telefono']}" for x in c.get("contactos", [])]),
                form_cliente, validar_cliente, crear_cliente, actualizar_cliente, lambda c: c["empresa"], "Nueva cuenta")

        with t_pro:
            sub_prov, sub_serv = st.tabs(["Proveedores (datos de contacto)", "Servicios y costos"])

            with sub_prov:
                def fila_proveedor(p):
                    con, mail, tel = resumen_contactos(p)
                    cta = p["cuentas"][0] if p.get("cuentas") else {}
                    return {"Proveedor": p["proveedor"], "Categoría": p["categoria"], "Ciudad": p["ciudad"], "Contacto": con, "Correo": mail, "Teléfono": tel,
                            "Banco": f"{cta.get('banco', '')} {cta.get('numero', '')}".strip(),
                            "Servicios": sum(1 for r in ss.proveedores_catalogo if r["proveedor"] == p["proveedor"])}
                panel_directorio(
                    "prv", ss.proveedores, fila_proveedor,
                    lambda p: " ".join([p["proveedor"], p["categoria"], p["ciudad"], p.get("ruc", "")] + [f"{x['nombre']} {x['correo']} {x['telefono']}" for x in p.get("contactos", [])]),
                    form_proveedor, validar_proveedor, crear_proveedor, actualizar_proveedor, lambda p: p["proveedor"], "Nuevo proveedor")

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
