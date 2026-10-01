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

# --- ESTILOS CSS: OPTIMIZACIÓN, CONTRASTE Y TAMAÑO DE TOTALES ---
st.markdown("""
    <style>
    .stApp, .main, header { background-color: #FFFFFF !important; color: #0F172A !important; }
    
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 14px;
        border: 2px solid #0F172A !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton>button:hover { background-color: #0F172A !important; color: #FFFFFF !important; }
    .stButton>button p { color: inherit !important; }
    
    div[data-baseweb="select"] > div, input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* TOTAL DESTACADO Y GRANDE */
    .total-box {
        padding: 10px 20px;
        border-radius: 8px;
        background-color: #F1F5F9;
        border-left: 6px solid #0F172A;
        font-size: 36px !important; /* Letra grande igual a las métricas */
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .total-label {
        font-size: 14px;
        color: #64748B;
        display: block;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: -5px;
    }
    
    /* Ajuste de márgenes superiores */
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
if st.sidebar.button("🏠 Panel Principal"): st.session_state.nav_menu = "Panel Principal"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("✨ Nueva Cotización"): st.session_state.nav_menu = "Nueva Cotización"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("📂 Consultar Cotizaciones"): st.session_state.nav_menu = "Consultar Cotizaciones"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("👥 Clientes y Proveedores"): st.session_state.nav_menu = "Directorios"; st.session_state.vista_cliente = False; st.rerun()

menu = st.session_state.nav_menu

# --- VISTA 1: PANEL PRINCIPAL ---
if menu == "Panel Principal":
    st.markdown("<h2>Karkajadas Group - Workspace</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ Crear Nueva Cotización"): st.session_state.nav_menu = "Nueva Cotización"; st.rerun()
    with c2:
        if st.button("📂 Ver Cotizaciones Guardadas"): st.session_state.nav_menu = "Consultar Cotizaciones"; st.rerun()
    with c3:
        if st.button("📊 Reportes y Dashboard"): st.success("Módulo de reportes en construcción.")
            
    st.markdown("---")
    st.markdown("### 📅 Eventos de esta Semana (Aprobados)")
    eventos_aprobados = [cot for cot in st.session_state.cotizaciones_guardadas if cot["estado"] == "Aprobada"]
    if eventos_aprobados:
        for ev in eventos_aprobados:
            st.info(f"✅ **{ev['fecha']}** | Evento: {ev['evento']} | Cliente: {ev['cliente']} | Código: {ev['codigo']} | Monto: ${ev['total']:.2f}")
    else:
        st.write("No hay eventos confirmados para esta semana.")

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva Cotización":
    st.markdown("<h3>Generador de Cotizaciones</h3>", unsafe_allow_html=True)
    
    codigo_sugerido = f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    
    # 1. LAYOUT SUPERIOR REESTRUCTURADO (Con Nombre de Evento)
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
    with col1: cod_cotizacion = st.text_input("Código Cotización", value=codigo_sugerido)
    with col2: nombre_evento = st.text_input("Nombre del Evento", placeholder="Ej. Fiesta Fin de Año")
    with col3: cliente_sel = st.selectbox("Cliente", clientes_lista)
    with col4: fecha_gral = st.date_input("Fecha General", datetime.now()) # Calendario Restaurado
    with col5: estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"])
        
    st.markdown("---")
    
    # 2. SECCIÓN DE ÍTEMS
    with st.expander("➕ Añadir servicio (con fecha y ciudad específica)", expanded=True):
        c_cat = st.selectbox("Servicio del Catálogo", [p["servicio"] for p in proveedores_catalogo])
        item_def = next(p for p in proveedores_catalogo if p["servicio"] == c_cat)
        
        ca, cb, cc, cd, ce, cf = st.columns(6)
        with ca: cant_add = st.number_input("Cant.", min_value=1, value=1)
        with cb: costo_add = st.number_input("Costo Unit. Prov ($)", value=item_def["precio_base"])
        with cc: fecha_item = st.date_input("Fecha", value=fecha_gral) # Calendario Restaurado
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

    # 3. TABLA INTERNA Y TOTALES
    if st.session_state.items_cot:
        st.markdown("#### Ítems Actuales en la Cotización (Vista Interna)")
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
                st.session_state.items_cot.pop(idx); st.rerun()
            st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)
            
        # TOTALES GRANDES
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

    # 4. VISTA CLIENTE (SIN FEES)
    if st.session_state.vista_cliente and st.session_state.items_cot:
        st.markdown("---")
        st.markdown(f"### 📄 Cotización Comercial: {nombre_evento}")
        st.write(f"**Cliente:** {cliente_sel} | **Código:** {cod_cotizacion} | **Fecha:** {fecha_gral}")
        
        datos_cliente = []
        for item in st.session_state.items_cot:
            # Cálculo matemático limpio para el cliente
            costo_real = item["costo"] * (1 + item["iva_prov"])
            fee_valor = costo_real * (item["fee_pct"] / 100.0)
            total_linea = (costo_real + fee_valor) * item["cantidad"]
            precio_unitario_cliente = total_linea / item["cantidad"] # Oculta el FEE prorrateándolo
            
            datos_cliente.append({
                "Servicio": item["servicio"],
                "Ciudad": item["ciudad"],
                "Fecha": item["fecha"],
                "Cant.": item["cantidad"],
                "V. Unitario": f"${precio_unitario_cliente:.2f}",
                "V. Total": f"${total_linea:.2f}"
            })
            
        df_cliente = pd.DataFrame(datos_cliente)
        st.table(df_cliente)
        st.markdown(f"<h3 style='text-align: right;'>TOTAL: ${total_general:.2f}</h3>", unsafe_allow_html=True)
        st.info("💡 Puedes seleccionar esta tabla, copiarla y pegarla directamente en un correo o Excel para enviarla al cliente.")

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
