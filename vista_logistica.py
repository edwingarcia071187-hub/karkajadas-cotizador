"""Logística: inventario, kits, órdenes de despacho y movimientos."""
from datetime import datetime
import pandas as pd
import streamlit as st
from constantes import EMPRESA
from logistica_datos import (CATEGORIAS, ESTADOS_EN_USO, ESTADOS_HISTORIAL, TIPOS, TIPOS_SERVICIO, UNIDADES, ajustar_stock, ahora, despachar,
                             disponible, donde_esta, estado_stock, fuera, item_por_codigo, lineas_para, nombre_item, nueva_orden,
                             pdf_despacho, pdf_etiquetas, qr_svg, reservado, siguiente_codigo_item, url_item, url_orden, codigo_orden)
from utilidades import dinero, encabezado_estandar, fmt_fecha

ss = st.session_state
SECCIONES_LOG = ["Inventario", "Kits", "Órdenes de despacho", "Movimientos"]
COLOR_ESTADO = {"Preparación": "#B8913F", "Despachada": "#5B7DB1", "En evento": "#2C8C84", "Recibida": "#7A68B5", "Cerrada": "#64748B"}


def _kpi(titulo, valor, color="#94A3B8"):
    return (f"<div style='background:#FFFFFF; border:1px solid #DCE3EC; border-left:5px solid {color}; border-radius:10px; padding:10px 14px;'>"
            f"<div style='font-size:0.7rem; font-weight:700; letter-spacing:0.06em; color:#64748B; text-transform:uppercase;'>{titulo}</div>"
            f"<div style='font-size:1.45rem; font-weight:800; color:#0F172A; line-height:1.2;'>{valor}</div></div>")


def _chip(estado):
    c = COLOR_ESTADO.get(estado, "#64748B")
    return (f"<span style='background:{c}22; color:{c}; border:1px solid {c}66; border-radius:999px; padding:2px 12px; "
            f"font-size:0.8rem; font-weight:700;'>{estado}</span>")


def mostrar(menu):
    encabezado_estandar("log", "Logística", "Inventario, kits y órdenes de despacho de bodega")
    ss.setdefault("log_seccion", "Inventario")
    st.segmented_control("Sección", SECCIONES_LOG, key="log_seccion", label_visibility="collapsed")
    seccion = ss.get("log_seccion") or "Inventario"
    if seccion == "Inventario":
        _inventario()
    elif seccion == "Kits":
        _kits()
    elif seccion == "Órdenes de despacho":
        _ordenes()
    else:
        _movimientos()


# =============================================================================== inventario
@st.dialog("Nuevo artículo")
def _dialogo_nuevo():
    with st.form("form_nuevo_item"):
        nombre = st.text_input("Nombre del artículo")
        c1, c2, c3 = st.columns(3)
        cat = c1.selectbox("Categoría", CATEGORIAS)
        uni = c2.selectbox("Unidad", UNIDADES)
        tipo = c3.selectbox("Tipo", TIPOS, help="Retornable: vuelve a bodega después del evento. Consumible: se gasta (globos, cinta, pilas).")
        c4, c5, c6 = st.columns(3)
        stock = c4.number_input("Stock inicial", min_value=0, step=1, value=0)
        minimo = c5.number_input("Stock mínimo", min_value=0, step=1, value=0)
        valor = c6.number_input("Valor unitario ($)", min_value=0.0, step=0.5, format="%.2f")
        ubi = st.text_input("Ubicación en bodega", placeholder="Ej.: Estante A-1")
        if st.form_submit_button("Guardar artículo", type="primary", use_container_width=True):
            if not nombre.strip():
                st.error("Escribe el nombre del artículo.")
            else:
                cod = siguiente_codigo_item()
                ss.inventario.append({"codigo": cod, "nombre": nombre.strip(), "categoria": cat, "unidad": uni, "tipo": tipo, "total": 0, "minimo": int(minimo),
                                      "valor": float(valor), "ubicacion": ubi.strip(), "foto": None, "notas": "", "actualizado": ahora()})
                ajustar_stock(cod, int(stock), "Ingreso inicial", "Artículo nuevo")
                ss.log_item = cod
                st.rerun()


