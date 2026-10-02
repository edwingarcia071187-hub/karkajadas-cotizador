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
    button[kind="secondary"]:hover { 
        background-color: #E2E8F0 !important; 
        color: #1E293B !important;
        border-color: #94A3B8 !important;
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

    div[data-baseweb="select"] > div, input, textarea {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    li[data-baseweb="option"], div[role="option"] {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        transition: all 0.2s ease;
    }
    li[data-baseweb="option"]:hover, div[role="option"]:hover {
        background-color: #EFF6FF !important; 
        color: #1D4ED8 !important; 
        font-weight: bold !important;
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

# --- INICIALIZACIÓN DE ESTADOS Y BASES DE DATOS VIVAS ---
if "nav_menu" not in st.session_state: st.session_state.nav_menu = "Panel principal"
if "modo_ingreso" not in st.session_state: st.session_state.modo_ingreso = "catalogo"
if "items_cot" not in st.session_state: st.session_state.items_cot = []
if "vista_cliente" not in st.session_state: st.session_state.vista_cliente = False
if "cotizaciones_guardadas" not in st.session_state:
    st.session_state.cotizaciones_guardadas = [
        {"codigo": "KG-20261002-001", "evento": "Fiesta fin de año", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-10-02", "estado": "Aprobada", "total": 1250.00},
    ]

ciudades_lista = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]
clientes_lista = ["Corrugadora Nacional Cransa S.A. (1791179382001)", "Siemens Ecuador S.A.", "Hilton Colón Quito", "Bebidas Arcacontinental", "Essity Ecuador", "Intaco Ecuador", "Levapan del Ecuador", "Industrias Lácteas Toni S.A."]

if "proveedores_catalogo" not in st.session_state:
    st.session_state.proveedores_catalogo = [
        {"servicio": "Cabina fotográfica", "proveedor": "SuperDuper Photobooth", "categoria": "Entretenimiento", "ciudad": "Quito", "precio_base": 300.0, "iva": 0.0, "descripcion": "Cabina ilimitada por 2 horas con fotos impresas."},
        {"servicio": "Animador corporativo", "proveedor": "Victor Ramírez", "categoria": "Animación", "ciudad": "Quito", "precio_base": 150.0, "iva": 0.15, "descripcion": "Animación profesional, dinámicas empresariales por 3 horas."},
        {"servicio": "Logística y transporte", "proveedor": "Karkajadas Group", "categoria": "Logística", "ciudad": "Quito", "precio_base": 40.0, "iva": 0.0, "descripcion": "Transporte de equipos y personal dentro del perímetro urbano."},
        {"servicio": "Carpa 6x6 blanca", "proveedor": "Carpas Pichincha", "categoria": "Estructuras", "ciudad": "Quito", "precio_base": 50.0, "iva": 0.15, "descripcion": "Carpa estructural blanca de 6x6 metros con montaje."},
        {"servicio": "Carpa 6x6 transparente", "proveedor": "Eventos VIP UIO", "categoria": "Estructuras", "ciudad": "Quito", "precio_base": 80.0, "iva": 0.15, "descripcion": "Carpa totalmente transparente para eventos nocturnos."},
        {"servicio": "Baby Park", "proveedor": "Karkajadas Group", "categoria": "Infantil", "ciudad": "Quito", "precio_base": 125.0, "iva": 0.0, "descripcion": "Parque infantil seguro para niños de 1 a 4 años."}
    ]

# --- MENÚ LATERAL ---
st.sidebar.markdown("### Karkajadas Group")
if st.sidebar.button("🏠 Panel principal", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Panel principal"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("✨ Nueva cotización", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Nueva cotización"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("📂 Consultar cotizaciones", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Consultar cotizaciones"; st.session_state.vista_cliente = False; st.rerun()
if st.sidebar.button("👥 Clientes y proveedores", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.session_state.vista_cliente = False; st.rerun()

menu = st.session_state.nav_menu

# --- VISTA 1: PANEL PRINCIPAL ---
if menu == "Panel principal":
    st.markdown("<h2 style='color: #0F172A; font-weight: 800;'>Karkajadas Group - Espacio de trabajo ERP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 16px; margin-top: -10px;'>Resumen ejecutivo y gestión operativa</p>", unsafe_allow_html=True)
    
    cots = st.session_state.cotizaciones_guardadas
    ingresos_aprobados = sum(c["total"] for c in cots if c["estado"] == "Aprobada")
    num_aprobadas = len([c for c in cots if c["estado"] == "Aprobada"])
    num_pendientes = len([c for c in cots if c["estado"] in ["Borrador", "Enviada"]])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Ingresos confirmados", f"${ingresos_aprobados:,.2f}")
    m2.metric("✅ Eventos aprobados", f"{num_aprobadas} eventos")
    m3.metric("⏳ Cotizaciones pendientes", f"{num_pendientes} en gestión")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🚀 Accesos rápidos")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("➕ Crear nueva cotización", use_container_width=True, type="primary"): st.session_state.nav_menu = "Nueva cotización"; st.rerun()
    with b2:
        if st.button("📂 Consultar archivo histórico", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Consultar cotizaciones"; st.rerun()
    with b3:
        if st.button("👥 Base de datos (terceros)", use_container_width=True, type="secondary"): st.session_state.nav_menu = "Directorios"; st.rerun()
            
    st.markdown("<hr style='margin: 20px 0; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("#### 📅 Cronograma de próximos eventos (aprobados)")
    eventos_aprobados = [cot for cot in cots if cot["estado"] == "Aprobada"]
    
    if eventos_aprobados:
        df_eventos = pd.DataFrame(eventos_aprobados)[["fecha", "evento", "cliente", "codigo", "total"]]
        df_eventos.columns = ["Fecha confirmada", "Nombre del evento", "Cliente corporativo", "Cód. cotización", "Monto total ($)"]
        df_eventos["Monto total ($)"] = df_eventos["Monto total ($)"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_eventos, use_container_width=True)
    else:
        st.info("No hay eventos confirmados para mostrar en este momento.")

# --- VISTA 2: NUEVA COTIZACIÓN ---
elif menu == "Nueva cotización":
    st.markdown("<h3>Generador de cotizaciones</h3>", unsafe_allow_html=True)
    codigo_sugerido = f"KG-{datetime.now().strftime('%Y%m%d')}-00{len(st.session_state.cotizaciones_guardadas)+1}"
    
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 2.5, 1.5, 1.5])
    with col1: cod_cotizacion = st.text_input("Código de cotización", value=codigo_sugerido)
    with col2: nombre_evento = st.text_input("Nombre del evento", placeholder="Ej. Fiesta de integración")
    with col3: cliente_sel = st.selectbox("Cliente", clientes_lista)
    with col4: fecha_gral = st.date_input("Fecha general", datetime.now()) 
    with col5: estado_cot = st.selectbox("Estado", ["Borrador", "Enviada", "Aprobada", "Cancelada"])
        
    st.markdown("---")
    
    with st.expander("🔍 Añadir proveedores y servicios", expanded=True):
        st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Seleccione el método de ingreso:</p>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Buscar en catálogo existente", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "catalogo" else "secondary"):
                st.session_state.modo_ingreso = "catalogo"
                st.rerun()
        with col_btn2:
            if st.button("✨ Crear servicio personalizado", use_container_width=True, type="primary" if st.session_state.modo_ingreso == "personalizado" else "secondary"):
                st.session_state.modo_ingreso = "personalizado"
                st.rerun()
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        if st.session_state.modo_ingreso == "catalogo":
            st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Paso 1: Buscar disponibilidad</p>", unsafe_allow_html=True)
            f1, f2 = st.columns([1, 2])
            with f1: ciudad_filtro = st.selectbox("Ciudad del servicio", ciudades_lista, index=0)
            with f2: palabra_busqueda = st.text_input("Palabra clave (opcional)", placeholder="Ej. carpa, animador...")
            
            resultados = []
            for p in st.session_state.proveedores_catalogo:
                if p["ciudad"] == ciudad_filtro:
                    if palabra_busqueda == "" or \
                       palabra_busqueda.lower() in p["servicio"].lower() or \
                       palabra_busqueda.lower() in p["proveedor"].lower() or \
                       palabra_busqueda.lower() in p["categoria"].lower() or \
                       palabra_busqueda.lower() in p.get("descripcion", "").lower():
                        resultados.append(p)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not resultados:
                st.warning(f"No se encontraron proveedores para '{palabra_busqueda}' en {ciudad_filtro}.")
            else:
                st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Paso 2: Seleccionar proveedor encontrado</p>", unsafe_allow_html=True)
                opciones_str = []
                for r in resultados:
                    iva_str = f"IVA {int(r['iva']*100)}%" if r['iva'] > 0 else "IVA 0%"
                    desc = r.get("descripcion", "Sin descripción")
                    opciones_str.append(f"{r['proveedor']} ➔ {r['servicio']} | {iva_str} | 📝 {desc}")
                
                seleccion = st.selectbox("Despliega para ver las opciones y elegir:", opciones_str)
                item_seleccionado = resultados[opciones_str.index(seleccion)]
                
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Paso 3: Definir cantidades y valores finales</p>", unsafe_allow_html=True)
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
            st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Paso 1: Ingresar datos del nuevo servicio/proveedor</p>", unsafe_allow_html=True)
            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1: nuevo_proveedor = st.text_input("Nombre del proveedor *")
            with nc2: nuevo_servicio = st.text_input("Servicio ofrecido *")
            with nc3: nueva_ciudad = st.selectbox("Ciudad del proveedor", ciudades_lista)
            with nc4: nueva_categoria = st.text_input("Categoría (ej. alimentos, audiovisual)")
            
            nueva_descripcion = st.text_area("Breve descripción / detalles técnicos (opcional)", height=68)
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 14px; font-weight: bold; color: #1E40AF;'>Paso 2: Definir valores para esta cotización</p>", unsafe_allow_html=True)
            ca, cb, cc, cd, ce = st.columns(5)
            with ca: fecha_item = st.date_input("Fecha específica", value=fecha_gral)
            with cb: cant_add = st.number_input("Cantidad a contratar", min_value=1, value=1)
            with cc: costo_add = st.number_input("Costo unit. negociado ($)", value=0.00, format="%.2f")
            with cd: iva_add = st.selectbox("Aplica IVA prov.", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x * 100)}%")
            with ce: fee_add = st.number_input("Margen / FEE (%)", value=20.00, step=5.00, format="%.2f")
            
            st.markdown("<br>", unsafe_allow_html=True)
            guardar_bd = st.checkbox("💾 Guardar este nuevo proveedor permanentemente en el catálogo maestro", value=True)
            
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
                            "servicio": nuevo_servicio, "proveedor": nuevo_proveedor,
                            "categoria": nueva_categoria if nueva_categoria else "Otros",
                            "ciudad": nueva_ciudad, "precio_base": costo_add, "iva": iva_add,
                            "descripcion": nueva_descripcion if nueva_descripcion else "Sin descripción"
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
            if st.button("💾 Guardar cotización interna", type="secondary"):
                st.session_state.cotizaciones_guardadas.append({
                    "codigo": cod_cotizacion, "evento": nombre_evento, "cliente": cliente_sel, 
                    "fecha": str(fecha_gral), "estado": estado_cot, "total": total_general
                })
                st.session_state.items_cot = [] 
                st.success("Cotización guardada exitosamente.")
        with btn2:
            if st.button("📄 Generar vista cliente (limpia)", type="primary"):
                st.session_state.vista_cliente = True
                st.rerun()

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

# --- VISTA 3: CONSULTAR COTIZACIONES ---
elif menu == "Consultar cotizaciones":
    st.markdown("<h3>Registro de cotizaciones</h3>", unsafe_allow_html=True)
    if st.session_state.cotizaciones_guardadas:
        st.dataframe(pd.DataFrame(st.session_state.cotizaciones_guardadas), use_container_width=True)
    else:
        st.write("No hay cotizaciones registradas aún.")

# --- VISTA 4: DIRECTORIOS ---
elif menu == "Directorios":
    st.markdown("<h3>Base de datos oficial</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Clientes", "Proveedores"])
    with t1: st.dataframe(pd.DataFrame({"Cliente": clientes_lista}), use_container_width=True)
    with t2: st.dataframe(pd.DataFrame(st.session_state.proveedores_catalogo), use_container_width=True)
