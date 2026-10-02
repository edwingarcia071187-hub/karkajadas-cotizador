import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Karkajadas Group - ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp, .main, header { background-color: #FFFFFF !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* Botones primarios (Azul corporativo) */
    button[kind="primary"] {
        background-color: #1E3A8A !important; 
        color: #FFFFFF !important;
        border-radius: 4px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        border: none !important; 
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover { background-color: #1E40AF !important; transform: translateY(-1px); box-shadow: 0 4px 6px rgba(30, 58, 138, 0.3); }

    /* Botones secundarios (Grises limpios) */
    button[kind="secondary"] {
        background-color: #F8FAFC !important; 
        color: #334155 !important;
        border-radius: 4px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #CBD5E1 !important; 
        box-shadow: none;
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover { background-color: #F1F5F9 !important; color: #0F172A !important; border-color: #94A3B8 !important; }
    
    [data-testid="stExpander"] { background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 6px !important; }
    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important; border-radius: 4px; }
    
    li[data-baseweb="option"], div[role="option"] { background-color: #FFFFFF !important; color: #1E293B !important; transition: all 0.1s ease; }
    li[data-baseweb="option"]:hover, div[role="option"]:hover { background-color: #EFF6FF !important; color: #1D4ED8 !important; font-weight: 600 !important; }
    table tbody tr:hover { background-color: #F1F5F9 !important; }
    
    .total-box { padding: 12px 20px; border-radius: 6px; background-color: #F8FAFC; border-left: 4px solid #1E3A8A; font-size: 28px !important; font-weight: 700; color: #0F172A; line-height: 1.2; border: 1px solid #E2E8F0; }
    .total-label { font-size: 12px; color: #64748B; display: block; font-weight: 600; text-transform: uppercase; margin-bottom: 2px; }
    
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if "nav_menu" not in st.session_state: st.session_state.nav_menu = "Panel principal"
if "modo_ingreso" not in st.session_state: st.session_state.modo_ingreso = "catalogo"
if "vista_directorio" not in st.session_state: st.session_state.vista_directorio = "clientes"
if "filtro_dashboard" not in st.session_state: st.session_state.filtro_dashboard = "Aprobada"
if "items_cot" not in st.session_state: st.session_state.items_cot = []
if "cotizacion_activa" not in st.session_state: st.session_state.cotizacion_activa = None
if "vista_cliente" not in st.session_state: st.session_state.vista_cliente = False
if "cliente_recien_creado" not in st.session_state: st.session_state.cliente_recien_creado = None

# Datos base de prueba (con items reales para que la carga funcione)
if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {
            "codigo": "KG-20261001-001", "evento": "Fiesta fin de año", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 414.00,
            "items": [{"servicio": "Cabina fotográfica", "proveedor": "SuperDuper Photobooth", "ciudad": "Quito", "fecha": "2026-12-15", "cantidad": 1, "costo": 300.0, "iva_prov": 0.0, "fee_pct": 20.0, "subtotal": 360.0}]
        },
        {"codigo": "KG-20261002-002", "evento": "Lanzamiento marca", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-11-10", "estado": "Enviada", "total": 3400.00, "items": []},
        {"codigo": "KG-20261003-003", "evento": "Cena directivos", "cliente": "Hilton Colón Quito", "fecha": "2026-10-20", "estado": "Borrador", "total": 850.00, "items": []},
    ]

ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]

if "clientes_catalogo" not in st.session_state:
    st.session_state.clientes_catalogo = [
        {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
        {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
        {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
    ]

if "proveedores_catalogo" not in st.session_state:
    st.session_state.proveedores_catalogo = [
        {"servicio": "Cabina fotográfica", "proveedor": "SuperDuper Photobooth", "categoria": "Entretenimiento", "ciudad": "Quito", "precio_base": 300.0, "iva": 0.0, "banco": "Pichincha", "cuenta": "Ahorros 2209666553", "descripcion": "Cabina ilimitada por 2 horas."},
        {"servicio": "Carpa 6x6 blanca", "proveedor": "Carpas Pichincha", "categoria": "Estructuras", "ciudad": "Quito", "precio_base": 50.0, "iva": 0.15, "banco": "Produbanco", "cuenta": "Ahorros 987654321", "descripcion": "Incluye montaje."},
    ]

# --- MENÚ LATERAL (ESTRUCTURA ERP) ---
st.sidebar.markdown("<h3 style='color: #0F172A; font-weight: 700;'>Karkajadas Group</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

if st.sidebar.button("Panel principal", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Panel principal"; st.rerun()
if st.sidebar.button("Base de datos y CRM", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.rerun()
if st.sidebar.button("Dashboard financiero", use_container_width=True, type="secondary"): st.warning("Módulo en desarrollo")
if st.sidebar.button("Forecast de ventas", use_container_width=True, type="secondary"): st.warning("Módulo en desarrollo")
if st.sidebar.button("Noticias corporativas", use_container_width=True, type="secondary"): st.info("No hay noticias nuevas hoy.")

st.sidebar.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 12px; color: #64748B; font-weight: 600;'>SOPORTE</p>", unsafe_allow_html=True)
if st.sidebar.button("Preguntas frecuentes", use_container_width=True, type="secondary"): pass
if st.sidebar.button("Manuales operativos", use_container_width=True, type="secondary"): pass

menu = st.session_state.nav_menu

# --- VISTA 1: PANEL PRINCIPAL ---
if menu == "Panel principal":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>Centro de control operativo</h2>", unsafe_allow_html=True)
    
    # ACCESOS RÁPIDOS
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Crear nueva cotización", use_container_width=True, type="primary"): 
            st.session_state.nav_menu = "Nueva cotización"
            st.session_state.cotizacion_activa = None
            st.session_state.items_cot = []
            st.rerun()
    with b2:
        if st.button("Base de clientes", use_container_width=True, type="secondary"): 
            st.session_state.nav_menu = "Directorios"
            st.session_state.vista_directorio = "clientes"
            st.rerun()
    with b3:
        if st.button("Base de proveedores", use_container_width=True, type="secondary"): 
            st.session_state.nav_menu = "Directorios"
            st.session_state.vista_directorio = "proveedores"
            st.rerun()
            
    st.markdown("<hr style='margin: 25px 0 15px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 14px; font-weight: 600;'>RESUMEN FINANCIERO (Clic para filtrar la tabla inferior)</p>", unsafe_allow_html=True)
    
    cots = st.session_state.cotizaciones_guardadas
    tot_aprobadas = sum(c["total"] for c in cots if c["estado"] == "Aprobada")
    tot_enviadas = sum(c["total"] for c in cots if c["estado"] == "Enviada")
    tot_borradores = sum(c["total"] for c in cots if c["estado"] == "Borrador")
    tot_canceladas = sum(c["total"] for c in cots if c["estado"] == "Cancelada")
    
    # MÉTRICAS INTERACTIVAS LIMPIAS
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
    
    # LISTADO INTERACTIVO CON BUSCADOR UNIFICADO
    with st.container():
        st.markdown("<div style='background-color: #F8FAFC; padding: 25px; border-radius: 8px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        col_tit, col_bus = st.columns([2, 1])
        with col_tit:
            st.markdown(f"<h4 style='color: #1E3A8A; margin: 0;'>Directorio de cotizaciones: {st.session_state.filtro_dashboard}</h4>", unsafe_allow_html=True)
        with col_bus:
            busqueda_universal = st.text_input("Buscar código, evento o cliente...", key="b_univ", label_visibility="collapsed")
        
        eventos_filtrados = [cot for cot in cots if cot["estado"] == st.session_state.filtro_dashboard]
        if busqueda_universal:
            term = busqueda_universal.lower()
            eventos_filtrados = [c for c in eventos_filtrados if term in c['codigo'].lower() or term in c['evento'].lower() or term in c['cliente'].lower()]
        
        st.markdown("<hr style='margin: 15px 0 10px 0; border-top: 2px solid #CBD5E1;'>", unsafe_allow_html=True)
        
        if eventos_filtrados:
            # Cabeceras
            cx = st.columns([1.5, 2, 2.5, 1.5, 1])
            cx[0].markdown("**Código / Fecha**")
            cx[1].markdown("**Evento**")
            cx[2].markdown("**Cliente**")
            cx[3].markdown("**Monto Total**")
            cx[4].markdown("**Acción**")
            st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            
            for cot in eventos_filtrados:
                cx = st.columns([1.5, 2, 2.5, 1.5, 1])
                cx[0].write(f"**{cot['codigo']}**\n\n{cot['fecha']}")
                cx[1].write(f"{cot['evento']}")
                cx[2].write(f"{cot['cliente']}")
                cx[3].write(f"**${cot['total']:,.2f}**")
                
                # Botón Abrir (ahora carga correctamente los ítems guardados)
                if cx[4].button("Abrir", key=f"abrir_{cot['codigo']}", type="secondary"):
                    st.session_state.cotizacion_activa = cot
                    # Cargar los ítems guardados, si no hay, lista vacía
                    st.session_state.items_cot = cot.get("items", [])
                    st.session_state.nav_menu = "Nueva cotización"
                    st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
        else:
            st.info("No hay resultados en esta categoría.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    st.markdown("<h3 style='font-weight: 700; color: #1E293B;'>Generador de cotizaciones</h3>", unsafe_allow_html=True)
    
    c_activa = st.session_state.cotizacion_activa
    lista_nombres_clientes = [c["empresa"] for c in st.session_state.clientes_catalogo]
    OPCION_NUEVO = "+ Crear nuevo cliente..."
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
    with col3: cliente_sel = st.selectbox("Cliente", lista_nombres_clientes, index=def_cli_idx)
    with col4: fecha_gral = st.date_input("Fecha del evento", datetime.now()) 
    with col5: estado_cot = st.selectbox("Estado actual", ["Borrador", "Enviada", "Aprobada", "Cancelada"], index=def_est_idx)
    
    if cliente_sel == OPCION_NUEVO:
        st.markdown("<div style='background-color: #F8FAFC; padding: 20px; border-radius: 6px; border: 1px solid #CBD5E1; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #0F172A; margin-top: 0; font-size: 16px;'>Registrar nuevo cliente en CRM</h4>", unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            i_emp = st.text_input("Razón social / Empresa *")
            i_ruc = st.text_input("RUC *")
            i_ciu = st.selectbox("Ciudad principal", ciudades_lista)
        with cc2:
            i_dir = st.text_input("Dirección matriz")
            i_web = st.text_input("Página web")
            i_cont = st.text_input("Persona contacto")
        with cc3:
            i_mail = st.text_input("Correo electrónico")
            i_tel = st.text_input("Teléfono")
            i_dias = st.number_input("Días de crédito", value=30, step=15)
            
        if st.button("Guardar y seleccionar cliente", type="primary"):
            if i_emp.strip() != "" and i_ruc.strip() != "":
                st.session_state.clientes_catalogo.append({
                    "empresa": i_emp, "ruc": i_ruc, "ciudad": i_ciu, "direccion": i_dir,
                    "web": i_web, "contacto": i_cont, "email": i_mail, "telefono": i_tel, "dias_credito": i_dias
                })
                st.session_state.cliente_recien_creado = i_emp
                st.rerun()
            else:
                st.error("Razón social y RUC son obligatorios.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    
    with st.expander("Añadir proveedores y servicios al detalle", expanded=True):
        st.markdown("<p style='font-size: 13px; font-weight: 600; color: #475569;'>SELECCIONE EL MÉTODO DE INGRESO:</p>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Buscar en catálogo existente", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "catalogo" else "secondary"):
                st.session_state.modo_ingreso = "catalogo"; st.rerun()
        with col_btn2:
            if st.button("Crear servicio personalizado", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "personalizado" else "secondary"):
                st.session_state.modo_ingreso = "personalizado"; st.rerun()
        
        st.markdown("<hr style='margin: 15px 0 10px 0;'>", unsafe_allow_html=True)
        
        if st.session_state.modo_ingreso == "catalogo":
            f1, f2 = st.columns([1, 2])
            with f1: ciudad_filtro = st.selectbox("Ciudad del servicio", ciudades_lista, index=0)
            with f2: palabra_busqueda = st.text_input("Filtrar por palabra clave (opcional)", placeholder="Ej. carpa, transporte...")
            
            resultados = []
            for p in st.session_state.proveedores_catalogo:
                if p["ciudad"] == ciudad_filtro:
                    if palabra_busqueda == "" or \
                       palabra_busqueda.lower() in p["servicio"].lower() or \
                       palabra_busqueda.lower() in p["proveedor"].lower():
                        resultados.append(p)
            
            if not resultados:
                st.warning("No se encontraron coincidencias en el catálogo.")
            else:
                opciones_str = []
                for r in resultados:
                    iva_str = f"IVA {int(r['iva']*100)}%" if r['iva'] > 0 else "IVA 0%"
                    desc = r.get("descripcion", "Sin descripción")
                    opciones_str.append(f"{r['proveedor']} ➔ {r['servicio']} | {iva_str} | {desc}")
                
                seleccion = st.selectbox("Seleccione el proveedor:", opciones_str)
                item_seleccionado = resultados[opciones_str.index(seleccion)]
                
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                ca, cb, cc, cd, ce = st.columns(5)
                with ca: fecha_item = st.date_input("Fecha específica", value=fecha_gral)
                with cb: cant_add = st.number_input("Cantidad", min_value=1, value=1)
                with cc: costo_add = st.number_input("Costo unit. ($)", value=float(item_seleccionado["precio_base"]))
                with cd: iva_add = st.selectbox("Aplica IVA", [0.0, 0.15], index=1 if item_seleccionado["iva"] > 0 else 0, format_func=lambda x: f"{int(x * 100)}%")
                with ce: fee_add = st.number_input("Margen FEE (%)", value=20.00, step=5.00, format="%.2f")
                    
                if st.button("Agregar ítem a la cotización", type="primary"):
                    st.session_state.items_cot.append({
                        "servicio": item_seleccionado["servicio"], "proveedor": item_seleccionado["proveedor"], 
                        "ciudad": ciudad_filtro, "fecha": str(fecha_item), "cantidad": cant_add, 
                        "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                    })
                    st.rerun()

        elif st.session_state.modo_ingreso == "personalizado":
            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1: nuevo_proveedor = st.text_input("Proveedor *")
            with nc2: nuevo_servicio = st.text_input("Servicio *")
            with nc3: nueva_ciudad = st.selectbox("Ciudad", ciudades_lista)
            with nc4: nueva_categoria = st.text_input("Categoría")
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: fecha_item = st.date_input("Fecha específica", value=fecha_gral)
            with cb: cant_add = st.number_input("Cantidad", min_value=1, value=1)
            with cc: costo_add = st.number_input("Costo unit. ($)", value=0.00, format="%.2f")
            with cd: iva_add = st.selectbox("Aplica IVA", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x * 100)}%")
            with ce: fee_add = st.number_input("Margen FEE (%)", value=20.00, step=5.00, format="%.2f")
            
            guardar_bd = st.checkbox("Guardar en catálogo maestro para el futuro", value=True)
            if st.button("Crear y agregar ítem", type="primary"):
                if nuevo_proveedor.strip() == "" or nuevo_servicio.strip() == "":
                    st.error("El nombre del proveedor y el servicio son obligatorios.")
                else:
                    st.session_state.items_cot.append({
                        "servicio": nuevo_servicio, "proveedor": nuevo_proveedor, 
                        "ciudad": nueva_ciudad, "fecha": str(fecha_item), "cantidad": cant_add, 
                        "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                    })
                    if guardar_bd:
                        st.session_state.proveedores_catalogo.append({
                            "servicio": nuevo_servicio, "proveedor": nuevo_proveedor, "categoria": nueva_categoria if nueva_categoria else "Otros",
                            "ciudad": nueva_ciudad, "precio_base": costo_add, "iva": iva_add, "banco": "Pendiente", "cuenta": "Pendiente", "descripcion": "Ingreso manual rápido"
                        })
                    st.rerun()

    if st.session_state.items_cot:
        st.markdown("<h4 style='color: #0F172A; margin-top: 30px;'>Detalle de costos y márgenes (Uso interno)</h4>", unsafe_allow_html=True)
        hx = st.columns([2.5, 1.5, 0.5, 1, 1, 1, 1, 0.5])
        hx[0].markdown("**Proveedor / Servicio**")
        hx[1].markdown("**Fecha / Ciudad**")
        hx[2].markdown("**Cant.**")
        hx[3].markdown("**Costo U.**")
        hx[4].markdown("**IVA**")
        hx[5].markdown("**FEE**")
        hx[6].markdown("**Subtotal**")
        hx[7].markdown("**Del**")
        st.markdown("<hr style='margin: 4px 0 10px 0; border-top: 2px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        subtotal_prov = 0; total_fee = 0; total_general = 0
        for idx, item in enumerate(st.session_state.items_cot):
            sub_costo = item["cantidad"] * item["costo"]
            sub_con_iva = sub_costo + (sub_costo * item["iva_prov"])
            fee_val = sub_con_iva * (item["fee_pct"] / 100.0)
            total_item = sub_con_iva + fee_val
            
            subtotal_prov += sub_con_iva; total_fee += fee_val; total_general += total_item
            
            cx = st.columns([2.5, 1.5, 0.5, 1, 1, 1, 1, 0.5])
            cx[0].write(f"**{item['proveedor']}** \n\n*{item['servicio']}*")
            cx[1].write(f"{item['fecha']} \n\n{item['ciudad']}")
            cx[2].write(f"x{item['cantidad']}")
            cx[3].write(f"${item['costo']:.2f}")
            cx[4].write(f"{int(item['iva_prov']*100)}%")
            cx[5].write(f"{item['fee_pct']:.2f}%")
            cx[6].write(f"**${total_item:.2f}**")
            if cx[7].button("X", key=f"del_{idx}", type="secondary"):
                st.session_state.items_cot.pop(idx); st.rerun()
            st.markdown("<hr style='margin: 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        t1.metric("Costos directos", f"${subtotal_prov:.2f}")
        t2.metric("Margen operativo", f"${total_fee:.2f}")
        t3.markdown(f"<div class='total-box'><span class='total-label'>Precio de venta al cliente</span>${total_general:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("Guardar cotización en el sistema", type="secondary"):
                if c_activa:
                    st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != cod_cotizacion]
                
                if cliente_sel == OPCION_NUEVO:
                    st.error("Guarde el cliente nuevo primero dando clic en 'Guardar y seleccionar cliente'.")
                else:
                    st.session_state.cotizaciones_guardadas.append({
                        "codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, 
                        "fecha": str(fecha_gral), "estado": estado_cot, "total": total_general, "items": st.session_state.items_cot.copy()
                    })
                    st.success("Cotización registrada exitosamente.")
        with btn2:
            if st.button("Generar propuesta comercial", type="primary"):
                st.session_state.vista_cliente = True; st.rerun()

    if st.session_state.vista_cliente and st.session_state.items_cot:
        st.markdown("---")
        st.markdown(f"<h3 style='color: #0F172A;'>Propuesta comercial: {nombre_evento}</h3>", unsafe_allow_html=True)
        st.write(f"**Cliente:** {cliente_sel} | **Código:** {cod_cotizacion} | **Fecha:** {fecha_gral}")
        
        datos_cliente = []
        for item in st.session_state.items_cot:
            costo_real = item["costo"] * (1 + item["iva_prov"])
            fee_valor = costo_real * (item["fee_pct"] / 100.0)
            total_linea = (costo_real + fee_valor) * item["cantidad"]
            precio_unitario_cliente = total_linea / item["cantidad"]
            datos_cliente.append({
                "Servicio": item["servicio"], "Ciudad": item["ciudad"], "Fecha": item["fecha"],
                "Cant.": item["cantidad"], "V. unitario": f"${precio_unitario_cliente:.2f}", "V. total": f"${total_linea:.2f}"
            })
        st.table(pd.DataFrame(datos_cliente))
        st.markdown(f"<h3 style='text-align: right; color: #1E3A8A;'>INVERSIÓN TOTAL: ${total_general:.2f}</h3>", unsafe_allow_html=True)

# --- VISTA 4: DIRECTORIOS ---
elif menu == "Directorios":
    st.markdown("<h2 style='color: #0F172A; font-weight: 700;'>Gestión de bases de datos (CRM)</h2>", unsafe_allow_html=True)
    
    dir_b1, dir_b2 = st.columns(2)
    with dir_b1:
        if st.button("Directorio de clientes corporativos", use_container_width=True, type="primary" if st.session_state.vista_directorio == "clientes" else "secondary"):
            st.session_state.vista_directorio = "clientes"; st.rerun()
    with dir_b2:
        if st.button("Catálogo de proveedores y servicios", use_container_width=True, type="primary" if st.session_state.vista_directorio == "proveedores" else "secondary"):
            st.session_state.vista_directorio = "proveedores"; st.rerun()
            
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
    
    if st.session_state.vista_directorio == "clientes":
        st.dataframe(pd.DataFrame(st.session_state.clientes_catalogo), use_container_width=True)
        
        with st.expander("Añadir registro manual de cliente"):
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                n_empresa = st.text_input("Razón social / Empresa *")
                n_ruc = st.text_input("RUC *")
                n_ciu = st.selectbox("Ciudad principal", ciudades_lista)
            with cc2:
                n_dir = st.text_input("Dirección matriz")
                n_web = st.text_input("Página web")
                n_contacto = st.text_input("Persona de contacto")
            with cc3:
                n_correo = st.text_input("Correo electrónico")
                n_tel = st.text_input("Teléfono")
                n_dias = st.number_input("Días de crédito permitidos", value=30, step=15)
                
            if st.button("Guardar en base de datos", type="primary"):
                if n_empresa and n_ruc:
                    st.session_state.clientes_catalogo.append({
                        "empresa": n_empresa, "ruc": n_ruc, "ciudad": n_ciu, "direccion": n_dir,
                        "web": n_web, "contacto": n_contacto, "email": n_correo, "telefono": n_tel, "dias_credito": n_dias
                    })
                    st.success("Registro ingresado correctamente.")
                    st.rerun()
                else:
                    st.error("Empresa y RUC son campos obligatorios.")

    elif st.session_state.vista_directorio == "proveedores":
        st.dataframe(pd.DataFrame(st.session_state.proveedores_catalogo), use_container_width=True)
        
        with st.expander("Añadir registro manual de proveedor"):
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_prov = st.text_input("Razón social / Proveedor *")
                p_serv = st.text_input("Servicio principal *")
                p_cat = st.text_input("Categoría")
            with cp2:
                p_ciu = st.selectbox("Ciudad base", ciudades_lista)
                p_costo = st.number_input("Costo estándar referencial ($)", value=0.00)
                p_iva = st.selectbox("Graba IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%")
            with cp3:
                st.markdown("<p style='font-size: 13px; font-weight: 600; margin-bottom: 5px;'>Datos financieros (Para pagos)</p>", unsafe_allow_html=True)
                p_banco = st.text_input("Institución financiera")
                p_cta = st.text_input("Tipo y número de cuenta")
                
            p_desc = st.text_area("Observaciones o descripción técnica")
            
            if st.button("Guardar en base de datos", type="primary"):
                if p_prov and p_serv:
                    st.session_state.proveedores_catalogo.append({
                        "servicio": p_serv, "proveedor": p_prov, "categoria": p_cat,
                        "ciudad": p_ciu, "precio_base": p_costo, "iva": p_iva,
                        "banco": p_banco, "cuenta": p_cta, "descripcion": p_desc
                    })
                    st.success("Registro ingresado correctamente.")
                    st.rerun()
                else:
                    st.error("Proveedor y Servicio son campos obligatorios.")
