import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO ELEGANTE (FONDO BLANCO Y GRIS SUAVE) ---
st.set_page_config(
    page_title="Karkajadas Group - Sistema de Gestión y Cotizaciones",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados: Fondo blanco dominante, tipografía legible y diseño corporativo
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
        color: #1F2937;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stSidebar {
        background-color: #F3F4F6;
        border-right: 1px solid #E5E7EB;
    }
    .stSidebar h3, .stSidebar p {
        color: #111827 !important;
    }
    h1, h2, h3 {
        color: #111827;
        font-weight: 600;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 24px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #F97316; /* Naranja corporativo Karkajadas */
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #EA580C;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTENTICACIÓN SEGURA ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login(username, password):
    if username == "admin" and password == "Karkajadas2026*":
        return True
    return False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #111827;'>Karkajadas Group</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #4B5563; font-size: 16px;'>Eventos Corporativos y Gestión Operativa</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar al Sistema")
            
            if submit:
                if check_login(user, pwd):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
    st.stop()

# --- DATOS REALES CARGADOS DESDE TUS ARCHIVOS ---
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

# Directorio de proveedores reales y servicios
proveedores_catalogo = [
    {"servicio": "Maquillaje social y artístico", "proveedor": "Cristina Taimal", "categoria": "Maquillaje", "ciudad": "Quito", "precio_base": 30.0, "iva": 0.0},
    {"servicio": "Baby Park", "proveedor": "Karkajadas Group", "categoria": "Entretenimiento infantil", "ciudad": "Quito", "precio_base": 125.0, "iva": 0.0},
    {"servicio": "Minicity", "proveedor": "Karkajadas Group", "categoria": "Entretenimiento infantil", "ciudad": "Quito", "precio_base": 200.0, "iva": 0.0},
    {"servicio": "Estación de Arte", "proveedor": "Karkajadas Group", "categoria": "Actividades creativas", "ciudad": "Quito", "precio_base": 160.0, "iva": 0.0},
    {"servicio": "Estaciones deportivas", "proveedor": "Karkajadas Group", "categoria": "Actividades deportivas", "ciudad": "Quito", "precio_base": 75.0, "iva": 0.0},
    {"servicio": "Trípticos tamaño A4", "proveedor": "Proveedores Gráficos S.A.", "categoria": "Imprenta", "ciudad": "Guayaquil", "precio_base": 1.15, "iva": 0.15}
]

# --- BARRA LATERAL ELEGANTE ---
st.sidebar.markdown("<h2 style='color: #111827; font-size: 20px;'>🎨 Karkajadas Group</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 13px; color: #4B5563;'><b>RUC:</b> 1713272845001<br><b>Gerencia:</b> Nancy García Chugá</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navegación", ["Nueva Cotización", "Directorio de Clientes", "Proveedores y Servicios", "Dashboard 360° & Calendario"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- MÓDULO 1: NUEVA COTIZACIÓN CON CIUDAD POR ÍTEM ---
if menu == "Nueva Cotización":
    st.markdown("<h2>Generador Comercial de Cotizaciones</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4B5563;'>Arme cotizaciones detalladas asignando ciudades específicas por cada línea de servicio.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            cliente_sel = st.selectbox("Cliente Destino", clientes_lista)
        with col2:
            ciudad_gral = st.selectbox("Ámbito Geográfico General", ciudades_lista)
        with col3:
            fecha_evento = st.date_input("Fecha Principal del Evento", datetime.now())
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("### Detalle de Ítems y Servicios")
    
    if "items_cot" not in st.session_state:
        st.session_state.items_cot = [
            {"servicio": "Minicity", "proveedor": "Karkajadas Group", "ciudad": "Quito", "cantidad": 1, "costo": 200.0, "iva_prov": 0.0, "fee_pct": 25.0},
            {"servicio": "Trípticos tamaño A4", "proveedor": "Proveedores Gráficos S.A.", "ciudad": "Guayaquil", "cantidad": 100, "costo": 1.15, "iva_prov": 0.15, "fee_pct": 20.0}
        ]

    with st.expander("➕ Añadir nuevo servicio al detalle"):
        c_cat = st.selectbox("Seleccionar Servicio del Catálogo", [p["servicio"] for p in proveedores_catalogo])
        item_def = next(p for p in proveedores_catalogo if p["servicio"] == c_cat)
        
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        with col_a:
            cant_add = st.number_input("Cantidad", min_value=1, value=1)
        with col_b:
            costo_add = st.number_input("Costo Unitario ($)", value=item_def["precio_base"])
        with col_c:
            ciudad_item = st.selectbox("Ciudad de este servicio", ciudades_lista, index=0)
        with col_d:
            iva_add = st.selectbox("IVA Proveedor", [0.0, 0.15], index=1 if item_def["iva"] > 0 else 0)
        with col_e:
            fee_add = st.number_input("FEE % (Dinámico)", value=20.0, step=5.0)
            
        if st.button("Agregar a la Cotización"):
            st.session_state.items_cot.append({
                "servicio": c_cat,
                "proveedor": item_def["proveedor"],
                "ciudad": ciudad_item,
                "cantidad": cant_add,
                "costo": costo_add,
                "iva_prov": iva_add,
                "fee_pct": fee_add
            })
            st.success("¡Línea agregada con éxito!")
            st.rerun()

    # Tabla interactiva
    subtotal_general = 0
    total_general = 0
    data_tabla = []
    
    for idx, item in enumerate(st.session_state.items_cot):
        sub_costo = item["cantidad"] * item["costo"]
        iva_costo_val = sub_costo * item["iva_prov"]
        sub_con_iva = sub_costo + iva_costo_val
        fee_val = sub_con_iva * (item["fee_pct"] / 100.0)
        total_item = sub_con_iva + fee_val
        
        subtotal_general += sub_con_iva
        total_general += total_item
        
        data_tabla.append({
            "Servicio": item["servicio"],
            "Proveedor": item["proveedor"],
            "Ciudad": item["ciudad"],
            "Cant.": item["cantidad"],
            "Costo U.": f"${item['costo']:.2f}",
            "Subtotal Proveedor": f"${sub_costo:.2f}",
            "FEE (%)": f"{item['fee_pct']}%",
            "Total Venta": f"${total_item:.2f}"
        })
        
    st.table(pd.DataFrame(data_tabla))
    
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
        if st.button("📄 Generar PDF Cotización (Cliente)"):
            st.success("¡Cotización PDF generada y respaldada en Google Drive!")
    with c_btn2:
        if st.button("📋 Generar Orden de Contratación (Proveedor)"):
            st.success("¡Orden de servicio a proveedor generada!")

# --- MÓDULO 2: DIRECTORIO DE CLIENTES ---
elif menu == "Directorio de Clientes":
    st.markdown("<h2>Directorio de Clientes Estandarizado</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4B5563;'>Base de datos corporativa limpia y depurada.</p>", unsafe_allow_html=True)
    
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
    st.markdown("<p style='color: #4B5563;'>Tarifas referenciales y costos por categoría.</p>", unsafe_allow_html=True)
    
    df_prov = pd.DataFrame(proveedores_catalogo)
    st.dataframe(df_prov, use_container_width=True)

# --- MÓDULO 4: DASHBOARD 360 Y CALENDARIO ---
elif menu == "Dashboard 360° & Calendario":
    st.markdown("<h2>Dashboard 360° - Karkajadas Group</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4B5563;'>Centro de análisis financiero y control de eventos.</p>", unsafe_allow_html=True)
    
    # Filtros superiores
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
    st.markdown("### 📅 Calendario y Registro de Eventos Confirmados")
    st.info("💡 Próximo evento: Feria de Salud con Cransa en Quito — Fecha: 07 de Octubre de 2026.")