def _inventario():
    inv = ss.inventario
    valor_total = sum(i["total"] * i["valor"] for i in inv)
    bajos = [i for i in inv if estado_stock(i) != "Normal"]
    afuera = sum(fuera(i["codigo"]) for i in inv)
    k = st.columns(4)
    k[0].markdown(_kpi("Artículos", len(inv)), unsafe_allow_html=True)
    k[1].markdown(_kpi("Valor del inventario", dinero(valor_total), "#5B7DB1"), unsafe_allow_html=True)
    k[2].markdown(_kpi("Bajo el mínimo", len(bajos), "#B5675F" if bajos else "#94A3B8"), unsafe_allow_html=True)
    k[3].markdown(_kpi("Unidades en eventos", afuera, "#2C8C84"), unsafe_allow_html=True)
    st.write("")

    with st.container(border=True, key="card_log_tabla"):
        f1, f2, f3, f4 = st.columns([2.2, 1.4, 1.2, 1.4], vertical_alignment="bottom")
        texto = f1.text_input("Buscar", placeholder="Nombre o código", key="log_buscar")
        cat = f2.selectbox("Categoría", ["Todas"] + CATEGORIAS, key="log_cat")
        tipo = f3.selectbox("Tipo", ["Todos"] + TIPOS, key="log_tipo")
        solo_bajos = f4.toggle("Solo bajo el mínimo", key="log_bajos")
        filas = []
        for i in inv:
            if texto and texto.lower() not in (i["nombre"] + i["codigo"]).lower():
                continue
            if cat != "Todas" and i["categoria"] != cat or tipo != "Todos" and i["tipo"] != tipo:
                continue
            est = estado_stock(i)
            if solo_bajos and est == "Normal":
                continue
            c = i["codigo"]
            filas.append({"Código": c, "Artículo": i["nombre"], "Categoría": i["categoria"], "Tipo": i["tipo"], "Unidad": i["unidad"], "Stock total": i["total"],
                          "En eventos": fuera(c), "Apartado": reservado(c), "Disponible": disponible(c), "Mínimo": i["minimo"],
                          "Valor unitario": dinero(i["valor"]), "Valor total": dinero(i["total"] * i["valor"]), "Ubicación": i["ubicacion"], "Estado": est})
        if filas:
            st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True, height=min(35 * (len(filas) + 1) + 3, 420))
        else:
            st.info("No hay artículos con ese filtro.")
        b1, b2, _ = st.columns([1.2, 1.6, 4])
        if b1.button("Nuevo artículo", key="log_nuevo", use_container_width=True, type="primary"):
            _dialogo_nuevo()
        b2.download_button("Etiquetas QR (PDF)", data=pdf_etiquetas(inv), file_name="Etiquetas_QR_inventario.pdf", mime="application/pdf", key="log_etq", use_container_width=True)

    codigos = [i["codigo"] for i in inv]
    if ss.get("log_item") not in codigos:
        ss.log_item = codigos[0]
    st.selectbox("Ver el detalle de un artículo", codigos, key="log_item", format_func=lambda c: f"{c} · {nombre_item(c)}")
    _detalle_item(item_por_codigo(ss.log_item))


