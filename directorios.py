"""Tablas y formularios de los directorios de clientes y proveedores."""
import pandas as pd
import streamlit as st
from html import escape as esc
from constantes import CIUDADES, EMPRESA, MENU_PROVEEDORES
from utilidades import navegar, selector_ciudad

ss = st.session_state


def _nom_contacto(c):
    return f"{c['nombre']} - {c['cargo']}" if c.get("cargo") else c["nombre"]


def encabezados(cols, titulos):
    for col, t in zip(cols, titulos):
        col.markdown(f"<span class='col-head'>{t}</span>", unsafe_allow_html=True)


def _vacio(v):
    return v is None or (isinstance(v, float) and pd.isna(v))


def limpiar_lista(df, columnas):
    """Convierte la tabla editable en lista de dicts y descarta las filas totalmente vacías."""
    filas = []
    for r in df.to_dict("records"):
        f = {c: "" if _vacio(r.get(c)) else str(r.get(c)).strip() for c in columnas}
        if any(f.values()):
            filas.append(f)
    return filas


def editor_lista(clave, filas, columnas, config):
    """Tabla editable donde se agregan (＋ al final), editan o borran filas: sirve para varios correos, teléfonos, sedes, cuentas..."""
    df = pd.DataFrame(filas, columns=columnas).astype(object)
    ed = st.data_editor(df, num_rows="dynamic", hide_index=True, use_container_width=True, column_config=config, key=clave)
    return limpiar_lista(ed, columnas)


COL_CONTACTOS = ["nombre", "cargo", "correo", "telefono"]


CFG_CONTACTOS = {"nombre": st.column_config.TextColumn("Nombre", width="medium"), "cargo": st.column_config.TextColumn("Cargo / área"),
                 "correo": st.column_config.TextColumn("Correo", width="medium"), "telefono": st.column_config.TextColumn("Teléfono")}


COL_DIRECCIONES = ["etiqueta", "direccion", "ciudad"]


CFG_DIRECCIONES = {"etiqueta": st.column_config.TextColumn("Etiqueta (matriz, bodega...)"),
                   "direccion": st.column_config.TextColumn("Dirección", width="large"),
                   "ciudad": st.column_config.SelectboxColumn("Ciudad", options=CIUDADES)}


COL_SERVICIOS = ["servicio", "categoria", "ciudad", "precio_base", "iva", "descripcion"]


CFG_SERVICIOS = {"servicio": st.column_config.TextColumn("Servicio", width="medium"), "categoria": st.column_config.TextColumn("Categoría"),
                 "ciudad": st.column_config.SelectboxColumn("Ciudad", options=CIUDADES),
                 "precio_base": st.column_config.NumberColumn("Costo ($)", min_value=0.0, format="$%.2f"),
                 "iva": st.column_config.SelectboxColumn("IVA", options=["0%", "15%"]), "descripcion": st.column_config.TextColumn("Descripción")}


COL_CUENTAS = ["banco", "tipo", "numero", "titular"]


CFG_CUENTAS = {"banco": st.column_config.TextColumn("Banco"), "tipo": st.column_config.SelectboxColumn("Tipo", options=["Ahorros", "Corriente"]),
               "numero": st.column_config.TextColumn("Número de cuenta"), "titular": st.column_config.TextColumn("Titular")}


def indice(opciones, valor):
    return opciones.index(valor) if valor in opciones else 0


def correos_invalidos(contactos):
    return [c["correo"] for c in contactos if c["correo"] and ("@" not in c["correo"] or " " in c["correo"])]


def siguiente_id(prefijo, lista):
    nums = [int(r["id"].split("-")[1]) for r in lista if str(r.get("id", "")).startswith(prefijo + "-")]
    return f"{prefijo}-{max(nums, default=0) + 1:03d}"


def aplanar_cliente(c):
    """Copia el contacto y la dirección principales (primera fila) a los campos simples que usa el PDF y las tablas."""
    con = c["contactos"][0] if c.get("contactos") else {}
    c["contacto"], c["email"], c["telefono"] = con.get("nombre", ""), con.get("correo", ""), con.get("telefono", "")
    c["direccion"] = c["direcciones"][0]["direccion"] if c.get("direcciones") else ""


def botones_formulario(prefijo, texto_guardar, cancelar):
    b1, b2, _ = st.columns([1.4, 1, 4])
    guardar = b1.button(texto_guardar, type="primary", use_container_width=True, key=f"{prefijo}_guardar")
    return guardar, (cancelar and b2.button("Cancelar", use_container_width=True, key=f"{prefijo}_cancelar"))


