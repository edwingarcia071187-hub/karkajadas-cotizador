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
    .brand-logo { font-size: 24px; font-weight: 900; color: #FFFFFF; margin-bottom: 25px; margin-top: 10px; text-align: left; padding-left: 5px; letter-spacing: 0.5px;}
    
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
if st.sidebar.button("Panel de inicio", use_container_width=True): st.session_state.nav_menu = "Panel de inicio"; st.rerun()
if st.sidebar.button("Reportes financieros", use_container_width=True): st.session_state.nav_menu = "Reportes financieros"; st.rerun()
if st.sidebar.button("Proyecciones de ventas", use_container_width=True): st.session_state.nav_menu = "Proyecciones de ventas"; st.rerun()
if st.sidebar.button("Noticias corporativas", use_container_width=True): st.session_state.nav_menu = "Noticias corporativas"; st.rerun()
st.sidebar.markdown("<p style='font-size: 11px; color: #64748B; font-weight: 700; margin-top: 20px; padding-left: 10px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
if st.sidebar.button("Centro de ayuda", use_container_width=True): st.session_state.nav_menu = "Centro de ayuda"; st.rerun()
if st.sidebar.button("Documentación operativa", use_container_width=True): st.session_state.nav_menu = "Documentación operativa"; st.rerun()

menu = st.session_state.nav_menu

# --- MÓDULOS EN CONSTRUCCIÓN ---
if menu in ["Reportes financieros", "Proyecciones de ventas", "Noticias corporativas", "Centro de ayuda", "Documentación operativa"]:
    st.markdown(f"<h2 style='color: #0F172A;'>{menu}</h2>", unsafe_allow_html=True)
    st.info("Módulo en construcción. Nuestro equipo de desarrollo está trabajando para habilitar esta funcionalidad.")

# --- VISTA 1: PANEL PRINCIPAL ---
elif menu == "Panel de inicio":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Panel de inicio</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Accesos Rápidos</h4>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Crear nueva cotización", use_container_width=True, type="primary"): 
                st.session_state.nav_menu = "Nueva cotización"; st.session_state.cotizacion_activa = None; st.session_state.items_cot = []; st.rerun()
        with b2:
            if st.button("Directorio de clientes", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.session_state.vista_directorio = "clientes"; st.rerun()
        with b3:
            if st.button("Red de proveedores", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.session_state.vista_directorio = "proveedores"; st.rerun()
    
    with st.container(border=True):
        st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Filtros Operativos</h4>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        lista_cli = sorted(list(set([c["cliente"] for c in st.session_state.cotizaciones_guardadas])))
        lista_mes = sorted(list(set([c["fecha"][:7] for c in st.session_state.cotizaciones_guardadas])))
        with col_f1: f_emp = st.selectbox("Empresa / Cuenta", ["Todas"] + lista_cli)
        with col_f2: f_mes = st.selectbox("Mes operativo", ["Todos"] + lista_mes)
        with col_f3: f_ciu = st.selectbox("Ciudad de facturación", ["Todas"] + ciudades_lista)

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

    with st.container(border=True):
        st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Estado del Portafolio</h4>", unsafe_allow_html=True)
        col_chart, col_leyenda = st.columns([1, 1.8])
        with col_chart:
            if tot_gen > 0:
                df_chart = pd.DataFrame({"Estado": ["Aprobadas", "Enviadas", "Borradores", "Canceladas"], "Monto": [tot_apr, tot_env, tot_bor, tot_can]})
                df_chart = df_chart[df_chart["Monto"] > 0]
                chart = alt.Chart(df_chart).mark_arc(innerRadius=65, outerRadius=110, cornerRadius=6, padAngle=0.03).encode(
                    theta=alt.Theta(field="Monto", type="quantitative"), 
                    color=alt.Color(field="Estado", type="nominal", scale=alt.Scale(domain=["Aprobadas", "Enviadas", "Borradores", "Canceladas"], range=["#059669", "#1E3A8A", "#94A3B8", "#EF4444"]), legend=None), 
                    tooltip=["Estado", alt.Tooltip("Monto", format="$,.2f")]
                ).properties(height=280)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Sin datos para los filtros seleccionados.")

        with col_leyenda:
            st.markdown("<p style='font-size: 13px; color: #64748B;'>Seleccione una métrica para filtrar el listado inferior:</p>", unsafe_allow_html=True)
            lm1, lm2 = st.columns(2)
            with lm1:
                if st.button(f"Aprobadas\n\n${tot_apr:,.2f}", use_container_width=True, type="secondary"): st.session_state.filtro_dashboard = "Aprobada"; st.rerun()
                if st.button(f"Borradores\n\n${tot_bor:,.2f}", use_container_width=True, type="secondary"): st.session_state.filtro_dashboard = "Borrador"; st.rerun()
            with lm2:
                if st.button(f"Enviadas\n\n${tot_env:,.2f}", use_container_width=True, type="secondary"): st.session_state.filtro_dashboard = "Enviada"; st.rerun()
                if st.button(f"Canceladas\n\n${tot_can:,.2f}", use_container_width=True, type="secondary"): st.session_state.filtro_dashboard = "Cancelada"; st.rerun()
    
    with st.container(border=True):
        col_tit, col_bus = st.columns([2, 1])
        with col_tit: st.markdown(f"<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Operaciones: {st.session_state.filtro_dashboard}</h4>", unsafe_allow_html=True)
        with col_bus: b_univ = st.text_input("Buscador...", key="b_u", label_visibility="collapsed", placeholder="Buscar código o cliente...")
        
        ev_filt = [cot for cot in cots_dash if cot["estado"] == st.session_state.filtro_dashboard]
        if b_univ: ev_filt = [c for c in ev_filt if b_univ.lower() in c['codigo'].lower() or b_univ.lower() in c['evento'].lower() or b_univ.lower() in c['cliente'].lower()]
        
        if ev_filt:
            cx = st.columns([1.5, 2, 2.5, 1.5, 1])
            cx[0].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>CÓDIGO / FECHA</span>", unsafe_allow_html=True)
            cx[1].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>EVENTO</span>", unsafe_allow_html=True)
            cx[2].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>CLIENTE</span>", unsafe_allow_html=True)
            cx[3].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>MONTO</span>", unsafe_allow_html=True)
            cx[4].markdown("<span style='font-size:12px; font-weight:700; color:#64748B;'>ACCIÓN</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            for cot in ev_filt:
                cx = st.columns([1.5, 2, 2.5, 1.5, 1])
                cx[0].write(f"**{cot['codigo']}**\n\n{cot['fecha']}")
                cx[1].write(f"{cot['evento']}")
                cx[2].write(f"{cot['cliente']}")
                cx[3].write(f"**${cot['total']:,.2f}**")
                with cx[4]:
                    if st.button("Abrir", key=f"ab_{cot['codigo']}", type="secondary", use_container_width=True):
                        st.session_state.cotizacion_activa = cot; st.session_state.items_cot = cot.get("items", []); st.session_state.nav_menu = "Nueva cotización"; st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
        else:
            st.info("No hay registros en esta categoría.")

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    
    sub_head = sum((i["cantidad"] * i["costo"] * (1 + i["iva_prov"])) * (1 + i["fee_pct"]/100.0) for i in st.session_state.items_cot)
    tot_head = sub_head * 1.15
    
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;'>
            <h2 style='font-weight: 700; color: #0F172A; margin: 0;'>Gestión de cotizaciones</h2>
            <div style='text-align: right;'>
                <span style='font-size: 13px; color: #64748B; font-weight: 600; text-transform: uppercase;'>Monto Estimado</span>
                <h1 style='margin: 0; color: #1E3A8A; font-weight: 800;'>${tot_head:,.2f}</h1>
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
        st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Información del evento</h4>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
        with col1: cod_cotizacion = st.text_input("Referencia", value=def_cod)
        with col2: nombre_evento = st.text_input("Nombre del evento", value=def_ev)
        with col3: cliente_sel = st.selectbox("Cuenta de cliente", lista_cli, index=def_cli_idx)
        with col4: fecha_gral = st.date_input("Fecha", datetime.now()) 
        with col5: estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"], index=def_est_idx)

    if cliente_sel == "+ Registrar nuevo cliente...":
        with st.container(border=True):
            st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Apertura de cuenta</h4>", unsafe_allow_html=True)
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
        st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Añadir servicios</h4>", unsafe_allow_html=True)
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
            with nc2: n_ser = st.text_input("Servicio *")
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
            st.markdown("<h4 style='color: #0F172A; font-size: 14px; margin-top:0; text-transform: uppercase;'>Estructura de costos</h4>", unsafe_allow_html=True)
            hx = st.columns([2.5, 1.4, 0.6, 1.0, 0.6, 1.2, 1.0, 0.4, 0.4, 0.4])
            titulos = ["PROVEEDOR / SERVICIO", "FECHA / ZONA", "CANT.", "COSTO U.", "IVA", "MARGEN", "SUBTOTAL", "", "", ""]
            for i, t in enumerate(titulos): hx[i].markdown(f"<span style='font-size:12px; font-weight:700; color:#64748B;'>{t}</span>", unsafe_allow_html=True)
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
            with ci: st.markdown(f"<div class='invoice-container'><div class='invoice-row'><span>Subtotal</span><span>${s_com:,.2f}</span></div><div class='invoice-row'><span>IVA 15%</span><span>${iva_cli:,.2f}</span></div><div class='invoice-total'><span>TOTAL</span><span>${t_cli:,.2f}</span></div></div><div style='clear:both;'></div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            ce, cg = st.columns([3, 1])
            with cg:
                if st.button("Guardar cotización", use_container_width=True, type="primary"):
                    if c_activa: st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != cod_cotizacion]
                    if cliente_sel == OPCION_NUEVO: st.error("Registre el cliente.")
                    else:
                        st.session_state.cotizaciones_guardadas.append({"codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, "fecha": str(fecha_gral), "estado": estado_cot, "total": t_cli, "items": st.session_state.items_cot.copy()})
                        st.success("Guardado exitoso."); st.session_state.nav_menu = "Panel de inicio"; st.rerun()

# --- VISTA 4: DIRECTORIOS ---
elif menu == "Directorios":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        t_cli, t_pro = st.tabs(["Directorio de clientes", "Red de proveedores"])
        with t_cli:
            df_c = pd.DataFrame(st.session_state.clientes_catalogo).rename(columns={"empresa": "Empresa", "ruc": "RUC", "ciudad": "Ciudad", "direccion": "Dirección", "web": "Web", "contacto": "Contacto", "email": "Correo", "telefono": "Teléfono", "dias_credito": "Días Crédito"})
            st.dataframe(df_c, use_container_width=True, hide_index=True)
            st.markdown("<hr style='margin: 15px 0;'><h4 style='color: #0F172A; font-size: 14px; text-transform: uppercase;'>Nueva cuenta</h4>", unsafe_allow_html=True)
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
            st.markdown("<hr style='margin: 15px 0;'><h4 style='color: #0F172A; font-size: 14px; text-transform: uppercase;'>Nuevo proveedor</h4>", unsafe_allow_html=True)
            cp1, cp2, cp3 = st.columns(3)
            with cp1: p_pro = st.text_input("Proveedor *"); p_ser = st.text_input("Servicio *"); p_cat = st.text_input("Categoría")
            with cp2: p_ciu = st.selectbox("Ciudad", ciudades_lista, key="p_ciu"); p_cos = st.number_input("Costo ($)", value=0.00); p_iva = st.selectbox("IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%", key="p_iva")
            with cp3: p_ban = st.text_input("Banco"); p_cta = st.text_input("Cuenta"); p_des = text_input = st.text_input("Observaciones")
            if st.button("Registrar proveedor", type="primary"):
                if p_pro and p_ser:
                    st.session_state.proveedores_catalogo.append({"servicio": p_ser, "proveedor": p_pro, "categoria": p_cat, "ciudad": p_ciu, "precio_base": p_cos, "iva": p_iva, "banco": p_ban, "cuenta": p_cta, "descripcion": p_des})
                    st.success("Registrado."); st.rerun()
                else: st.error("Obligatorio Proveedor y Servicio.")