def _detalle_item(it):
    cod = it["codigo"]
    with st.container(border=True, key="card_log_det"):
        c_foto, c_dat, c_qr = st.columns([1.3, 2.6, 1.3])
        with c_foto:
            if it["foto"]:
                st.image(it["foto"], use_container_width=True)
            else:
                st.markdown("<div style='height:150px; border:1px dashed #CBD5E1; border-radius:10px; display:flex; align-items:center; justify-content:center; "
                            "color:#94A3B8; font-size:0.85rem;'>Sin foto de referencia</div>", unsafe_allow_html=True)
            sub = st.file_uploader("Foto de referencia", type=["png", "jpg", "jpeg"], key=f"foto_{cod}", label_visibility="collapsed",
                                   help="En el celular puedes tomar la foto directamente.")
            if sub is not None and it["foto"] != sub.getvalue():
                it["foto"] = sub.getvalue()
                it["actualizado"] = ahora()
                st.rerun()
        with c_dat:
            st.markdown(f"<div style='font-size:1.25rem; font-weight:800; color:#0F172A;'>{it['nombre']}</div>"
                        f"<div style='color:#64748B; font-size:0.9rem; margin-bottom:8px;'>{cod} · {it['categoria']} · {it['tipo']} · {it['unidad']} · {it['ubicacion'] or 'Sin ubicación'}</div>",
                        unsafe_allow_html=True)
            m = st.columns(4)
            m[0].metric("Stock total", it["total"])
            m[1].metric("En eventos", fuera(cod))
            m[2].metric("Apartado", reservado(cod))
            m[3].metric("Disponible", disponible(cod))
            st.caption(f"Valor unitario {dinero(it['valor'])} · valor total {dinero(it['total'] * it['valor'])} · stock mínimo {it['minimo']} · "
                       f"{estado_stock(it)} · actualizado {it['actualizado']}".replace("$", "\\$"))
        with c_qr:
            st.markdown(f"<div style='text-align:center;'>{qr_svg(url_item(cod), 140)}</div>", unsafe_allow_html=True)
            st.caption("Escanea con la cámara del celular para abrir este artículo.")
            st.download_button("Etiqueta (PDF)", data=pdf_etiquetas([it]), file_name=f"Etiqueta_{cod}.pdf", mime="application/pdf", key=f"etq_{cod}", use_container_width=True)

        t1, t2, t3, t4 = st.tabs(["Dónde está", "Movimientos", "Editar", "Ingreso o ajuste"])
        with t1:
            filas = donde_esta(cod)
            if filas:
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
            else:
                st.caption("Todo el stock está en bodega.")
        with t2:
            mov = [{"Fecha": m["fecha"], "Movimiento": m["tipo"], "Cantidad": m["cantidad"], "Saldo": m["saldo"], "Orden": m["orden"], "Detalle": m["detalle"]}
                   for m in reversed(ss.kardex) if m["item"] == cod]
            st.dataframe(pd.DataFrame(mov), hide_index=True, use_container_width=True, height=min(35 * (len(mov) + 1) + 3, 260)) if mov else st.caption("Sin movimientos.")
        with t3:
            with st.form(f"form_edit_{cod}"):
                nombre = st.text_input("Nombre", it["nombre"])
                e1, e2, e3 = st.columns(3)
                cat = e1.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(it["categoria"]) if it["categoria"] in CATEGORIAS else 0)
                uni = e2.selectbox("Unidad", UNIDADES, index=UNIDADES.index(it["unidad"]) if it["unidad"] in UNIDADES else 0)
                tipo = e3.selectbox("Tipo", TIPOS, index=TIPOS.index(it["tipo"]))
                e4, e5, e6 = st.columns(3)
                minimo = e4.number_input("Stock mínimo", min_value=0, step=1, value=int(it["minimo"]))
                valor = e5.number_input("Valor unitario ($)", min_value=0.0, step=0.5, value=float(it["valor"]), format="%.2f")
                ubi = e6.text_input("Ubicación en bodega", it["ubicacion"])
                notas = st.text_area("Notas", it["notas"], height=70)
                if st.form_submit_button("Guardar cambios", type="primary"):
                    it.update(nombre=nombre.strip() or it["nombre"], categoria=cat, unidad=uni, tipo=tipo, minimo=int(minimo), valor=float(valor),
                              ubicacion=ubi.strip(), notas=notas, actualizado=ahora())
                    st.rerun()
        with t4:
            with st.form(f"form_aj_{cod}", clear_on_submit=True):
                a1, a2 = st.columns(2)
                tipo_m = a1.selectbox("Tipo de movimiento", ["Ingreso por compra", "Ajuste de inventario", "Baja por daño o pérdida"])
                cant = a2.number_input("Cantidad", min_value=1, step=1, value=1, help="En el ajuste de inventario puedes sumar o restar con el signo.")
                signo = st.radio("Efecto en el stock", ["Suma", "Resta"], horizontal=True, index=1 if tipo_m == "Baja por daño o pérdida" else 0)
                motivo = st.text_input("Motivo o referencia", placeholder="Ej.: factura 001-123, conteo físico, globos reventados")
                if st.form_submit_button("Registrar movimiento", type="primary"):
                    delta = int(cant) * (1 if signo == "Suma" else -1)
                    if tipo_m == "Baja por daño o pérdida":
                        delta = -abs(delta)
                    if tipo_m == "Ingreso por compra":
                        delta = abs(delta)
                    ajustar_stock(cod, delta, tipo_m, motivo.strip() or "Sin detalle")
                    st.rerun()


# =============================================================================== kits
def _servicios_propios():
    nombres = {r["servicio"] for r in ss.proveedores_catalogo if r["proveedor"] == EMPRESA} | set(ss.recetas)
    return sorted(nombres)


