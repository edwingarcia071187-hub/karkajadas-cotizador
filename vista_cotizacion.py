"""Nueva cotización."""
import pandas as pd
import streamlit as st
from datetime import date
from constantes import CIUDADES, IVA_CLIENTE, NUEVO_CLIENTE
from directorios import asegurar_proveedor, crear_cliente, faltantes_proveedor, form_cliente, validar_cliente
from documentos import generar_pdf
from utilidades import _k, calcular_linea, dialogo_editar, dialogo_salida, encabezado_estandar, estado_formulario, guardar_cotizacion, proveedor_de, selector_ciudad, siguiente_codigo, total_cliente

ss = st.session_state


def mostrar(menu):
    items = ss.items_cot
    tot_head = total_cliente(items)

    if ss.pop("confirmar_salida", False):
        dialogo_salida()
    def _monto():
        st.markdown(f"<div class='monto-badge'><div class='monto-label'>Monto estimado</div><div class='monto-valor'>${tot_head:,.2f}</div></div>", unsafe_allow_html=True)
    encabezado_estandar("cot", "Gestión de cotizaciones", "Datos del evento, servicios y totales", derecha=_monto)

    activa = ss.cotizacion_activa
    lista_cli = [c["empresa"] for c in ss.clientes_catalogo] + [NUEVO_CLIENTE]
    ESTADOS_COT = ["Borrador", "Enviada", "Aprobada", "Cancelada"]
    if "cliente_pendiente" in ss:   # cliente recién creado: queda seleccionado
        ss[_k("cli")] = ss.pop("cliente_pendiente")
    # el valor inicial solo se pasa la primera vez (después manda lo que el usuario haya elegido)
    ini_cli = {} if _k("cli") in ss else {"index": lista_cli.index(activa["cliente"]) if activa and activa["cliente"] in lista_cli else 0}
    ini_est = {} if _k("est") in ss else {"index": ESTADOS_COT.index(activa["estado"]) if activa else 0}
    fecha_def = date.fromisoformat(activa["fecha"]) if activa else date.today()

    with st.container(border=True, key="card_5"):
        st.markdown("<div class='section-title'>Información del evento</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c6, c5 = st.columns([1.4, 1.8, 2.3, 1.4, 1.1, 1.4])
        cod_cotizacion = c1.text_input("Referencia", value=activa["codigo"] if activa else siguiente_codigo(), key=_k("cod"))
        nombre_evento = c2.text_input("Nombre del evento", value=activa["evento"] if activa else "", key=_k("ev"))
        cliente_sel = c3.selectbox("Cuenta de cliente", lista_cli, key=_k("cli"), **ini_cli)
        fecha_gral = c4.date_input("Fecha", fecha_def, key=_k("fec"))
        invitados_cot = c6.number_input("Invitados", min_value=0, step=10, value=int(activa.get("invitados", 0)) if activa else 0, key=_k("inv"),
                                        help="Cantidad aproximada de invitados; pasa a las fichas de proveedores")
        estado_cot = c5.selectbox("Estado", ESTADOS_COT, key=_k("est"), **ini_est)

    if ss.cot_base is None:   # primera vez que se pinta el formulario: esto es "sin cambios"
        ss.cot_base = estado_formulario()

    if cliente_sel == NUEVO_CLIENTE:
        with st.container(border=True, key="card_6"):
            nuevo = form_cliente("nc", "<div class='section-title' style='color:#059669; border-color:#059669;'>Apertura de cuenta corporativa</div>")
            if nuevo:
                err = validar_cliente(nuevo)
                if err:
                    st.error(err)
                else:
                    crear_cliente(nuevo)
                    ss.cliente_pendiente = nuevo["empresa"]
                    st.rerun()

    with st.container(border=True, key="card_7"), st.expander(f"AÑADIR SERVICIOS  ·  {len(items)} en la cotización", expanded=True):
        tab_cat, tab_man = st.tabs(["Seleccionar del catálogo", "Ingreso manual"])

        with tab_cat:
            f1, f2, f3 = st.columns([1.1, 1.1, 1.8])
            ciu_f = f1.selectbox("Ciudad", CIUDADES, index=0, key="cat_ciu")
            en_ciudad = [p for p in ss.proveedores_catalogo if p["ciudad"] == ciu_f]
            cat_f = f2.selectbox("Categoría", ["Todas"] + sorted({p.get("categoria", "") for p in en_ciudad if p.get("categoria")}), key="cat_cat")
            pal_b = f3.text_input("Buscar", placeholder="Proveedor o servicio...", key="cat_bus").strip().lower()

            res = [p for p in en_ciudad
                   if (cat_f == "Todas" or p.get("categoria") == cat_f)
                   and (not pal_b or pal_b in f"{p['servicio']} {p['proveedor']}".lower())]
            res.sort(key=lambda p: (p["servicio"].lower(), p["precio_base"]))   # mismo servicio junto y de menor a mayor costo
            if not res:
                st.info(f"No hay servicios en {ciu_f} con ese filtro. Puedes registrarlos en la pestaña «Ingreso manual».")
            else:
                t_izq, t_der = st.columns([2.05, 1], gap="medium")
                df_cat = pd.DataFrame([{
                    "Servicio": r["servicio"], "Proveedor": r["proveedor"],
                    "Costo ($)": float(r["precio_base"]), "IVA": f"{int(r['iva'] * 100)}%"} for r in res])
                with t_izq:
                    ev_cat = st.dataframe(
                        df_cat, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row",
                        key=f"cat_tbl_{ciu_f}_{cat_f}_{pal_b}", height=min(35 * (len(df_cat) + 1) + 3, 215),
                        column_config={"Servicio": st.column_config.TextColumn(width=165), "Proveedor": st.column_config.TextColumn(width=150),
                                       "Costo ($)": st.column_config.NumberColumn(format="$%.2f", width=75),
                                       "IVA": st.column_config.TextColumn(width=50)})
                    st.caption(f"{len(res)} servicio(s) en {ciu_f}. Del mismo servicio, primero el más económico.")
                item_sel = res[ev_cat.selection.rows[0]] if ev_cat.selection.rows else None
                with t_der:
                    if not item_sel:
                        st.markdown("<div style='padding:14px; border:1px dashed #C9D3E0; border-radius:8px; color:#64748B; font-size:0.9rem; margin-top:4px;'>Elige un servicio de la tabla (recuadro de la izquierda) para completar los datos.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding:8px 12px; background:#EEF2F7; border-left:5px solid #1E3A8A; border-radius:6px; font-size:0.88rem; color:#0F172A; line-height:1.35;'>"
                                    f"<b>{item_sel['servicio']}</b><br>{item_sel['proveedor']} · {ciu_f}"
                                    + ("<br><span style='color:#B45309;'>Ficha del proveedor pendiente</span>" if faltantes_proveedor(proveedor_de(item_sel["proveedor"])) else "") + "</div>", unsafe_allow_html=True)
                        d1, d2 = st.columns([1.5, 1])
                        f_it = d1.date_input("Fecha", value=fecha_gral)
                        can_it = d2.number_input("Cantidad", min_value=1, value=1)
                        d3, d4, d5 = st.columns([1.05, 1.2, 1])
                        cos_it = d3.number_input("Costo ($)", value=float(item_sel["precio_base"]))
                        iva_it = d4.selectbox("IVA", [0.0, 0.15], index=1 if item_sel["iva"] > 0 else 0, format_func=lambda x: f"{int(x*100)}%")
                        fee_it = d5.number_input("Margen", value=20.00, step=5.00, format="%.2f")
                        if st.button("Agregar a la cotización", type="primary", use_container_width=True, key="add_cat"):
                            items.append({"servicio": item_sel["servicio"], "proveedor": item_sel["proveedor"], "ciudad": ciu_f, "fecha": str(f_it),
                                          "cantidad": can_it, "costo": cos_it, "iva_prov": iva_it, "fee_pct": fee_it})
                            st.rerun()

        with tab_man:
            nc1, nc2, nc3, nc4 = st.columns(4)
            n_pro = nc1.text_input("Proveedor *")
            n_ser = nc2.text_input("Servicio *")
            n_ciu = selector_ciudad(nc3, "Ciudad op.", "mc_c")
            n_cat = nc4.text_input("Categoría")
            ca, cb, cc, cd, ce, cf = st.columns([1.3, 0.8, 1.1, 0.9, 1.0, 1.4], vertical_alignment="bottom")
            f_it_m = ca.date_input("Fecha de servicio", value=fecha_gral, key="mc_f")
            can_it_m = cb.number_input("Cantidad", min_value=1, value=1, key="mc_ca")
            cos_it_m = cc.number_input("Costo unit. ($)", value=0.00, format="%.2f", key="mc_co")
            iva_it_m = cd.selectbox("IVA prov.", [0.0, 0.15], index=1, format_func=lambda x: f"{int(x*100)}%", key="mc_i")
            fee_it_m = ce.number_input("Margen (%)", value=20.00, step=5.00, format="%.2f", key="mc_ma")
            g_bd = st.checkbox("Guardar en directorio", value=True)
            if cf.button("Agregar", type="primary", use_container_width=True, key="add_man"):
                if n_pro.strip() and n_ser.strip():
                    items.append({"servicio": n_ser, "proveedor": n_pro, "ciudad": n_ciu, "fecha": str(f_it_m),
                                  "cantidad": can_it_m, "costo": cos_it_m, "iva_prov": iva_it_m, "fee_pct": fee_it_m})
                    if g_bd:
                        if asegurar_proveedor(n_pro.strip(), n_ciu, n_cat or "General"):
                            ss.aviso_pendiente = f"Proveedor «{n_pro.strip()}» creado. Complétalo luego en Directorios."
                        ss.proveedores_catalogo.append({"servicio": n_ser, "proveedor": n_pro.strip(), "categoria": n_cat or "General", "ciudad": n_ciu,
                                                        "precio_base": cos_it_m, "iva": iva_it_m, "descripcion": "Manual"})
                    st.rerun()
                else:
                    st.error("Proveedor y servicio requeridos.")

    if items:
        with st.container(border=True, key="card_8"):
            st.markdown("<div class='section-title'>Estructura de costos</div>", unsafe_allow_html=True)
            # Una línea por servicio, una columna por dato. Los 4 últimos anchos son ✎ ↑ ↓ ✕ (botones compactos)
            ANCHOS = [2.0, 2.2, 1.15, 0.95, 0.6, 1.0, 0.6, 0.8, 1.0, 1.1, 0.38, 0.38, 0.38, 0.38]
            TITULOS = ["PROVEEDOR", "SERVICIO", "FECHA", "CIUDAD", "CANT.", "COSTO U.", "IVA", "MARGEN %", "MARGEN $", "SUBTOTAL", "", "", "", ""]
            NUM = {4, 5, 6, 7, 8, 9}   # columnas numéricas: alineadas a la derecha

            s_prov = t_fee = s_com = 0.0
            accion = None  # (tipo, idx): se ejecuta una sola vez al final, fuera del bucle
            with st.container(key="tabla_costos"):
                with st.container(key="costos_head"):
                    hx = st.columns(ANCHOS, vertical_alignment="center")
                    for i, t in enumerate(TITULOS):
                        hx[i].markdown(f"<div class='col-head{' num' if i in NUM else ''}'>{t}</div>", unsafe_allow_html=True)

                for idx, item in enumerate(items):
                    c_iva, f_val, p_ven = calcular_linea(item)
                    s_prov += c_iva; t_fee += f_val; s_com += p_ven

                    valores = [
                        f"<b>{item['proveedor']}</b>", item["servicio"], item["fecha"], item["ciudad"],
                        f"{item['cantidad']}", f"${item['costo']:,.2f}", f"{int(item['iva_prov'] * 100)}%",
                        f"{item['fee_pct']:.0f}%", f"<span class='pos'>+${f_val:,.2f}</span>", f"<b>${p_ven:,.2f}</b>",
                    ]
                    cx = st.columns(ANCHOS, vertical_alignment="center")
                    for i, v in enumerate(valores):
                        cx[i].markdown(f"<div class='cell{' num' if i in NUM else ''}'>{v}</div>", unsafe_allow_html=True)
                    if cx[10].button("✎", key=f"edit_{idx}", help="Editar este servicio"):
                        accion = ("edit", idx)
                    if cx[11].button("↑", key=f"mv_up_{idx}", disabled=idx == 0, help="Subir"):
                        accion = ("up", idx)
                    if cx[12].button("↓", key=f"mv_dn_{idx}", disabled=idx == len(items) - 1, help="Bajar"):
                        accion = ("dn", idx)
                    if cx[13].button("✕", key=f"del_{idx}", help="Eliminar"):
                        accion = ("del", idx)

            if accion and accion[0] == "edit":
                dialogo_editar(accion[1])
            elif accion:
                tipo, i = accion
                if tipo == "del":
                    items.pop(i)
                else:
                    j = i - 1 if tipo == "up" else i + 1
                    items[i], items[j] = items[j], items[i]
                st.rerun()

            iva_cli = s_com * IVA_CLIENTE
            t_cli = s_com + iva_cli
            # Barra inferior fija: totales y acciones siempre a la vista aunque la cotización sea larga
            with st.container(key="barra_total"):
                cm1, cm2, ci, c_acc = st.columns([1.1, 1.1, 1.7, 1.15], vertical_alignment="center")
                cm1.markdown(f"<div class='metric-tile'><div class='internal-metrics'>Costos operativos</div><div class='internal-metrics-value'>${s_prov:,.2f}</div></div>", unsafe_allow_html=True)
                cm2.markdown(f"<div class='metric-tile ganancia'><div class='internal-metrics'>Rentabilidad</div><div class='internal-metrics-value'>${t_fee:,.2f}</div></div>", unsafe_allow_html=True)
                ci.markdown(f"<div class='invoice-container'><div class='invoice-row'><span>Subtotal</span><span>${s_com:,.2f}</span></div><div class='invoice-row'><span>IVA 15%</span><span>${iva_cli:,.2f}</span></div><div class='invoice-total'><span>TOTAL INVERSIÓN</span><span>${t_cli:,.2f}</span></div></div>", unsafe_allow_html=True)
                c_save = c_pdf = c_acc
                if c_save.button("Guardar cotización", use_container_width=True, type="primary", key="btn_save"):
                    if guardar_cotizacion(activa, cod_cotizacion, nombre_evento, cliente_sel, fecha_gral, estado_cot, t_cli, invitados_cot):
                        st.toast("Cotización guardada. Ya puedes generar el PDF.")

                # El PDF se habilita cuando la cotización está guardada y sin cambios pendientes (así siempre refleja lo guardado)
                guardada = ss.cotizacion_activa
                pdf, ayuda = None, "Guarda la cotización para generar el PDF."
                if guardada and estado_formulario() == ss.cot_base:
                    try:
                        cli_pdf = next((c for c in ss.clientes_catalogo if c["empresa"] == guardada["cliente"]), None)
                        pdf, ayuda = generar_pdf(guardada, cli_pdf), "Descargar la cotización en PDF."
                    except ImportError:
                        ayuda = "Falta instalar reportlab (agrégalo a requirements.txt)."
                elif guardada:
                    ayuda = "Hay cambios sin guardar: guarda la cotización para actualizar el PDF."
                c_pdf.download_button("Generar PDF", data=pdf or b"", file_name=f"{(guardada or {}).get('codigo', 'cotizacion')}.pdf",
                                      mime="application/pdf", disabled=pdf is None, use_container_width=True, key="btn_pdf", help=ayuda)
