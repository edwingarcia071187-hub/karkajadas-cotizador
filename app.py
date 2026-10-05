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
.block-container { padding-top: 4rem !important; padding-bottom: 2rem !important; max-width: 98% !important; }
.stApp, .main, header { background-color: #EEF2F7 !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }

[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { color: #FFFFFF !important; background-color: #1E293B !important; border-radius: 4px !important; margin: 10px !important; }
[data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapsedControl"] svg { fill: #FFFFFF !important; }

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important; border: 1px solid #DDE5EE !important; background-color: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(15,23,42,.05), 0 6px 16px rgba(15,23,42,.06) !important; padding: 18px 25px !important; margin-bottom: 16px !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { border: none !important; background-color: transparent !important; box-shadow: none !important; padding: 0 !important; }

/* Botones globales: verde = avanzar, azul = neutro */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background-color: #059669 !important; border: 1px solid #059669 !important; color: #FFFFFF !important;
    border-radius: 8px !important; font-weight: 600 !important; transition: all .2s ease !important;
    box-shadow: 0 1px 2px rgba(5,150,105,.25), 0 3px 8px rgba(5,150,105,.18) !important;
}
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { background-color: #047857 !important; transform: translateY(-1px); }
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background-color: #1E3A8A !important; border: 1px solid #1E3A8A !important; color: #FFFFFF !important;
    border-radius: 8px !important; font-weight: 600 !important; transition: all .2s ease !important;
    box-shadow: 0 1px 2px rgba(30,58,138,.25), 0 3px 8px rgba(30,58,138,.18) !important;
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
[class*="st-key-mv_"] button { background: #FFFFFF !important; border: 1px solid #CBD5E1 !important; color: #475569 !important; box-shadow: 0 1px 2px rgba(15,23,42,.10) !important; border-radius: 6px !important; }
[class*="st-key-mv_"] button:hover { background: #EFF6FF !important; color: #1E3A8A !important; border-color: #93C5FD !important; }
[class*="st-key-mv_"] button:disabled { opacity: .35; }
[class*="st-key-del_"] button { background: #EF4444 !important; border: 1px solid #EF4444 !important; color: #FFF !important; font-weight: 700 !important; border-radius: 6px !important; box-shadow: 0 1px 2px rgba(239,68,68,.35) !important; }
[class*="st-key-del_"] button:hover { background: #DC2626 !important; }

/* Tabla "Estructura de costos": cada servicio es una franja suave (fondo + sombra) separada de la siguiente, sin cuadrícula */
.st-key-tabla_costos { gap: 8px !important; }
.st-key-tabla_costos [data-testid="stHorizontalBlock"] {
    gap: .4rem !important; align-items: center !important; padding: 7px 12px;
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; box-shadow: 0 1px 2px rgba(15,23,42,.06);
}
.st-key-costos_head { margin-bottom: -2px; }
.st-key-costos_head [data-testid="stHorizontalBlock"] { background: transparent; border: none; box-shadow: none; padding-top: 0; padding-bottom: 0; }
.st-key-tabla_costos [data-testid="stMarkdownContainer"] p, .st-key-tabla_costos [data-testid="stElementContainer"] { margin: 0 !important; }
.cell { font-size: 14px; color: #1E293B; line-height: 26px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell.num, .col-head.num { text-align: right; }
.cell .pos { color: #059669; font-weight: 600; }

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

/* Formularios y títulos */
/* Campos: el borde y el radio van en el contenedor externo; el <input> interno queda sin borde.
   (Antes ambos tenían borde con radios distintos y el recuadro no cerraba bien en las esquinas) */
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
    background-color: #F4F7FB !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; min-height: 40px !important; overflow: hidden;
    box-shadow: inset 0 1px 2px rgba(15,23,42,.06) !important; transition: background-color .15s, border-color .15s;
}
div[data-baseweb="input"]:hover, div[data-baseweb="select"] > div:hover { border-color: #94A3B8 !important; }
div[data-baseweb="base-input"] { background: transparent !important; border: none !important; border-radius: 0 !important; }
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { background: transparent !important; border: none !important; box-shadow: none !important; color: #1E293B !important; border-radius: 0 !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within, div[data-baseweb="select"] > div:focus-within { background-color: #FFFFFF !important; border-color: #1E3A8A !important; box-shadow: 0 0 0 3px rgba(30,58,138,.15) !important; }

/* Pestañas: barra con fondo y pestaña activa elevada */
div[data-baseweb="tab-list"] { gap: 4px !important; background: #EEF2F7; padding: 4px; border-radius: 10px; }
button[data-baseweb="tab"] { border-radius: 8px !important; padding: 6px 16px !important; height: auto !important; }
button[data-baseweb="tab"][aria-selected="true"] { background: #FFFFFF !important; box-shadow: 0 1px 3px rgba(15,23,42,.15); }
div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none !important; }
.stSelectbox label, .stTextInput label, .stNumberInput label { font-size: 13px !important; color: #64748B !important; font-weight: 600 !important; margin-bottom: 4px !important; }
.section-title { color: #0F172A; font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 12px; letter-spacing: .5px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; }
.col-head { font-size: 11px; font-weight: 700; color: #64748B; }
.metric-tile { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #1E3A8A; border-radius: 10px; padding: 12px 16px; box-shadow: 0 1px 2px rgba(15,23,42,.06); }
.metric-tile.ganancia { border-left-color: #059669; }
.internal-metrics { font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .4px; }
.internal-metrics-value { font-size: 22px; font-weight: 800; color: #0F172A; }
.metric-tile.ganancia .internal-metrics-value { color: #047857; }
.invoice-container { float: right; width: 320px; background-color: #F8FAFC; padding: 20px; border-radius: 12px; border: 1px solid #CBD5E1; box-shadow: 0 1px 2px rgba(15,23,42,.06), 0 4px 12px rgba(15,23,42,.06); }

/* Monto estimado (encabezado de la cotización) */
.monto-badge { text-align: right; color: #FFFFFF; padding: 12px 26px 14px; border-radius: 14px; border-top: 3px solid #34D399;
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); box-shadow: 0 8px 20px rgba(30,58,138,.30); }
.monto-label { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #BFDBFE; }
.monto-valor { font-size: 36px; font-weight: 800; line-height: 1.1; font-variant-numeric: tabular-nums; }
.monto-valor .mon { font-size: 20px; color: #6EE7B7; margin-right: 3px; vertical-align: top; position: relative; top: 5px; }
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
    """Guarda (o reemplaza en su misma posición) la cotización. Devuelve True si se guardó."""
    if cliente == NUEVO_CLIENTE:
        st.error("Registre el cliente.")
        return False
    nueva = {"codigo": codigo, "evento": evento, "cliente": cliente, "fecha": str(fecha),
             "estado": estado, "total": total, "items": [dict(i) for i in ss.items_cot]}
    lista = ss.cotizaciones_guardadas
    pos = next((i for i, c in enumerate(lista) if activa and c["codigo"] == activa["codigo"]), None)
    if pos is None:
        lista.append(nueva)
    else:
        lista[pos] = nueva
    st.toast("Cotización guardada")
    return True


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
    st.sidebar.button(opcion, use_container_width=True, key=f"nav_{opcion}", on_click=ir, args=(opcion,))
st.sidebar.markdown("<p style='font-size:11px; color:#64748B; font-weight:700; margin-top:20px; padding-left:10px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
for opcion in MENU_SOPORTE:
    st.sidebar.button(opcion, use_container_width=True, key=f"nav_{opcion}", on_click=ir, args=(opcion,))

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
    with st.container(border=True):
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
    with st.container(border=True):
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
    with st.container(border=True):
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
                                    legend=alt.Legend(title="Distribución", orient="bottom")),
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

                base = alt.Chart(df).encode(
                    x=alt.X("Mes:O", sort=orden, title="Mes Operativo", axis=alt.Axis(labelAngle=0, grid=False, labelColor="#64748B")),
                    y=alt.Y("Monto:Q", stack=None, title=y_title, axis=alt.Axis(format="$,.0f", gridColor="#E2E8F0", labelColor="#64748B")),
                    color=alt.Color("Estado:N", scale=alt.Scale(domain=estados_graf, range=[COLORES[e] for e in estados_graf]),
                                    legend=alt.Legend(title=None, orient="bottom") if len(estados_graf) > 1 else None),
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
    with st.container(border=True):
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

    st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;'>
            <h2 style='font-weight:800; color:#0F172A; margin:0;'>Gestión de cotizaciones</h2>
            <div class='monto-badge'>
                <div class='monto-label'>Monto estimado</div>
                <div class='monto-valor'><span class='mon'>$</span>{tot_head:,.2f}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    activa = ss.cotizacion_activa
    lista_cli = [c["empresa"] for c in ss.clientes_catalogo] + [NUEVO_CLIENTE]
    cli_def = ss.pop("cliente_recien_creado", None) or (activa["cliente"] if activa else None)
    idx_cli = lista_cli.index(cli_def) if cli_def in lista_cli else 0
    ESTADOS_COT = ["Borrador", "Enviada", "Aprobada", "Cancelada"]
    idx_est = ESTADOS_COT.index(activa["estado"]) if activa else 0
    fecha_def = date.fromisoformat(activa["fecha"]) if activa else date.today()

    with st.container(border=True):
        col_tit, col_btn = st.columns([4, 1])
        col_tit.markdown("<div class='section-title'>Información del evento</div>", unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
        cod_cotizacion = c1.text_input("Referencia", value=activa["codigo"] if activa else siguiente_codigo())
        nombre_evento = c2.text_input("Nombre del evento", value=activa["evento"] if activa else "")
        cliente_sel = c3.selectbox("Cuenta de cliente", lista_cli, index=idx_cli)
        fecha_gral = c4.date_input("Fecha", fecha_def)
        estado_cot = c5.selectbox("Estado", ESTADOS_COT, index=idx_est)

        # El botón se dibuja DESPUÉS de los campos: antes fallaba con NameError porque usaba variables aún no definidas
        with col_btn:
            if st.button("Guardar cambios", type="primary", use_container_width=True, key="btn_s_top"):
                if guardar_cotizacion(activa, cod_cotizacion, nombre_evento, cliente_sel, fecha_gral, estado_cot, tot_head):
                    ss.nav_menu = "Panel de inicio"
                    st.rerun()

    if cliente_sel == NUEVO_CLIENTE:
        with st.container(border=True):
            nuevo = form_cliente("nc", "<div class='section-title' style='color:#059669; border-color:#059669;'>Apertura de cuenta corporativa</div>")
            if nuevo:
                ss.clientes_catalogo.append(nuevo)
                ss.cliente_recien_creado = nuevo["empresa"]
                st.rerun()

    with st.container(border=True):
        st.markdown("<div class='section-title'>Añadir servicios</div>", unsafe_allow_html=True)
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
                ca, cb, cc, cd, ce = st.columns(5)
                f_it = ca.date_input("Fecha de servicio", value=fecha_gral)
                can_it = cb.number_input("Cantidad", min_value=1, value=1)
                cos_it = cc.number_input("Costo unit. ($)", value=float(item_sel["precio_base"]))
                iva_it = cd.selectbox("IVA prov.", [0.0, 0.15], index=1 if item_sel["iva"] > 0 else 0, format_func=lambda x: f"{int(x*100)}%")
                fee_it = ce.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f")
                if st.button("Agregar a la cotización", type="primary"):
                    items.append({"servicio": item_sel["servicio"], "proveedor": item_sel["proveedor"], "ciudad": ciu_f, "fecha": str(f_it),
                                  "cantidad": can_it, "costo": cos_it, "iva_prov": iva_it, "fee_pct": fee_it})
                    st.rerun()

        with tab_man:
            nc1, nc2, nc3, nc4 = st.columns(4)
            n_pro = nc1.text_input("Proveedor *")
            n_ser = nc2.text_input("Servicio *")
            n_ciu = nc3.selectbox("Ciudad op.", CIUDADES, key="mc_c")
            n_cat = nc4.text_input("Categoría")
            ca, cb, cc, cd, ce = st.columns(5)
            f_it_m = ca.date_input("Fecha de servicio", value=fecha_gral, key="mc_f")
            can_it_m = cb.number_input("Cantidad", min_value=1, value=1, key="mc_ca")
            cos_it_m = cc.number_input("Costo unit. ($)", value=0.00, format="%.2f", key="mc_co")
            iva_it_m = cd.selectbox("IVA prov.", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x*100)}%", key="mc_i")
            fee_it_m = ce.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f", key="mc_ma")
            g_bd = st.checkbox("Guardar en directorio", value=True)
            if st.button("Registrar y agregar", type="primary"):
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
        with st.container(border=True):
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
            st.markdown("<br>", unsafe_allow_html=True)
            cm1, cm2, ci = st.columns([1.2, 1.2, 1.6])
            cm1.markdown(f"<div class='metric-tile'><div class='internal-metrics'>Costos operativos</div><div class='internal-metrics-value'>${s_prov:,.2f}</div></div>", unsafe_allow_html=True)
            cm2.markdown(f"<div class='metric-tile ganancia'><div class='internal-metrics'>Rentabilidad (Ganancia)</div><div class='internal-metrics-value'>${t_fee:,.2f}</div></div>", unsafe_allow_html=True)
            ci.markdown(f"<div class='invoice-container'><div class='invoice-row'><span>Subtotal</span><span>${s_com:,.2f}</span></div><div class='invoice-row'><span>IVA 15%</span><span>${iva_cli:,.2f}</span></div><div class='invoice-total'><span>TOTAL INVERSIÓN</span><span>${t_cli:,.2f}</span></div></div><div style='clear:both;'></div>", unsafe_allow_html=True)

            st.markdown("<hr style='border-top:1px solid #E2E8F0; margin:20px 0;'>", unsafe_allow_html=True)
            _, cg = st.columns([3, 1])
            if cg.button("Guardar cotización final", use_container_width=True, type="primary", key="btn_save_bot"):
                if guardar_cotizacion(activa, cod_cotizacion, nombre_evento, cliente_sel, fecha_gral, estado_cot, t_cli):
                    ss.nav_menu = "Panel de inicio"
                    st.rerun()

# =============================================================================
# VISTA 3: DIRECTORIOS
# =============================================================================
elif menu == "Directorios":
    st.markdown("<h2 style='color:#0F172A; font-weight:800; margin-bottom:20px;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)

    with st.container(border=True):
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
