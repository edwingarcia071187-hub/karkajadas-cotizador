"""Órdenes a proveedores."""
import pandas as pd
import streamlit as st
from constantes import EMPRESA
from directorios import completar_proveedor, faltantes_proveedor
from documentos import pdf_ficha, pdf_orden
from formulario_evento import bloque_evento
from utilidades import agrupar_por_proveedor, aprobadas_con, encabezado_modulo, evento_inicial, firma_items, fmt_fecha, proveedor_de, proveedor_inicial

ss = st.session_state


def mostrar(menu):
    encabezado_modulo("prov",
        "<style>.block-container{padding-top:2.4rem !important;}</style>"
        "<div style='background:#134E4A; border-radius:14px; padding:12px 24px; margin:0 0 12px 0;'>"
        "<div style='font-size:0.78rem; font-weight:600; color:#99F6E4;'>Operaciones</div>"
        "<div style='font-size:1.9rem; font-weight:900; color:#FFFFFF; line-height:1.05; letter-spacing:-0.02em;'>Órdenes a proveedores</div></div>",
        unsafe_allow_html=True)
    lista = aprobadas_con(propio=False)
    if not lista:
        st.info("No hay cotizaciones aprobadas con servicios de proveedores externos. Cuando apruebes una, aparecerá aquí.")
    else:
        etiquetas = {f"{c['codigo']} · {c['evento']} · {c['cliente']}": c for c in lista}
        cot = etiquetas[st.selectbox("Cotización aprobada", list(etiquetas), key="prov_cot")]
        cod = cot["codigo"]
        externos = {p: its for p, its in agrupar_por_proveedor(cot).items() if p != EMPRESA}
        listo_evento = cod in ss.eventos
        n_fichas = sum(1 for p in externos if f"{cod}|{p}" in ss.fichas)
        st.caption(f"{len(externos)} proveedor(es) en esta cotización · {n_fichas} ficha(s) guardada(s) · "
                   + ("datos del evento listos" if listo_evento else "faltan los datos del evento"))
        tab_ev, tab_fi = st.tabs(["1. Datos del evento", "2. Fichas de proveedores"])

        with tab_ev:
            st.caption("Fecha, lugar, horario, quién recibe, montaje... Se escriben una sola vez y salen en cada ficha y en el pedido a bodega.")
            ev = bloque_evento(cot, "prov")
        with tab_fi:
            ev = {**evento_inicial(cot), **ss.eventos.get(cod, {})}
            if not listo_evento:
                st.warning("Primero guarda los datos del evento (pestaña 1). Sin ellos no se pueden descargar las fichas.")
            for n, (prov, items) in enumerate(externos.items()):
                clave = f"{cod}|{prov}"
                guardada = ss.fichas.get(clave)
                with st.container(border=True, key=f"orden_{n}"):
                    cab1, cab2 = st.columns([4, 1.6], vertical_alignment="center")
                    estado = ("<span class='badge-estado' style='color:#047857; background:#D1FAE5;'>FICHA GUARDADA</span>" if guardada
                              else "<span class='badge-estado' style='color:#B45309; background:#FEF3C7;'>PENDIENTE</span>")
                    cab1.markdown(f"<div style='font-size:1.15rem; font-weight:800; color:#0F172A;'>{prov} &nbsp;{estado}</div>", unsafe_allow_html=True)
                    if guardada and guardada.get("firma") != firma_items(items):
                        w1, w2 = st.columns([4, 1.4], vertical_alignment="center")
                        w1.warning("La cotización cambió después de guardar esta ficha. Actualízala para que coincida.")
                        if w2.button("Actualizar desde la cotización", key=f"act_{n}_{cod}", type="primary", use_container_width=True):
                            ss.fichas.pop(clave, None)
                            st.rerun()
                    falta = faltantes_proveedor(proveedor_de(prov))
                    if falta:
                        q1, q2 = st.columns([4, 1.6], vertical_alignment="center")
                        q1.warning(f"A este proveedor le falta: {', '.join(falta)}.")
                        q2.button("Completar proveedor", key=f"comp_{n}_{cod}", type="primary", use_container_width=True,
                                  on_click=completar_proveedor, args=(prov, items[0]["ciudad"]))
                    fp = {**proveedor_inicial(cot, prov, items), **{k: v for k, v in (guardada or {}).items() if k != "firma"}}
                    st.dataframe(pd.DataFrame([{"Servicio": i["servicio"], "Fecha": fmt_fecha(i["fecha"]), "Ciudad": i["ciudad"], "Cantidad": i["cantidad"]} for i in items]),
                                 hide_index=True, use_container_width=True, height=min(35 * (len(items) + 1) + 3, 240))
                    con = proveedor_de(prov).get("contactos", [])
                    if con:
                        st.caption("Contacto en el directorio: " + " · ".join(f"{x['nombre']} {x['telefono']}".strip() for x in con))
                    with st.expander("Completar ficha de contratación"):
                        with st.form(f"form_ficha_{n}_{cod}"):
                            serv = st.text_area("Servicio requerido", fp["servicio"], height=150, key=f"fp_s_{n}_{cod}")
                            g1, g2, g3, g4 = st.columns(4)
                            tot = g1.text_input("Total", fp["total"], key=f"fp_t_{n}_{cod}")
                            abo = g2.text_input("Abono", fp["abono"], key=f"fp_a_{n}_{cod}")
                            gar = g3.text_input("Garantía", fp["garantia"], key=f"fp_g_{n}_{cod}")
                            tra = g4.text_input("Transporte", fp["transporte"], key=f"fp_tr_{n}_{cod}")
                            h1, h2 = st.columns(2)
                            pago = h1.text_input("Forma de pago", fp["pago"], key=f"fp_p_{n}_{cod}")
                            fac = h2.text_input("Factura", fp["factura"], key=f"fp_f_{n}_{cod}")
                            ali_fi = st.segmented_control("¿Esta ficha lleva las necesidades de alimentación (vegetarianos, alergias)?", ["Sí", "No"],
                                                          default="Sí" if fp.get("alimentacion", True) else "No", key=f"fp_al_{n}_{cod}") or "Sí"
                            st.caption("La accesibilidad siempre se incluye. Apaga la alimentación solo si el servicio no tiene relación con comida.")
                            if st.form_submit_button("Guardar ficha", type="primary"):
                                ss.fichas[clave] = {"servicio": serv, "total": tot, "abono": abo, "garantia": gar, "transporte": tra,
                                                    "pago": pago, "factura": fac, "alimentacion": ali_fi == "Sí", "firma": firma_items(items)}
                                st.rerun()
                    d1, d2 = st.columns(2)
                    d1.download_button("Ficha de contratación (PDF)", data=pdf_ficha(cot, prov, ev, fp) if listo_evento else b"", disabled=not listo_evento,
                                       file_name=f"Ficha_{cod}_{prov.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True, key=f"dlf_{n}_{cod}")
                    d2.download_button("Orden de servicios - checklist (PDF)", data=pdf_orden(cot, prov, items),
                                       file_name=f"Orden_{cod}_{prov.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True, key=f"dl_{n}_{cod}")
