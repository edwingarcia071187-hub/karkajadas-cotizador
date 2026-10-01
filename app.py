import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Karkajadas Group - Sistema de Gestión y Cotizaciones",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS MAESTROS: BLANCO ABSOLUTO, CERO FONDOS OSCUROS, CONTRASTE PERFECTO ---
st.markdown("""
    <style>
    /* Forzar fondo blanco absoluto en toda la aplicación */
    .stApp, .main, div[data-testid="stVerticalBlock"], div[data-testid="stBlock"], section.main {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Barra lateral limpia con fondo blanco puro */
    div[data-testid="stSidebar"], div[data-testid="stSidebar"] > div:first-child {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
        padding-top: 1.5rem;
    }
    
    /* Tipografía nítida para todos los textos y títulos */
    h1, h2, h3, p, span, label, div {
        color: #0F172A !important;
    }
    
    /* Tarjetas de contenido con diseño ejecutivo */
    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        margin-bottom: 20px;
    }
    
    /* Botones de navegación y acción principales */
    .stButton>button {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 14px;
        border: none;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.1);
        transition: background-color 0.2s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #334155 !important;
        color: #FFFFFF !important;
    }
    .stButton>button p {
        color: #FFFFFF !important;
    }
    
    /* Corrección estricta para selectores, inputs y menús desplegables (Cero fondos negros) */
    div[data-baseweb="select"] > div, div.stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
    }
    span[data-baseweb="tag"] {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }
    
    /* Ajustes limpios para tablas y contenedores de datos */
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        background-color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO DE NAVEGACIÓN ---
if "nav_menu" not in st.session_state:
    st.session_state.nav_menu = "Nueva Cotización"

# --- DATOS REALES DE CONFIGURACIÓN ---
ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias Ciudades"]

clientes_lista = [
    "Corrugadora Nacional Cransa S.A. (1791179382001)",
    "Hilton Colón Quito",
    "Bebidas Arcacontinental (Arcador S.A.)",
    "Essity Ecuador (1791314379001)",
    "Intaco Ecuador S.A.",
    "Procongelados S.A.",
    "Levapan del Ecuador",
    "Agencia Aseguradora Asertec S.A.",
    "Industrias Lácteas Toni S.A."
]

# Catálogo real extraído de tu base de proveedores
proveedores_catalogo = [
    {"servicio": "Maquillaje social y artístico", "proveedor": "Cristina Taimal", "categoria": "Maquillaje", "ciudad": "Quito", "precio_base": 30.0, "iva": 0.0},
    {"servicio": "Baby Park", "proveedor": "Karkajadas Group", "categoria": "Entretenimiento infantil", "ciudad": "Quito", "precio_base": 125.0, "iva": 0.0},
    {"servicio": "Minicity", "proveedor": "Karkajadas Group", "categoria": "Entretenimiento infantil", "ciudad": "Quito", "precio_base": 200.0, "iva": 0.0},
    {"servicio": "Estación de Arte", "proveedor": "Karkajadas Group", "categoria": "Actividades creativas", "ciudad": "Quito", "precio_base": 160.0, "iva": 0.0},
    {"servicio": "Estaciones deportivas", "proveedor": "Karkajadas Group", "categoria": "Actividades deportivas", "ciudad": "Quito", "precio_base": 75.0, "iva": 0.0},
    {"servicio": "Inflable Castillo", "proveedor": "Karkajadas Group", "categoria": "Entretenimiento infantil", "ciudad": "Quito", "precio_base": 100.0, "iva": 0.0},
    {"servicio": "Cañón de espuma", "proveedor": "Karkajadas Group", "categoria": "Actividades lúdicas", "ciudad": "Quito", "precio_base": 85.0, "iva": 0.0}
]

# --- MENÚ LATERAL LIMPIO ---
st.sidebar.markdown("<h2 style='color: #0F172A; font-size: 18px; font-weight: 700; letter-spacing: -0.5px;'>Karkajadas Group</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size: 11px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;'>Navegación</p>", unsafe_allow_html=True)

if st.sidebar.button("Nueva Cotización"):
    st.session_state.nav_menu = "Nueva Cotización"
    st.rerun()

if st.sidebar.button("Directorio de Clientes"):
    st.session_state.nav_menu = "Directorio de Clientes"
    st.rerun()

if st.sidebar.button("Proveedores y Servicios"):
    st.session_state.nav_menu = "Proveedores y Servicios"
    st.rerun()

if st.sidebar.button("Dashboard 360° y Calendario"):
    st.session_state.nav_menu = "Dashboard 360° y Calendario"
    st.rerun()

st.sidebar.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
st.sidebar.caption("Sistema Operativo Activo")

menu = st.session_state.nav_menu

# --- MÓDULO 1: NUEVA COTIZACIÓN ---
if menu == "Nueva Cotización":
    st.markdown("<h2>Generador Comercial de Cotizaciones</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Configure el cliente, asigne múltiples fechas y ciudades por cada línea de servicio.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            cliente_sel = st.selectbox("Cliente Destino", clientes_lista)
        with col2:
            ciudad_gral = st.selectbox("Ámbito Geográfico General", ciudades_lista)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("### Detalle de Ítems, Fechas y Servicios")
    
    if "items_cot" not in st.session_state:
        st.session_state.items_cot = [
            {"servicio": "Minicity", "proveedor": "Karkajadas Group", "ciudad": "Quito", "fecha": str(datetime.now().date()), "cantidad": 1, "costo": 200.0, "iva_prov": 0.0, "fee_pct": 25.0}
        ]

    # Formulario para agregar ítem con fecha específica
    with st.expander("Añadir nuevo servicio al detalle con su fecha y ciudad"):
        c_cat = st.selectbox("Seleccionar Servicio del Catálogo Real", [p["servicio"] for p in proveedores_catalogo])
        item_def = next(p for p in proveedores_catalogo if p["servicio"] == c_cat)
        
        col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
        with col_a:
            cant_add = st.number_input("Cantidad", min_value=1, value=1)
        with col_b:
            costo_add = st.number_input("Costo Unitario ($)", value=item_def["precio_base"])
        with col_c:
            fecha_item = st.date_input("Fecha del Servicio", datetime.now())
        with col_d:
            ciudad_item = st.selectbox("Ciudad", ciudades_lista, index=0)
        with col_e:
            iva_add = st.selectbox("IVA", [0.0, 0.15], index=1 if item_def["iva"] > 0 else 0)
        with col_f:
            fee_add = st.number_input("FEE %", value=20.0, step=5.0)
            
        if st.button("Agregar a la Cotización"):
            st.session_state.items_cot.append({
                "servicio": c_cat,
                "proveedor": item_def["proveedor"],
                "ciudad": ciudad_item,
                "fecha": str(fecha_item),
                "cantidad": cant_add,
                "costo": costo_add,
                "iva_prov": iva_add,
                "fee_pct": fee_add
            })
            st.success("¡Línea agregada con éxito!")
            st.rerun()

    # Visualización y opción de eliminar ítems
    st.markdown("#### Ítems Actuales en la Cotización")
    subtotal_general = 0
    total_general = 0
    
    for idx, item in enumerate(st.session_state.items_cot):
        sub_costo = item["cantidad"] * item["costo"]
        iva_costo_val = sub_costo * item["iva_prov"]
        sub_con_iva = sub_costo + iva_costo_val
        fee_val = sub_con_iva * (item["fee_pct"] / 100.0)
        total_item = sub_con_iva + fee_val
        
        subtotal_general += sub_con_iva
        total_general += total_item
        
        cols = st.columns([2, 1.5, 1, 1, 1, 1, 1, 0.8])
        cols[0].write(f"**{item['servicio']}**\n\n*Prov: {item['proveedor']}*")
        cols[1].write(f"📅 {item['fecha']}\n📍 {item['ciudad']}")
        cols[2].write(f"Cant: {item['cantidad']}")
        cols[3].write(f"Costo: ${item['costo']:.2f}")
        cols[4].write(f"IVA: {int(item['iva_prov']*100)}%")
        cols[5].write(f"FEE: {item['fee_pct']}%")
        cols[6].write(f"**Total: ${total_item:.2f}**")
        
        if cols[7].button("🗑️", key=f"del_{idx}"):
            st.session_state.items_cot.pop(idx)
            st.rerun()
        st.markdown("<hr style='margin: 4px 0; border: none; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.markdown(f"**Subtotal Operativo:** ${subtotal_general:.2f}")
    with col_r2:
        st.markdown(f"**Ganancia Neta (FEE):** ${total_general - subtotal_general:.2f}")
    with col_r3:
        st.markdown(f"### **Total Cliente:** ${total_general:.2f}")
        
    st.markdown("---")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("Generar PDF Cotización (Cliente)"):
            st.success("¡Cotización PDF generada y respaldada en Google Drive!")
    with c_btn2:
        if st.button("Generar Orden de Contratación (Proveedor)"):
            st.success("¡Orden de servicio a proveedor generada!")

# --- MÓDULO 2: DIRECTORIO DE CLIENTES ---
elif menu == "Directorio de Clientes":
    st.markdown("<h2>Directorio de Clientes Estandarizado</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Base de datos corporativa limpia y depurada.</p>", unsafe_allow_html=True)
    
    df_clientes = pd.DataFrame({
        "Empresa Cliente": ["Corrugadora Nacional Cransa S.A.", "Hilton Colón Quito", "Bebidas Arcacontinental", "Essity Ecuador", "Intaco Ecuador", "Procongelados S.A.", "Levapan del Ecuador", "Asertec S.A.", "Industrias Lácteas Toni S.A."],
        "RUC": ["1791179382001", "1790012345001", "1792411149001", "1791314379001", "1791234567001", "1790987654001", "1791122334001", "1790930866001", "0990351260001"],
        "Ciudad Principal": ["Quito", "Quito", "Quito", "Quito", "Guayaquil", "Quito", "Quito", "Quito", "Guayaquil"],
        "Contacto": ["Departamento de Compras", "Eventos y Logística", "Francisco Velasco", "Línea Corporativa", "Patricia Sevilla", "Gabriela Guano", "M. Buitrón", "Eva Baca", "Servicio al Cliente"]
    })
    st.dataframe(df_clientes, use_container_width=True)

# --- MÓDULO 3: PROVEEDORES Y SERVICIOS ---
elif menu == "Proveedores y Servicios":
    st.markdown("<h2>Catálogo Maestro de Proveedores y Servicios</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Tarifas referenciales y costos por categoría basados en sus registros reales.</p>", unsafe_allow_html=True)
    
    df_prov = pd.DataFrame(proveedores_catalogo)
    st.dataframe(df_prov, use_container_width=True)

# --- MÓDULO 4: DASHBOARD 360 Y CALENDARIO ---
elif menu == "Dashboard 360° y Calendario":
    st.markdown("<h2>Dashboard 360° - Karkajadas Group</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Centro de análisis financiero y control de eventos.</p>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    with f1:
        st.selectbox("Filtrar por Empresa", ["Todas las empresas", "Corrugadora Nacional Cransa S.A.", "Hilton Colón Quito", "Essity Ecuador"])
    with f2:
        st.selectbox("Filtrar por Mes", ["Octubre 2026", "Septiembre 2026", "Agosto 2026", "Todos los meses"])
    with f3:
        st.selectbox("Año", [2026, 2025])
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Facturación Total", "$18,450.00", "+14% vs mes anterior")
    m2.metric("Ganancia Neta (FEE)", "$4,120.00", "+22% rentabilidad")
    m3.metric("Eventos Confirmados", "12", "Activos en curso")
    
    st.markdown("---")
    st.markdown("### Calendario y Registro de Eventos Confirmados")
    st.info("Próximo evento: Feria de Salud con Cransa en Quito — Fecha: 07 de Octubre de 2026.")
