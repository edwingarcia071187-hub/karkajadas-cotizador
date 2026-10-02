import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Karkajadas Group - ERP",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp, .main, header { background-color: #FFFFFF !important; color: #1E293B !important; }
    
    button[kind="primary"] {
        background-color: #1E3A8A !important; 
        color: #FFFFFF !important;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 15px;
        border: none !important; 
        box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.2);
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover { background-color: #1E40AF !important; transform: translateY(-2px); box-shadow: 0 6px 8px -1px rgba(30, 58, 138, 0.3); }

    button[kind="secondary"] {
        background-color: #F8FAFC !important; 
        color: #475569 !important;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 15px;
        border: 1px solid #CBD5E1 !important; 
        box-shadow: none;
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover { background-color: #E2E8F0 !important; color: #1E293B !important; border-color: #94A3B8 !important; transform: translateY(-1px); }
    
    [data-testid="stExpander"] { background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] > div, input, textarea { background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important; }
    
    li[data-baseweb="option"], div[role="option"] { background-color: #FFFFFF !important; color: #1E293B !important; transition: all 0.2s ease; }
    li[data-baseweb="option"]:hover, div[role="option"]:hover { background-color: #EFF6FF !important; color: #1D4ED8 !important; font-weight: bold !important; }
    table tbody tr:hover { background-color: #EFF6FF !important; }
    
    .total-box { padding: 10px 20px; border-radius: 8px; background-color: #EFF6FF; border-left: 6px solid #1D4ED8; font-size: 36px !important; font-weight: 800; color: #1E3A8A; line-height: 1.2; border: 1px solid #BFDBFE; }
    .total-label { font-size: 14px; color: #3B82F6; display: block; font-weight: 600; text-transform: uppercase; margin-bottom: -5px; }
    
    /* Buscadores de tabla más sutiles */
    .buscador-tabla input { background-color: #F8FAFC !important; font-size: 13px !important; }
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

if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {"codigo": "KG-20261001-001", "evento": "Fiesta fin de año", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 1250.00, "items": []},
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

# --- MENÚ LATERAL ---
st.sidebar.markdown("### Karkajadas Group")
if st.sidebar.button("🏠 Panel principal", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Panel principal"; st.rerun()
if st.sidebar.button("✨ Nueva cotización", use_container_width=True, type="secondary"): 
    st.session_state.nav_menu = "Nueva cotización"; st.session_state.cotizacion_activa = None; st.session_state.items_cot = []; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("👥 Base de datos y CRM", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.rerun()

menu = st.session_state.nav_menu

# --- VISTA 1: PANEL PRINCIPAL ---
if menu == "Panel principal":
    st.markdown("<h2 style='color: #0F172A; font-weight: 800;'>Karkajadas Group - Centro de control</h2>", unsafe_allow_html=True)
    
    # 1. ACCESOS RÁPIDOS EN LA PARTE SUPERIOR
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("➕ Crear nueva cotización", use_container_width=True, type="primary"): 
            st.session_state.nav_menu = "Nueva cotización"; st.session_state.cotizacion_activa = None; st.session_state.items_cot = []; st.rerun()
    with b2:
        if st.button("👥 Base de clientes", use_container_width=True, type="secondary"): 
            st.session_state.nav_menu = "Directorios"; st.session_state.vista_directorio = "clientes"; st.rerun()
    with b3:
        if st.button("🏭 Base de proveedores", use_container_width=True, type="secondary"): 
            st.session_state.nav_menu = "Directorios"; st.session_state.vista_directorio = "proveedores"; st.rerun()
            
    st.markdown("<hr style='margin: 15px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 14px; margin-top: -10px; font-weight: 600;'>RESUMEN FINANCIERO (Haz clic para filtrar detalles)</p>", unsafe_allow_html=True)
    
    cots = st.session_state.cotizaciones_guardadas
    tot_aprobadas = sum(c["total"] for c in cots if c["estado"] == "Aprobada")
    tot_enviadas = sum(c["total"] for c in cots if c["estado"] == "Enviada")
    tot_borradores = sum(c["total"] for c in cots if c["estado"] == "Borrador")
    tot_canceladas = sum(c["total"] for c in cots if c["estado"] == "Cancelada")
    
    # 2. MÉTRICAS INTERACTIVAS
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if st.button(f"✅ Aprobadas\n\n${tot_aprobadas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Aprobada" else "secondary"):
            st.session_state.filtro_dashboard = "Aprobada"; st.rerun()
    with m2:
        if st.button(f"⏳ Enviadas\n\n${tot_enviadas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Enviada" else "secondary"):
            st.session_state.filtro_dashboard = "Enviada"; st.rerun()
    with m3:
        if st.button(f"📝 Borradores\n\n${tot_borradores:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Borrador" else "secondary"):
            st.session_state.filtro_dashboard = "Borrador"; st.rerun()
    with m4:
        if st.button(f"❌ Canceladas\n\n${tot_canceladas:,.2f}", use_container_width=True, type="primary" if st.session_state.filtro_dashboard == "Cancelada" else "secondary"):
            st.session_state.filtro_dashboard = "Cancelada"; st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. LISTADO INTERACTIVO CON BUSCADORES POR COLUMNA
    with st.container():
        st.markdown(f"<div style='background-color: #F8FAFC; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color: #1E3A8A; margin-top: 0;'>📋 Directorio de cotizaciones: {st.session_state.filtro_dashboard}s</h4>", unsafe_allow_html=True)
        
        # Fila de buscadores
        sf1, sf2, sf3, sf4, sf5 = st.columns([1.5, 2, 2.5, 1.5, 1])
        st.markdown("<div class='buscador-tabla'>", unsafe_allow_html=True)
        b_cod = sf1.text_input("🔍 Buscar código", key="b_cod")
        b_eve = sf2.text_input("🔍 Buscar evento", key="b_eve")
        b_cli = sf3.text_input("🔍 Buscar cliente", key="b_cli")
        b_fec = sf4.text_input("🔍 Buscar fecha", key="b_fec")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Filtro lógico
        eventos_filtrados = [cot for cot in cots if cot["estado"] == st.session_state.filtro_dashboard]
        if b_cod: eventos_filtrados = [c for c in eventos_filtrados if b_cod.lower() in c['codigo'].lower()]
        if b_eve: eventos_filtrados = [c for c in eventos_filtrados if b_eve.lower() in c['evento'].lower()]
        if b_cli: eventos_filtrados = [c for c in eventos_filtrados if b_cli.lower() in c['cliente'].lower()]
        if b_fec: eventos_filtrados = [c for c in eventos_filtrados if b_fec.lower() in c['fecha'].lower()]
        
        st.markdown("<hr style='margin: 10px 0; border-top: 2px solid #CBD5E1;'>", unsafe_allow_html=True)
        
        if eventos_filtrados:
            for cot in eventos_filtrados:
                cx = st.columns([1.5, 2, 2.5, 1.5, 1])
                cx[0].write(f"**{cot['codigo']}**")
                cx[1].write(f"{cot['evento']}")
                cx[2].write(f"{cot['cliente']}")
                cx[3].write(f"📅 {cot['fecha']}\n\n**${cot['total']:,.2f}**")
                if cx[4].button("Abrir 📂", key=f"abrir_{cot['codigo']}", type="secondary"):
                    st.session_state.cotizacion_activa = cot
                    st.session_state.items_cot = cot.get("items", [])
                    st.session_state.nav_menu = "Nueva cotización"
                    st.rerun()
                st.markdown("<hr style='margin: 4px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        else:
            st.info("No hay resultados que coincidan con la búsqueda.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    st.markdown("<h3>Generador y editor de cotizaciones</h3>", unsafe_allow_html=True)
    
    c_activa = st.session_state.cotizacion_activa
    lista_nombres_clientes = [c["empresa"] for c in st.session_state.clientes_catalogo]
    
    # Añadimos la opción de crear nuevo al final de la lista
    OPCION_NUEVO = "+ Crear nuevo cliente..."
    lista_nombres_clientes.append(OPCION_NUEVO)
    
    def_cod = c_activa["codigo"] if c_activa else f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    def_ev = c_activa["evento"] if c_activa else ""
    
    # Lógica para autoseleccionar el cliente recién creado
    if st.session_state.cliente_recien_creado:
        def_cli_idx = lista_nombres_clientes.index(st.session_state.cliente_recien_creado)
        st.session_state.cliente_recien_creado = None # Limpiar estado
    else:
        def_cli_idx = lista_nombres_clientes.index(c_activa["cliente"]) if c_activa and c_activa["cliente"] in lista_nombres_clientes else 0
        
    def_est_idx = ["Borrador", "Enviada", "Aprobada", "Cancelada"].index(c_activa["estado"]) if c_activa else 0
    
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
    with col1: cod_cotizacion = st.text_input("Código de cotización", value=def_cod)
    with col2: nombre_evento = st.text_input("Nombre del evento", value=def_ev, placeholder="Ej. Fiesta de integración")
    with col3: cliente_sel = st.selectbox("Cliente", lista_nombres_clientes, index=def_cli_idx)
    with col4: fecha_gral = st.date_input("Fecha general", datetime.now()) 
    with col5: estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"], index=def_est_idx)
    
    # 4. FORMULARIO EN LÍNEA: Aparece SOLO si seleccionas "+ Crear nuevo cliente..."
    if cliente_sel == OPCION_NUEVO:
        st.markdown("<div style='background-color: #F8FAFC; padding: 20px; border-radius: 8px; border: 2px dashed #3B82F6; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1E3A8A; margin-top: 0;'>✨ Registrar nuevo cliente en el sistema</h4>", unsafe_allow_html=True)
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
            
        if st.button("💾 Guardar y autoseleccionar", type="primary"):
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
    
    with st.expander("🔍 Añadir proveedores y servicios", expanded=True):
        st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Seleccione el método de ingreso:</p>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Buscar en catálogo existente", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "catalogo" else "secondary"):
                st.session_state.modo_ingreso = "catalogo"; st.rerun()
        with col_btn2:
            if st.button("✨ Crear servicio personalizado (Rápido)", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "personalizado" else "secondary"):
                st.session_state.modo_ingreso = "personalizado"; st.rerun()
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        if st.session_state.modo_ingreso == "catalogo":
            f1, f2 = st.columns([1, 2])
            with f1: ciudad_filtro = st.selectbox("Ciudad del servicio", ciudades_lista, index=0)
            with f2: palabra_busqueda = st.text_input("Palabra clave (opcional)", placeholder="Ej. carpa, animador...")
            
            resultados = []
            for p in st.session_state.proveedores_catalogo:
                if p["ciudad"] == ciudad_filtro:
                    if palabra_busqueda == "" or \
                       palabra_busqueda.lower() in p["servicio"].lower() or \
                       palabra_busqueda.lower() in p["proveedor"].lower():
                        resultados.append(p)
            
            if not resultados:
                st.warning(f"No se encontraron proveedores para '{palabra_busqueda}' en {ciudad_filtro}.")
            else:
                opciones_str = []
                for r in resultados:
                    iva_str = f"IVA {int(r['iva']*100)}%" if r['iva'] > 0 else "IVA 0%"
                    desc = r.get("descripcion", "Sin descripción")
                    opciones_str.append(f"{r['proveedor']} ➔ {r['servicio']} | {iva_str} | 📝 {desc}")
                
                seleccion = st.selectbox("Despliega para ver las opciones y elegir:", opciones_str)
                item_seleccionado = resultados[opciones_str.index(seleccion)]
                
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                ca, cb, cc, cd, ce = st.columns(5)
                with ca: fecha_item = st.date_input("Fecha específica", value=fecha_gral)
                with cb: cant_add = st.number_input("Cantidad a contratar", min_value=1, value=1)
                with cc: costo_add = st.number_input("Costo unit. negociado ($)", value=float(item_seleccionado["precio_base"]))
                with cd: iva_add = st.selectbox("Aplica IVA prov.", [0.0, 0.15], index=1 if item_seleccionado["iva"] > 0 else 0, format_func=lambda x: f"{int(x * 100)}%")
                with ce: fee_add = st.number_input("Margen / FEE (%)", value=20.00, step=5.00, format="%.2f")
                    
                if st.button("➕ Agregar este ítem a la cotización", type="primary"):
                    st.session_state.items_cot.append({
                        "servicio": item_seleccionado["servicio"], "proveedor": item_seleccionado["proveedor"], 
                        "ciudad": ciudad_filtro, "fecha": str(fecha_item), "cantidad": cant_add, 
                        "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                    })
                    st.rerun()

        elif st.session_state.modo_ingreso == "personalizado":
            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1: nuevo_proveedor = st.text_input("Nombre del proveedor *")
            with nc2: nuevo_servicio = st.text_input("Servicio ofrecido *")
            with nc3: nueva_ciudad = st.selectbox("Ciudad del proveedor", ciudades_lista)
            with nc4: nueva_categoria = st.text_input("Categoría (ej. alimentos)")
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: fecha_item = st.date_input("Fecha específica", value=fecha_gral)
            with cb: cant_add = st.number_input("Cantidad a contratar", min_value=1, value=1)
            with cc: costo_add = st.number_input("Costo unit. negociado ($)", value=0.00, format="%.2f")
            with cd: iva_add = st.selectbox("Aplica IVA prov.", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x * 100)}%")
            with ce: fee_add = st.number_input("Margen / FEE (%)", value=20.00, step=5.00, format="%.2f")
            
            guardar_bd = st.checkbox("💾 Guardar en catálogo maestro", value=True)
            if st.button("➕ Crear y agregar a la cotización", type="primary"):
                if nuevo_proveedor.strip() == "" or nuevo_servicio.strip() == "":
                    st.error("⚠️ El nombre del proveedor y el servicio son obligatorios.")
                else:
                    st.session_state.items_cot.append({
                        "servicio": nuevo_servicio, "proveedor": nuevo_proveedor, 
                        "ciudad": nueva_ciudad, "fecha": str(fecha_item), "cantidad": cant_add, 
                        "costo": costo_add, "iva_prov": iva_add, "fee_pct": fee_add
                    })
                    if guardar_bd:
                        st.session_state.proveedores_catalogo.append({
                            "servicio": nuevo_servicio, "proveedor": nuevo_proveedor, "categoria": nueva_categoria if nueva_categoria else "Otros",
                            "ciudad": nueva_ciudad, "precio_base": costo_add, "iva": iva_add, "banco": "Pendiente", "cuenta": "Pendiente", "descripcion": "Agregado rápidamente"
                        })
                    st.rerun()

    if st.session_state.items_cot:
        st.markdown("#### Ítems actuales en la cotización (vista interna)")
        hx = st.columns([2.5, 1.5, 0.5, 1, 1, 1, 1, 0.5])
        hx[0].markdown("**Proveedor / servicio**")
        hx[1].markdown("**Fecha / ciudad**")
        hx[2].markdown("**Cant.**")
        hx[3].markdown("**Costo u.**")
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
        t1.metric("Costo base proveedores", f"${subtotal_prov:.2f}")
        t2.metric("Ganancia neta (FEE)", f"${total_fee:.2f}")
        t3.markdown(f"<div class='total-box'><span class='total-label'>Total cliente</span>${total_general:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("💾 Guardar / Actualizar cotización", type="secondary"):
                if c_activa:
                    st.session_state.cotizaciones_guardadas = [c for c in st.session_state.cotizaciones_guardadas if c["codigo"] != cod_cotizacion]
                
                # Si guardas pero no tenías cliente válido (ej. estabas creando), no permitas crasheos
                if cliente_sel == OPCION_NUEVO:
                    st.error("Por favor guarda el cliente nuevo primero dando clic en 'Guardar y autoseleccionar'.")
                else:
                    st.session_state.cotizaciones_guardadas.append({
                        "codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, 
                        "fecha": str(fecha_gral), "estado": estado_cot, "total": total_general, "items": st.session_state.items_cot.copy()
                    })
                    st.success("¡Cotización guardada exitosamente en el sistema!")
        with btn2:
            if st.button("📄 Generar vista cliente (limpia)", type="primary"):
                st.session_state.vista_cliente = True; st.rerun()

    if st.session_state.vista_cliente and st.session_state.items_cot:
        st.markdown("---")
        st.markdown(f"### 📄 Cotización comercial: {nombre_evento}")
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
        st.markdown(f"<h3 style='text-align: right;'>TOTAL: ${total_general:.2f}</h3>", unsafe_allow_html=True)

# --- VISTA 4: DIRECTORIOS (CRM COMPLETO) ---
elif menu == "Directorios":
    st.markdown("<h3>Módulo CRM: Clientes y proveedores</h3>", unsafe_allow_html=True)
    
    dir_b1, dir_b2 = st.columns(2)
    with dir_b1:
        if st.button("👥 Base de clientes", use_container_width=True, type="primary" if st.session_state.vista_directorio == "clientes" else "secondary"):
            st.session_state.vista_directorio = "clientes"; st.rerun()
    with dir_b2:
        if st.button("🏭 Base de proveedores", use_container_width=True, type="primary" if st.session_state.vista_directorio == "proveedores" else "secondary"):
            st.session_state.vista_directorio = "proveedores"; st.rerun()
            
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    if st.session_state.vista_directorio == "clientes":
        st.markdown("#### Directorio corporativo de clientes")
        st.dataframe(pd.DataFrame(st.session_state.clientes_catalogo), use_container_width=True)
        
        with st.expander("➕ Añadir nuevo cliente corporativo"):
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
                
            if st.button("Guardar cliente en el CRM", type="primary"):
                if n_empresa and n_ruc:
                    st.session_state.clientes_catalogo.append({
                        "empresa": n_empresa, "ruc": n_ruc, "ciudad": n_ciu, "direccion": n_dir,
                        "web": n_web, "contacto": n_contacto, "email": n_correo, "telefono": n_tel, "dias_credito": n_dias
                    })
                    st.success("¡Cliente agregado al catálogo!")
                    st.rerun()
                else:
                    st.error("⚠️ La empresa y el RUC son obligatorios.")

    elif st.session_state.vista_directorio == "proveedores":
        st.markdown("#### Catálogo maestro de proveedores y servicios")
        st.dataframe(pd.DataFrame(st.session_state.proveedores_catalogo), use_container_width=True)
        
        with st.expander("➕ Añadir nuevo proveedor al catálogo"):
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                p_prov = st.text_input("Nombre del proveedor o empresa *")
                p_serv = st.text_input("Servicio estrella que ofrece *")
                p_cat = st.text_input("Categoría")
            with cp2:
                p_ciu = st.selectbox("Ciudad base", ciudades_lista)
                p_costo = st.number_input("Costo base estándar ($)", value=0.00)
                p_iva = st.selectbox("Graba IVA", [0.0, 0.15], format_func=lambda x: f"{int(x*100)}%")
            with cp3:
                st.markdown("**Datos bancarios (Módulo de pagos)**")
                p_banco = st.text_input("Banco")
                p_cta = st.text_input("Tipo y N° de cuenta")
                
            p_desc = st.text_area("Descripción y detalles del servicio")
            
            if st.button("Guardar proveedor en catálogo", type="primary"):
                if p_prov and p_serv:
                    st.session_state.proveedores_catalogo.append({
                        "servicio": p_serv, "proveedor": p_prov, "categoria": p_cat,
                        "ciudad": p_ciu, "precio_base": p_costo, "iva": p_iva,
                        "banco": p_banco, "cuenta": p_cta, "descripcion": p_desc
                    })
                    st.success("¡Proveedor agregado al catálogo maestro!")
                    st.rerun()
                else:
                    st.error("⚠️ El proveedor y el servicio son obligatorios.")
