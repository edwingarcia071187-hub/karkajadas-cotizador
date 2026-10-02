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

# --- ESTILOS CSS: AZUL CORPORATIVO Y ELEGANCIA ---
st.markdown("""
    <style>
    .stApp, .main, header { background-color: #FFFFFF !important; color: #1E293B !important; }
    
    .stButton>button {
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
    .stButton>button:hover { 
        background-color: #1E40AF !important; 
        color: #FFFFFF !important; 
        transform: translateY(-2px); 
        box-shadow: 0 6px 8px -1px rgba(30, 58, 138, 0.3);
    }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px 20px;
        border-left: 5px solid #3B82F6; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        background-color: #F0F9FF !important; 
        border-color: #BAE6FD !important;
    }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; color: #0F172A !important; }
    
    [data-testid="stExpander"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] > div, input {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* HOVER ATRACTIVO EN LISTAS Y RADIOS */
    li[data-baseweb="option"], div[role="option"], label[data-baseweb="radio"] {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        transition: all 0.2s ease;
    }
    li[data-baseweb="option"]:hover, div[role="option"]:hover, label[data-baseweb="radio"]:hover {
        background-color: #EFF6FF !important; 
        color: #1D4ED8 !important; 
    }

    table tbody tr:hover { background-color: #EFF6FF !important; }
    
    .total-box {
        padding: 10px 20px;
        border-radius: 8px;
        background-color: #EFF6FF;
        border-left: 6px solid #1D4ED8;
        font-size: 36px !important; 
        font-weight: 800;
        color: #1E3A8A; 
        line-height: 1.2;
        border: 1px solid #BFDBFE;
    }
    .total-label { font-size: 14px; color: #3B82F6; display: block; font-weight: 600; text-transform: uppercase; margin-bottom: -5px; }
    .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if "nav_menu" not in st.session_state: st.session_state.nav_menu = "Panel Principal"
if "items_cot" not in st.session_state: st.session_state.items_cot = []
if "vista_cliente" not in st.session_state: st.session_state.vista_cliente = False
if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {"codigo": "KG-20260928-01", "evento": "Fiesta Fin de Año", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-10-02", "estado": "Aprobada", "total": 1250.00},
    ]

# --- BASES DE DATOS ---
ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias Ciudades"]
clientes_lista = ["Corrugadora Nacional Cransa S.A. (1791179382001)", "Siemens Ecuador S.A.", "Hilton Colón Quito", "Bebidas Arcacontinental", "Essity Ecuador", "Intaco Ecuador", "Levapan del Ecuador", "Industrias Lácteas Toni S.A."]

# Base de datos ampliada con el campo "descripcion"
proveedores_catalogo = [
    {"servicio": "Cabina fotográfica", "proveedor": "SuperDuper Photobooth", "categoria": "Entretenimiento", "ciudad": "Quito", "precio_base": 300.0, "iva": 0.0, "descripcion": "Servicio de cabina ilimitada por 2 horas, incluye props y fotos impresas."},
    {"servicio": "Animador corporativo", "proveedor": "Victor Ramírez", "categoria": "Animación", "ciudad": "Quito", "precio_base": 150.0, "iva": 0.15, "descripcion": "Animación profesional, dinámicas de integración empresarial por 3 horas."},
    {"servicio": "Logística y transporte", "proveedor": "Karkajadas Group", "categoria": "Logística", "ciudad": "Quito", "precio_base": 40.0, "iva": 0.0, "descripcion": "Transporte de equipos y personal dentro del perímetro urbano."},
    {"servicio": "Carpa 6x6 Blanca", "proveedor": "Carpas Pichincha", "categoria": "Estructuras", "ciudad": "Quito", "precio_base": 50.0, "iva": 0.15, "descripcion": "Carpa estructural blanca de 6x6 metros, incluye montaje y desmontaje."},
    {"servicio": "Carpa 6x6 Transparente", "proveedor": "Eventos VIP UIO", "categoria": "Estructuras", "ciudad": "Quito", "precio_base": 80.0, "iva": 0.15, "descripcion": "Carpa elegante totalmente transparente, ideal para eventos nocturnos."},
    {"servicio": "Carpa 6x6 Blanca", "proveedor": "Eventos Guayas", "categoria": "Estructuras", "ciudad": "Guayaquil", "precio_base": 60.0, "iva": 0.15, "descripcion": "Carpa estándar para clima cálido."},
    {"servicio": "Baby Park", "proveedor": "Karkajadas Group", "categoria": "Infantil", "ciudad": "Quito", "precio_base": 125.0, "iva": 0.0, "descripcion": "Parque infantil seguro para niños de 1 a 4 años con estimulación temprana."}
]

# --- MENÚ LATERAL ---
st.sidebar.markdown("### Karkajadas Group")
if st.sidebar.button("🏠 Panel Principal", use_container_width=True): st.session_state.nav_menu = "Panel Principal"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("✨ Nueva Cotización", use_container_width=True): st.session_state.nav_menu = "Nueva Cotización"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("📂 Consultar Cotizaciones", use_container_width=True): st.session_state.nav_menu = "Consultar Cotizaciones"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("👥 Clientes y Proveedores", use_container_width=True): st.session_state.nav_menu = "Directorios"; st.session_state.vista_cliente = False; st.rerun()

menu = st.session_state.nav_menu

# --- VISTA 1: PANEL PRINCIPAL (HOME PRO) ---
if menu == "Panel Principal":
    st.markdown("<h2 style='color: #0F172A; font-weight: 800;'>Karkajadas Group - ERP Workspace</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 16px; margin-top: -10px;'>Resumen Ejecutivo y Gestión Operativa</p>", unsafe_allow_html=True)
    
    cots = st.session_state.cotizaciones_guardadas
    ingresos_aprobados = sum(c["total"] for c in cots if c["estado"] == "Aprobada")
    num_aprobadas = len([c for c in cots if c["estado"] == "Aprobada"])
    num_pendientes = len([c for c in cots if c["estado"] in ["Borrador", "Enviada"]])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Ingresos Confirmados", f"${ingresos_aprobados:,.2f}")
    m2.metric("✅ Eventos Aprobados", f"{num_aprobadas} eventos")
    m3.metric("⏳ Cotizaciones Pendientes", f"{num_pendientes} en gestión")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🚀 Accesos Rápidos")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("➕ Crear Nueva Cotización", use_container_width=True): st.session_state.nav_menu = "Nueva Cotización"; st.rerun()
    with b2:
        if st.button("📂 Consultar Archivo Histórico", use_container_width=True): st.session_state.nav_menu = "Consultar Cotizaciones"; st.rerun()
    with b3:
        if st.button("👥 Base de Datos (Terceros)", use_container_width=True): st.session_state.nav_menu = "Directorios"; st.rerun()
            
    st.markdown("<hr style='margin: 20px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("#### 📅 Cronograma de Próximos Eventos (Aprobados)")
    eventos_aprobados = [cot for cot in cots if cot["estado"] == "Aprobada"]
    
    if eventos_aprobados:
        df_eventos = pd.DataFrame(eventos_aprobados)[["fecha", "evento", "cliente", "codigo", "total"]]
        df_eventos.columns = ["Fecha Confirmada", "Nombre del Evento", "Cliente Corporativo", "Cod. Cotización", "Monto Total ($)"]
        df_eventos["Monto Total ($)"] = df_eventos["Monto Total ($)"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_eventos, use_container_width=True)
    else:
        st.info("No hay eventos confirmados para mostrar en este momento.")

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva Cotización":
    st.markdown("<h3>Generador de Cotizaciones</h3>", unsafe_allow_html=True)
    codigo_sugerido = f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
    with col1: cod_cotizacion = st.text_input("Código Cotización", value=codigo_sugerido)
    with col2: nombre_evento = st.text_input("Nombre del Evento", placeholder="Ej. Fiesta Fin de Año")
    with col3: cliente_sel = st.selectbox("Cliente", clientes_lista)
    with col4: fecha_gral = st.date_input("Fecha General", datetime.now()) 
    with col5: estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"])
        
    st.markdown("---")
    
    with st.expander("🔍 Buscador de Proveedores y Servicios", expanded=True):
        st.markdown("<p style='font-size: 15px; font-weight: bold; color: #1E40AF;'>PASO 1: Buscar Disponibilidad</p>", unsafe_allow_html=True)
        f1, f2 = st.columns([1, 2])
        with f1:
            ciudad_filtro = st.selectbox("Ciudad del Servicio", ciudades_lista, index=0)
        with f2:
            palabra_busqueda = st.text_input("Palabra clave (Ej. Carpa, Animador)", placeholder="Escribe para filtrar los resultados...")
        
        # Filtro Dinámico
        resultados = []
        for p in proveedores_catalogo:
            if p["ciudad"] == ciudad_filtro:
                if palabra_busqueda == "" or \
                   palabra_busqueda.lower() in p["servicio"].lower() or \
                   palabra_busqueda.lower() in p["proveedor"].lower() or \
                   palabra_busqueda.lower() in p["categoria"].lower():
                    resultados.append(p)
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        if not resultados:
            st.warning(f"No se encontraron proveedores para '{palabra_busqueda}' en {ciudad_filtro}.")
        else:
            st.markdown("<p style='font-size: 15px; font-weight: bold; color: #1E40AF;'>PASO 2: Proveedores Encontrados</p>", unsafe_allow_html=True)
            
            # Formato de la lista (Sin precio base, con IVA y Descripción)
            opciones_str = []
            for r in resultados:
                iva_str = f"IVA: {int(r['iva']*100)}%" if r['iva'] > 0 else "IVA: 0%"
                desc = r.get("descripcion", "Descripción pendiente de agregar a la base de datos.")
                opciones_str.append(f"🔹 {r['servicio']} | {r['proveedor']} | {iva_str} | 📝 {desc}")
            
            # Lista de selección dinámica y limpia
            seleccion = st.radio("Seleccione el servicio exacto:", opciones_str, label_visibility="collapsed")
            item_seleccionado = resultados[opciones_str.index(seleccion)]
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 15px; font-weight: bold; color: #1E40AF;'>PASO 3: Definir Cantidades y Valores Finales</p>", unsafe_allow_html=True)
            
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: fecha_item = st.date_input("Fecha Específica", value=fecha_gral)
            with cb: cant_add = st.number_input("Cantidad a contratar", min_value=1, value=1)
            with cc: costo_add = st.number_input("Costo Unit. Negociado ($)", value=float(item_seleccionado["precio_base"]))
            with cd: iva_add = st.selectbox("Aplica IVA Prov.", [0.0, 0.15], index=1 if item_seleccionado["iva"] > 0 else 0, format_func=lambda x: f"{int(x * 100)}%")
            with ce: fee_add = st.number_input("Margen / FEE (%)", value=20.00, step=5.00, format="%.2f")
                
            if st.button("➕ Agregar este ítem a la Cotización"):
                st.session_state.items_cot.append({
                    "servicio": item_seleccionado["servicio"], 
                    "proveedor": item_seleccionado["proveedor"], 
                    "ciudad": ciudad_filtro,
                    "fecha": str(fecha_item), 
                    "cantidad": cant_add, 
                    "costo": costo_add,
                    "iva_prov": iva_add, 
                    "fee_pct": fee_add
                })
                st.rerun()

    if st.session_state.items_cot:
        st.markdown("#### Ítems Actuales en la Cotización (Vista Interna)")
        
        hx = st.columns([2.5, 1.5, 0.5, 1, 1, 1, 1, 0.5])
        hx[0].markdown("**Servicio / Proveedor**")
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
            cx[0].write(f"**{item['servicio']}** \n\n*{item['proveedor']}*")
            cx[1].write(f"{item['fecha']} \n\n{item['ciudad']}")
            cx[2].write(f"x{item['cantidad']}")
            cx[3].write(f"${item['costo']:.2f}")
            cx[4].write(f"{int(item['iva_prov']*100)}%")
            cx[5].write(f"{item['fee_pct']:.2f}%")
            cx[6].write(f"**${total_item:.2f}**")
            if cx[7].button("X", key=f"del_{idx}"):
                st.session_state.items_cot.pop(idx); st.rerun()
            st.markdown("<hr style='margin: 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        t1.metric("Costo Base Proveedores", f"${subtotal_prov:.2f}")
        t2.metric("Ganancia Neta (FEE)", f"${total_fee:.2f}")
        t3.markdown(f"<div class='total-box'><span class='total-label'>TOTAL CLIENTE</span>${total_general:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("💾 Guardar Cotización Interna"):
                st.session_state.cotizaciones_guardadas.append({
                    "codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, 
                    "fecha": str(fecha_gral), "estado": estado_cot, "total": total_general
                })
                st.session_state.items_cot = [] 
                st.success("Cotización guardada exitosamente.")
        with btn2:
            if st.button("📄 Generar Vista Cliente (Limpia)"):
                st.session_state.vista_cliente = True
                st.rerun()

    if st.session_state.vista_cliente and st.session_state.items_cot:
        st.markdown("---")
        st.markdown(f"### 📄 Cotización Comercial: {nombre_evento}")
        st.write(f"**Cliente:** {cliente_sel} | **Código:** {cod_cotizacion} | **Fecha:** {fecha_gral}")
        
        datos_cliente = []
        for item in st.session_state.items_cot:
            costo_real = item["costo"] * (1 + item["iva_prov"])
            fee_valor = costo_real * (item["fee_pct"] / 100.0)
            total_linea = (costo_real + fee_valor) * item["cantidad"]
            precio_unitario_cliente = total_linea / item["cantidad"]
            
            datos_cliente.append({
                "Servicio": item["servicio"], "Ciudad": item["ciudad"], "Fecha": item["fecha"],
                "Cant.": item["cantidad"], "V. Unitario": f"${precio_unitario_cliente:.2f}", "V. Total": f"${total_linea:.2f}"
            })
            
        st.table(pd.DataFrame(datos_cliente))
        st.markdown(f"<h3 style='text-align: right;'>TOTAL: ${total_general:.2f}</h3>", unsafe_allow_html=True)

# --- VISTA 3: CONSULTAR COTIZACIONES ---
elif menu == "Consultar Cotizaciones":
    st.markdown("<h3>Registro de Cotizaciones</h3>", unsafe_allow_html=True)
    if st.session_state.cotizaciones_guardadas:
        st.dataframe(pd.DataFrame(st.session_state.cotizaciones_guardadas), use_container_width=True)
    else:
        st.write("No hay cotizaciones registradas aún.")

# --- VISTA 4: DIRECTORIOS ---
elif menu == "Directorios":
    st.markdown("<h3>Base de Datos</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Clientes", "Proveedores"])
    with t1: st.dataframe(pd.DataFrame({"Cliente": clientes_lista}), use_container_width=True)
    with t2: st.dataframe(pd.DataFrame(proveedores_catalogo), use_container_width=True)
