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

# --- ESTILOS CSS: INTERFAZ PRO Y TARJETAS DE MÉTRICAS ---
st.markdown("""
    <style>
    .stApp, .main, header { background-color: #FFFFFF !important; color: #0F172A !important; }
    
    /* Botones de acción rápida: Anchos y elegantes */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 15px;
        border: 2px solid #0F172A !important; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background-color: #0F172A !important; color: #FFFFFF !important; transform: translateY(-2px); }
    .stButton>button p { color: inherit !important; }
    
    /* Convertir las Métricas (KPIs) en Tarjetas PRO */
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 5px solid #0F172A;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }
    
    /* Inputs y Selectores */
    div[data-baseweb="select"] > div, input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* TOTAL DESTACADO */
    .total-box {
        padding: 10px 20px;
        border-radius: 8px;
        background-color: #F8FAFC;
        border-left: 6px solid #0F172A;
        font-size: 36px !important; 
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        border: 1px solid #E2E8F0;
    }
    .total-label { font-size: 14px; color: #64748B; display: block; font-weight: 600; text-transform: uppercase; margin-bottom: -5px; }
    
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
        {"codigo": "KG-20260929-02", "evento": "Lanzamiento Producto", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-10-15", "estado": "Aprobada", "total": 3450.50},
        {"codigo": "KG-20260930-01", "evento": "Cena Corporativa", "cliente": "Hilton Colón Quito", "fecha": "2026-11-05", "estado": "Borrador", "total": 850.00},
    ]

# --- BASES DE DATOS ---
ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias Ciudades"]
clientes_lista = ["Corrugadora Nacional Cransa S.A. (1791179382001)", "Siemens Ecuador S.A.", "Hilton Colón Quito", "Bebidas Arcacontinental", "Essity Ecuador", "Intaco Ecuador", "Levapan del Ecuador", "Industrias Lácteas Toni S.A."]
proveedores_catalogo = [
    {"servicio": "Cabina fotográfica", "proveedor": "SuperDuper Photobooth", "precio_base": 300.0, "iva": 0.0},
    {"servicio": "Animador corporativo", "proveedor": "Victor Ramírez", "precio_base": 150.0, "iva": 0.15},
    {"servicio": "Logística y transporte", "proveedor": "Karkajadas Group", "precio_base": 40.0, "iva": 0.0},
    {"servicio": "Papá Noel / Personaje", "proveedor": "Jairto Arciniegas", "precio_base": 180.0, "iva": 0.0},
    {"servicio": "Parlante y micrófonos", "proveedor": "Karkajadas Group", "precio_base": 45.0, "iva": 0.0},
    {"servicio": "Baby Park", "proveedor": "Karkajadas Group", "precio_base": 125.0, "iva": 0.0}
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
    
    # 1. KPIs (Indicadores Clave)
    cots = st.session_state.cotizaciones_guardadas
    ingresos_aprobados = sum(c["total"] for c in cots if c["estado"] == "Aprobada")
    num_aprobadas = len([c for c in cots if c["estado"] == "Aprobada"])
    num_pendientes = len([c for c in cots if c["estado"] in ["Borrador", "Enviada"]])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Ingresos Confirmados (Aprobados)", f"${ingresos_aprobados:,.2f}")
    m2.metric("✅ Eventos Aprobados", f"{num_aprobadas} eventos")
    m3.metric("⏳ Cotizaciones Pendientes", f"{num_pendientes} en gestión")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. BOTONES DE ACCIÓN RÁPIDA (Estilo Bloque)
    st.markdown("#### 🚀 Accesos Rápidos")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("➕ Crear Nueva Cotización", use_container_width=True): st.session_state.nav_menu = "Nueva Cotización"; st.rerun()
    with b2:
        if st.button("📂 Consultar Archivo Histórico", use_container_width=True): st.session_state.nav_menu = "Consultar Cotizaciones"; st.rerun()
    with b3:
        if st.button("👥 Base de Datos (Terceros)", use_container_width=True): st.session_state.nav_menu = "Directorios"; st.rerun()
            
    st.markdown("<hr style='margin: 20px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    # 3. CRONOGRAMA DE EVENTOS (Tabla de Datos Profesional)
    st.markdown("#### 📅 Cronograma de Próximos Eventos (Solo Aprobados)")
    eventos_aprobados = [cot for cot in cots if cot["estado"] == "Aprobada"]
    
    if eventos_aprobados:
        # Transformar a DataFrame para una vista de tabla limpia
        df_eventos = pd.DataFrame(eventos_aprobados)
        # Reordenar y renombrar columnas para que se vea elegante
        df_eventos = df_eventos[["fecha", "evento", "cliente", "codigo", "total"]]
        df_eventos.columns = ["Fecha Confirmada", "Nombre del Evento", "Cliente Corporativo", "Cod. Cotización", "Monto Total ($)"]
        
        # Formato de moneda
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
    
    with st.expander("➕ Añadir servicio (con fecha y ciudad específica)", expanded=True):
        c_cat = st.selectbox("Servicio del Catálogo", [p["servicio"] for p in proveedores_catalogo])
        item_def = next(p for p in proveedores_catalogo if p["servicio"] == c_cat)
        
        ca, cb, cc, cd, ce, cf = st.columns(6)
        with ca: cant_add = st.number_input("Cant.", min_value=1, value=1)
        with cb: costo_add = st.number_input("Costo Unit. Prov ($)", value=item_def["precio_base"])
        with cc: fecha_item = st.date_input("Fecha", value=fecha_gral) 
        with cd: ciudad_item = st.selectbox("Ciudad", ciudades_lista, index=0)
        with ce: iva_add = st.selectbox("IVA Prov.", [0.0, 0.15], index=1 if item_def["iva"] > 0 else 0)
        with cf: fee_add = st.number_input("FEE %", value=20.0, step=5.0)
            
        if st.button("Agregar a la Cotización"):
            st.session_state.items_cot.append({
                "servicio": c_cat, "proveedor": item_def["proveedor"], "ciudad": ciudad_item,
                "fecha": str(fecha_item), "cantidad": cant_add, "costo": costo_add,
                "iva_prov": iva_add, "fee_pct": fee_add
            })
            st.rerun()

    if st.session_state.items_cot:
        st.markdown("#### Ítems Actuales en la Cotización (Vista Interna)")
        subtotal_prov = 0; total_fee = 0; total_general = 0
        
        for idx, item in enumerate(st.session_state.items_cot):
            sub_costo = item["cantidad"] * item["costo"]
            sub_con_iva = sub_costo + (sub_costo * item["iva_prov"])
            fee_val = sub_con_iva * (item["fee_pct"] / 100.0)
            total_item = sub_con_iva + fee_val
            
            subtotal_prov += sub_con_iva; total_fee += fee_val; total_general += total_item
            
            cx = st.columns([2.5, 1.5, 0.5, 1, 1, 1, 1, 0.5])
            cx[0].write(f"**{item['servicio']}** (*{item['proveedor']}*)")
            cx[1].write(f"{item['fecha']} | {item['ciudad']}")
            cx[2].write(f"x{item['cantidad']}")
            cx[3].write(f"${item['costo']:.2f}")
            cx[4].write(f"IVA {int(item['iva_prov']*100)}%")
            cx[5].write(f"FEE {item['fee_pct']}%")
            cx[6].write(f"**${total_item:.2f}**")
            if cx[7].button("X", key=f"del_{idx}"):
                st.session_state.items_cot.pop(idx); st.rerun()
            st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)
            
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
