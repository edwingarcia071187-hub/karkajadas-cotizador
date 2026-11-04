"""Directorios de clientes y proveedores."""
import pandas as pd
import streamlit as st
from constantes import CIUDADES, MENU_CLIENTES, MENU_PROVEEDORES
from directorios import _vacio, actualizar_cliente, actualizar_proveedor, crear_cliente, crear_proveedor, faltantes_proveedor, form_cliente, form_proveedor, panel_directorio, resumen_contactos, validar_cliente, validar_proveedor
from utilidades import encabezado_estandar

ss = st.session_state


def mostrar(menu):
    encabezado_estandar("dir", menu, "Cuentas, contactos y datos de facturación" if menu == MENU_CLIENTES else "Contactos, servicios y costos")

    with st.container(border=True, key="card_9"):
        if menu == MENU_CLIENTES:
            def fila_cliente(c):
                con, mail, tel = resumen_contactos(c)
                return {"Empresa": c["empresa"], "RUC": c["ruc"], "Ciudad": c["ciudad"], "Contacto": con, "Correo": mail, "Teléfono": tel,
                        "Direcciones": len(c.get("direcciones", [])), "Días crédito": c["dias_credito"]}
            panel_directorio(
                "cli", ss.clientes_catalogo, fila_cliente,
                lambda c: " ".join([c["empresa"], c["ruc"], c["ciudad"]] + [f"{x['nombre']} {x['correo']} {x['telefono']}" for x in c.get("contactos", [])]),
                form_cliente, validar_cliente, crear_cliente, actualizar_cliente, lambda c: c["empresa"], "Nueva cuenta")

        if menu == MENU_PROVEEDORES:
            sub_prov, sub_serv = st.tabs(["Proveedores (datos de contacto)", "Servicios y costos"])

            with sub_prov:
                def fila_proveedor(p):
                    con, mail, tel = resumen_contactos(p)
                    cta = p["cuentas"][0] if p.get("cuentas") else {}
                    return {"Proveedor": p["proveedor"], "Estado": "Incompleto" if faltantes_proveedor(p) else "Completo",
                            "Categoría": p["categoria"], "Ciudad": p["ciudad"], "Contacto": con, "Correo": mail, "Teléfono": tel,
                            "Banco": f"{cta.get('banco', '')} {cta.get('numero', '')}".strip(),
                            "Servicios": sum(1 for r in ss.proveedores_catalogo if r["proveedor"] == p["proveedor"])}
                n_inc = sum(1 for p in ss.proveedores if faltantes_proveedor(p))
                ss.setdefault("dir_prv_solo", False)
                if n_inc:
                    a1, a2 = st.columns([4, 1.6], vertical_alignment="center")
                    a1.warning(f"{n_inc} proveedor(es) por completar (falta RUC o un contacto con teléfono).")
                    a2.checkbox("Ver solo los incompletos", key="dir_prv_solo")
                else:
                    ss.dir_prv_solo = False
                    st.caption("Todos los proveedores tienen su información básica completa.")
                panel_directorio(
                    "prv", ss.proveedores, fila_proveedor,
                    lambda p: " ".join([p["proveedor"], p["categoria"], p["ciudad"], p.get("ruc", "")] + [f"{x['nombre']} {x['correo']} {x['telefono']}" for x in p.get("contactos", [])]),
                    form_proveedor, validar_proveedor, crear_proveedor, actualizar_proveedor, lambda p: p["proveedor"], "Nuevo proveedor",
                    filtro=(lambda p: bool(faltantes_proveedor(p))) if ss.dir_prv_solo else None)

            with sub_serv:
                st.caption("Edita directamente en la tabla: cambia un valor con doble clic, agrega una fila con ＋ al final, o borra una fila seleccionándola y pulsando la papelera.")
                ver_s = ss.setdefault("serv_ver", 0)
                nombres = [p["proveedor"] for p in ss.proveedores]
                df_s = pd.DataFrame([{"proveedor": r["proveedor"], "servicio": r["servicio"], "categoria": r.get("categoria", ""), "ciudad": r["ciudad"],
                                      "precio_base": float(r["precio_base"]), "iva": f"{int(r['iva'] * 100)}%", "descripcion": r.get("descripcion", "")}
                                     for r in ss.proveedores_catalogo],
                                    columns=["proveedor", "servicio", "categoria", "ciudad", "precio_base", "iva", "descripcion"])
                ed_s = st.data_editor(
                    df_s, num_rows="dynamic", hide_index=True, use_container_width=True, key=f"serv_ed_{ver_s}",
                    column_config={"proveedor": st.column_config.SelectboxColumn("Proveedor", options=nombres, required=True),
                                   "servicio": st.column_config.TextColumn("Servicio", required=True),
                                   "categoria": st.column_config.TextColumn("Categoría"),
                                   "ciudad": st.column_config.SelectboxColumn("Ciudad", options=CIUDADES),
                                   "precio_base": st.column_config.NumberColumn("Costo ($)", min_value=0.0, format="$%.2f"),
                                   "iva": st.column_config.SelectboxColumn("IVA", options=["0%", "15%"]),
                                   "descripcion": st.column_config.TextColumn("Descripción")})
                if st.button("Guardar cambios en servicios", type="primary", key="serv_save"):
                    nuevos, error = [], None
                    for r in ed_s.to_dict("records"):
                        f = {k: ("" if _vacio(v) else v) for k, v in r.items()}
                        if not any(str(v).strip() for v in f.values()):
                            continue
                        if not (str(f["proveedor"]).strip() and str(f["servicio"]).strip()):
                            error = "Cada servicio necesita proveedor y nombre del servicio."
                            break
                        nuevos.append({"proveedor": f["proveedor"], "servicio": str(f["servicio"]).strip(), "categoria": str(f["categoria"]).strip(),
                                       "ciudad": f["ciudad"] or CIUDADES[0], "precio_base": float(f["precio_base"] or 0),
                                       "iva": 0.15 if f["iva"] == "15%" else 0.0, "descripcion": str(f["descripcion"]).strip()})
                    if error:
                        st.error(error)
                    else:
                        ss.proveedores_catalogo = nuevos
                        ss.serv_ver += 1
                        st.toast("Servicios guardados")
                        st.rerun()