def form_cliente(prefijo, titulo_html="", datos=None, cancelar=False):
    """Formulario de cliente (nuevo o edición). Devuelve dict con los datos, "cancelar" o None."""
    d = datos or {}
    if titulo_html:
        st.markdown(titulo_html, unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([2.3, 1.4, 1.3, 1.8, 1])
    emp = c1.text_input("Razón social / empresa *", value=d.get("empresa", ""), key=f"{prefijo}_emp")
    ruc = c2.text_input("RUC *", value=d.get("ruc", ""), key=f"{prefijo}_ruc")
    ciu = selector_ciudad(c3, "Ciudad principal", f"{prefijo}_ciu", d.get("ciudad"))
    web = c4.text_input("Sitio web", value=d.get("web", ""), key=f"{prefijo}_web")
    dias = c5.number_input("Días crédito", min_value=0, value=int(d.get("dias_credito", 30)), step=15, key=f"{prefijo}_dias")
    t_con, t_dir = st.tabs(["Contactos (correos y teléfonos)", "Direcciones"])
    with t_con:
        st.caption("Una fila por persona o correo. La primera fila es el contacto principal y es la que sale en la cotización.")
        contactos = editor_lista(f"{prefijo}_con", d.get("contactos", []), COL_CONTACTOS, CFG_CONTACTOS)
    with t_dir:
        st.caption("Una fila por sede o dirección de entrega. La primera es la principal.")
        direcciones = editor_lista(f"{prefijo}_dirs", d.get("direcciones", []), COL_DIRECCIONES, CFG_DIRECCIONES)
    guardar, cancel = botones_formulario(prefijo, "Guardar cambios" if datos else "Guardar cuenta", cancelar)
    if cancel:
        return "cancelar"
    if guardar:
        if not (emp.strip() and ruc.strip()):
            st.error("Razón social y RUC son requeridos.")
        elif correos_invalidos(contactos):
            st.error(f"Revisa estos correos: {', '.join(correos_invalidos(contactos))}")
        else:
            return {"empresa": emp.strip(), "ruc": ruc.strip(), "ciudad": ciu, "web": web.strip(), "dias_credito": dias,
                    "contactos": contactos, "direcciones": direcciones}
    return None


def form_proveedor(prefijo, titulo_html="", datos=None, cancelar=False):
    d = datos or {}
    if titulo_html:
        st.markdown(titulo_html, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2.3, 1.4, 1.6, 1.3])
    nom = c1.text_input("Proveedor *", value=d.get("proveedor", ""), key=f"{prefijo}_nom")
    ruc = c2.text_input("RUC", value=d.get("ruc", ""), key=f"{prefijo}_ruc")
    cat = c3.text_input("Categoría general", value=d.get("categoria", ""), key=f"{prefijo}_cat")
    ciu = selector_ciudad(c4, "Ciudad base", f"{prefijo}_ciu", d.get("ciudad"))
    obs = st.text_input("Observaciones", value=d.get("observaciones", ""), key=f"{prefijo}_obs")
    t_srv, t_con, t_dir, t_cta = st.tabs(["Servicios y costos", "Contactos (correos y teléfonos)", "Direcciones", "Cuentas bancarias"])
    with t_con:
        st.caption("Una fila por persona o correo. La primera fila es el contacto principal.")
        contactos = editor_lista(f"{prefijo}_con", d.get("contactos", []), COL_CONTACTOS, CFG_CONTACTOS)
    with t_dir:
        direcciones = editor_lista(f"{prefijo}_dirs", d.get("direcciones", []), COL_DIRECCIONES, CFG_DIRECCIONES)
    with t_cta:
        st.caption("Puede tener varias cuentas. La primera es la que se usa por defecto para pagos.")
        cuentas = editor_lista(f"{prefijo}_cta", d.get("cuentas", []), COL_CUENTAS, CFG_CUENTAS)
    with t_srv:
        st.caption("Todo lo que ofrece este proveedor: una fila por servicio (sonido, pantallas, TVs...). Estos servicios aparecen al cotizar.")
        srv_ini = [dict(r) for r in ss.proveedores_catalogo if d and r["proveedor"] == d.get("proveedor")]
        df_srv = pd.DataFrame(srv_ini, columns=COL_SERVICIOS)
        df_srv["iva"] = df_srv["iva"].map(lambda x: f"{int(x * 100)}%")
        ed_srv = st.data_editor(df_srv, num_rows="dynamic", hide_index=True, use_container_width=True, column_config=CFG_SERVICIOS, key=f"{prefijo}_srv")
    guardar, cancel = botones_formulario(prefijo, "Guardar cambios" if datos else "Registrar proveedor", cancelar)
    if cancel:
        return "cancelar"
    if guardar:
        if not nom.strip():
            st.error("El nombre del proveedor es obligatorio.")
        elif correos_invalidos(contactos):
            st.error(f"Revisa estos correos: {', '.join(correos_invalidos(contactos))}")
        elif any(_vacio(r["servicio"]) or not str(r["servicio"]).strip() for r in ed_srv.to_dict("records") if any(not _vacio(v) and str(v).strip() for v in r.values())):
            st.error("Cada servicio necesita su nombre.")
        else:
            servicios = []
            for r in ed_srv.to_dict("records"):
                if _vacio(r["servicio"]) or not str(r["servicio"]).strip():
                    continue
                servicios.append({"servicio": str(r["servicio"]).strip(), "categoria": "" if _vacio(r["categoria"]) else str(r["categoria"]).strip(),
                                  "ciudad": ciu if _vacio(r["ciudad"]) else r["ciudad"], "precio_base": 0.0 if _vacio(r["precio_base"]) else float(r["precio_base"]),
                                  "iva": 0.15 if r["iva"] == "15%" else 0.0, "descripcion": "" if _vacio(r["descripcion"]) else str(r["descripcion"]).strip()})
            return {"servicios": servicios, "proveedor": nom.strip(), "ruc": ruc.strip(), "categoria": cat.strip(), "ciudad": ciu, "observaciones": obs.strip(),
                    "contactos": contactos, "direcciones": direcciones, "cuentas": cuentas}
    return None


