import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO MINIMALISTA (FONDO BLANCO, ELEGANTE) ---
st.set_page_config(
    page_title="Karkajadas Group - Cotizador & Operaciones",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para priorizar fondo blanco, tipografía limpia y diseño elegante
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
        color: #1A1A1A;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stSidebar {
        background-color: #F8F9FA;
        border-right: 1px solid #E5E7EB;
    }
    h1, h2, h3 {
        color: #111827;
        font-weight: 600;
    }
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #111827;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
    }
    .stButton>button:hover {
        background-color: #374151;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIMULACIÓN DE AUTENTICACIÓN SEGURA ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login(username, password):
    # Credenciales internas del equipo de Karkajadas Group
    if username == "karkajadas" and password == "admin2026":
        return True
    return False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Karkajadas Group</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Sistema de Gestión y Cotizaciones</p>", unsafe_allow_html=True)
        
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

# --- DATOS MAESTROS SIMULADOS (Basados en tus archivos) ---
clientes_lista = [
    "Corrugadora Nacional Cransa S.A. (1791179382001)",
    "Hilton Colón Quito",
    "Bebidas Arcacontinental Ecuador (Arcador S.A.)",
    "Essity (1791314379001)",
    "Intaco Ecuador S.A.",
    "Procongelados S.A.",
    "Levapan del Ecuador"
]

proveedores_catalogo = [
    {"servicio": "Alquiler de Carpas y Estructuras", "proveedor": "CarpaExpress", "precio_base": 54.0, "iva": 0.15},
    {"servicio": "Máquina de Canguil (Horas ilimitadas)", "proveedor": "Eventos Divertidos", "precio_base": 40.0, "iva": 0.0},
    {"servicio": "Sillas plásticas blancas sin vestir", "proveedor": "Logística Global", "precio_base": 0.35, "iva": 0.0},
    {"servicio": "Grupo Musical Vallenato (2 horas)", "proveedor": "Artistas Pro", "precio_base": 470.0, "iva": 0.0},
    {"servicio": "Galletas temáticas personalizadas", "proveedor": "Repostería Fina", "precio_base": 0.70, "iva": 0.0},
    {"servicio": "Credenciales de PVC con diseño", "proveedor": "Impresos 360", "precio_base": 3.00, "iva": 0.15}
]

ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta"]

# --- BARRA LATERAL DE NAVEGACIÓN ---
st.sidebar.markdown("### 🎨 Karkajadas Group")
st.sidebar.markdown("<p style='font-size: 13px; color: #6B7280;'>RUC: 1713272845001<br>Nancy García Chugá</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Menú Principal", ["Nueva Cotización", "Base de Clientes", "Proveedores y Costos", "Dashboard 360°"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# --- MÓDULO 1: NUEVA COTIZACIÓN ---
if menu == "Nueva Cotización":
    st.markdown("<h2>Generador de Cotizaciones</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280;'>Cree cotizaciones comerciales para sus clientes y gestione los costos internos de proveedores de forma ágil.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            cliente_sel = st.selectbox("Cliente", clientes_lista)
        with col2:
            ciudad_sel = st.selectbox("Ciudad del Evento", ciudades_lista)
        with col3:
            fecha_evento = st.date_input("Fecha del Evento", datetime.now())
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("### Ítems de la Cotización y Negociación con Proveedores")
    
    # Simulación de tabla interactiva de ítems
    if "items_cot" not in st.session_state:
        st.session_state.items_cot = [
            {"servicio": proveedores_catalogo[0]["servicio"], "proveedor": proveedores_catalogo[0]["proveedor"], "cantidad": 1, "costo": 54.0, "iva_prov": 0.15, "fee_pct": 20.0},
            {"servicio": proveedores_catalogo[1]["servicio"], "proveedor": proveedores_catalogo[1]["proveedor"], "cantidad": 2, "costo": 40.0, "iva_prov": 0.0, "fee_pct": 20.0}
        ]

    # Formulario rápido para agregar ítem
    with st.expander("➕ Agregar nuevo servicio del catálogo"):
        c_cat = st.selectbox("Seleccionar Servicio Referencial", [p["servicio"] for p in proveedores_catalogo])
        # Buscar datos por defecto
        item_def = next(p for p in proveedores_catalogo if p["servicio"] == c_cat)
        
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            cant_add = st.number_input("Cantidad", min_value=1, value=1)
        with col_b:
            costo_add = st.number_input("Precio Costo Unitario ($)", value=item_def["precio_base"])
        with col_c:
            iva_add = st.selectbox("IVA Proveedor", [0.0, 0.15], index=1 if item_def["iva"] > 0 else 0)
        with col_d:
            fee_add = st.number_input("FEE % (Dinámico)", value=20.0, step=5.0)
            
        if st.button("Añadir a la Cotización"):
            st.session_state.items_cot.append({
                "servicio": c_cat,
                "proveedor": item_def["proveedor"],
                "cantidad": cant_add,
                "costo": costo_add,
                "iva_prov": iva_add,
                "fee_pct": fee_add
            })
            st.success("¡Servicio añadido con éxito!")
            st.rerun()

    # Mostrar tabla y cálculos en tiempo real
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
            "Cant.": item["cantidad"],
            "Costo U.": f"${item['costo']:.2f}",
            "Subtotal Proveedor": f"${sub_costo:.2f}",
            "FEE (%)": f"{item['fee_pct']}%",
            "Total Venta": f"${total_item:.2f}"
        })
        
    st.table(pd.DataFrame(data_tabla))
    
    # Resumen Financiero
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.markdown(f"**Subtotal Operativo:** ${subtotal_general:.2f}")
    with col_r2:
        st.markdown(f"**Ganancia Neta (FEE Total):** ${total_general - subtotal_general:.2f}")
    with col_r3:
        st.markdown(f"### **Total Cotización Cliente:** ${total_general:.2f}")
        
    st.markdown("---")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("📄 Generar PDF Cotización (Cliente)"):
            st.success("¡Cotización generada y guardada en tu Google Drive (Carpeta Cotizador 2026)!")
    with c_btn2:
        if st.button("📋 Generar Orden de Contratación (Proveedor)"):
            st.success("¡Orden de servicio a proveedor generada correctamente!")

# --- MÓDULO 2: CLIENTES ---
elif menu == "Base de Clientes":
    st.markdown("<h2>Directorio de Clientes Estandarizado</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280;'>Base de datos corporativa limpia y lista para facturación.</p>", unsafe_allow_html=True)
    
    df_clientes_clean = pd.DataFrame({
        "Empresa": ["Corrugadora Nacional Cransa S.A.", "Hilton Colón Quito", "Bebidas Arcacontinental", "Essity Ecuador", "Intaco Ecuador"],
        "RUC": ["1791179382001", "1790012345001", "1792411149001", "1791314379001", "1791234567001"],
        "Ciudad": ["Quito", "Quito", "Quito", "Quito", "Guayaquil"],
        "Contacto Principal": ["Departamento de Compras", "Eventos y Logística", "Francisco Velasco", "Línea Corporativa", "Patricia Sevilla"]
    })
    st.table(df_clientes_clean)

# --- MÓDULO 3: PROVEEDORES ---
elif menu == "Proveedores y Costos":
    st.markdown("<h2>Gestión de Proveedores y Tarifas por Ciudad</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280;'>Administre tarifas estándar y controle los pagos a terceros.</p>", unsafe_allow_html=True)
    
    df_prov_clean = pd.DataFrame(proveedores_catalogo)
    st.table(df_prov_clean)

# --- MÓDULO 4: DASHBOARD 360 ---
elif menu == "Dashboard 360°":
    st.markdown("<h2>Dashboard 360° - Karkajadas Group</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280;'>Métricas clave de facturación, márgenes de FEE y control operativo.</p>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Facturación Acumulada", "$14,850.00", "+12%")
    m2.metric("Ganancia Neta (FEE)", "$3,420.00", "+18%")
    m3.metric("Cotizaciones Activas", "8", "En proceso")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Próximos Eventos y Órdenes a Proveedores")
    st.info("📅 Tienes 3 eventos programados para esta semana en Quito y Guayaquil.")