def _kits():
    st.caption("Escribe una sola vez qué lleva cada servicio de Karkajadas. Cuando se aprueba una cotización, la orden de bodega se arma sola con todo lo que el servicio necesita.")
    servicios = _servicios_propios()
    resumen = []
    for s in servicios:
        r = ss.recetas.get(s)
        resumen.append({"Servicio": s, "Tipo": TIPOS_SERVICIO[r["tipo"]] if r else "Sin configurar", "Artículos del kit": len(r["componentes"]) if r else 0})
    pendientes = [x["Servicio"] for x in resumen if x["Tipo"] == "Sin configurar"]
    if pendientes:
        st.warning("Falta configurar: " + ", ".join(pendientes) + ". Mientras tanto no se puede generar la orden de bodega de las cotizaciones que los incluyan.")
    with st.container(border=True, key="card_log_kits"):
        s = st.selectbox("Servicio de Karkajadas", servicios, key="kit_serv")
        r = ss.recetas.get(s, {"tipo": "Material", "componentes": []})
        tipos = list(TIPOS_SERVICIO)
        with st.form(f"form_kit_{s}"):
            tipo = st.radio("¿Qué es este servicio?", tipos, index=tipos.index(r["tipo"]), format_func=lambda t: TIPOS_SERVICIO[t], horizontal=True,
                            help="Si es un servicio de personas (por ejemplo, un coach), no sale nada de bodega.")
            nombres = [i["nombre"] for i in ss.inventario]
            df = pd.DataFrame([{"Artículo": nombre_item(c["item"]), "Cantidad por unidad vendida": c["cantidad"]} for c in r["componentes"]],
                              columns=["Artículo", "Cantidad por unidad vendida"])
            st.caption("Qué sale de bodega por cada unidad que se cotiza (parlante, pedestal, pilas, extensión...).")
            ed = st.data_editor(df, num_rows="dynamic", hide_index=True, use_container_width=True, key=f"kit_ed_{s}",
                                column_config={"Artículo": st.column_config.SelectboxColumn("Artículo", options=nombres, required=True),
                                               "Cantidad por unidad vendida": st.column_config.NumberColumn("Cantidad por unidad vendida", min_value=1, step=1, default=1)})
            if st.form_submit_button("Guardar kit", type="primary"):
                por_nombre = {i["nombre"]: i["codigo"] for i in ss.inventario}
                comp = {}
                for _, f in ed.iterrows():
                    n = str(f["Artículo"])
                    if n in por_nombre:
                        comp[por_nombre[n]] = comp.get(por_nombre[n], 0) + int(f["Cantidad por unidad vendida"] or 1)
                ss.recetas[s] = {"tipo": tipo, "componentes": [{"item": c, "cantidad": q} for c, q in comp.items()] if tipo != "Servicio" else []}
                st.rerun()
    st.dataframe(pd.DataFrame(resumen), hide_index=True, use_container_width=True)


# =============================================================================== órdenes de despacho
def _ordenes():
    filtros = {"Por preparar": ("Preparación",), "En uso ahora": ESTADOS_EN_USO, "Historial": ESTADOS_HISTORIAL, "Todas": None}
    ss.setdefault("log_filtro", "Por preparar")
    st.pills("Ver", list(filtros), key="log_filtro", label_visibility="collapsed")
    est = filtros[ss.get("log_filtro") or "Todas"]
    ordenes = [o for o in ss.ordenes_log.values() if est is None or o["estado"] in est]

    with st.expander("Generar una orden desde una cotización aprobada", expanded=bool(_pendientes()) and not ordenes):
        _generar()

    with st.container(border=True, key="card_log_ord"):
        if not ordenes:
            st.info("No hay órdenes en esta vista.")
            return
        st.dataframe(pd.DataFrame([{"Orden": o["codigo"], "Evento": o["evento"], "Empresa": o["cliente"], "Fecha del evento": fmt_fecha(o["fecha_evento"]),
                                    "Estado": o["estado"], "Artículos": len(o["lineas"])} for o in ordenes]), hide_index=True, use_container_width=True)
        codigos = [o["codigo"] for o in ordenes]
        if ss.get("log_orden") not in codigos:
            ss.log_orden = codigos[0]
        st.selectbox("Abrir la orden", codigos, key="log_orden", format_func=lambda c: f"{c} · {ss.ordenes_log[c]['evento']} · {ss.ordenes_log[c]['cliente']}")
    _detalle_orden(ss.ordenes_log[ss.log_orden])