# --- Altas, cambios y validaciones de clientes y proveedores
def validar_cliente(d, cid=None):
    for c in ss.clientes_catalogo:
        if c["id"] != cid and c["ruc"] == d["ruc"]:
            return f"Ya existe una cuenta con ese RUC ({c['empresa']})."
        if c["id"] != cid and c["empresa"].lower() == d["empresa"].lower():
            return "Ya existe una cuenta con ese nombre."
    return None


def crear_cliente(d):
    d["id"] = siguiente_id("CLI", ss.clientes_catalogo)
    aplanar_cliente(d)
    ss.clientes_catalogo.append(d)


def actualizar_cliente(cid, nuevo):
    c = next(x for x in ss.clientes_catalogo if x["id"] == cid)
    viejo = c["empresa"]
    c.update(nuevo)
    aplanar_cliente(c)
    if viejo != c["empresa"]:   # las cotizaciones ya guardadas siguen apuntando a la misma cuenta
        for q in ss.cotizaciones_guardadas:
            if q["cliente"] == viejo:
                q["cliente"] = c["empresa"]


def validar_proveedor(d, pid=None):
    actual = next((x for x in ss.proveedores if x["id"] == pid), None)
    if actual and actual["proveedor"] == EMPRESA and d["proveedor"].strip() != EMPRESA:
        return f"«{EMPRESA}» es la empresa propia (sus servicios salen de bodega); no se puede cambiar su nombre."
    if any(p["id"] != pid and p["proveedor"].lower() == d["proveedor"].lower() for p in ss.proveedores):
        return "Ya existe un proveedor con ese nombre."
    return None


def crear_proveedor(d):
    servicios = d.pop("servicios", [])
    d["id"] = siguiente_id("PRV", ss.proveedores)
    ss.proveedores.append(d)
    ss.proveedores_catalogo.extend({**sv, "proveedor": d["proveedor"]} for sv in servicios)


def actualizar_proveedor(pid, nuevo):
    p = next(x for x in ss.proveedores if x["id"] == pid)
    viejo = p["proveedor"]
    servicios = nuevo.pop("servicios", None)
    p.update(nuevo)
    if p["proveedor"] != viejo:   # el cambio de nombre llega a las cotizaciones, a las fichas guardadas y a los servicios
        for lista in [c["items"] for c in ss.cotizaciones_guardadas] + [ss.items_cot]:
            for it in lista:
                if it["proveedor"] == viejo:
                    it["proveedor"] = p["proveedor"]
        ss.fichas = {(k.rsplit("|", 1)[0] + "|" + p["proveedor"] if k.endswith("|" + viejo) else k): v for k, v in ss.fichas.items()}
    if servicios is not None:   # los servicios del formulario reemplazan a los anteriores de este proveedor
        ss.proveedores_catalogo = [r for r in ss.proveedores_catalogo if r["proveedor"] != viejo] + [{**sv, "proveedor": p["proveedor"]} for sv in servicios]


