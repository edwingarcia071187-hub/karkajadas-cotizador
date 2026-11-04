"""Panel de control."""
import altair as alt
import pandas as pd
import streamlit as st
from constantes import CIUDADES, COLORES, ESTADOS, MENU_CLIENTES, MENU_PROVEEDORES, MESES_ES, SIN_FILTRO
from estilos import css_tarjeta_activa
from utilidades import encabezado_estandar, fijar_estado, ir, limpiar_filtros, navegar

ss = st.session_state


def mostrar(menu):

    # 1. Título + accesos rápidos
    def _accesos():
        b1, b2, b3 = st.columns(3)
        b1.button("Crear cotización", use_container_width=True, type="primary", key="go_new",
                  on_click=ir, args=("Nueva cotización",), kwargs={"cotizacion_activa": None, "items_cot": []})
        b2.button("Directorio de clientes", use_container_width=True, type="secondary", key="go_cli", on_click=navegar, args=(MENU_CLIENTES,))
        b3.button("Directorio de proveedores", use_container_width=True, type="secondary", key="go_pro", on_click=navegar, args=(MENU_PROVEEDORES,))
    encabezado_estandar("panel", "Panel de control", "Resumen ejecutivo", volver=False, derecha=_accesos)

    # 2. Filtros globales (con key para poder borrarlos desde el botón "Borrar selección")
    cotizaciones = ss.cotizaciones_guardadas
    ciudad_cliente = {c["empresa"]: c["ciudad"] for c in ss.clientes_catalogo}
    with st.container(border=True, key="card_2"):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:0;'>Filtros operativos globales</div>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        col_f1.selectbox("Filtrar por empresa / cuenta", ["Todas"] + sorted({c["cliente"] for c in cotizaciones}), key="f_emp")
        col_f2.selectbox("Filtrar por mes operativo", ["Todos"] + sorted({c["fecha"][:7] for c in cotizaciones}), key="f_mes")
        col_f3.selectbox("Filtrar por ciudad", ["Todas"] + CIUDADES, key="f_ciu")

    cots_dash = [
        c for c in cotizaciones
        if (ss.f_emp == "Todas" or c["cliente"] == ss.f_emp)
        and (ss.f_mes == "Todos" or c["fecha"][:7] == ss.f_mes)
        and (ss.f_ciu == "Todas" or ciudad_cliente.get(c["cliente"], "Desconocida") == ss.f_ciu)
    ]

    tot = {e: sum(c["total"] for c in cots_dash if c["estado"] == e) for e in ESTADOS}
    # Total general: todas las cotizaciones, sin filtros y de todos los tiempos (las canceladas no cuentan como ingreso)
    total_general = sum(c["total"] for c in cotizaciones if c["estado"] != "Cancelada")
    estado_actual = ss.filtro_estado_tabla
    hay_filtros = estado_actual != "Todas" or any(ss[k] != v for k, v in SIN_FILTRO.items())

    # 3. Tarjetas + gráficos
    with st.container(border=True, key="card_3"):
        c_tit, c_clear = st.columns([3, 2], vertical_alignment="center")
        c_tit.markdown("<div class='section-title'>Análisis financiero interactivo</div>", unsafe_allow_html=True)
        with c_clear:
            if hay_filtros:   # enlace discreto: borra tarjeta, filtros globales y buscador
                st.button(f"↺ Borrar filtros · Total general ${total_general:,.2f}", key="clear_btn", on_click=limpiar_filtros)
            else:
                st.markdown(f"<div class='total-general'>Total general: <b>${total_general:,.2f}</b></div>", unsafe_allow_html=True)

        etiquetas = {"Aprobada": "APROBADAS", "Enviada": "ENVIADAS", "Borrador": "BORRADORES", "Cancelada": "CANCELADAS"}
        for col, e in zip(st.columns(4), ESTADOS):
            col.button(f"{etiquetas[e]}\n${tot[e]:,.2f}", use_container_width=True, key=f"kpi_{e}", on_click=fijar_estado, args=(e,))

        st.markdown(f"<style>{css_tarjeta_activa(estado_actual)}</style>", unsafe_allow_html=True)  # anillo en la tarjeta activa

        st.markdown("<br>", unsafe_allow_html=True)
        col_donut, col_ley, col_trend = st.columns([0.95, 1.25, 2.45], gap="medium")

        with col_donut:
            if estado_actual == "Todas":   # distribución por estado
                df_donut = pd.DataFrame({"Segmento": ESTADOS, "Monto": [tot[e] for e in ESTADOS]})
                dominio, paleta, titulo_leyenda = ESTADOS, [COLORES[e] for e in ESTADOS], "Distribución por estado"
            else:                          # una tarjeta elegida: reparte ese estado por cliente (tonos del color de la tarjeta)
                por_cli = {}
                for c in cots_dash:
                    if c["estado"] == estado_actual:
                        por_cli[c["cliente"]] = por_cli.get(c["cliente"], 0.0) + c["total"]
                df_donut = pd.DataFrame({"Segmento": list(por_cli), "Monto": list(por_cli.values())})
                dominio = list(por_cli)
                base_rgb = tuple(int(COLORES[estado_actual][i:i + 2], 16) for i in (1, 3, 5))
                n = max(len(dominio), 1)
                paleta = ["#%02X%02X%02X" % tuple(int(v + (255 - v) * (0.55 * i / max(n - 1, 1))) for v in base_rgb) for i in range(n)]
                titulo_leyenda = f"{estado_actual}s por cliente"
            df_donut = df_donut[df_donut["Monto"] > 0]
            if df_donut.empty:
                st.info("Sin datos para distribución.")
            else:
                donut = alt.Chart(df_donut).mark_arc(innerRadius={"expr": "min(width, height) / 2 * 0.56"}, outerRadius={"expr": "min(width, height) / 2"}, cornerRadius=4, padAngle=0.03).encode(
                    theta=alt.Theta("Monto:Q"),
                    color=alt.Color("Segmento:N", scale=alt.Scale(domain=dominio, range=paleta), legend=None),
                    tooltip=[alt.Tooltip("Segmento", title="Detalle"), alt.Tooltip("Monto", format="$,.2f")],
                ).properties(height=176, padding={"left": 6, "right": 6, "top": 6, "bottom": 6})
                st.altair_chart(donut, use_container_width=True)
                # leyenda propia en su recuadro de alto fijo: si hay muchas empresas, solo ese recuadro se desplaza
                col_de = dict(zip(dominio, paleta))
                total_d = float(df_donut["Monto"].sum())
                filas_ley = "".join(
                    f"<div style='display:flex; align-items:center; gap:8px; padding:4px 0; font-size:0.82rem; color:#334155;'>"
                    f"<span style='width:10px; height:10px; border-radius:50%; background:{col_de[r.Segmento]}; flex:none;'></span>"
                    f"<span style='flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;' title='{r.Segmento}'>{r.Segmento}</span>"
                    f"<span style='flex:none; font-weight:700; color:#0F172A;'>{r.Monto / total_d:.0%}</span></div>"
                    for r in df_donut.itertuples())
                with col_ley:
                    st.markdown(f"<div style='height:176px; margin-top:8px; overflow-y:auto; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:8px 14px;'>"
                                f"<div style='font-size:0.74rem; font-weight:700; color:#64748B; letter-spacing:.04em; padding-bottom:4px; border-bottom:1px solid #E2E8F0; margin-bottom:2px;'>{titulo_leyenda}</div>{filas_ley}</div>",
                                unsafe_allow_html=True)

        with col_trend:
            # "Todas" = una serie por estado (incluye canceladas); una tarjeta = solo esa serie
            estados_graf = ESTADOS if estado_actual == "Todas" else [estado_actual]
            y_title = "Volumen ($)" if estado_actual == "Todas" else f"Volumen {estado_actual.upper()} ($)"
            filas = [c for c in cots_dash if c["estado"] in estados_graf]

            if filas:
                # Eje completo de meses (los meses sin movimiento valen 0, así la línea no une puntos lejanos)
                meses = pd.period_range(min(c["fecha"][:7] for c in cots_dash), max(c["fecha"][:7] for c in cots_dash), freq="M")
                orden = [f"{MESES_ES[p.month - 1]} {p.year}" for p in meses]
                df = pd.DataFrame({"Periodo": [pd.Period(c["fecha"][:7], "M") for c in filas],
                                   "Estado": [c["estado"] for c in filas], "Monto": [c["total"] for c in filas]})
                df = (df.pivot_table(index="Periodo", columns="Estado", values="Monto", aggfunc="sum")
                        .reindex(index=meses, columns=estados_graf).fillna(0.0))
                df.index = orden
                df = df.rename_axis(index="Mes", columns="Estado").stack().rename("Monto").reset_index()

                # symbolOpacity=1: la leyenda no hereda la transparencia del área
                color = alt.Color("Estado:N", scale=alt.Scale(domain=estados_graf, range=[COLORES[e] for e in estados_graf]),
                                  legend=alt.Legend(title=None, orient="top", symbolOpacity=1, symbolType="circle", labelFontSize=11, padding=2) if len(estados_graf) > 1 else None)
                base = alt.Chart(df).encode(
                    x=alt.X("Mes:O", sort=orden, title="Mes operativo", axis=alt.Axis(labelAngle=0, grid=False, labelColor="#64748B")),
                    y=alt.Y("Monto:Q", stack=None, title=y_title, axis=alt.Axis(format="$,.0f", gridColor="#E2E8F0", labelColor="#64748B")),
                    color=color,
                )
                grafico = (
                    base.mark_area(opacity=0.14, interpolate="monotone")                       # área sutil del color de la tarjeta
                    + base.mark_line(strokeWidth=2.5, interpolate="monotone")
                    + base.mark_point(filled=True, size=70, opacity=1).encode(
                        tooltip=["Estado:N", alt.Tooltip("Mes:O", title="Periodo"), alt.Tooltip("Monto:Q", format="$,.2f", title="Total")])
                ).properties(height=225, padding={"left": 4, "right": 8, "top": 4, "bottom": 4})
                st.altair_chart(grafico, use_container_width=True)
            else:
                st.markdown(f"<div style='padding-top:100px; text-align:center; color:#64748B;'>No hay ingresos registrados en la categoría <b>{estado_actual}</b> para el periodo seleccionado.</div>", unsafe_allow_html=True)

    # 4. Tabla detallada
    with st.container(border=True, key="card_4"):
        col_tit, col_bus = st.columns([2, 1])
        col_tit.markdown(f"<div class='section-title'>Detalle operativo: {estado_actual.upper()}</div>", unsafe_allow_html=True)
        busqueda = col_bus.text_input("Buscador...", key="b_u", label_visibility="collapsed", placeholder="Buscar código, evento o cliente...").lower()

        ev_filt = [c for c in cots_dash
                   if (estado_actual == "Todas" or c["estado"] == estado_actual)
                   and (not busqueda or busqueda in f"{c['codigo']} {c['evento']} {c['cliente']}".lower())]

        if ev_filt:
            ANCHOS = [1.3, 0.95, 1.9, 1.05, 2.5, 1.0, 0.8]
            TIT = ["CÓDIGO", "FECHA", "EVENTO", "ESTADO", "CLIENTE CORPORATIVO", "MONTO", ""]
            with st.container(key="tabla_det"):
                with st.container(key="det_head"):
                    hx = st.columns(ANCHOS, vertical_alignment="center")
                    for i, t in enumerate(TIT):
                        hx[i].markdown(f"<div class='col-head{' num' if i == 5 else ''}'>{t}</div>", unsafe_allow_html=True)
                for cot in ev_filt:
                    col_e = COLORES[cot["estado"]]
                    cx = st.columns(ANCHOS, vertical_alignment="center")
                    cx[0].markdown(f"<div class='cell'><b>{cot['codigo']}</b></div>", unsafe_allow_html=True)
                    cx[1].markdown(f"<div class='cell' style='color:#475569;'>{cot['fecha']}</div>", unsafe_allow_html=True)
                    cx[2].markdown(f"<div class='cell'>{cot['evento']}</div>", unsafe_allow_html=True)
                    cx[3].markdown(f"<div class='cell'><span class='badge-estado' style='color:{col_e}; background:{col_e}1F;'>{cot['estado'].upper()}</span></div>", unsafe_allow_html=True)
                    cx[4].markdown(f"<div class='cell'>{cot['cliente']}</div>", unsafe_allow_html=True)
                    cx[5].markdown(f"<div class='cell num'><b>${cot['total']:,.2f}</b></div>", unsafe_allow_html=True)
                    cx[6].button("Abrir", key=f"ab_{cot['codigo']}", type="secondary", use_container_width=True,
                                 on_click=ir, args=("Nueva cotización",),
                                 kwargs={"cotizacion_activa": cot, "items_cot": [dict(i) for i in cot.get("items", [])]})
        else:
            st.info("No hay cotizaciones para mostrar.")
