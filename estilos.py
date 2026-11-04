"""Estilos (CSS) del ERP."""
import streamlit as st
from constantes import COLORES, ESTADOS


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


def css_pills_estado():
    """Botones del filtro de estado: lo elegido toma el color de ese estado (los mismos de las tarjetas y gráficos del panel)."""
    reglas = ['.st-key-rep_est button[data-variant="pills"][aria-pressed="true"]:nth-child(1){background:#334155 !important;border-color:#334155 !important;}']
    for i, e in enumerate(ESTADOS, start=2):
        c = COLORES[e]
        reglas.append(f'.st-key-rep_est button[data-variant="pills"][aria-pressed="true"]:nth-child({i}){{background:{c} !important;border-color:{c} !important;color:#FFFFFF !important;}}')
    return "".join(reglas)


def css_tarjeta_activa(estado):
    """Tarjeta seleccionada: fondo tenue del color del estado y borde más marcado."""
    if estado not in COLORES:
        return ""
    c = COLORES[estado]
    sel = ", ".join(f"div.st-key-kpi_{estado} button{p}" for p in ("", ":hover", ":focus", ":active"))
    return f"{sel}{{background:{c}1A !important;border:1px solid {c} !important;border-left:10px solid {c} !important;}}"


def aplicar_estilos():
    st.markdown(f"<style>{CSS_BASE}{css_kpi()}{css_pills_estado()}</style>", unsafe_allow_html=True)
