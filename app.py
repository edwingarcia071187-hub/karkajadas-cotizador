import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Karkajadas Group - ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS AVANZADOS Y COLORIMETRÍA ---
st.markdown("""
    <style>
    /* Fondo principal y tipografía */
    .stApp, .main, header { background-color: #F8FAFC !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* ----------------------------------------------------
       BOTONES: VERDE (Avanzar/Crear), AZUL (Neutro), ROJO (Borrar)
       ---------------------------------------------------- */
    /* Botones PRIMARIOS = VERDE ESMERALDA (Acciones de éxito) */
    button[kind="primary"] {
        background-color: #059669 !important; 
        border: 1px solid #059669 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover { background-color: #047857 !important; transform: translateY(-2px); box-shadow: 0 4px 6px rgba(5, 150, 105, 0.3) !important;}

    /* Botones SECUNDARIOS = AZUL CORPORATIVO (Navegación / Filtros) */
    button[kind="secondary"] {
        background-color: #1E3A8A !important; 
        border: 1px solid #1E3A8A !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover { background-color: #1E40AF !important; transform: translateY(-2px); }

    /* BOTONES COMPACTOS DE LA TABLA (Flechas y Borrar) */
    div[data-testid="column"]:nth-child(8) button,
    div[data-testid="column"]:nth-child(9) button {
        background-color: transparent !important;
        border: 1px solid #CBD5E1 !important;
        color: #475569 !important;
        padding: 0 !important; min-height: 32px !important; height: 32px !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }
    div[data-testid="column"]:nth-child(8) button:hover,
    div[data-testid="column"]:nth-child(9) button:hover { background-color: #F1F5F9 !important; color: #1E3A8A !important; }

    /* BOTÓN ROJO DE ELIMINAR (Fila 10 de la tabla) */
    div[data-testid="column"]:nth-child(10) button {
        background-color: #EF4444 !important; 
        border: 1px solid #EF4444 !important;
        color: white !important;
        padding: 0 !important; min-height: 32px !important; height: 32px !important;
        border-radius: 4px !important;
        font-weight: bold !important;
    }
    div[data-testid="column"]:nth-child(10) button:hover { background-color: #DC2626 !important; }

    /* ----------------------------------------------------
       PANEL LATERAL (Simetría, sombreado y hover 3D)
       ---------------------------------------------------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important;
    }
    .brand-logo { font-size: 24px; font-weight: 900; color: #FFFFFF; margin-bottom: 25px; margin-top: 10px; padding-left: 5px; letter-spacing: 0.5px;}
    
    /* Configuración SIMÉTRICA de los botones del sidebar */
    [data-testid="stSidebar"] button {
        background-color: #1E293B !important; 
        border: 1px solid #334155 !important;
        color: #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        margin-bottom: 8px !important;
        width: 100% !important; /* Fuerza a todos al mismo tamaño */
        display: block !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] button p { width: 100% !important; text-align: left !important; font-weight: 500 !important; margin: 0 !important;}
    
    /* Efecto Hover: Sombreado, se aclara y levanta */
    [data-testid="stSidebar"] button:hover { 
        background-color: #334155 !important; 
        color: #FFFFFF !important;
        border-color: #475569 !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
        transform: translateY(-2px) !important; 
    }

    /* ----------------------------------------------------
       DISEÑO DE CONTENEDORES NATIVOS Y FACTURA
       ---------------------------------------------------- */
    /* Tarjetas nativas de Streamlit para que todo esté alineado */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
    }
    /* Evitar que el panel lateral herede el borde blanco */
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { border: none !important; background-color: transparent !important; box-shadow: none !important; padding: 0 !important; }

    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important; border-radius: 6px !important; }
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: 600 !important; color: #64748B !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #1E3A8A !important; border-bottom: 3px solid #1E3A8A !important; }
    
    .invoice-container { float: right; width: 340px; background-color: #FFFFFF; padding: 25px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .invoice-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px; color: #475569; }
    .invoice-total { display: flex; justify-content: space-between; border-top: 2px solid #CBD5E1; padding-top: 15px; margin-top: 15px; font-size: 24px; font-weight: 800; color: #1E3A8A; }
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if "nav_menu" not in st.session_state: st.session_state.nav_menu = "Panel de inicio"
if "filtro_dashboard" not in st.session_state: st.session_state.filtro_dashboard = "Aprobada"
if "items_cot" not in st.session_state: st.session_state.items_cot = []
if "cotizacion_activa" not in st.session_state: st.session_state.cotizacion_activa = None
if "cliente_recien_creado" not in st.session_state: st.session_state.cliente_recien_creado = None

ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]

# --- GENERACIÓN DE BASE DE DATOS ---
if "proveedores_catalogo" not in st.session_state:
    cat_temp = []
    servicios_base = [("Cabina fotográfica 360", "Entretenimiento", 300.0, 0.0), ("Carpa estructural 6x6", "Estructuras", 50.0, 0.15), ("Animador corporativo", "Animación", 150.0, 0.15), ("Catering premium", "Alimentos", 25.0, 0.15), ("Sonido profesional", "Audiovisual", 180.0, 0.15), ("Iluminación robótica", "Audiovisual", 120.0, 0.15), ("Logística pesada", "Logística", 80.0, 0.0), ("Alquiler mobiliario", "Mobiliario", 150.0, 0.15), ("Decoración floral", "Decoración", 350.0, 0.15), ("Maestro ceremonias", "Talento", 250.0, 0.15)]
    for ciu in ciudades_lista:
        for serv, cat, precio, iva in servicios_base:
            cat_temp.append({"servicio": serv, "proveedor": f"Pro{cat} {ciu[:3].upper()}", "categoria": cat, "ciudad": ciu, "precio_base": precio, "iva": iva, "banco": "Banco", "cuenta": f"Cta. {ciu[:3].upper()}-{len(cat_temp)}", "descripcion": "Servicio estandarizado."})
    st.session_state.proveedores_catalogo = cat_temp

if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {"codigo": "KG-20261001-001", "evento": "Fiesta fin de año", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 414.00, "items": [{"servicio": "Cabina fotográfica 360", "proveedor": "ProEntretenimiento QUI", "ciudad": "Quito", "fecha": "2026-12-15", "cantidad": 1, "costo": 300.0, "iva_prov": 0.0, "fee_pct": 20.0}]},
        {"codigo": "KG-20261002-002", "evento": "Lanzamiento de marca", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-11-10", "estado": "Enviada", "total": 3400.00, "items": []},
        {"codigo": "KG-20261003-003", "evento": "Cena de directivos", "cliente": "Hilton Colón Quito", "fecha": "2026-10-20", "estado": "Borrador", "total": 850.00, "items": []},
        {"codigo": "KG-20261004-004", "evento": "Capacitación anual", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-08-05", "estado": "Aprobada", "total": 1250.00, "items": []},
    ]

if "clientes_catalogo" not in st.session_state:
    st.session_state.clientes_catalogo = [
        {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
        {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
        {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
    ]

# --- MENÚ LATERAL REDISEÑADO ---
st.sidebar.markdown("<div class='brand-logo'>Karkajadas Group</div>", unsafe_allow_html=True)
if st.sidebar.button("Panel de inicio"): st.session_state.nav_menu = "Panel de inicio"; st.rerun()
if st.sidebar.button("Reportes financieros"): st.session_state.nav_menu = "Reportes financieros"; st.rerun()
if st.sidebar.button("Proyecciones de ventas"): st.session_state.nav_menu = "Proyecciones de ventas"; st.rerun()
if st.sidebar.button("Noticias corporativas"): st.session_state.nav_menu = "Noticias corporativas"; st.rerun()
st.sidebar.markdown("<p style='font-size: 11px; color: #94A3B8; font-weight: 700; margin-top: 20px; padding-left: 5px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
if st.sidebar.button("Centro de ayuda"): st.session_state.nav_menu = "Centro de ayuda"; st.rerun()
if st.sidebar.button("Documentación operativa"): st.session_state.nav_menu = "Documentación operativa"; st.rerun()

menu = st.session_state.nav_menu

# --- MÓDULOS EN CONSTRUCCIÓN ---
if menu in ["Reportes financieros", "Proyecciones de ventas", "Noticias corporativas", "Centro de ayuda", "Documentación operativa"]:
    st.markdown(f"<h2 style='color: #0F172A; font-weight: 700;'>{menu}</h2>", unsafe_allow_html=True)
    st.info("Módulo en construcción. Nuestro equipo de desarrollo está trabajando para habilitar esta funcionalidad.")

# --- VISTA 1: PANEL PRINCIPAL ---
elif menu == "Panel de inicio":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Panel de inicio</h2>", unsafe_allow_html=True)
    
    # 1. ACCESOS RÁPIDOS (Contenedor Nativo)
    with st.container(border=True):
