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

# --- ESTILOS CSS AVANZADOS Y COLORIMETRÍA SEMÁNTICA ---
st.markdown("""
    <style>
    /* Tipografía y fondos principales */
    .stApp, .main, header { background-color: #F8FAFC !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* Contenedores estilo Tarjeta (QuickBooks style) */
    .card-container {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Títulos de Sección (Jerarquía Visual) */
    .section-title {
        color: #0F172A;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #E2E8F0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ----------------------------------------------------
       COLORIMETRÍA DE BOTONES
       ---------------------------------------------------- */
    /* Botones PRIMARIOS por defecto (AZUL CORPORATIVO) */
    button[kind="primary"] {
        background-color: #1E3A8A !important; 
        color: #FFFFFF !important;
        border-radius: 4px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        border: none !important; 
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover { background-color: #1E40AF !important; }

    /* Botones SECUNDARIOS (Gris claro / Bordes sutiles) */
    button[kind="secondary"] {
        background-color: #FFFFFF !important; 
        color: #475569 !important;
        border-radius: 4px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #CBD5E1 !important; 
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover { background-color: #F1F5F9 !important; border-color: #94A3B8 !important; color: #0F172A !important; }

    /* BOTONES VERDES (Crear, Avanzar, Guardar, Agregar) */
    div[data-testid="element-container"]:has(.btn-verde) + div[data-testid="element-container"] button {
        background-color: #059669 !important; 
        color: #FFFFFF !important; 
        border: none !important;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2) !important;
    }
    div[data-testid="element-container"]:has(.btn-verde) + div[data-testid="element-container"] button:hover { background-color: #047857 !important; transform: translateY(-1px); }

    /* BOTÓN ROJO (Eliminar - Fila 10 de tablas) */
    div[data-testid="column"]:nth-child(10) button {
        background-color: #EF4444 !important; 
        color: white !important;
        border: none !important;
        padding: 0 !important;
        min-height: 32px !important; height: 32px !important;
        font-weight: bold;
    }
    div[data-testid="column"]:nth-child(10) button:hover { background-color: #DC2626 !important; }

    /* Botones Compactos de Tabla (Flechas) */
    div[data-testid="column"]:nth-child(8) button,
    div[data-testid="column"]:nth-child(9) button {
        padding: 0 !important;
        min-height: 32px !important; height: 32px !important;
        font-size: 14px !important;
    }

    /* Esconder marcadores CSS */
    div[data-testid="element-container"]:has(.btn-marker) { display: none !important; margin: 0 !important; padding: 0 !important; height: 0 !important; }

    /* ----------------------------------------------------
       DISEÑO DEL MENÚ LATERAL Y TABS (PESTAÑAS)
       ---------------------------------------------------- */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important; border-right: none !important; }
    .brand-logo { font-size: 22px; font-weight: 900; color: #FFFFFF; margin-bottom: 25px; margin-top: 10px; text-align: left; padding-left: 10px; letter-spacing: 0.5px; }
    [data-testid="stSidebar"] button[kind="secondary"] { background-color: transparent !important; border: none !important; text-align: left !important; justify-content: flex-start !important; color: #CBD5E1 !important; box-shadow: none !important;}
    [data-testid="stSidebar"] button[kind="secondary"]:hover { background-color: rgba(255, 255, 255, 0.1) !important; color: #FFFFFF !important; transform: translateX(3px);}

    /* Personalización de Pestañas (Tabs) de Streamlit para que luzcan Enterprise */
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: 600 !important; color: #64748B !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #1E3A8A !important; border-bottom: 3px solid #1E3A8A !important; }

    /* ----------------------------------------------------
       MÓDULO FINANCIERO TIPO FACTURA
       ---------------------------------------------------- */
    .invoice-total-container { float: right; width: 320px; text-align: right; background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; }
    .invoice-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 15px; color: #475569; }
    .invoice-final-total { display: flex; justify-content: space-between; border-top: 2px solid #CBD5E1; padding-top: 15px; margin-top: 15px; font-size: 22px; font-weight: 800; color: #1E3A8A; }
    .internal-metrics { font-size: 13px; color: #64748B; margin-bottom: 5px; text-transform: uppercase; font-weight: 600;}
    .internal-metrics-value { font-size: 20px; font-weight: 700; color: #0F172A; }
    
    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important; border-radius: 4px; }
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

# --- GENERACIÓN DE BASE DE DATOS DE PRUEBA ---
if "proveedores_catalogo" not in st.session_state:
    cat_temp = []
    servicios_base = [
        ("Cabina fotográfica 360", "Entretenimiento", 300.0, 0.0),
        ("Carpa estructural 6x6 blanca", "Estructuras", 50.0, 0.15),
        ("Animador corporativo master", "Animación", 150.0, 0.15),
        ("Catering premium por persona", "Alimentos", 25.0, 0.15),
        ("Sonido y amplificación profesional", "Audiovisual", 180.0, 0.15),
        ("Iluminación perimetral y robótica", "Audiovisual", 120.0, 0.15),
        ("Transporte y logística pesada", "Logística", 80.0, 0.0),
        ("Alquiler sillas y mesas", "Mobiliario", 150.0, 0.15),
        ("Decoración floral corporativa", "Decoración", 350.0, 0.15),
        ("Maestro de ceremonias", "Talento", 250.0, 0.15)
    ]
    for ciu in ciudades_lista:
        prefijo = ciu[:3].upper()
        for serv, cat, precio, iva in servicios_base:
            cat_temp.append({
                "servicio": serv, "proveedor": f"Pro{cat} {prefijo}", "categoria": cat,
                "ciudad": ciu, "precio_base": precio, "iva": iva,
                "banco": "Banco Comercial", "cuenta": f"Cta. {prefijo}-{len(cat_temp)}",
                "descripcion": f"Servicio estandarizado operativo en {ciu}."
            })
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
if st.sidebar.button("Nueva cotización"): st.session_state.nav_menu = "Nueva cotización"; st.session_state.cotizacion_activa = None; st.session_state.items_cot = []; st.rerun()
if st.sidebar.button("Gestión de cuentas (CRM)"): st.session_state.nav_menu = "Directorios"; st.rerun()
if st.sidebar.button("Reportes financieros"): st.session_state.nav_menu = "Reportes financieros"; st.rerun()
if st.sidebar.button("Proyecciones de ventas"): st.session_state.nav_menu = "Proyecciones de ventas"; st.rerun()
if st.sidebar.button("Noticias corporativas"): st.session_state.nav_menu = "Noticias corporativas"; st.rerun()

st.sidebar.markdown("<hr style='margin: 10px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 11px; color: #94A3B8; font-weight: 700; letter-spacing: 1px; padding-left: 10px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
if st.sidebar.button("Centro de ayuda"): st.session_state.nav_menu = "Centro de ayuda"; st.rerun()
if st.sidebar.button("Documentación operativa"): st.session_state.nav_menu = "Documentación operativa"; st.rerun()

menu = st.session_state.nav_menu

# --- MÓDULOS EN CONSTRUCCIÓN ---
if menu in ["Reportes financieros", "Proyecciones de ventas", "Noticias corporativas", "Centro de ayuda", "Documentación operativa"]:
    st.markdown(f"<h2 style='color: #0F172A; font-weight: 700;'>{menu}</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.info("Módulo en construcción. Nuestro equipo de desarrollo está trabajando para habilitar esta funcionalidad.")

# --- VISTA 1: PANEL PRINCIPAL ---
elif menu == "Panel de inicio":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Panel de inicio</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Filtros de rendimiento operativo</div>", unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1.5])
    lista_clientes_dropdown = sorted(list(set([c["cliente"] for c in st.session_state.cotizaciones_guardadas])))
    lista_meses_dropdown = sorted(list(set([c["fecha"][:7] for c in st.session_state.cotizaciones_guardadas])))
    
    with col_f1: filtro_empresa = st.selectbox("Empresa / Cuenta", ["Todas"] + lista_clientes_dropdown)
    with col_f2: filtro_mes = st.selectbox("Mes operativo (Año-Mes)", ["Todos"] + lista_meses_dropdown)
    with col_f3: filtro_ciudad = st.selectbox("Ciudad de facturación", ["Todas"] + ciudades_lista)
    with col_f4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
        if st.button("Crear cotización", use_container_width=True, type="primary"):
            st.session_state.nav_menu = "Nueva cotización"
            st.session_state.cotizacion_activa = None
            st.session_state.items_cot = []
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Filtrado lógico de Dashboard
    cots_dash = []
    for c in st.session_state.cotizaciones_guardadas:
        ciu_cliente = "Desconocida"
        for cli in st.session_state.clientes_catalogo:
            if cli["empresa"] == c["cliente"]:
                ciu_cliente = cli["ciudad"]
                break
        if filtro_empresa != "Todas" and c["cliente"] != filtro_empresa: continue
        if filtro_mes != "Todos" and c["fecha"][:7] != filtro_mes: continue
        if filtro_ciudad != "Todas" and ciu_cliente != filtro_ciudad: continue
        cots_dash.append(c)

    tot_aprobadas = sum(c["total"] for c in cots_dash if c["estado"] == "Aprobada")
    tot_enviadas = sum(c["total"] for c in cots_dash if c["estado"] == "Enviada")
    tot_borradores = sum(c["total"] for c in cots_dash if c["estado"] == "Borrador")
    tot_canceladas = sum(c["total"] for c in cots_dash if c["estado"] == "Cancelada")
    tot_general = tot_aprobadas + tot_enviadas + tot_borradores + tot_canceladas

    # Gráfico y Métricas
    col_chart, col_leyenda = st.columns([1, 1.8])
    with col_chart:
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size:15px;'>Distribución</div>", unsafe_allow_html=True)
        if tot_general > 0:
            df_chart = pd.DataFrame({
                "Estado": ["Aprobadas", "Enviadas", "Borradores", "Canceladas"],
                "Monto": [tot_aprobadas, tot_enviadas, tot_borradores, tot_canceladas]
            })
            df_chart = df_chart[df_chart["Monto"] > 0]
            chart = alt.Chart(df_chart).mark_arc(innerRadius=45).encode(
                theta=alt.Theta(field="Monto", type="quantitative"),
                color=alt.Color(field="Estado", type="nominal", 
                                scale=alt.Scale(domain=["Aprobadas", "Enviadas", "Borradores", "Canceladas"], 
                                                range=["#059669", "#3B82F6", "#94A3B8", "#EF4444"]),
                                legend=None),
                tooltip=["Estado", "Monto"]
            ).properties(height=200)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No hay datos.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_leyenda:
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size:15px;'>Rendimiento por estado (Clic para filtrar tabla inferior)</div>", unsafe_allow_html=True)
        lm1, lm2 = st.columns(2)
        with lm1:
            if st.button(f"Aprobadas\n\n${tot_aprobadas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Aprobada" else "secondary"): st.session_state.filtro_dashboard = "Aprobada"; st.rerun()
            if st.button(f"Borradores\n\n${tot_borradores:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Borrador" else "secondary"): st.session_state.filtro_dashboard = "Borrador"; st.rerun()
        with lm2:
            if st.button(f"Enviadas\n\n${tot_enviadas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Enviada" else "secondary"): st.session_state.filtro_dashboard = "Enviada"; st.rerun()
            if st.button(f"Canceladas\n\n${tot_canceladas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Cancelada" else "secondary"): st.session_state.filtro_dashboard = "Cancelada"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Directorio Filtrado
    with st.container():
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)
        col_tit, col_bus = st.columns([2, 1])
        with col_tit:
            st.markdown(f"<div class='section-title'>Detalle de operaciones: {st.session_state.filtro_dashboard}</div>", unsafe_allow_html=True)
        with col_bus:
            busqueda_universal = st.text_input("Buscador rápido...", key="b_univ", label_visibility="collapsed", placeholder="Buscar documento...")
        
        eventos_filtrados = [cot for cot in cots_dash if cot["estado"] == st.session_state.filtro_dashboard]
        if busqueda_universal:
            term = busqueda_universal.lower()
            eventos_filtrados = [c for c in eventos_filtrados if term in c['codigo'].lower() or term in c['evento'].lower() or term in c['cliente'].lower()]
        
        if eventos_filtrados:
            cx = st.columns([1.5, 2, 2.5, 1.5, 1])
            cx[0].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>CÓDIGO / FECHA</span>", unsafe_allow_html=True)
            cx[1].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>EVENTO</span>", unsafe_allow_html=True)
            cx[2].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>CLIENTE CORPORATIVO</span>", unsafe_allow_html=True)
            cx[3].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>MONTO ESTIMADO</span>", unsafe_allow_html=True)
            cx[4].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>ACCIÓN</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            
            for cot in eventos_filtrados:
                cx = st.columns([1.5, 2, 2.5, 1.5, 1])
                cx[0].write(f"**{cot['codigo']}**\n\n{cot['fecha']}")
                cx[1].write(f"{cot['evento']}")
                cx[2].write(f"{cot['cliente']}")
                cx[3].write(f"**${cot['total']:,.2f}**")
                
                with cx[4]:
                    if st.button("Abrir", key=f"abrir_{cot['codigo']}", type="secondary", use_container_width=True):
                        st.session_state.cotizacion_activa = cot
                        st.session_state.items_cot = cot.get("items", [])
                        st.session_state.nav_menu = "Nueva cotización"
                        st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
        else:
            st.info("No hay registros en esta categoría de estatus.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    
    sub_comercial_header = 0
    for item in st.session_state.items_cot:
        c_linea = item["cantidad"] * item["costo"]
        c_con_iva = c_linea + (c_linea * item["iva_prov"])
        f_val = c_con_iva * (item["fee_pct"] / 100.0)
        sub_comercial_header += (c_con_iva + f_val)
    total_final_header = sub_comercial_header * 1.15
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
            <h2 style='font-weight: 700; color: #0F172A; margin: 0;'>Gestión de cotizaciones</h2>
            <div style='text-align: right;'>
                <span style='font-size: 13px; color: #64748B; font-weight: 700; text-transform: uppercase;'>Monto Total Estimado</span>
                <h1 style='margin: 0; color: #1E3A8A; font-weight: 800;'>${total_final_header:,.2f}</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    c_activa = st.session_state.cotizacion_activa
    lista_nombres_clientes = [c["empresa"] for c in st.session_state.clientes_catalogo]
    OPCION_NUEVO = "+ Registrar nuevo cliente..."
    lista_nombres_clientes.append(OPCION_NUEVO)
    
    def_cod = c_activa["codigo"] if c_activa else f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    def_ev = c_activa["evento"] if c_activa else ""
    
    if st.session_state.cliente_recien_creado:
        def_cli_idx = lista_nombres_clientes.index(st.session_state.cliente_recien_creado)
        st.session_state.cliente_recien_creado = None 
    else:
        def_cli_idx = lista_nombres_clientes.index(c_activa["cliente"]) if c_activa and c_activa["cliente"] in lista_nombres_clientes else 0
        
    def_est_idx = ["Borrador", "Enviada", "Aprobada", "Cancelada"].index(c_activa["estado"]) if c_activa else 0
    
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Información del evento</div>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
    with col1: cod_cotizacion = st.text_input("Referencia", value=def_cod)
    with col2: nombre_evento = st.text_input("Nombre del evento", value=def_ev)
    with col3: cliente_sel = st.selectbox("Cuenta de cliente", lista_nombres_clientes, index=def_cli_idx)
    with col4: fecha_gral = st.date_input("Fecha del evento", datetime.now()) 
    with col5: estado_cot = st.selectbox("Estado comercial", ["Borrador", "Enviada", "Aprobada", "Cancelada"], index=def_est_idx)
    st.markdown("</div>", unsafe_allow_html=True)

    if cliente_sel == OPCION_NUEVO:
        st.markdown("<div class='card-container' style='border-top: 3px solid #059669; margin-top: -10px;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size:15px; border:none;'>Apertura de nueva cuenta</div>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            i_emp = st.text_input("Razón social / Empresa *")
            i_ruc = st.text_input("RUC *")
            i_ciu = st.selectbox("Ciudad de facturación", ciudades_lista)
        with cc2:
            i_dir = st.text_input("Dirección corporativa")
            i_web = st.text_input("Sitio web")
            i_cont = st.text_input("Contacto principal")
        with cc3:
            i_mail = st.text_input("Correo electrónico")
            i_tel = st.text_input("Teléfono directo")
            i_dias = st.number_input("Días de crédito", value=30, step=15)
            
        st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
        if st.button("Guardar y aplicar", type="primary"):
            if i_emp.strip() != "" and i_ruc.strip() != "":
                st.session_state.clientes_catalogo.append({
                    "empresa": i_emp, "ruc": i_ruc, "ciudad": i_ciu, "direccion": i_dir,
                    "web": i_web, "contacto": i_cont, "email": i_mail, "telefono": i_tel, "dias_credito": i_dias
                })
                st.session_state.cliente_recien_creado = i_emp
                st.rerun()
            else:
                st.error("Razón social y RUC son requeridos.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Añadir servicios e insumos</div>", unsafe_allow_html=True)
    
    # USO DE PESTAÑAS (TABS) NATIVAS EN LUGAR DE BOTONES SEPARADOS
    tab_cat, tab_man = st.tabs(["Seleccionar del catálogo", "Ingreso manual"])
    
    with tab_cat:
        st.markdown("<br>", unsafe_allow_html=True)
        f1, f2 = st.columns([1, 2])
        with f1: ciudad_filtro = st.selectbox("Filtrar por ciudad", ciudades_lista, index=0)
        with f2: palabra_busqueda = st.text_input("Término de búsqueda (opcional)", placeholder="Buscar por proveedor o servicio...")
        
        resultados = []
        for p in st.session_state.proveedores_catalogo:
            if p["ciudad"] == ciudad_filtro:
                if palabra_busqueda == "" or \
                   palabra_busqueda.lower() in p["servicio"].lower() or \
                   palabra_busqueda.lower() in p["proveedor"].lower():
                    resultados.append(p)
        
        if not resultados:
            st.warning("No se encontraron registros en el catálogo actual.")
        else:
            opciones_str = []
            for r in resultados:
                iva_str = f"IVA {int(r['iva']*100)}%" if r['iva'] > 0 else "IVA 0%"
                desc = r.get("descripcion", "")
                opciones_str.append(f"{r['proveedor']} ➔ {r['servicio']} | {iva_str} | {desc}")
            
            seleccion = st.selectbox("Seleccione el proveedor corporativo:", opciones_str)
            item_seleccionado = resultados[opciones_str.index(seleccion)]
            
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: fecha_item = st.date_input("Fecha de ejecución", value=fecha_gral)
            with cb: cant_add = st.number_input("Cantidad", min_value=1, value=1)
            with cc: costo_add = st.number_input("Costo unitario ($)", value=float(item_seleccionado["precio_base"]))
            with cd: iva_add = st.selectbox("IVA", [0.0, 0.15], index=1 if item_seleccionado["iva"] > 0 else 0, format_func=lambda x: f"{int(x * 100)}%")
            with ce: fee_add = st.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f")
            
            st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
            if st.button("Agregar a la cotización", type="primary"):
                st.session_state.items_cot.append({
                    "servicio": item_seleccionado["servicio"], "proveedor": item_seleccionado["proveedor"], 
                    "ciudad": ciudad_filtro, "fecha": str(fecha_item), "cantidad": cant_add, 
                    "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                })
                st.rerun()

    with tab_man:
        st.markdown("<br>", unsafe_allow_html=True)
        nc1, nc2, nc3, nc4 = st.columns(4)
        with nc1: nuevo_proveedor = st.text_input("Razón social (Proveedor) *")
        with nc2: nuevo_servicio = st.text_input("Detalle del servicio *")
        with nc3: nueva_ciudad = st.selectbox("Ciudad operativa", ciudades_lista, key="mc_ciu")
        with nc4: nueva_categoria = st.text_input("Categoría de gasto")
        
        ca, cb, cc, cd, ce = st.columns(5)
        with ca: fecha_item = st.date_input("Fecha de ejecución", value=fecha_gral, key="mc_fec")
        with cb: cant_add = st.number_input("Cantidad", min_value=1, value=1, key="mc_can")
        with cc: costo_add = st.number_input("Costo unitario ($)", value=0.00, format="%.2f", key="mc_cos")
        with cd: iva_add = st.selectbox("IVA", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x * 100)}%", key="mc_iva")
        with ce: fee_add = st.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f", key="mc_mar")
        
        guardar_bd = st.checkbox("Registrar proveedor en el directorio corporativo", value=True)
        
        st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
        if st.button("Registrar y agregar", type="primary"):
            if nuevo_proveedor.strip() == "" or nuevo_servicio.strip() == "":
                st.error("Razón social y detalle del servicio son requeridos.")
            else:
                st.session_state.items_cot.append({
                    "servicio": nuevo_servicio, "proveedor": nuevo_proveedor, 
                    "ciudad": nueva_ciudad, "fecha": str(fecha_item), "cantidad": cant_add, 
                    "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                })
                if guardar_bd:
                    st.session_state.proveedores_catalogo.append({
                        "servicio": nuevo_servicio, "proveedor": nuevo_proveedor, "categoria": nueva_categoria if nueva_categoria else "General",
                        "ciudad": nueva_ciudad, "precio_base": costo_add, "iva": iva_add, "banco": "Pendiente", "cuenta": "Pendiente", "descripcion": "Ingreso manual"
                    })
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.items_cot:
        st.markdown("<div class='card-container' style='padding-bottom: 10px;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Estructura de costos</div>", unsafe_allow_html=True)
        
        hx = st.columns([2.5, 1.4, 0.6, 1.0, 0.6, 1.2, 1.0, 0.4, 0.4, 0.4])
        hx[0].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>PROVEEDOR / SERVICIO</span>", unsafe_allow_html=True)
        hx[1].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>FECHA / ZONA</span>", unsafe_allow_html=True)
        hx[2].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>CANT.</span>", unsafe_allow_html=True)
        hx[3].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>COSTO U.</span>", unsafe_allow_html=True)
        hx[4].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>IVA</span>", unsafe_allow_html=True)
        hx[5].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>MARGEN ($)</span>", unsafe_allow_html=True)
        hx[6].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>SUBTOTAL</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 4px 0 10px 0; border-top: 1px solid #CBD5E1;'>", unsafe_allow_html=True)
        
        subtotal_prov = 0; total_fee = 0; subtotal_comercial = 0
        
        for idx, item in enumerate(st.session_state.items_cot):
            costo_linea = item["cantidad"] * item["costo"]
            iva_prov_val = costo_linea * item["iva_prov"]
            costo_con_iva = costo_linea + iva_prov_val
            fee_val = costo_con_iva * (item["fee_pct"] / 100.0)
            precio_venta_linea = costo_con_iva + fee_val
            
            subtotal_prov += costo_con_iva
            total_fee += fee_val
            subtotal_comercial += precio_venta_linea
            
            cx = st.columns([2.5, 1.4, 0.6, 1.0, 0.6, 1.2, 1.0, 0.4, 0.4, 0.4])
            cx[0].write(f"**{item['proveedor']}** \n\n<span style='color:#475569;'>{item['servicio']}</span>", unsafe_allow_html=True)
            cx[1].write(f"{item['fecha']} \n\n<span style='color:#475569;'>{item['ciudad']}</span>", unsafe_allow_html=True)
            cx[2].write(f"{item['cantidad']}")
            cx[3].write(f"${item['costo']:,.2f}")
            cx[4].write(f"{int(item['iva_prov']*100)}%")
            cx[5].write(f"<span style='color:#64748B;'>{item['fee_pct']:.0f}%</span> <span style='font-weight:600; color:#059669;'>+${fee_val:,.2f}</span>", unsafe_allow_html=True)
            cx[6].write(f"**${precio_venta_linea:,.2f}**")
            
            with cx[7]:
                if st.button("↑", key=f"up_{idx}", disabled=(idx == 0), type="secondary"):
                    st.session_state.items_cot.insert(idx - 1, st.session_state.items_cot.pop(idx)); st.rerun()
            with cx[8]:
                if st.button("↓", key=f"down_{idx}", disabled=(idx == len(st.session_state.items_cot) - 1), type="secondary"):
                    st.session_state.items_cot.insert(idx + 1, st.session_state.items_cot.pop(idx)); st.rerun()
            with cx[9]:
                if st.button("X", key=f"del_{idx}"):
                    st.session_state.items_cot.pop(idx); st.rerun()
            st.markdown("<hr style='margin: 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
        iva_cliente_final = subtotal_comercial * 0.15
        total_cliente_final = subtotal_comercial + iva_cliente_final

        st.markdown("<br>", unsafe_allow_html=True)
        col_met1, col_met2, col_inv = st.columns([1.2, 1.2, 1.6])
        
        with col_met1:
            st.markdown(f"<div class='internal-metrics'>Costos operativos</div><div class='internal-metrics-value'>${subtotal_prov:,.2f}</div>", unsafe_allow_html=True)
        with col_met2:
            st.markdown(f"<div class='internal-metrics'>Rentabilidad (Ganancia)</div><div class='internal-metrics-value'>${total_fee:,.2f}</div>", unsafe_allow_html=True)
        with col_inv:
            st.markdown(f"""
            <div class='invoice-total-container'>
                <div class='invoice-row'><span>Subtotal</span><span>${subtotal_comercial:,.2f}</span></div>
                <div class='invoice-row'><span>IVA 15%</span><span>${iva_cliente_final:,.2f}</span></div>
                <div class='invoice-final-total'><span>TOTAL INVERSIÓN</span><span>${total_cliente_final:,.2f}</span></div>
            </div>
            <div style="clear:both;"></div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        col_espacio, col_guardar = st.columns([3, 1.2])
        with col_guardar:
            st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
            if st.button("Guardar cotización final", use_container_width=True, type="primary"):
                if c_activa:
                    st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != cod_cotizacion]
                
                if cliente_sel == OPCION_NUEVO:
                    st.error("Registre la cuenta del cliente antes de guardar.")
                else:
                    st.session_state.cotizaciones_guardadas.append({
                        "codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, 
                        "fecha": str(fecha_gral), "estado": estado_cot, "total": total_cliente_final, "items": st.session_state.items_cot.copy()
                    })
                    st.success("Documento registrado exitosamente.")
                    st.session_state.nav_menu = "Panel de inicio" 
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA 4: DIRECTORIOS (CRM) ---
elif menu == "Directorios":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='card-container' style='padding-bottom:10px;'>", unsafe_allow_html=True)
    tab_cli, tab_prov = st.tabs(["Directorio de clientes corporativos", "Red de proveedores homologados"])
    
    with tab_cli:
        st.markdown("<br>", unsafe_allow_html=True)
        df_clientes = pd.DataFrame(st.session_state.clientes_catalogo)
        df_clientes = df_clientes.rename(columns={
            "empresa": "Empresa", "ruc": "RUC", "ciudad": "Ciudad", 
            "direccion": "Dirección", "web": "Sitio web", "contacto": "Contacto", 
            "email": "Correo electrónico", "telefono": "Teléfono", "dias_credito": "Días de crédito"
        })
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        
        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size:16px; border:none;'>Apertura de nueva cuenta corporativa</div>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            n_empresa = st.text_input("Razón social / Empresa *")
            n_ruc = st.text_input("Registro Único de Contribuyentes (RUC) *")
            n_ciu = st.selectbox("Ciudad de facturación", ciudades_lista, key="cc_ciu")
        with cc2:
            n_dir = st.text_input("Dirección fiscal")
            n_web = st.text_input("Sitio web corporativo")
            n_contacto = st.text_input("Contacto autorizado")
        with cc3:
            n_correo = st.text_input("Correo electrónico financiero")
            n_tel = st.text_input("Teléfono directo")
            n_dias = st.number_input("Días de crédito asignados", value=30, step=15, key="cc_dias")
            
        st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
        if st.button("Registrar cuenta en el sistema", type="primary"):
            if n_empresa and n_ruc:
                st.session_state.clientes_catalogo.append({
                    "empresa": n_empresa, "ruc": n_ruc, "ciudad": n_ciu, "direccion": n_dir,
                    "web": n_web, "contacto": n_contacto, "email": n_correo, "telefono": n_tel, "dias_credito": n_dias
                })
                st.success("Cuenta corporativa registrada correctamente.")
                st.rerun()
            else:
                st.error("Razón social y RUC son requerimientos obligatorios.")

    with tab_prov:
        st.markdown("<br>", unsafe_allow_html=True)
        df_proveedores = pd.DataFrame(st.session_state.proveedores_catalogo)
        df_proveedores = df_proveedores.rename(columns={
            "servicio": "Servicio", "proveedor": "Proveedor", "categoria": "Categoría",
            "ciudad": "Ciudad", "precio_base": "Costo base ($)", "iva": "IVA",
            "banco": "Banco", "cuenta": "Cuenta", "descripcion": "Descripción"
        })
        df_proveedores["IVA"] = df_proveedores["IVA"].apply(lambda x: f"{int(x*100)}%")
        df_proveedores["Costo base ($)"] = df_proveedores["Costo base ($)"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_proveedores, use_container_width=True, hide_index=True)
        
        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size:16px; border:none;'>Registro de nuevo proveedor</div>", unsafe_allow_html=True)
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            p_prov = st.text_input("Razón social / Proveedor *")
            p_serv = st.text_input("Servicio o insumo principal *")
            p_cat = st.text_input("Categoría de gasto")
        with cp2:
            p_ciu = st.selectbox("Sede operativa", ciudades_lista, key="cp_ciu")
            p_costo = st.number_input("Costo referencial estándar ($)", value=0.00, key="cp_cos")
            p_iva = st.selectbox("IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%", key="cp_iva")
        with cp3:
            p_banco = st.text_input("Institución financiera")
            p_cta = st.text_input("Tipo y número de cuenta")
            p_desc = st.text_input("Condiciones técnicas cortas")
        
        st.markdown('<span class="btn-marker btn-verde"></span>', unsafe_allow_html=True)
        if st.button("Registrar proveedor", type="primary"):
            if p_prov and p_serv:
                st.session_state.proveedores_catalogo.append({
                    "servicio": p_serv, "proveedor": p_prov, "categoria": p_cat,
                    "ciudad": p_ciu, "precio_base": p_costo, "iva": p_iva,
                    "banco": p_banco, "cuenta": p_cta, "descripcion": p_desc
                })
                st.success("Proveedor registrado correctamente.")
                st.rerun()
            else:
                st.error("Razón social y Servicio principal son campos obligatorios.")
    st.markdown("</div>", unsafe_allow_html=True)
