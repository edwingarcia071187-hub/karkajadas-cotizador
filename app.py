import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Karkajadas Group - ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS AVANZADOS ---
st.markdown("""
    <style>
    /* Tipografía y fondos principales */
    .stApp, .main, header { background-color: #FFFFFF !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* ----------------------------------------------------
       COLORIMETRÍA DE BOTONES
       ---------------------------------------------------- */
    /* Botones primarios por defecto (Azul corporativo) */
    button[kind="primary"] {
        background-color: #1E3A8A !important; 
        color: #FFFFFF !important;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 14px;
        border: none !important; 
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover { background-color: #1E40AF !important; transform: translateY(-1px); }

    /* Botones secundarios (Grises para filtros y opciones) */
    button[kind="secondary"] {
        background-color: #F8FAFC !important; 
        color: #334155 !important;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #CBD5E1 !important; 
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover { background-color: #E2E8F0 !important; color: #0F172A !important; }
    
    /* BOTONES VERDES (Acciones de Avanzar: Crear, Guardar, Agregar) */
    div[data-testid="element-container"]:has(.btn-verde) + div[data-testid="element-container"] button {
        background-color: #059669 !important; 
        color: #FFFFFF !important; 
        border: none !important;
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2) !important;
    }
    div[data-testid="element-container"]:has(.btn-verde) + div[data-testid="element-container"] button:hover { background-color: #047857 !important; }

    /* Ajuste súper compacto para botones de acción en la tabla (Columnas 8, 9 y 10) */
    div[data-testid="column"]:nth-child(8) button,
    div[data-testid="column"]:nth-child(9) button,
    div[data-testid="column"]:nth-child(10) button {
        padding: 0.2rem 0.2rem !important;
        font-size: 11px !important;
        min-height: 28px !important;
    }
    /* BOTÓN ROJO (Eliminar X en columna 10) */
    div[data-testid="column"]:nth-child(10) button { background-color: #EF4444 !important; color: white !important; border: none !important; }
    div[data-testid="column"]:nth-child(10) button:hover { background-color: #DC2626 !important; }

    /* ----------------------------------------------------
       DISEÑO DEL MENÚ LATERAL (Elegante y Corporativo)
       ---------------------------------------------------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 50%, #334155 100%) !important;
    }
    /* Logo de la empresa Brillante */
    .brand-logo {
        font-size: 22px;
        font-weight: 900;
        background: linear-gradient(90deg, #38BDF8, #E0E7FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 25px;
        margin-top: 10px;
        text-align: center;
        letter-spacing: 0.5px;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #F8FAFC !important; }
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    [data-testid="stSidebar"] button:hover { background-color: rgba(255, 255, 255, 0.15) !important; border-color: #38BDF8 !important; }

    /* ----------------------------------------------------
       MODULO FINANCIERO TIPO FACTURA
       ---------------------------------------------------- */
    .invoice-container {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 15px 25px;
        width: 100%;
        text-align: right;
    }
    .inv-row { display: flex; justify-content: space-between; font-size: 15px; color: #475569; margin-bottom: 6px;}
    .inv-total { 
        display: flex; justify-content: space-between; 
        font-size: 32px !important; /* TOTAL MUCHO MÁS GRANDE */
        font-weight: 900; color: #1E3A8A; 
        margin-top: 10px; padding-top: 10px; border-top: 2px solid #CBD5E1;
    }

    /* ----------------------------------------------------
       OPTIMIZACIÓN DE ESPACIOS
       ---------------------------------------------------- */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    [data-testid="stExpander"] { background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 6px !important; margin-bottom: 10px !important;}
    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important; border-radius: 4px; }
    table tbody tr:hover { background-color: #F1F5F9 !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if "nav_menu" not in st.session_state: st.session_state.nav_menu = "Panel de inicio"
if "modo_ingreso" not in st.session_state: st.session_state.modo_ingreso = "catalogo"
if "vista_directorio" not in st.session_state: st.session_state.vista_directorio = "clientes"
if "filtro_dashboard" not in st.session_state: st.session_state.filtro_dashboard = "Aprobada"
if "items_cot" not in st.session_state: st.session_state.items_cot = []
if "cotizacion_activa" not in st.session_state: st.session_state.cotizacion_activa = None
if "vista_cliente" not in st.session_state: st.session_state.vista_cliente = False
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
        ("Alquiler sillas y mesas (x100)", "Mobiliario", 150.0, 0.15),
        ("Decoración floral corporativa", "Decoración", 350.0, 0.15),
        ("Maestro de ceremonias bilingüe", "Talento", 250.0, 0.15)
    ]
    for ciu in ciudades_lista:
        prefijo = ciu[:3].upper()
        for serv, cat, precio, iva in servicios_base:
            cat_temp.append({
                "servicio": serv, "proveedor": f"Pro{cat} {prefijo}", "categoria": cat,
                "ciudad": ciu, "precio_base": precio, "iva": iva,
                "banco": "Banco Comercial", "cuenta": f"Cta. {prefijo}-{len(cat_temp)}",
                "descripcion": f"Servicio estándar operativo en {ciu}."
            })
    st.session_state.proveedores_catalogo = cat_temp

if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {
            "codigo": "KG-20261001-001", "evento": "Fiesta fin de año", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 414.00,
            "items": [{"servicio": "Cabina fotográfica 360", "proveedor": "ProEntretenimiento QUI", "ciudad": "Quito", "fecha": "2026-12-15", "cantidad": 1, "costo": 300.0, "iva_prov": 0.0, "fee_pct": 20.0}]
        },
        {"codigo": "KG-20261002-002", "evento": "Lanzamiento de marca", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-11-10", "estado": "Enviada", "total": 3400.00, "items": []},
        {"codigo": "KG-20261003-003", "evento": "Cena de directivos", "cliente": "Hilton Colón Quito", "fecha": "2026-10-20", "estado": "Borrador", "total": 850.00, "items": []},
    ]

if "clientes_catalogo" not in st.session_state:
    st.session_state.clientes_catalogo = [
        {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
        {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
        {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
    ]

# --- MENÚ LATERAL (ESTRUCTURA ERP GERENCIAL CON FONDO ELEGANTE) ---
st.sidebar.markdown("<div class='brand-logo'>Karkajadas Group</div>", unsafe_allow_html=True)

if st.sidebar.button("Panel de inicio", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Panel de inicio"; st.rerun()
if st.sidebar.button("Gestión de cuentas (CRM)", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.rerun()
if st.sidebar.button("Reportes financieros", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Reportes financieros"; st.rerun()
if st.sidebar.button("Proyecciones de ventas", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Proyecciones de ventas"; st.rerun()
if st.sidebar.button("Noticias corporativas", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Noticias corporativas"; st.rerun()

st.sidebar.markdown("<hr style='margin: 10px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 11px; color: #94A3B8; font-weight: 600; letter-spacing: 1px;'>SOPORTE Y PROCESOS</p>", unsafe_allow_html=True)
if st.sidebar.button("Centro de ayuda", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Centro de ayuda"; st.rerun()
if st.sidebar.button("Documentación operativa", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Documentación operativa"; st.rerun()

menu = st.session_state.nav_menu

# --- MÓDULOS EN CONSTRUCCIÓN ---
if menu in ["Reportes financieros", "Proyecciones de ventas", "Noticias corporativas", "Centro de ayuda", "Documentación operativa"]:
    st.markdown(f"<h2 style='color: #0F172A; font-weight: 700;'>{menu}</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 15px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.info("Módulo en construcción. Nuestro equipo de desarrollo está trabajando para habilitar esta funcionalidad.")

# --- VISTA 1: PANEL PRINCIPAL ---
elif menu == "Panel de inicio":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Panel de inicio</h2>", unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
        if st.button("Crear nueva cotización", use_container_width=True, type="primary"): 
            st.session_state.nav_menu = "Nueva cotización"
            st.session_state.cotizacion_activa = None
            st.session_state.items_cot = []
            st.rerun()
    with b2:
        if st.button("Directorio de clientes", use_container_width=True, type="secondary"): 
            st.session_state.nav_menu = "Directorios"
            st.session_state.vista_directorio = "clientes"
            st.rerun()
    with b3:
        if st.button("Directorio de proveedores", use_container_width=True, type="secondary"): 
            st.session_state.nav_menu = "Directorios"
            st.session_state.vista_directorio = "proveedores"
            st.rerun()
            
    st.markdown("<hr style='margin: 25px 0 15px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 14px; font-weight: 600;'>RESUMEN FINANCIERO (Seleccione para filtrar el portafolio inferior)</p>", unsafe_allow_html=True)
    
    cots = st.session_state.cotizaciones_guardadas
    tot_aprobadas = sum(c["total"] for c in cots if c["estado"] == "Aprobada")
    tot_enviadas = sum(c["total"] for c in cots if c["estado"] == "Enviada")
    tot_borradores = sum(c["total"] for c in cots if c["estado"] == "Borrador")
    tot_canceladas = sum(c["total"] for c in cots if c["estado"] == "Cancelada")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if st.button(f"Aprobadas\n\n${tot_aprobadas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Aprobada" else "secondary"):
            st.session_state.filtro_dashboard = "Aprobada"; st.rerun()
    with m2:
        if st.button(f"Enviadas\n\n${tot_enviadas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Enviada" else "secondary"):
            st.session_state.filtro_dashboard = "Enviada"; st.rerun()
    with m3:
        if st.button(f"Borradores\n\n${tot_borradores:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Borrador" else "secondary"):
            st.session_state.filtro_dashboard = "Borrador"; st.rerun()
    with m4:
        if st.button(f"Canceladas\n\n${tot_canceladas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Cancelada" else "secondary"):
            st.session_state.filtro_dashboard = "Cancelada"; st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background-color: #F8FAFC; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        col_tit, col_bus = st.columns([2, 1])
        with col_tit:
            st.markdown(f"<h4 style='color: #1E3A8A; margin: 0;'>Portafolio de cotizaciones: {st.session_state.filtro_dashboard}</h4>", unsafe_allow_html=True)
        with col_bus:
            busqueda_universal = st.text_input("Buscar por código, evento o cliente...", key="b_univ", label_visibility="collapsed")
        
        eventos_filtrados = [cot for cot in cots if cot["estado"] == st.session_state.filtro_dashboard]
        if busqueda_universal:
            term = busqueda_universal.lower()
            eventos_filtrados = [c for c in eventos_filtrados if term in c['codigo'].lower() or term in c['evento'].lower() or term in c['cliente'].lower()]
        
        st.markdown("<hr style='margin: 10px 0; border-top: 2px solid #CBD5E1;'>", unsafe_allow_html=True)
        
        if eventos_filtrados:
            cx = st.columns([1.5, 2, 2.5, 1.5, 1])
            cx[0].markdown("**Código / Fecha**")
            cx[1].markdown("**Evento**")
            cx[2].markdown("**Cliente corporativo**")
            cx[3].markdown("**Inversión total**")
            cx[4].markdown("**Acción**")
            st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            
            for cot in eventos_filtrados:
                cx = st.columns([1.5, 2, 2.5, 1.5, 1])
                cx[0].write(f"**{cot['codigo']}**\n\n{cot['fecha']}")
                cx[1].write(f"{cot['evento']}")
                cx[2].write(f"{cot['cliente']}")
                cx[3].write(f"**${cot['total']:,.2f}**")
                
                if cx[4].button("Abrir", key=f"abrir_{cot['codigo']}", type="secondary"):
                    st.session_state.cotizacion_activa = cot
                    st.session_state.items_cot = cot.get("items", [])
                    st.session_state.nav_menu = "Nueva cotización"
                    st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
        else:
            st.info("No hay registros en esta categoría.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    st.markdown("<h3 style='font-weight: 700; color: #1E293B; margin-bottom: 0px;'>Gestión de cotizaciones</h3>", unsafe_allow_html=True)
    
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
    
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
    with col1: cod_cotizacion = st.text_input("Código de cotización", value=def_cod)
    with col2: nombre_evento = st.text_input("Nombre del evento", value=def_ev, placeholder="Ej. Integración corporativa")
    with col3: cliente_sel = st.selectbox("Cuenta de cliente", lista_nombres_clientes, index=def_cli_idx)
    with col4: fecha_gral = st.date_input("Fecha del evento", datetime.now()) 
    with col5: estado_cot = st.selectbox("Estado comercial", ["Borrador", "Enviada", "Aprobada", "Cancelada"], index=def_est_idx)
    
    if cliente_sel == OPCION_NUEVO:
        st.markdown("<div style='background-color: #F8FAFC; padding: 15px; border-radius: 6px; border: 1px solid #CBD5E1; margin-top: 10px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #0F172A; margin-top: 0; font-size: 15px;'>Apertura de nueva cuenta</h4>", unsafe_allow_html=True)
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
            
        st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
        if st.button("Guardar y aplicar a cotización", type="primary"):
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

    with st.expander("Gestionar servicios e insumos", expanded=True):
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Seleccionar del catálogo", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "catalogo" else "secondary"):
                st.session_state.modo_ingreso = "catalogo"; st.rerun()
        with col_btn2:
            if st.button("Ingreso manual", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "personalizado" else "secondary"):
                st.session_state.modo_ingreso = "personalizado"; st.rerun()
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        if st.session_state.modo_ingreso == "catalogo":
            f1, f2 = st.columns([1, 2])
            with f1: ciudad_filtro = st.selectbox("Filtrar por ciudad", ciudades_lista, index=0)
            with f2: palabra_busqueda = st.text_input("Término de búsqueda (opcional)", placeholder="Ej. transporte, animación...")
            
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
                    desc = r.get("descripcion", "Sin información técnica")
                    opciones_str.append(f"{r['proveedor']} ➔ {r['servicio']} | {iva_str} | {desc}")
                
                seleccion = st.selectbox("Seleccione el proveedor corporativo:", opciones_str)
                item_seleccionado = resultados[opciones_str.index(seleccion)]
                
                ca, cb, cc, cd, ce = st.columns(5)
                with ca: fecha_item = st.date_input("Fecha de ejecución", value=fecha_gral)
                with cb: cant_add = st.number_input("Cantidad", min_value=1, value=1)
                with cc: costo_add = st.number_input("Costo unit. ($)", value=float(item_seleccionado["precio_base"]))
                with cd: iva_add = st.selectbox("IVA", [0.0, 0.15], index=1 if item_seleccionado["iva"] > 0 else 0, format_func=lambda x: f"{int(x * 100)}%")
                with ce: fee_add = st.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f")
                
                st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
                if st.button("Agregar línea a la cotización", type="primary"):
                    st.session_state.items_cot.append({
                        "servicio": item_seleccionado["servicio"], "proveedor": item_seleccionado["proveedor"], 
                        "ciudad": ciudad_filtro, "fecha": str(fecha_item), "cantidad": cant_add, 
                        "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                    })
                    st.rerun()

        elif st.session_state.modo_ingreso == "personalizado":
            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1: nuevo_proveedor = st.text_input("Razón social (Proveedor) *")
            with nc2: nuevo_servicio = st.text_input("Detalle del servicio *")
            with nc3: nueva_ciudad = st.selectbox("Ciudad operativa", ciudades_lista)
            with nc4: nueva_categoria = st.text_input("Categoría de gasto")
            
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: fecha_item = st.date_input("Fecha de ejecución", value=fecha_gral)
            with cb: cant_add = st.number_input("Cantidad", min_value=1, value=1)
            with cc: costo_add = st.number_input("Costo unit. ($)", value=0.00, format="%.2f")
            with cd: iva_add = st.selectbox("IVA", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x * 100)}%")
            with ce: fee_add = st.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f")
            
            guardar_bd = st.checkbox("Registrar proveedor en el directorio corporativo", value=True)
            
            st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
            if st.button("Registrar y agregar línea", type="primary"):
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

    if st.session_state.items_cot:
        st.markdown("<h4 style='color: #0F172A; margin-top: 20px;'>Estructura de costos (Uso interno)</h4>", unsafe_allow_html=True)
        
        hx = st.columns([2.5, 1.4, 0.5, 0.9, 0.6, 0.8, 1.0, 0.4, 0.4, 0.4])
        hx[0].markdown("**Proveedor / Servicio**")
        hx[1].markdown("**Fecha / Zona**")
        hx[2].markdown("**Cant.**")
        hx[3].markdown("**Costo u.**")
        hx[4].markdown("**IVA**")
        hx[5].markdown("**Margen**")
        hx[6].markdown("**Subtotal ($)**")
        st.markdown("<hr style='margin: 2px 0 8px 0; border-top: 2px solid #E2E8F0;'>", unsafe_allow_html=True)
        
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
            
            cx = st.columns([2.5, 1.4, 0.5, 0.9, 0.6, 0.8, 1.0, 0.4, 0.4, 0.4])
            cx[0].write(f"**{item['proveedor']}** \n\n*{item['servicio']}*")
            cx[1].write(f"{item['fecha']} \n\n{item['ciudad']}")
            cx[2].write(f"x{item['cantidad']}")
            cx[3].write(f"${item['costo']:.2f}")
            cx[4].write(f"{int(item['iva_prov']*100)}%")
            cx[5].write(f"{item['fee_pct']:.2f}%")
            cx[6].write(f"**${precio_venta_linea:.2f}**")
            
            if cx[7].button("▲", key=f"up_{idx}", disabled=(idx == 0), use_container_width=True):
                st.session_state.items_cot.insert(idx - 1, st.session_state.items_cot.pop(idx))
                st.rerun()
            if cx[8].button("▼", key=f"down_{idx}", disabled=(idx == len(st.session_state.items_cot) - 1), use_container_width=True):
                st.session_state.items_cot.insert(idx + 1, st.session_state.items_cot.pop(idx))
                st.rerun()
            if cx[9].button("X", key=f"del_{idx}", use_container_width=True):
                st.session_state.items_cot.pop(idx)
                st.rerun()
            st.markdown("<hr style='margin: 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
        # CÁLCULOS TIPO FACTURA PARA EL CLIENTE
        iva_cliente_final = subtotal_comercial * 0.15
        total_cliente_final = subtotal_comercial + iva_cliente_final

        st.markdown("<br>", unsafe_allow_html=True)
        col_met1, col_met2, col_inv = st.columns([1.2, 1.2, 1.6])
        
        with col_met1:
            st.metric("Costos operativos", f"${subtotal_prov:,.2f}")
        with col_met2:
            st.metric("Rentabilidad", f"${total_fee:,.2f}")
        with col_inv:
            st.markdown(f"""
            <div class='invoice-container'>
                <div class='inv-row'><span>Subtotal</span><span>${subtotal_comercial:,.2f}</span></div>
                <div class='inv-row'><span>IVA 15%</span><span>${iva_cliente_final:,.2f}</span></div>
                <div class='inv-total'><span>TOTAL INVERSIÓN</span><span>${total_cliente_final:,.2f}</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn1, btn2 = st.columns(2)
        with btn1:
            st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
            if st.button("Guardar documento actual", type="primary"):
                if c_activa:
                    st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != cod_cotizacion]
                
                if cliente_sel == OPCION_NUEVO:
                    st.error("Registre la cuenta del cliente antes de guardar la cotización.")
                else:
                    st.session_state.cotizaciones_guardadas.append({
                        "codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, 
                        "fecha": str(fecha_gral), "estado": estado_cot, "total": total_cliente_final, "items": st.session_state.items_cot.copy()
                    })
                    st.success("Documento comercial registrado en el historial.")
        with btn2:
            st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
            if st.button("Generar propuesta comercial", type="primary"):
                st.session_state.vista_cliente = True; st.rerun()

    if st.session_state.vista_cliente and st.session_state.items_cot:
        st.markdown("---")
        st.markdown(f"<h3 style='color: #0F172A;'>Propuesta comercial: {nombre_evento}</h3>", unsafe_allow_html=True)
        st.write(f"**Cuenta:** {cliente_sel} | **Referencia:** {cod_cotizacion} | **Fecha de emisión:** {fecha_gral}")
        
        datos_cliente = []
        for item in st.session_state.items_cot:
            costo_linea = item["cantidad"] * item["costo"]
            iva_prov_val = costo_linea * item["iva_prov"]
            costo_con_iva = costo_linea + iva_prov_val
            fee_val = costo_con_iva * (item["fee_pct"] / 100.0)
            precio_venta_linea = costo_con_iva + fee_val
            precio_unitario = precio_venta_linea / item["cantidad"]
            
            datos_cliente.append({
                "Detalle de servicio": item["servicio"], "Lugar de ejecución": item["ciudad"], "Fecha": item["fecha"],
                "Cant.": item["cantidad"], "Valor unitario": f"${precio_unitario:.2f}", "Valor total": f"${precio_venta_linea:.2f}"
            })
        st.table(pd.DataFrame(datos_cliente))
        
        # Resumen financiero en la vista del cliente
        st.markdown(f"""
        <div style='text-align: right; margin-top: 10px;'>
            <p style='font-size: 16px; color: #475569; margin: 0;'>Subtotal: ${subtotal_comercial:,.2f}</p>
            <p style='font-size: 16px; color: #475569; margin: 0;'>IVA 15%: ${iva_cliente_final:,.2f}</p>
            <h3 style='color: #1E3A8A; margin-top: 5px;'>TOTAL: ${total_cliente_final:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)

# --- VISTA 4: DIRECTORIOS (CRM) ---
elif menu == "Directorios":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700;'>Gestión de cuentas (CRM)</h2>", unsafe_allow_html=True)
    
    dir_b1, dir_b2 = st.columns(2)
    with dir_b1:
        if st.button("Directorio de clientes", use_container_width=True, type="primary" if st.session_state.vista_directorio == "clientes" else "secondary"):
            st.session_state.vista_directorio = "clientes"; st.rerun()
    with dir_b2:
        if st.button("Red de proveedores", use_container_width=True, type="primary" if st.session_state.vista_directorio == "proveedores" else "secondary"):
            st.session_state.vista_directorio = "proveedores"; st.rerun()
            
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
    
    if st.session_state.vista_directorio == "clientes":
        df_clientes = pd.DataFrame(st.session_state.clientes_catalogo)
        df_clientes = df_clientes.rename(columns={
            "empresa": "Empresa", "ruc": "RUC", "ciudad": "Ciudad", 
            "direccion": "Dirección", "web": "Sitio web", "contacto": "Contacto", 
            "email": "Correo electrónico", "telefono": "Teléfono", "dias_credito": "Días de crédito"
        })
        st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        
        with st.expander("Apertura de nueva cuenta corporativa"):
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                n_empresa = st.text_input("Razón social / Empresa *")
                n_ruc = st.text_input("Registro Único de Contribuyentes (RUC) *")
                n_ciu = st.selectbox("Ciudad de facturación", ciudades_lista)
            with cc2:
                n_dir = st.text_input("Dirección fiscal")
                n_web = st.text_input("Sitio web corporativo")
                n_contacto = st.text_input("Contacto autorizado")
            with cc3:
                n_correo = st.text_input("Correo electrónico financiero")
                n_tel = st.text_input("Teléfono directo")
                n_dias = st.number_input("Días de crédito asignados", value=30, step=15)
                
            st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
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

    elif st.session_state.vista_directorio == "proveedores":
        df_proveedores = pd.DataFrame(st.session_state.proveedores_catalogo)
        df_proveedores = df_proveedores.rename(columns={
            "servicio": "Servicio", "proveedor": "Proveedor", "categoria": "Categoría",
            "ciudad": "Ciudad", "precio_base": "Costo base ($)", "iva": "IVA",
            "banco": "Banco", "cuenta": "Cuenta", "descripcion": "Descripción"
        })
        df_proveedores["IVA"] = df_proveedores["IVA"].apply(lambda x: f"{int(x*100)}%")
        df_proveedores["Costo base ($)"] = df_proveedores["Costo base ($)"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_proveedores, use_container_width=True, hide_index=True)
        
        with st.expander("Registro de nuevo proveedor"):
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_prov = st.text_input("Razón social / Proveedor *")
                p_serv = st.text_input("Servicio o insumo principal *")
                p_cat = st.text_input("Categoría de gasto")
            with cp2:
                p_ciu = st.selectbox("Sede operativa", ciudades_lista)
                p_costo = st.number_input("Costo referencial estándar ($)", value=0.00)
                p_iva = st.selectbox("IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%")
            with cp3:
                st.markdown("<p style='font-size: 13px; font-weight: 600; margin-bottom: 5px;'>Información bancaria</p>", unsafe_allow_html=True)
                p_banco = st.text_input("Institución financiera")
                p_cta = st.text_input("Tipo y número de cuenta")
                
            p_desc = st.text_area("Condiciones técnicas y observaciones")
            
            st.markdown('<span class="btn-verde" style="display:none;"></span>', unsafe_allow_html=True)
            if st.button("Registrar proveedor en el sistema", type="primary"):
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