def asegurar_proveedor(nombre, ciudad, categoria):
    """Si se registra un servicio de un proveedor que no está en el directorio, se crea el proveedor."""
    if not any(p["proveedor"].lower() == nombre.lower() for p in ss.proveedores):
        crear_proveedor({"proveedor": nombre, "ruc": "", "categoria": categoria, "ciudad": ciudad, "observaciones": "",
                         "contactos": [], "direcciones": [], "cuentas": []})
        return True
    return False


def faltantes_proveedor(p):
    """Qué le falta a un proveedor para considerarse completo: RUC y un contacto con teléfono (la empresa propia no se revisa)."""
    if not p:
        return ["estar en el directorio"]
    if p.get("proveedor") == "Karkajadas Group":
        return []
    falta = []
    if not str(p.get("ruc", "")).strip():
        falta.append("RUC")
    if not any(str(c.get("telefono", "")).strip() for c in p.get("contactos", [])):
        falta.append("contacto con teléfono")
    return falta


def completar_proveedor(nombre, ciudad):
    """Lleva al directorio; si el proveedor no existe todavía, lo crea para poder completarlo."""
    asegurar_proveedor(nombre, ciudad, "General")
    ss.dir_prv_solo = True
    navegar(MENU_PROVEEDORES)


def resumen_contactos(r):
    """Contacto principal + cuántos más hay."""
    con = r.get("contactos", [])
    extra = f" (+{len(con) - 1})" if len(con) > 1 else ""
    return (con[0]["nombre"] if con else "", (con[0]["correo"] if con else "") + extra, con[0]["telefono"] if con else "")


def abrir_nuevo(k):
    ss[f"dir_{k}_nuevo"] = True
    ss[f"dir_{k}_ver"] += 1   # deselecciona la fila de la tabla


def panel_directorio(k, registros, fila_tabla, texto_busqueda, form, validar, crear, actualizar, nombre, etiqueta_nuevo, filtro=None):
    """Tabla con búsqueda; al seleccionar una fila se edita; el botón de nuevo abre el formulario vacío."""
    ss.setdefault(f"dir_{k}_ver", 0)
    ss.setdefault(f"dir_{k}_nuevo", False)
    ver = ss[f"dir_{k}_ver"]
    c_b, c_n = st.columns([3, 1], vertical_alignment="center")
    busq = c_b.text_input("Buscar", key=f"dir_{k}_b", label_visibility="collapsed", placeholder="Buscar...").lower()
    c_n.button(f"＋ {etiqueta_nuevo}", key=f"dir_{k}_btn_nuevo", on_click=abrir_nuevo, args=(k,), use_container_width=True, type="primary")
    vis = [r for r in registros if (not busq or busq in texto_busqueda(r).lower()) and (filtro is None or filtro(r))]
    sel = []
    if vis:
        ev = st.dataframe(pd.DataFrame([fila_tabla(r) for r in vis]), hide_index=True, use_container_width=True, on_select="rerun",
                          selection_mode="single-row", key=f"dir_{k}_t{ver}", height=min(35 * (len(vis) + 1) + 3, 340))
        sel = ev.selection.rows
        if not sel:
            st.caption("Haz clic en el recuadro a la izquierda de una fila para editarla.")
    else:
        st.info("No hay registros que coincidan.")

    def cerrar():
        ss[f"dir_{k}_nuevo"] = False
        ss[f"dir_{k}_ver"] += 1
        st.rerun()

    if sel and sel[0] < len(vis):
        reg = vis[sel[0]]
        ss[f"dir_{k}_nuevo"] = False
        with st.container(border=True, key=f"card_dir_{k}_e"):
            res = form(f"e{k}_{reg['id']}_{ver}", f"<div class='section-title'>Editar: {esc(nombre(reg))}</div>", reg, True)
            if res == "cancelar":
                cerrar()
            elif res:
                err = validar(res, reg["id"])
                if err:
                    st.error(err)
                else:
                    actualizar(reg["id"], res)
                    st.toast("Cambios guardados")
                    cerrar()
    elif ss[f"dir_{k}_nuevo"]:
        with st.container(border=True, key=f"card_dir_{k}_n"):
            res = form(f"n{k}_{ver}", f"<div class='section-title' style='color:#059669; border-color:#059669;'>{etiqueta_nuevo}</div>", None, True)
            if res == "cancelar":
                cerrar()
            elif res:
                err = validar(res, None)
                if err:
                    st.error(err)
                else:
                    crear(res)
                    st.toast("Registrado")
                    cerrar()
