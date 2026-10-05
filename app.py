import json
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
.st-key-tabla_costos { gap: 8px !important; }
.st-key-tabla_costos [data-testid="stHorizontalBlock"] {
    gap: .4rem !important; align-items: center !important; padding: 7px 12px;
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 10px; box-shadow: 0 1px 2px rgba(15,23,42,.06);
}
.st-key-costos_head [data-testid="stHorizontalBlock"] { background: transparent; border: none; box-shadow: none; padding: 0 12px 2px; }
/* Streamlit resta 1rem al contenedor de markdown para compensar el margen del <p>; al quitar el margen hay que quitar también ese ajuste */
.st-key-tabla_costos [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.st-key-tabla_costos [data-testid="stMarkdownContainer"] p, .st-key-tabla_costos [data-testid="stElementContainer"] { margin: 0 !important; }
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
         "precio_base": precio, "iva": iva, "banco": "Banco", "cuenta": "Cta.", "descripcion": "Estándar"}
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


def form_cliente(prefijo, titulo_html=""):
    """Formulario de cliente reutilizado en 'Nueva cotización' y en 'Directorios'. Devuelve dict o None."""
    if titulo_html:
        st.markdown(titulo_html, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        emp = st.text_input("Razón social / Empresa *", key=f"{prefijo}_emp")
        ruc = st.text_input("RUC *", key=f"{prefijo}_ruc")
        ciu = st.selectbox("Ciudad", CIUDADES, key=f"{prefijo}_ciu")
    with c2:
        dire = st.text_input("Dirección", key=f"{prefijo}_dir")
        web = st.text_input("Sitio web", key=f"{prefijo}_web")
        cont = st.text_input("Contacto", key=f"{prefijo}_cont")
    with c3:
        mail = st.text_input("Correo", key=f"{prefijo}_mail")
        tel = st.text_input("Teléfono", key=f"{prefijo}_tel")
        dias = st.number_input("Días crédito", value=30, step=15, key=f"{prefijo}_dias")
    if st.button("Guardar cuenta", type="primary", key=f"{prefijo}_save"):
        if emp.strip() and ruc.strip():
            return {"empresa": emp, "ruc": ruc, "ciudad": ciu, "direccion": dire, "web": web,
                    "contacto": cont, "email": mail, "telefono": tel, "dias_credito": dias}
        st.error("Razón social y RUC son requeridos.")
    return None


# =============================================================================
# MENÚ LATERAL
# =============================================================================
st.sidebar.markdown("<div class='brand-logo'>Karkajadas Group</div>", unsafe_allow_html=True)
MENU_PRINCIPAL = ["Panel de inicio", "Reportes financieros", "Proyecciones de ventas", "Noticias corporativas"]
MENU_SOPORTE = ["Centro de ayuda", "Documentación operativa"]

for opcion in MENU_PRINCIPAL:
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
            df_donut = pd.DataFrame({"Estado": ESTADOS, "Monto": [tot[e] for e in ESTADOS]})
            df_donut = df_donut[df_donut["Monto"] > 0]
            if df_donut.empty:
                st.info("Sin datos para distribución.")
            else:
                donut = alt.Chart(df_donut).mark_arc(innerRadius=45, outerRadius=90, cornerRadius=4, padAngle=0.03).encode(
                    theta=alt.Theta("Monto:Q"),
                    color=alt.Color("Estado:N", scale=alt.Scale(domain=ESTADOS, range=[COLORES[e] for e in ESTADOS]),
                                    legend=alt.Legend(title="Distribución", orient="bottom", columns=2)),
                    tooltip=["Estado", alt.Tooltip("Monto", format="$,.2f")],
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
            ANCHOS = [1.5, 2, 2.5, 1.5, 1]
            encabezados(st.columns(ANCHOS), ["CÓDIGO / FECHA", "EVENTO / ESTADO", "CLIENTE CORPORATIVO", "MONTO ESTIMADO", "ACCIÓN"])
            st.markdown("<hr style='margin:2px 0 5px 0; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)
            for cot in ev_filt:
                cx = st.columns(ANCHOS)
                cx[0].write(f"**{cot['codigo']}**\n\n<span style='font-size:12px; color:#475569;'>{cot['fecha']}</span>", unsafe_allow_html=True)
                cx[1].write(f"{cot['evento']}\n\n<span style='font-size:11px; font-weight:800; color:{COLORES[cot['estado']]};'>{cot['estado'].upper()}</span>", unsafe_allow_html=True)
                cx[2].write(cot["cliente"])
                cx[3].write(f"**${cot['total']:,.2f}**")
                cx[4].button("Abrir", key=f"ab_{cot['codigo']}", type="secondary", use_container_width=True,
                             on_click=ir, args=("Nueva cotización",),
                             kwargs={"cotizacion_activa": cot, "items_cot": [dict(i) for i in cot.get("items", [])]})
                st.markdown("<hr style='margin:2px 0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
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
                ss.clientes_catalogo.append(nuevo)
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
                        ss.proveedores_catalogo.append({"servicio": n_ser, "proveedor": n_pro, "categoria": n_cat or "General", "ciudad": n_ciu,
                                                        "precio_base": cos_it_m, "iva": iva_it_m, "banco": "N/A", "cuenta": "N/A", "descripcion": "Manual"})
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
# VISTA 3: DIRECTORIOS
# =============================================================================
elif menu == "Directorios":
    st.markdown("<h2 style='color:#0F172A; font-weight:800; margin-bottom:20px;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)

    with st.container(border=True, key="card_9"):
        t_cli, t_pro = st.tabs(["Directorio de clientes", "Red de proveedores"])

        with t_cli:
            df_c = pd.DataFrame(ss.clientes_catalogo).rename(columns={
                "empresa": "Empresa", "ruc": "RUC", "ciudad": "Ciudad", "direccion": "Dirección", "web": "Web",
                "contacto": "Contacto", "email": "Correo", "telefono": "Teléfono", "dias_credito": "Días Crédito"})
            st.dataframe(df_c, use_container_width=True, hide_index=True)
            st.markdown("<hr style='margin:15px 0;'>", unsafe_allow_html=True)
            nuevo = form_cliente("dir", "<div class='section-title' style='border:none;'>Nueva cuenta corporativa</div>")
            if nuevo:
                ss.clientes_catalogo.append(nuevo)
                st.toast("Cuenta registrada")
                st.rerun()

        with t_pro:
            df_p = pd.DataFrame(ss.proveedores_catalogo).rename(columns={
                "servicio": "Servicio", "proveedor": "Proveedor", "categoria": "Categoría", "ciudad": "Ciudad",
                "precio_base": "Costo ($)", "iva": "IVA", "banco": "Banco", "cuenta": "Cuenta", "descripcion": "Descripción"})
            df_p["IVA"] = df_p["IVA"].map(lambda x: f"{int(x*100)}%")
            df_p["Costo ($)"] = df_p["Costo ($)"].map(lambda x: f"${x:,.2f}")
            st.dataframe(df_p, use_container_width=True, hide_index=True)
            st.markdown("<hr style='margin:15px 0;'><div class='section-title' style='border:none;'>Nuevo proveedor</div>", unsafe_allow_html=True)
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_pro = st.text_input("Proveedor *"); p_ser = st.text_input("Servicio *"); p_cat = st.text_input("Categoría")
            with cp2:
                p_ciu = st.selectbox("Ciudad", CIUDADES, key="p_ciu"); p_cos = st.number_input("Costo ($)", value=0.00)
                p_iva = st.selectbox("IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%", key="p_iva")
            with cp3:
                p_ban = st.text_input("Banco"); p_cta = st.text_input("Cuenta"); p_des = st.text_input("Observaciones")
            if st.button("Registrar proveedor", type="primary"):
                if p_pro and p_ser:
                    ss.proveedores_catalogo.append({"servicio": p_ser, "proveedor": p_pro, "categoria": p_cat, "ciudad": p_ciu,
                                                    "precio_base": p_cos, "iva": p_iva, "banco": p_ban, "cuenta": p_cta, "descripcion": p_des})
                    st.toast("Proveedor registrado")
                    st.rerun()
                else:
                    st.error("Obligatorio Proveedor y Servicio.")
