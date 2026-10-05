import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (MÁXIMA EXPANSIÓN) ---
st.set_page_config(
    page_title="Karkajadas Group - ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS AVANZADOS Y COLORIMETRÍA ESTRICTA ---
st.markdown("""
    <style>
    /* Ajuste de márgenes principales para que no se corte el título */
    .block-container { padding-top: 4rem !important; padding-bottom: 2rem !important; max-width: 98% !important; }
    .stApp, .main, header { background-color: #F8FAFC !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* Mostrar control de colapso de menú lateral */
    [data-testid="collapsedControl"] { color: #FFFFFF !important; background-color: #1E293B !important; border-radius: 4px !important; margin: 10px !important;}
    [data-testid="collapsedControl"] svg { fill: #FFFFFF !important; }

    /* Contenedores nativos de Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 8px !important; border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
        padding: 15px 25px !important; margin-bottom: 15px !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { border: none !important; background-color: transparent !important; box-shadow: none !important; padding: 0 !important; }

    /* ----------------------------------------------------
       BOTONES GLOBALES: VERDE (Avanzar), AZUL (Neutro)
       ---------------------------------------------------- */
    button[kind="primary"] {
        background-color: #059669 !important; border: 1px solid #059669 !important; color: #FFFFFF !important;
        border-radius: 4px !important; padding: 0.5rem 1.2rem !important; font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2) !important; transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover { background-color: #047857 !important; transform: translateY(-1px); }

    button[kind="secondary"] {
        background-color: #1E3A8A !important; border: 1px solid #1E3A8A !important; color: #FFFFFF !important;
        border-radius: 4px !important; padding: 0.5rem 1.2rem !important; font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2) !important; transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover { background-color: #1E40AF !important; transform: translateY(-1px); }

    /* ----------------------------------------------------
       MÉTODO INFALIBLE PARA BOTONES DE MÉTRICAS (KPIs)
       ---------------------------------------------------- */
    /* Ocultar gancho invisible */
    div[data-testid="element-container"]:has(.kpi-marker) { display: none !important; margin: 0 !important; padding: 0 !important; height: 0 !important; }

    /* Estilo base para los 4 botones KPI */
    div[data-testid="element-container"]:has(.kpi-marker) + div[data-testid="element-container"] button {
        width: 100% !important; padding: 15px 20px !important; border-radius: 8px !important;
        height: auto !important; min-height: 90px !important; border: none !important;
        display: flex !important; justify-content: flex-start !important; text-align: left !important;
        transition: all 0.2s ease !important; color: white !important;
    }
    div[data-testid="element-container"]:has(.kpi-marker) + div[data-testid="element-container"] button p {
        font-size: 16px !important; font-weight: 800 !important; line-height: 1.4 !important;
        white-space: pre-wrap !important; margin: 0 !important;
    }
    div[data-testid="element-container"]:has(.kpi-marker) + div[data-testid="element-container"] button:hover { transform: translateY(-3px) !important; }

    /* Aprobadas -> Verde */
    div[data-testid="element-container"]:has(.kpi-aprobada) + div[data-testid="element-container"] button { background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; box-shadow: 0 4px 6px rgba(5,150,105,0.3) !important; }
    /* Enviadas -> Azul */
    div[data-testid="element-container"]:has(.kpi-enviada) + div[data-testid="element-container"] button { background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%) !important; box-shadow: 0 4px 6px rgba(30,58,138,0.3) !important; }
    /* Borradores -> Gris */
    div[data-testid="element-container"]:has(.kpi-borrador) + div[data-testid="element-container"] button { background: linear-gradient(135deg, #64748B 0%, #475569 100%) !important; box-shadow: 0 4px 6px rgba(100,116,139,0.3) !important; }
    /* Canceladas -> Rojo */
    div[data-testid="element-container"]:has(.kpi-cancelada) + div[data-testid="element-container"] button { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important; box-shadow: 0 4px 6px rgba(239,68,68,0.3) !important; }

    /* ----------------------------------------------------
       BOTONES COMPACTOS DE LA TABLA
       ---------------------------------------------------- */
    div[data-testid="column"]:nth-child(8) button, div[data-testid="column"]:nth-child(9) button {
        background-color: transparent !important; border: 1px solid #CBD5E1 !important; color: #475569 !important;
        padding: 0 !important; min-height: 28px !important; height: 28px !important; box-shadow: none !important; width: 100%;
    }
    div[data-testid="column"]:nth-child(8) button:hover, div[data-testid="column"]:nth-child(9) button:hover { background-color: #F1F5F9 !important; color: #1E3A8A !important; }

    div[data-testid="column"]:nth-child(10) button {
        background-color: #EF4444 !important; border: 1px solid #EF4444 !important; color: white !important;
        padding: 0 !important; min-height: 28px !important; height: 28px !important; font-weight: bold !important; width: 100%;
    }
    div[data-testid="column"]:nth-child(10) button:hover { background-color: #DC2626 !important; }

    /* ----------------------------------------------------
       PANEL LATERAL (Simetría Absoluta)
       ---------------------------------------------------- */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important; }
    .brand-logo { font-size: 22px; font-weight: 900; color: #FFFFFF; margin-bottom: 20px; margin-top: 5px; padding-left: 5px; letter-spacing: 0.5px;}
    
    [data-testid="stSidebar"] div[data-testid="stButton"] { width: 100% !important; margin-bottom: 2px !important; }
    [data-testid="stSidebar"] div[data-testid="stButton"] button {
        background-color: #1E293B !important; border: 1px solid #334155 !important; color: #CBD5E1 !important;
        border-radius: 8px !important; padding: 12px 15px !important; 
        width: 100% !important; display: flex !important; justify-content: flex-start !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important; transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] button p { width: 100% !important; text-align: left !important; font-weight: 500 !important; margin: 0 !important;}
    [data-testid="stSidebar"] div[data-testid="stButton"] button:hover { 
        background-color: #334155 !important; color: #FFFFFF !important; border-color: #475569 !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.4) !important; transform: translateX(4px) !important; 
    }

    /* Formularios y Títulos */
    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important; border-radius: 4px !important; min-height: 38px !important;}
    .stSelectbox label, .stTextInput label, .stNumberInput label { font-size: 13px !important; color: #64748B !important; font-weight: 600 !important; margin-bottom: 4px !important;}
    .section-title { color: #0F172A; font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px;}
    
    .invoice-container { float: right; width: 320px; background-color: #F8FAFC; padding: 20px; border-radius: 6px; border: 1px solid #CBD5E1; }
    .invoice-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; color: #475569; }
    .invoice-total { display: flex; justify-content: space-between; border-top: 2px solid #CBD5E1; padding-top: 10px; margin-top: 10px; font-size: 20px; font-weight: 800; color: #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if "nav_menu" not in st.session_state: st.session_state.nav_menu = "Panel de inicio"
if "items_cot" not in st.session_state: st.session_state.items_cot = []
if "cotizacion_activa" not in st.session_state: st.session_state.cotizacion_activa = None
if "cliente_recien_creado" not in st.session_state: st.session_state.cliente_recien_creado = None
if "filtro_estado_tabla" not in st.session_state: st.session_state.filtro_estado_tabla = "Todas"

ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]

# --- BASE DE DATOS DE PRUEBA ---
if "proveedores_catalogo" not in st.session_state:
    cat_temp = []
    servicios_base = [("Cabina fotográfica 360", "Entretenimiento", 300.0, 0.0), ("Carpa estructural 6x6", "Estructuras", 50.0, 0.15), ("Animador corporativo", "Animación", 150.0, 0.15), ("Catering premium", "Alimentos", 25.0, 0.15), ("Sonido profesional", "Audiovisual", 180.0, 0.15)]
    for ciu in ciudades_lista:
        for serv, cat, precio, iva in servicios_base:
            cat_temp.append({"servicio": serv, "proveedor": f"Pro{cat} {ciu[:3].upper()}", "categoria": cat, "ciudad": ciu, "precio_base": precio, "iva": iva, "banco": "Banco", "cuenta": f"Cta.", "descripcion": "Estándar"})
    st.session_state.proveedores_catalogo = cat_temp

if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {"codigo": "KG-20261215-001", "evento": "Fiesta corporativa", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 1414.00, "items": [{"servicio": "Cabina fotográfica", "proveedor": "Pro", "ciudad": "Quito", "fecha": "2026-12-15", "cantidad": 1, "costo": 300.0, "iva_prov": 0.0, "fee_pct": 20.0}]},
        {"codigo": "KG-20261110-002", "evento": "Lanzamiento de marca", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-11-10", "estado": "Enviada", "total": 2248.40, "items": [{"servicio": "Sonido profesional", "proveedor": "Pro", "ciudad": "Quito", "fecha": "2026-11-10", "cantidad": 1, "costo": 180.0, "iva_prov": 0.15, "fee_pct": 20.0}]},
        {"codigo": "KG-20261020-003", "evento": "Cena de directivos", "cliente": "Hilton Colón Quito", "fecha": "2026-10-20", "estado": "Borrador", "total": 834.50, "items": [{"servicio": "Catering premium", "proveedor": "Pro", "ciudad": "Quito", "fecha": "2026-10-20", "cantidad": 1, "costo": 25.0, "iva_prov": 0.15, "fee_pct": 20.0}]},
        {"codigo": "KG-20260905-004", "evento": "Capacitación anual", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-09-05", "estado": "Aprobada", "total": 3150.00, "items": [{"servicio": "Logística", "proveedor": "Pro", "ciudad": "Quito", "fecha": "2026-09-05", "cantidad": 1, "costo": 1000.0, "iva_prov": 0.0, "fee_pct": 15.0}]},
        {"codigo": "KG-20260812-005", "evento": "Activación BTL", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-08-12", "estado": "Aprobada", "total": 1850.00, "items": [{"servicio": "Animador corporativo", "proveedor": "Pro", "ciudad": "Quito", "fecha": "2026-08-12", "cantidad": 5, "costo": 150.0, "iva_prov": 0.15, "fee_pct": 20.0}]},
        {"codigo": "KG-20261005-006", "evento": "Feria de exposición", "cliente": "Hilton Colón Quito", "fecha": "2026-10-05", "estado": "Aprobada", "total": 2200.00, "items": [{"servicio": "Carpa", "proveedor": "Pro", "ciudad": "Quito", "fecha": "2026-10-05", "cantidad": 2, "costo": 50.0, "iva_prov": 0.15, "fee_pct": 20.0}]}
    ]

if "clientes_catalogo" not in st.session_state:
    st.session_state.clientes_catalogo = [
        {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
        {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
        {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
    ]

# --- MENÚ LATERAL ---
st.sidebar.markdown("<div class='brand-logo'>Karkajadas Group</div>", unsafe_allow_html=True)
if st.sidebar.button("Panel de inicio", use_container_width=True): st.session_state.nav_menu = "Panel de inicio"; st.rerun()
if st.sidebar.button("Reportes financieros", use_container_width=True): st.session_state.nav_menu = "Reportes financieros"; st.rerun()
if st.sidebar.button("Proyecciones de ventas", use_container_width=True): st.session_state.nav_menu = "Proyecciones de ventas"; st.rerun()
if st.sidebar.button("Noticias corporativas", use_container_width=True): st.session_state.nav_menu = "Noticias corporativas"; st.rerun()
st.sidebar.markdown("<p style='font-size: 11px; color: #64748B; font-weight: 700; margin-top: 20px; padding-left: 10px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
if st.sidebar.button("Centro de ayuda", use_container_width=True): st.session_state.nav_menu = "Centro de ayuda"; st.rerun()
if st.sidebar.button("Documentación operativa", use_container_width=True): st.session_state.nav_menu = "Documentación operativa"; st.rerun()

menu = st.session_state.nav_menu

if menu in ["Reportes financieros", "Proyecciones de ventas", "Noticias corporativas", "Centro de ayuda", "Documentación operativa"]:
    st.markdown(f"<h2 style='color: #0F172A; font-weight: 800;'>{menu}</h2>", unsafe_allow_html=True)
    st.info("Módulo en construcción.")

# --- VISTA 1: PANEL PRINCIPAL (ALTA DENSIDAD BI) ---
elif menu == "Panel de inicio":
    
    # 1. ACCESOS RÁPIDOS Y TÍTULO COMPACTO
    with st.container(border=True):
        col_tit, col_btns = st.columns([1, 2.5])
        with col_tit:
            st.markdown("<h3 style='color: #0F172A; font-weight: 800; margin: 0; padding-top: 5px;'>Panel de Control</h3>", unsafe_allow_html=True)
            st.markdown("<span style='color: #64748B; font-size: 13px; font-weight:600;'>Resumen Ejecutivo</span>", unsafe_allow_html=True)
        with col_btns:
            b1, b2, b3 = st.columns(3) 
            with b1:
                if st.button("Crear cotización", use_container_width=True, type="primary"): 
                    st.session_state.nav_menu = "Nueva cotización"; st.session_state.cotizacion_activa = None; st.session_state.items_cot = []; st.rerun()
            with b2:
                if st.button("Directorio Clientes", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.session_state.vista_directorio = "clientes"; st.rerun()
            with b3:
                if st.button("Directorio Proveedores", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.session_state.vista_directorio = "proveedores"; st.rerun()
    
    # 2. FILTROS OPERATIVOS GLOBALES
    with st.container(border=True):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:0;'>Filtros Operativos Globales</div>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        lista_cli = sorted(list(set([c["cliente"] for c in st.session_state.cotizaciones_guardadas])))
        lista_mes = sorted(list(set([c["fecha"][:7] for c in st.session_state.cotizaciones_guardadas])))
        with col_f1: f_emp = st.selectbox("Empresa / Cuenta", ["Todas"] + lista_cli, label_visibility="collapsed")
        with col_f2: f_mes = st.selectbox("Mes operativo", ["Todos"] + lista_mes, label_visibility="collapsed")
        with col_f3: f_ciu = st.selectbox("Ciudad de facturación", ["Todas"] + ciudades_lista, label_visibility="collapsed")

    cots_dash = []
    for c in st.session_state.cotizaciones_guardadas:
        ciu_cliente = next((cli["ciudad"] for cli in st.session_state.clientes_catalogo if cli["empresa"] == c["cliente"]), "Desconocida")
        if f_emp != "Todas" and c["cliente"] != f_emp: continue
        if f_mes != "Todos" and c["fecha"][:7] != f_mes: continue
        if f_ciu != "Todas" and ciu_cliente != f_ciu: continue
        cots_dash.append(c)

    tot_apr = sum(c["total"] for c in cots_dash if c["estado"] == "Aprobada")
    tot_env = sum(c["total"] for c in cots_dash if c["estado"] == "Enviada")
    tot_bor = sum(c["total"] for c in cots_dash if c["estado"] == "Borrador")
    tot_can = sum(c["total"] for c in cots_dash if c["estado"] == "Cancelada")
    tot_gen = tot_apr + tot_env + tot_bor + tot_can

    # 3. ANÁLISIS VISUAL Y MÉTRICAS (KPIs 100% Funcionales)
    with st.container(border=True):
        st.markdown("<div class='section-title'>Análisis Visual del Portafolio</div>", unsafe_allow_html=True)
        
        # Fila de Botones KPI (El CSS inyectado los colorea perfectamente)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown("<div class='kpi-marker kpi-aprobada'></div>", unsafe_allow_html=True)
            if st.button(f"APROBADAS\n${tot_apr:,.2f}", use_container_width=True, key="btn_apr"): st.session_state.filtro_estado_tabla = "Aprobada"; st.rerun()
        with m2:
            st.markdown("<div class='kpi-marker kpi-enviada'></div>", unsafe_allow_html=True)
            if st.button(f"ENVIADAS\n${tot_env:,.2f}", use_container_width=True, key="btn_env"): st.session_state.filtro_estado_tabla = "Enviada"; st.rerun()
        with m3:
            st.markdown("<div class='kpi-marker kpi-borrador'></div>", unsafe_allow_html=True)
            if st.button(f"BORRADORES\n${tot_bor:,.2f}", use_container_width=True, key="btn_bor"): st.session_state.filtro_estado_tabla = "Borrador"; st.rerun()
        with m4:
            st.markdown("<div class='kpi-marker kpi-cancelada'></div>", unsafe_allow_html=True)
            if st.button(f"CANCELADAS\n${tot_can:,.2f}", use_container_width=True, key="btn_can"): st.session_state.filtro_estado_tabla = "Cancelada"; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_donut, col_trend = st.columns([1, 2.5])
        
        with col_donut:
            if tot_gen > 0:
                df_chart = pd.DataFrame({"Estado": ["Aprobada", "Enviada", "Borrador", "Cancelada"], "Monto": [tot_apr, tot_env, tot_bor, tot_can]})
                df_chart = df_chart[df_chart["Monto"] > 0]
                # Eliminamos el Padding para evitar el TypeError
                chart = alt.Chart(df_chart).mark_arc(innerRadius=45, outerRadius=90, cornerRadius=4, padAngle=0.03).encode(
                    theta=alt.Theta(field="Monto", type="quantitative"), 
                    color=alt.Color(field="Estado", type="nominal", scale=alt.Scale(domain=["Aprobada", "Enviada", "Borrador", "Cancelada"], range=["#059669", "#1E3A8A", "#64748B", "#EF4444"]), legend=alt.Legend(title="Distribución", orient="bottom")), 
                    tooltip=["Estado", alt.Tooltip("Monto", format="$,.2f")]
                ).properties(height=260)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Sin datos para distribución.")

        with col_trend:
            # Gráfico de BARRAS (No Timeline Irreal). Cambia según el estado visualizado en la tabla.
            estado_actual = st.session_state.filtro_estado_tabla
            color_barras = {"Aprobada": "#059669", "Enviada": "#1E3A8A", "Borrador": "#64748B", "Cancelada": "#EF4444"}.get(estado_actual, "#059669")
            
            df_bar = pd.DataFrame([{"Fecha": c["fecha"], "Monto": c["total"]} for c in cots_dash if c["estado"] == estado_actual])
            
            if not df_bar.empty:
                df_bar["Fecha"] = pd.to_datetime(df_bar["Fecha"]).dt.strftime('%Y-%m-%d')
                df_bar = df_bar.groupby("Fecha")["Monto"].sum().reset_index().sort_values("Fecha")
                
                chart_bar = alt.Chart(df_bar).mark_bar(color=color_barras, cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=30).encode(
                    x=alt.X('Fecha:O', title='Fecha de Operación', axis=alt.Axis(labelAngle=-45, grid=False, labelColor='#64748B')),
                    y=alt.Y('Monto:Q', title=f'Volumen {estado_actual.upper()} ($)', axis=alt.Axis(format='$,.0f', gridColor='#E2E8F0', labelColor='#64748B')),
                    tooltip=[alt.Tooltip('Fecha:O', title='Fecha'), alt.Tooltip('Monto:Q', format='$,.2f', title='Total')]
                ).properties(height=260)
                st.altair_chart(chart_bar, use_container_width=True)
            else:
                st.markdown(f"<div style='padding-top:100px; text-align:center; color:#64748B;'>No hay ingresos registrados en la categoría <b>{estado_actual}</b> para el periodo seleccionado.</div>", unsafe_allow_html=True)

    # 4. TABLA DETALLADA CON SELECTOR EXPLÍCITO Sincronizado
    with st.container(border=True):
        st.markdown("<div class='section-title'>Detalle Operativo de Cotizaciones</div>", unsafe_allow_html=True)
        
        col_rad, col_bus = st.columns([2, 1])
        with col_rad:
            # Selector vinculado directamente a la misma variable que cambian los botones KPI
            st.radio("Filtro de visualización en tabla:", ["Todas", "Aprobada", "Enviada", "Borrador", "Cancelada"], horizontal=True, key="filtro_estado_tabla")
        with col_bus:
            b_univ = st.text_input("Buscador...", key="b_u", label_visibility="collapsed", placeholder="Buscar código o cliente...")
        
        st.markdown("<hr style='margin: 5px 0 15px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        ev_filt = cots_dash
        if st.session_state.filtro_estado_tabla != "Todas":
            ev_filt = [cot for cot in cots_dash if cot["estado"] == st.session_state.filtro_estado_tabla]
        if b_univ:
            ev_filt = [c for c in ev_filt if b_univ.lower() in c['codigo'].lower() or b_univ.lower() in c['evento'].lower() or b_univ.lower() in c['cliente'].lower()]
        
        if ev_filt:
            cx = st.columns([1.5, 2, 2.5, 1.5, 1])
            cx[0].markdown("<span style='font-size:11px; font-weight:700; color:#64748B;'>CÓDIGO / FECHA</span>", unsafe_allow_html=True)
            cx[1].markdown("<span style='font-size:11px; font-weight:700; color:#64748B;'>EVENTO / ESTADO</span>", unsafe_allow_html=True)
            cx[2].markdown("<span style='font-size:11px; font-weight:700; color:#64748B;'>CLIENTE CORPORATIVO</span>", unsafe_allow_html=True)
            cx[3].markdown("<span style='font-size:11px; font-weight:700; color:#64748B;'>MONTO ESTIMADO</span>", unsafe_allow_html=True)
            cx[4].markdown("<span style='font-size:11px; font-weight:700; color:#64748B;'>ACCIÓN</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 2px 0 5px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            
            for cot in ev_filt:
                cx = st.columns([1.5, 2, 2.5, 1.5, 1])
                cx[0].write(f"**{cot['codigo']}**\n\n<span style='font-size:12px; color:#475569;'>{cot['fecha']}</span>", unsafe_allow_html=True)
                
                col_est = "#059669" if cot['estado'] == "Aprobada" else ("#1E3A8A" if cot['estado'] == "Enviada" else ("#64748B" if cot['estado'] == "Borrador" else "#EF4444"))
                cx[1].write(f"{cot['evento']}\n\n<span style='font-size:11px; font-weight:800; color:{col_est};'>{cot['estado'].upper()}</span>", unsafe_allow_html=True)
                
                cx[2].write(f"{cot['cliente']}")
                cx[3].write(f"**${cot['total']:,.2f}**")
                with cx[4]:
                    if st.button("Abrir", key=f"ab_{cot['codigo']}", type="secondary", use_container_width=True):
                        st.session_state.cotizacion_activa = cot; st.session_state.items_cot = cot.get("items", []); st.session_state.nav_menu = "Nueva cotización"; st.rerun()
                st.markdown("<hr style='margin: 2px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
        else:
            st.info(f"No hay cotizaciones para mostrar.")

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    
    sub_head = sum((i["cantidad"] * i["costo"] * (1 + i["iva_prov"])) * (1 + i["fee_pct"]/100.0) for i in st.session_state.items_cot)
    tot_head = sub_head * 1.15
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;'>
            <h2 style='font-weight: 800; color: #0F172A; margin: 0;'>Gestión de cotizaciones</h2>
            <div style='text-align: right;'>
                <span style='font-size: 12px; color: #64748B; font-weight: 700; text-transform: uppercase;'>Monto Estimado</span><br>
                <span style='color: #1E3A8A; font-weight: 800; font-size: 28px; line-height:1;'>${tot_head:,.2f}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    c_activa = st.session_state.cotizacion_activa
    lista_cli = [c["empresa"] for c in st.session_state.clientes_catalogo] + ["+ Registrar nuevo cliente..."]
    def_cod = c_activa["codigo"] if c_activa else f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    def_ev = c_activa["evento"] if c_activa else ""
    def_cli_idx = lista_cli.index(st.session_state.cliente_recien_creado) if st.session_state.cliente_recien_creado else (lista_cli.index(c_activa["cliente"]) if c_activa and c_activa["cliente"] in lista_cli else 0)
    st.session_state.cliente_recien_creado = None 
    def_est_idx = ["Borrador", "Enviada", "Aprobada", "Cancelada"].index(c_activa["estado"]) if c_activa else 0
    
    with st.container(border=True):
        col_tit, col_btn = st.columns([4, 1])
        with col_tit: st.markdown("<div class='section-title'>Información del evento</div>", unsafe_allow_html=True)
        with col_btn:
            if st.button("Guardar cambios", type="primary", use_container_width=True, key="btn_s_top"):
                if cliente_sel == "+ Registrar nuevo cliente...": st.error("Registre el cliente.")
                else:
                    if c_activa: st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != c_activa["codigo"]]
                    st.session_state.cotizaciones_guardadas.append({"codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, "fecha": str(fecha_gral), "estado": estado_cot, "total": tot_head, "items": st.session_state.items_cot.copy()})
                    st.success("Guardado."); st.session_state.nav_menu = "Panel de inicio"; st.rerun()

        col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
        with col1: cod_cotizacion = st.text_input("Referencia", value=def_cod)
        with col2: nombre_evento = st.text_input("Nombre del evento", value=def_ev)
        with col3: cliente_sel = st.selectbox("Cuenta de cliente", lista_cli, index=def_cli_idx)
        with col4: fecha_gral = st.date_input("Fecha", datetime.now()) 
        with col5: estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"], index=def_est_idx)

    if cliente_sel == "+ Registrar nuevo cliente...":
        with st.container(border=True):
            st.markdown("<div class='section-title' style='color:#059669; border-color:#059669;'>Apertura de cuenta corporativa</div>", unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns(3)
            with cc1: i_emp = st.text_input("Razón social *"); i_ruc = st.text_input("RUC *"); i_ciu = st.selectbox("Ciudad", ciudades_lista)
            with cc2: i_dir = st.text_input("Dirección"); i_web = st.text_input("Sitio web"); i_cont = st.text_input("Contacto")
            with cc3: i_mail = st.text_input("Correo"); i_tel = st.text_input("Teléfono"); i_dias = st.number_input("Días crédito", value=30, step=15)
            if st.button("Guardar y aplicar", type="primary"):
                if i_emp.strip() != "" and i_ruc.strip() != "":
                    st.session_state.clientes_catalogo.append({"empresa": i_emp, "ruc": i_ruc, "ciudad": i_ciu, "direccion": i_dir, "web": i_web, "contacto": i_cont, "email": i_mail, "telefono": i_tel, "dias_credito": i_dias})
                    st.session_state.cliente_recien_creado = i_emp; st.rerun()
                else: st.error("Razón social y RUC son requeridos.")

    with st.container(border=True):
        st.markdown("<div class='section-title'>Añadir servicios</div>", unsafe_allow_html=True)
        tab_cat, tab_man = st.tabs(["Seleccionar del catálogo", "Ingreso manual"])
        
        with tab_cat:
            f1, f2 = st.columns([1, 2])
            with f1: ciu_f = st.selectbox("Filtrar ciudad", ciudades_lista, index=0)
            with f2: pal_b = st.text_input("Buscar proveedor/servicio...")
            
            res = [p for p in st.session_state.proveedores_catalogo if p["ciudad"] == ciu_f and (pal_b.lower() in p["servicio"].lower() or pal_b.lower() in p["proveedor"].lower())]
            if not res: st.warning("No hay registros.")
            else:
                opc = [f"{r['proveedor']} ➔ {r['servicio']} | IVA {int(r['iva']*100)}% | {r.get('descripcion','')}" for r in res]
                sel = st.selectbox("Proveedor:", opc)
                item_sel = res[opc.index(sel)]
                ca, cb, cc, cd, ce = st.columns(5)
                with ca: f_it = st.date_input("Fecha de servicio", value=fecha_gral)
                with cb: can_it = st.number_input("Cantidad", min_value=1, value=1)
                with cc: cos_it = st.number_input("Costo unit. ($)", value=float(item_sel["precio_base"]))
                with cd: iva_it = st.selectbox("IVA prov.", [0.0, 0.15], index=1 if item_sel["iva"] > 0 else 0, format_func=lambda x: f"{int(x*100)}%")
                with ce: fee_it = st.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f")
                
                if st.button("Agregar a la cotización", type="primary"):
                    st.session_state.items_cot.append({"servicio": item_sel["servicio"], "proveedor": item_sel["proveedor"], "ciudad": ciu_f, "fecha": str(f_it), "cantidad": can_it, "costo": cos_it, "iva_prov": iva_it, "fee_pct": fee_it})
                    st.rerun()

        with tab_man:
            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1: n_pro = st.text_input("Proveedor *")
            with nc2: n_ser = text_input = st.text_input("Servicio *")
            with nc3: n_ciu = st.selectbox("Ciudad op.", ciudades_lista, key="mc_c")
            with nc4: n_cat = st.text_input("Categoría")
            
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: f_it_m = st.date_input("Fecha de servicio", value=fecha_gral, key="mc_f")
            with cb: can_it_m = st.number_input("Cantidad", min_value=1, value=1, key="mc_ca")
            with cc: cos_it_m = st.number_input("Costo unit. ($)", value=0.00, format="%.2f", key="mc_co")
            with cd: iva_it_m = st.selectbox("IVA prov.", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x*100)}%", key="mc_i")
            with ce: fee_it_m = st.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f", key="mc_ma")
            g_bd = st.checkbox("Guardar en directorio", value=True)
            
            if st.button("Registrar y agregar", type="primary"):
                if n_pro.strip() and n_ser.strip():
                    st.session_state.items_cot.append({"servicio": n_ser, "proveedor": n_pro, "ciudad": n_ciu, "fecha": str(f_it_m), "cantidad": can_it_m, "costo": cos_it_m, "iva_prov": iva_it_m, "fee_pct": fee_it_m})
                    if g_bd: st.session_state.proveedores_catalogo.append({"servicio": n_ser, "proveedor": n_pro, "categoria": n_cat if n_cat else "General", "ciudad": n_ciu, "precio_base": cos_it_m, "iva": iva_it_m, "banco": "N/A", "cuenta": "N/A", "descripcion": "Manual"})
                    st.rerun()
                else: st.error("Proveedor y servicio requeridos.")

    if st.session_state.items_cot:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Estructura de costos</div>", unsafe_allow_html=True)
            hx = st.columns([2.5, 1.4, 0.6, 1.0, 0.6, 1.2, 1.0, 0.4, 0.4, 0.4])
            titulos = ["PROVEEDOR / SERVICIO", "FECHA / ZONA", "CANT.", "COSTO U.", "IVA", "MARGEN", "SUBTOTAL", "", "", ""]
            for i, t in enumerate(titulos): hx[i].markdown(f"<span style='font-size:11px; font-weight:700; color:#64748B;'>{t}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 4px 0 10px 0; border-top: 1px solid #CBD5E1;'>", unsafe_allow_html=True)
            
            s_prov = 0; t_fee = 0; s_com = 0
            for idx, item in enumerate(st.session_state.items_cot):
                c_lin = item["cantidad"] * item["costo"]
                c_iva = c_lin + (c_lin * item["iva_prov"])
                f_val = c_iva * (item["fee_pct"] / 100.0)
                p_ven = c_iva + f_val
                s_prov += c_iva; t_fee += f_val; s_com += p_ven
                
                cx = st.columns([2.5, 1.4, 0.6, 1.0, 0.6, 1.2, 1.0, 0.4, 0.4, 0.4])
                cx[0].write(f"**{item['proveedor']}** \n\n<span style='color:#475569;'>{item['servicio']}</span>", unsafe_allow_html=True)
                cx[1].write(f"{item['fecha']} \n\n<span style='color:#475569;'>{item['ciudad']}</span>", unsafe_allow_html=True)
                cx[2].write(f"{item['cantidad']}")
                cx[3].write(f"${item['costo']:,.2f}")
                cx[4].write(f"{int(item['iva_prov']*100)}%")
                cx[5].write(f"<span style='color:#64748B;'>{item['fee_pct']:.0f}%</span> <span style='font-weight:600; color:#059669;'>+${f_val:,.2f}</span>", unsafe_allow_html=True)
                cx[6].write(f"**${p_ven:,.2f}**")
                
                with cx[7]:
                    if st.button("↑", key=f"u_{idx}", disabled=(idx == 0), type="secondary"): st.session_state.items_cot.insert(idx - 1, st.session_state.items_cot.pop(idx)); st.rerun()
                with cx[8]:
                    if st.button("↓", key=f"d_{idx}", disabled=(idx == len(st.session_state.items_cot) - 1), type="secondary"): st.session_state.items_cot.insert(idx + 1, st.session_state.items_cot.pop(idx)); st.rerun()
                with cx[9]:
                    if st.button("X", key=f"x_{idx}", type="primary"): st.session_state.items_cot.pop(idx); st.rerun() 
                st.markdown("<hr style='margin: 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
                
            iva_cli = s_com * 0.15; t_cli = s_com + iva_cli
            st.markdown("<br>", unsafe_allow_html=True)
            cm1, cm2, ci = st.columns([1.2, 1.2, 1.6])
            with cm1: st.markdown(f"<div class='internal-metrics'>Costos operativos</div><div class='internal-metrics-value'>${s_prov:,.2f}</div>", unsafe_allow_html=True)
            with cm2: st.markdown(f"<div class='internal-metrics'>Rentabilidad (Ganancia)</div><div class='internal-metrics-value'>${t_fee:,.2f}</div>", unsafe_allow_html=True)
            with ci: st.markdown(f"<div class='invoice-container'><div class='invoice-row'><span>Subtotal</span><span>${s_com:,.2f}</span></div><div class='invoice-row'><span>IVA 15%</span><span>${iva_cli:,.2f}</span></div><div class='invoice-total'><span>TOTAL INVERSIÓN</span><span>${t_cli:,.2f}</span></div></div><div style='clear:both;'></div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            ce, cg = st.columns([3, 1])
            with cg:
                if st.button("Guardar cotización final", use_container_width=True, type="primary", key="btn_save_bot"):
                    if c_activa: st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != c_activa["codigo"]]
                    if cliente_sel == "+ Registrar nuevo cliente...": st.error("Registre el cliente.")
                    else:
                        st.session_state.cotizaciones_guardadas.append({"codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, "fecha": str(fecha_gral), "estado": estado_cot, "total": t_cli, "items": st.session_state.items_cot.copy()})
                        st.success("Guardado exitoso."); st.session_state.nav_menu = "Panel de inicio"; st.rerun()

# --- VISTA 4: DIRECTORIOS ---
elif menu == "Directorios":
    st.markdown("<h2 style='color: #0F172A; font-weight: 800; margin-bottom: 20px;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        t_cli, t_pro = st.tabs(["Directorio de clientes", "Red de proveedores"])
        with t_cli:
            df_c = pd.DataFrame(st.session_state.clientes_catalogo).rename(columns={"empresa": "Empresa", "ruc": "RUC", "ciudad": "Ciudad", "direccion": "Dirección", "web": "Web", "contacto": "Contacto", "email": "Correo", "telefono": "Teléfono", "dias_credito": "Días Crédito"})
            st.dataframe(df_c, use_container_width=True, hide_index=True)
            st.markdown("<hr style='margin: 15px 0;'><div class='section-title' style='border:none;'>Nueva cuenta corporativa</div>", unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns(3)
            with cc1: n_emp = st.text_input("Empresa *"); n_ruc = st.text_input("RUC *"); n_ciu = st.selectbox("Ciudad", ciudades_lista, key="c_ciu")
            with cc2: n_dir = st.text_input("Dirección"); n_web = st.text_input("Web"); n_cont = st.text_input("Contacto")
            with cc3: n_corr = st.text_input("Correo"); n_tel = st.text_input("Teléfono"); n_dias = st.number_input("Días crédito", value=30, step=15)
            if st.button("Registrar cuenta", type="primary"):
                if n_emp and n_ruc:
                    st.session_state.clientes_catalogo.append({"empresa": n_emp, "ruc": n_ruc, "ciudad": n_ciu, "direccion": n_dir, "web": n_web, "contacto": n_cont, "email": n_corr, "telefono": n_tel, "dias_credito": n_dias})
                    st.success("Registrado."); st.rerun()
                else: st.error("Obligatorio Empresa y RUC.")

        with t_pro:
            df_p = pd.DataFrame(st.session_state.proveedores_catalogo).rename(columns={"servicio": "Servicio", "proveedor": "Proveedor", "categoria": "Categoría", "ciudad": "Ciudad", "precio_base": "Costo ($)", "iva": "IVA", "banco": "Banco", "cuenta": "Cuenta", "descripcion": "Descripción"})
            df_p["IVA"] = df_p["IVA"].apply(lambda x: f"{int(x*100)}%"); df_p["Costo ($)"] = df_p["Costo ($)"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_p, use_container_width=True, hide_index=True)
            st.markdown("<hr style='margin: 15px 0;'><div class='section-title' style='border:none;'>Nuevo proveedor</div>", unsafe_allow_html=True)
            cp1, cp2, cp3 = st.columns(3)
            with cp1: p_pro = st.text_input("Proveedor *"); p_ser = st.text_input("Servicio *"); p_cat = st.text_input("Categoría")
            with cp2: p_ciu = st.selectbox("Ciudad", ciudades_lista, key="p_ciu"); p_cos = st.number_input("Costo ($)", value=0.00); p_iva = st.selectbox("IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%", key="p_iva")
            with cp3: p_ban = st.text_input("Banco"); p_cta = st.text_input("Cuenta"); p_des = text_input = st.text_input("Observaciones")
            if st.button("Registrar proveedor", type="primary"):
                if p_pro and p_ser:
                    st.session_state.proveedores_catalogo.append({"servicio": p_ser, "proveedor": p_pro, "categoria": p_cat, "ciudad": p_ciu, "precio_base": p_cos, "iva": p_iva, "banco": p_ban, "cuenta": p_cta, "descripcion": p_des})
                    st.success("Registrado."); st.rerun()
                else: st.error("Obligatorio Proveedor y Servicio.")
