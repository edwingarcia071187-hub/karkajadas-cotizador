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

# --- ESTILOS CSS: OPTIMIZACIÓN DE ESPACIO Y CONTRASTE DE BOTONES ---
st.markdown("""
    <style>
    /* Fondo blanco absoluto */
    .stApp, .main, header {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    
    /* Botones principales con contorno claro y elegante para ser visibles */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 14px;
        border: 2px solid #0F172A !important; /* CONTORNO AZUL MARINO/NEGRO ELEGANTE */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
    }
    .stButton>button p {
        color: inherit !important;
    }
    
    /* Tarjetas del menú principal */
    .nav-card {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        background-color: #F8FAFC;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        cursor: pointer;
        transition: 0.3s;
    }
    .nav-card:hover {
        border-color: #0F172A;
        transform: translateY(-2px);
    }
    
    /* Reducir espacios vacíos innecesarios arriba */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Inputs y Selectores limpios */
    div[data-baseweb="select"] > div, input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* Totales destacados */
    .total-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #F1F5F9;
        border-left: 5px solid #0F172A;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE BASES DE DATOS Y ESTADOS ---
if "nav_menu" not in st.session_state:
    st.session_state.nav_menu = "Panel Principal"
if "items_cot" not in st.session_state:
    st.session_state.items_cot = []
if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {"codigo": "KG-20260928-01", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-10-02", "estado": "Aprobada", "total": 1250.00},
        {"codigo": "KG-20260929-02", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-10-04", "estado": "Aprobada", "total": 840.50},
        {"codigo": "KG-20260930-01", "cliente": "Hilton Colón Quito", "fecha": "2026-10-15", "estado": "Enviada", "total": 450.00}
    ]

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
if st.sidebar.button("🏠 Panel Principal"): st.session_state.nav_menu = "Panel Principal"; st.rerun()
if st.sidebar.button("✨ Nueva Cotización"): st.session_state.nav_menu = "Nueva Cotización"; st.rerun()
if st.sidebar.button("📂 Consultar Cotizaciones"): st.session_state.nav_menu = "Consultar Cotizaciones"; st.rerun()
if st.sidebar.button("👥 Clientes y Proveedores"): st.session_state.nav_menu = "Directorios"; st.rerun()

menu = st.session_state.nav_menu

# --- VISTA 1: PANEL PRINCIPAL (HOME) ---
if menu == "Panel Principal":
    st.markdown("<h2>Karkajadas Group - Workspace</h2>", unsafe_allow_html=True)
    
    # Tarjetas de Navegación Rápida
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ Crear Nueva Cotización"):
            st.session_state.nav_menu = "Nueva Cotización"
            st.rerun()
    with c2:
        if st.button("📂 Ver Cotizaciones Guardadas"):
            st.session_state.nav_menu = "Consultar Cotizaciones"
            st.rerun()
    with c3:
        if st.button("📊 Reportes y Dashboard"):
            st.success("Módulo de reportes en construcción.")
            
    st.markdown("---")
    
    # Visualizador de Eventos de la Semana (Solo Aprobadas)
    st.markdown("### 📅 Eventos de esta Semana (Cotizaciones Aprobadas)")
    
    # CORRECCIÓN DE LA LÍNEA DEL ERROR (for en lugar de para)
    eventos_aprobados = [cot for cot in st.session_state.cotizaciones_guardadas if cot["estado"] == "Aprobada"]
    
    if eventos_aprobados:
        for ev in eventos_aprobados:
            st.info(f"✅ **{ev['fecha']}** | Cliente: {ev['cliente']} | Código: {ev['codigo']} | Monto: ${ev['total']:.2f}")
    else:
        st.write("No hay eventos confirmados para esta semana.")

# --- VISTA 2: NUEVA COTIZACIÓN (LAYOUT COMPACTO) ---
elif menu == "Nueva Cotización":
    st.markdown("<h3>Generador de Cotizaciones</h3>", unsafe_allow_html=True)
    
    # Generar código automático sugerido
    codigo_sugerido = f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    
    # 1. LAYOUT SUPERIOR SÚPER COMPACTO
    col1, col2, col3, col4 = st.columns([1.5, 3, 1.5, 1.5])
    with col1:
        cod_cotizacion = st.text_input("Código Cotización", value=codigo_sugerido)
    with col2:
        cliente_sel = st.selectbox("Cliente", clientes_lista)
    with col3:
        fecha_gral = st.text_input("Fecha Gral. (YYYY-MM-DD)", value=str(datetime.now().date()))
    with col4:
        estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"])
        
    st.markdown("---")
    
    # 2. SECCIÓN DE ÍTEMS
    with st.expander("➕ Añadir servicio (con fecha y ciudad específica)", expanded=True):
        c_cat = st.selectbox("Servicio del Catálogo", [p["servicio"] for p in proveedores_catalogo])
        item_def = next(p for p in proveedores_catalogo if p["servicio"] == c_cat)
        
        ca, cb, cc, cd, ce, cf = st.columns(6)
        with ca: cant_add = st.number_input("Cant.", min_value=1, value=1)
        with cb: costo_add = st.number_input("Costo Unit. ($)", value=item_def["precio_base"])
        with cc: fecha_item = st.text_input("Fecha", value=fecha_gral)
        with cd: ciudad_item = st.selectbox("Ciudad", ciudades_lista, index=0)
        with ce: iva_add = st.selectbox("IVA Prov.", [0.0, 0.15], index=1 if item_def["iva"] > 0 else 0)
        with cf: fee_add = st.number_input("FEE %", value=20.0, step=5.0)
            
        if st.button("Agregar a la Cotización"):
            st.session_state.items_cot.append({
                "servicio": c_cat, "proveedor": item_def["proveedor"], "ciudad": ciudad_item,
                "fecha": fecha_item, "cantidad": cant_add, "costo": costo_add,
                "iva_prov": iva_add, "fee_pct": fee_add
            })
            st.rerun()

    # 3. TABLA DE ÍTEMS ACTUALES
    if st.session_state.items_cot:
        subtotal_prov = 0
        total_fee = 0
        total_general = 0
        
        for idx, item in enumerate(st.session_state.items_cot):
            sub_costo = item["cantidad"] * item["costo"]
            sub_con_iva = sub_costo + (sub_costo * item["iva_prov"])
            fee_val = sub_con_iva * (item["fee_pct"] / 100.0)
            total_item = sub_con_iva + fee_val
            
            subtotal_prov += sub_con_iva
            total_fee += fee_val
            total_general += total_item
            
            cx = st.columns([2.5, 1.5, 0.5, 1, 1, 1, 1, 0.5])
            cx[0].write(f"**{item['servicio']}** (*{item['proveedor']}*)")
            cx[1].write(f"{item['fecha']} | {item['ciudad']}")
            cx[2].write(f"x{item['cantidad']}")
            cx[3].write(f"${item['costo']:.2f}")
            cx[4].write(f"IVA {int(item['iva_prov']*100)}%")
            cx[5].write(f"FEE {item['fee_pct']}%")
            cx[6].write(f"**${total_item:.2f}**")
            if cx[7].button("X", key=f"del_{idx}"):
                st.session_state.items_cot.pop(idx)
                st.rerun()
            st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)
            
        # 4. TOTALES REESTRUCTURADOS Y CLAROS
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        t1.metric("Costo Base Proveedores", f"${subtotal_prov:.2f}")
        t2.metric("Ganancia Neta (FEE)", f"${total_fee:.2f}")
        t3.markdown(f"<div class='total-box'>TOTAL: ${total_general:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("💾 Guardar Cotización"):
                st.session_state.cotizaciones_guardadas.append({
                    "codigo": cod_cotizacion, "cliente": cliente_sel, 
                    "fecha": fecha_gral, "estado": estado_cot, "total": total_general
                })
                st.session_state.items_cot = [] # Limpiar actual
                st.success("Cotización guardada exitosamente.")
        with btn2:
            if st.button("📄 Generar PDF para el Cliente"):
                st.success("PDF generado.")

# --- VISTA 3: CONSULTAR COTIZACIONES ---
elif menu == "Consultar Cotizaciones":
    st.markdown("<h3>Registro de Cotizaciones</h3>", unsafe_allow_html=True)
    df_cot = pd.DataFrame(st.session_state.cotizaciones_guardadas)
    if not df_cot.empty:
        st.dataframe(df_cot, use_container_width=True)
    else:
        st.write("No hay cotizaciones registradas aún.")

# --- VISTA 4: DIRECTORIOS ---
elif menu == "Directorios":
    st.markdown("<h3>Base de Datos de Clientes y Proveedores</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Clientes", "Proveedores"])
    with t1:
        st.dataframe(pd.DataFrame({"Cliente": clientes_lista}), use_container_width=True)
    with t2:
        st.dataframe(pd.DataFrame(proveedores_catalogo), use_container_width=True)