def _pendientes():
    return [c for c in ss.cotizaciones_guardadas if c["estado"] == "Aprobada" and any(i["proveedor"] == EMPRESA for i in c["items"])
            and codigo_orden(c) not in ss.ordenes_log]


def _generar():
    aprob = _pendientes()
    if not aprob:
        st.caption("No hay cotizaciones aprobadas pendientes de orden de bodega.")
        return
    etiquetas = {f"{c['codigo']} · {c['evento']} · {c['cliente']}": c for c in aprob}
    cot = etiquetas[st.selectbox("Cotización aprobada", list(etiquetas), key="log_cot")]
    lineas, sin_config, solo_serv = lineas_para(cot)
    if sin_config:
        st.warning("Estos servicios de Karkajadas aún no tienen kit: " + ", ".join(sin_config) + ". Configúralos en la sección Kits.")
    if solo_serv:
        st.caption("No salen de bodega (son servicios de personas): " + ", ".join(solo_serv) + ".")
    if lineas:
        st.dataframe(pd.DataFrame([{"Artículo": l["articulo"], "Cantidad": l["requerido"], "Para": l["origen"], "Disponible hoy": disponible(l["item"])} for l in lineas]),
                     hide_index=True, use_container_width=True)
        falta = [l["articulo"] for l in lineas if l["requerido"] > disponible(l["item"])]
        if falta:
            st.warning("No alcanza el stock de: " + ", ".join(falta) + ".")
    elif not sin_config:
        st.info("Esta cotización no tiene materiales de Karkajadas que salgan de bodega.")
    st.button("Generar orden de despacho", type="primary", key="log_gen", disabled=bool(sin_config) or not lineas, on_click=_crear_orden, args=(cot, lineas))


def _crear_orden(cot, lineas):
    o = nueva_orden(cot, lineas)
    ss.log_orden, ss.log_filtro = o["codigo"], "Por preparar"


