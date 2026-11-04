"""Reportes financieros y exportación a Excel."""
import pandas as pd
import streamlit as st
from datetime import date
from datetime import datetime
from io import BytesIO
from constantes import CIUDADES, ESTADOS
from utilidades import calcular_linea, encabezado_estandar, fmt_fecha, normalizar_multi

ss = st.session_state


def excel_cotizaciones(cots):
    """Libro de Excel con tres hojas: cotizaciones, detalle de ítems y resumen por estado."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    azul, gris = "1E3A8A", "F1F5F9"
    borde = Border(bottom=Side(style="thin", color="DCE3EC"))
    dinero_fmt = '"$"#,##0.00'

    def hoja(ws, titulos, filas, anchos, cols_dinero=(), cols_fecha=()):
        ws.append(titulos)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=azul)
            c.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        ws.row_dimensions[1].height = 26
        for f in filas:
            ws.append(f)
        for fila in ws.iter_rows(min_row=2):
            for c in fila:
                c.border = borde
                if c.column in cols_dinero:
                    c.number_format = dinero_fmt
                if c.column in cols_fecha:
                    c.number_format = "dd/mm/yyyy"
                    c.alignment = Alignment(horizontal="center")
        for i, a in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(i)].width = a
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    def f_(txt):
        try:
            return datetime.strptime(str(txt)[:10], "%Y-%m-%d")
        except ValueError:
            return str(txt)

    ws1 = wb.active
    ws1.title = "Cotizaciones"
    hoja(ws1, ["Código", "Evento", "Cliente", "Fecha", "Estado", "Servicios", "Total con IVA ($)"],
         [[c["codigo"], c["evento"], c["cliente"], f_(c["fecha"]), c["estado"], len(c["items"]), round(c["total"], 2)] for c in cots],
         [18, 30, 36, 13, 12, 11, 18], cols_dinero=(7,), cols_fecha=(4,))
    n = len(cots) + 1
    ws1.append([])
    ws1.append(["Total", "", "", "", "", sum(len(c["items"]) for c in cots), round(sum(c["total"] for c in cots), 2)])
    for c in ws1[n + 2]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor=gris)
    ws1.cell(n + 2, 7).number_format = dinero_fmt

    ws2 = wb.create_sheet("Detalle de ítems")
    filas = []
    for c in cots:
        for it in c["items"]:
            base, fee, venta = calcular_linea(it)
            filas.append([c["codigo"], c["evento"], c["cliente"], c["estado"], it["servicio"], it["proveedor"], it["ciudad"], f_(it["fecha"]),
                          it["cantidad"], it["costo"], it["iva_prov"], it["fee_pct"] / 100.0, round(base, 2), round(fee, 2), round(venta, 2)])
    hoja(ws2, ["Código", "Evento", "Cliente", "Estado", "Servicio", "Proveedor", "Ciudad", "Fecha", "Cantidad", "Costo unit. ($)",
               "IVA proveedor", "Margen", "Costo con IVA ($)", "Margen ($)", "Precio de venta ($)"],
         filas, [18, 26, 32, 12, 28, 28, 14, 13, 10, 14, 12, 10, 16, 13, 18], cols_dinero=(10, 13, 14, 15), cols_fecha=(8,))
    for fila in ws2.iter_rows(min_row=2):
        fila[10].number_format = "0%"
        fila[11].number_format = "0%"

    ws3 = wb.create_sheet("Resumen por estado")
    ws3.append(["Estado", "Cotizaciones", "Total con IVA ($)", "% del total"])
    gran = sum(c["total"] for c in cots)
    for e in ESTADOS:   # valores calculados aquí (no fórmulas): se ven también en la vista protegida de Excel
        de = [c for c in cots if c["estado"] == e]
        tot_e = round(sum(c["total"] for c in de), 2)
        ws3.append([e, len(de), tot_e, (tot_e / gran) if gran else 0])
    ws3.append(["Total", len(cots), round(gran, 2), 1 if gran else 0])
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=azul)
        c.alignment = Alignment(horizontal="center", vertical="center")
    for fila in ws3.iter_rows(min_row=2):
        fila[2].number_format = dinero_fmt
        fila[3].number_format = "0%"
        for c in fila:
            c.border = borde
    for c in ws3[ws3.max_row]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor=gris)
    for i, a in enumerate([16, 15, 20, 12], 1):
        ws3.column_dimensions[get_column_letter(i)].width = a

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def mostrar(menu):
    encabezado_estandar("rep", "Reportes financieros", "Listado de cotizaciones y exportación a Excel")
    cots_all = ss.cotizaciones_guardadas
    with st.container(border=True, key="card_rep1"):
        st.markdown("<div class='section-title' style='border:none; margin-bottom:0;'>Filtros del reporte</div>", unsafe_allow_html=True)
        ss.setdefault("rep_est", ["Todas"])
        ss.setdefault("rep_cli", ["Todos"])
        st.pills("Estado", ["Todas"] + ESTADOS, selection_mode="multi", key="rep_est", on_change=normalizar_multi, args=("rep_est", "Todas"))
        r2, r3, r4, r5 = st.columns([2.6, 1.6, 1.2, 1.2])
        r2.multiselect("Cliente", ["Todos"] + sorted({c["cliente"] for c in cots_all}), key="rep_cli", on_change=normalizar_multi, args=("rep_cli", "Todos"))
        f_ciu = r3.selectbox("Ciudad del servicio", ["Todas"] + CIUDADES, key="rep_ciu")
        fechas = sorted(c["fecha"] for c in cots_all) or [str(date.today())]
        f_des = r4.date_input("Desde", value=date.fromisoformat(fechas[0]), key="rep_des")
        f_has = r5.date_input("Hasta", value=date.fromisoformat(fechas[-1]), key="rep_has")
        f_est = ESTADOS if ("Todas" in ss.rep_est or not ss.rep_est) else ss.rep_est
        f_cli = ss.rep_cli
    sel = [c for c in cots_all
           if c["estado"] in f_est and ("Todos" in f_cli or not f_cli or c["cliente"] in f_cli)
           and (f_ciu == "Todas" or any(i["ciudad"] == f_ciu for i in c["items"]))
           and f_des.isoformat() <= c["fecha"] <= f_has.isoformat()]
    sel.sort(key=lambda c: c["fecha"], reverse=True)

    with st.container(border=True, key="card_rep2"):
        k1, k2, k3 = st.columns([1.2, 1.2, 1.6], vertical_alignment="center")
        k1.markdown(f"<div class='monto-badge' style='margin-left:0;'><div class='monto-label'>Cotizaciones</div><div class='monto-valor'>{len(sel)}</div></div>", unsafe_allow_html=True)
        k2.markdown(f"<div class='monto-badge' style='margin-left:0;'><div class='monto-label'>Total con IVA</div><div class='monto-valor'>${sum(c['total'] for c in sel):,.2f}</div></div>", unsafe_allow_html=True)
        with k3:
            if sel:
                st.download_button("Descargar Excel", data=excel_cotizaciones(sel), key="rep_xlsx", use_container_width=True, type="secondary",
                                   file_name=f"cotizaciones_{date.today():%Y%m%d}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   help="Incluye tres hojas: cotizaciones, detalle de ítems y resumen por estado")
            else:
                st.button("Descargar Excel", disabled=True, use_container_width=True, key="rep_xlsx_off")
        if sel:
            st.dataframe(pd.DataFrame([{"Código": c["codigo"], "Evento": c["evento"], "Cliente": c["cliente"], "Fecha": fmt_fecha(c["fecha"]),
                                        "Estado": c["estado"], "Servicios": len(c["items"]), "Total ($)": c["total"]} for c in sel]),
                         hide_index=True, use_container_width=True, height=min(35 * (len(sel) + 1) + 3, 340),
                         column_config={"Total ($)": st.column_config.NumberColumn(format="$%.2f")})
        else:
            st.info("No hay cotizaciones con esos filtros.")
