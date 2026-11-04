"""Bodega."""
import pandas as pd
import streamlit as st
from constantes import EMPRESA
from documentos import pdf_hoja_bodega, pdf_pedido_bodega
from formulario_evento import bloque_evento
from utilidades import aprobadas_con, encabezado_modulo, evento_inicial, fmt_fecha

ss = st.session_state


def mostrar(menu):
    encabezado_modulo("bod",
        "<style>.block-container{padding-top:2.4rem !important;}</style>"
        "<div style='background:#134E4A; border-radius:14px; padding:12px 24px; margin:0 0 12px 0;'>"
        "<div style='font-size:0.78rem; font-weight:600; color:#99F6E4;'>Operaciones</div>"
        "<div style='font-size:1.9rem; font-weight:900; color:#FFFFFF; line-height:1.05; letter-spacing:-0.02em;'>Bodega</div></div>",
        unsafe_allow_html=True)
    lista = aprobadas_con(propio=True)
    if not lista:
        st.info(f"No hay cotizaciones aprobadas con servicios de {EMPRESA}. Cuando apruebes una, aparecerá aquí.")
    else:
        etiquetas = {f"{c['codigo']} · {c['evento']} · {c['cliente']}": c for c in lista}
        cot = etiquetas[st.selectbox("Cotización aprobada", list(etiquetas), key="bod_cot")]
        cod = cot["codigo"]
        items = [i for i in cot["items"] if i["proveedor"] == EMPRESA]
        hojas = ss.hojas.setdefault(cod, {})
        if cod not in ss.eventos:
            st.warning("Faltan los datos del evento (fecha, lugar, horario, quién recibe...). Complétalos aquí para generar el pedido.")
            with st.expander("Datos del evento", expanded=True):
                bloque_evento(cot, "bod")
        else:
            ev = {**evento_inicial(cot), **ss.eventos[cod]}
            with st.expander("Datos del evento"):
                ev = bloque_evento(cot, "bod")
            tab_ped, tab_chk = st.tabs(["Pedido a bodega", "Checklist del bodeguero"])

            with tab_ped:
                st.caption("Pedido generado desde la cotización aprobada: los servicios de Karkajadas Group que deben salir de bodega.")
                filas = []
                for i in items:
                    hoja = hojas.get(i["servicio"], [])
                    if not hoja:
                        est = "Sin checklist"
                    else:
                        est = f"Salió {sum(p['salio'] for p in hoja)}/{len(hoja)} · Regresó {sum(p['regreso'] for p in hoja)}/{len(hoja)}"
                    filas.append({"Servicio": i["servicio"], "Cantidad": i["cantidad"], "Fecha": fmt_fecha(i["fecha"]), "Ciudad": i["ciudad"], "Estado en bodega": est})
                st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True, height=min(35 * (len(filas) + 1) + 3, 300))
                st.download_button("Pedido a bodega (PDF)", data=pdf_pedido_bodega(cot, items, ev), file_name=f"Pedido_bodega_{cod}.pdf", mime="application/pdf", key=f"dlp_{cod}")

            with tab_chk:
                st.caption("El bodeguero detalla las piezas de cada servicio y marca cuando salen y cuando regresan. Lo que guardas aquí queda como plantilla para la próxima vez.")
                for j, it in enumerate(items):
                    s_ = it["servicio"]
                    with st.container(border=True, key=f"chk_{j}"):
                        st.markdown(f"<div style='font-size:1.05rem; font-weight:800; color:#0F172A;'>{s_} <span style='font-weight:600; color:#64748B;'>· {it['cantidad']} unidad(es) · {fmt_fecha(it['fecha'])} · {it['ciudad']}</span></div>", unsafe_allow_html=True)
                        actual = hojas.get(s_)
                        if actual is None and ss.plantillas.get(s_):
                            if st.button("Usar las piezas de la última vez", key=f"plt_{j}_{cod}", type="primary"):
                                hojas[s_] = [{"pieza": p["pieza"], "cantidad": p["cantidad"] * int(it["cantidad"]), "salio": False, "regreso": False, "obs": ""} for p in ss.plantillas[s_]]
                                st.rerun()
                        df = pd.DataFrame(actual or [], columns=["pieza", "cantidad", "salio", "regreso", "obs"])
                        if df.empty:
                            df = pd.DataFrame([{"pieza": "", "cantidad": 1, "salio": False, "regreso": False, "obs": ""}])
                        ver = ss.get(f"hoja_ver_{cod}_{j}", 0)
                        with st.form(f"form_hoja_{cod}_{j}_{ver}"):
                            ed = st.data_editor(df, num_rows="dynamic", hide_index=True, use_container_width=True, key=f"hoja_{cod}_{j}_{ver}",
                                                column_config={"pieza": st.column_config.TextColumn("Pieza", required=True),
                                                               "cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1, default=1),
                                                               "salio": st.column_config.CheckboxColumn("Salió", default=False),
                                                               "regreso": st.column_config.CheckboxColumn("Regresó", default=False),
                                                               "obs": st.column_config.TextColumn("Observación")})
                            if st.form_submit_button("Guardar checklist", type="primary"):
                                filas = [{"pieza": str(r["pieza"]).strip(), "cantidad": int(r["cantidad"] or 1), "salio": bool(r["salio"]),
                                          "regreso": bool(r["regreso"]), "obs": "" if str(r["obs"]) == "nan" else str(r["obs"])}
                                         for _, r in ed.iterrows() if str(r["pieza"]).strip() and str(r["pieza"]) != "nan"]
                                hojas[s_] = filas
                                q = max(int(it["cantidad"]), 1)
                                ss.plantillas[s_] = [{"pieza": p["pieza"], "cantidad": max(round(p["cantidad"] / q), 1)} for p in filas]
                                st.rerun()
                        hoja = hojas.get(s_, [])
                        if hoja:
                            st.caption(f"Salió {sum(p['salio'] for p in hoja)} de {len(hoja)} · Regresó {sum(p['regreso'] for p in hoja)} de {len(hoja)}")
                st.download_button("Checklist de bodega (PDF)", data=pdf_hoja_bodega(cot, items, ev), file_name=f"Checklist_bodega_{cod}.pdf", mime="application/pdf", key=f"dlh_{cod}")