def _detalle_orden(o):
    cod = o["codigo"]
    with st.container(border=True, key="card_log_ordet"):
        c1, c2 = st.columns([4, 1.2])
        with c1:
            st.markdown(f"<div style='font-size:1.25rem; font-weight:800; color:#0F172A;'>{cod} · {o['evento']}</div>"
                        f"<div style='color:#64748B; margin:2px 0 8px;'>{o['cliente']} · evento el {fmt_fecha(o['fecha_evento'])} · cotización {o['cot']}</div>"
                        f"{_chip(o['estado'])}", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='text-align:center;'>{qr_svg(url_orden(cod), 96)}</div>", unsafe_allow_html=True)
        if o["estado"] == "Preparación":
            _preparar(o)
        else:
            st.dataframe(pd.DataFrame([{"Artículo": l["articulo"], "Para": l["origen"] or "Adicional", "Unidad": l["unidad"], "Pedido": l["requerido"],
                                        "Despachado": l["preparado"]} for l in o["lineas"]]), hide_index=True, use_container_width=True)
            st.caption(f"Despachada el {o['fecha_despacho']} · responsable {o['responsable']} · {o['vehiculo']} · chofer {o['chofer']} · salida {o['hora_salida']}")
            st.caption("La recepción de esta orden (retorno, novedades y fotos) llega en la siguiente etapa.")
        st.download_button("Orden de despacho (PDF)", data=pdf_despacho(o), file_name=f"Despacho_{cod}.pdf", mime="application/pdf", key=f"dld_{cod}")


def _preparar(o):
    cod = o["codigo"]
    with st.expander("Agregar un artículo que no está en el kit"):
        a1, a2, a3 = st.columns([3, 1, 1.2], vertical_alignment="bottom")
        art = a1.selectbox("Artículo", [i["codigo"] for i in ss.inventario], format_func=nombre_item, key=f"add_art_{cod}")
        cant = a2.number_input("Cantidad", min_value=1, step=1, value=1, key=f"add_can_{cod}")
        if a3.button("Agregar", key=f"add_btn_{cod}", use_container_width=True):
            ex = next((l for l in o["lineas"] if l["item"] == art), None)
            if ex:
                ex["requerido"] += int(cant)
            else:
                b = item_por_codigo(art)
                o["lineas"].append({"item": art, "articulo": b["nombre"], "unidad": b["unidad"], "requerido": int(cant), "preparado": 0, "listo": False,
                                    "origen": "", "adicional": True})
            o["ver"] += 1
            st.rerun()
    df = pd.DataFrame([{"Artículo": l["articulo"], "Para": l["origen"] or "Adicional", "Unidad": l["unidad"], "Pedido": l["requerido"],
                        "Disponible": disponible(l["item"], excepto=cod), "Preparado": l["preparado"], "Listo": l["listo"], "Quitar": False} for l in o["lineas"]])
    with st.form(f"form_prep_{cod}_{o['ver']}"):
        ed = st.data_editor(df, hide_index=True, use_container_width=True, key=f"ed_lin_{cod}_{o['ver']}",
                            disabled=["Artículo", "Para", "Unidad", "Pedido", "Disponible"],
                            column_config={"Preparado": st.column_config.NumberColumn("Preparado", min_value=0, step=1),
                                           "Listo": st.column_config.CheckboxColumn("Listo"), "Quitar": st.column_config.CheckboxColumn("Quitar")})
        t1, t2, t3 = st.columns(3)
        resp = t1.text_input("Responsable de bodega", o["responsable"])
        veh = t2.text_input("Vehículo", o["vehiculo"], placeholder="Ej.: Camioneta blanca · PBX-1234")
        cho = t3.text_input("Chofer", o["chofer"])
        t4, t5 = st.columns([1, 3])
        try:
            h0 = datetime.strptime(o["hora_salida"], "%H:%M").time() if o["hora_salida"] else None
        except ValueError:
            h0 = None
        hora = t4.time_input("Hora de salida", h0, step=900)
        obs = t5.text_area("Observaciones", o["obs"], height=68)
        g1, g2, _ = st.columns([1.2, 1.4, 3])
        guardar = g1.form_submit_button("Guardar avance", type="primary", use_container_width=True)
        enviar = g2.form_submit_button("Despachar orden", type="primary", use_container_width=True)
    if guardar or enviar:
        nuevas = []
        for l, (_, f) in zip(o["lineas"], ed.iterrows()):
            if f["Quitar"]:
                continue
            l["preparado"], l["listo"] = int(f["Preparado"] or 0), bool(f["Listo"])
            if l["listo"] and l["preparado"] <= 0:
                l["preparado"] = l["requerido"]   # al marcar "Listo" sin escribir cantidad, se toma lo pedido
            nuevas.append(l)
        o["lineas"] = nuevas
        o.update(responsable=resp.strip(), vehiculo=veh.strip(), chofer=cho.strip(), hora_salida=hora.strftime("%H:%M") if hora else "", obs=obs)
        errores = []
        if enviar:
            if not o["lineas"]:
                errores.append("La orden no tiene artículos.")
            errores += [f"{l['articulo']}: marca la casilla Listo cuando esté preparado." for l in o["lineas"] if not l["listo"] or l["preparado"] <= 0]
            errores += [f"{l['articulo']}: preparaste {l['preparado']} y solo hay {disponible(l['item'], excepto=cod)} disponibles." for l in o["lineas"]
                        if l["preparado"] > disponible(l["item"], excepto=cod)]
            if not o["responsable"]:
                errores.append("Escribe el responsable de bodega.")
        if errores:
            for e in errores:
                st.error(e)
            o["ver"] += 1
        elif enviar:
            despachar(o)
            st.rerun()
        else:
            o["ver"] += 1
            st.rerun()


# =============================================================================== movimientos
def _movimientos():
    with st.container(border=True, key="card_log_mov"):
        c1, c2 = st.columns(2)
        art = c1.selectbox("Artículo", ["Todos"] + [i["codigo"] for i in ss.inventario], format_func=lambda c: "Todos" if c == "Todos" else f"{c} · {nombre_item(c)}", key="mov_art")
        tipos = sorted({m["tipo"] for m in ss.kardex})
        tipo = c2.selectbox("Movimiento", ["Todos"] + tipos, key="mov_tipo")
        filas = [{"Fecha": m["fecha"], "Artículo": nombre_item(m["item"]), "Movimiento": m["tipo"], "Cantidad": m["cantidad"], "Saldo": m["saldo"],
                  "Orden": m["orden"], "Detalle": m["detalle"]}
                 for m in reversed(ss.kardex) if (art == "Todos" or m["item"] == art) and (tipo == "Todos" or m["tipo"] == tipo)]
        if filas:
            st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True, height=min(35 * (len(filas) + 1) + 3, 520))
        else:
            st.info("No hay movimientos con ese filtro.")
