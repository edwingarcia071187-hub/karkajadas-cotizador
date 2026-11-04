"""Funciones de uso general: navegación, cotizaciones, formatos y datos del evento."""
import json
import streamlit as st
from datetime import datetime
from constantes import CIUDADES, DIAS, EMPRESA, IVA_CLIENTE, MESES, NUEVO_CLIENTE, OBS_BASE, OTRA, SIN_FILTRO

ss = st.session_state


def ir(destino, **estado):
    """Callback de navegación: cambia de vista y, opcionalmente, fija otras variables de sesión."""
    ss.nav_menu = destino
    ss.update(estado)
    ss.cot_sid += 1
    ss.cot_base = None


def _k(nombre):
    """Clave de un campo del formulario de cotización (cambia con cada apertura del módulo)."""
    return f"cot_{nombre}_{ss.cot_sid}"


def estado_formulario():
    """Foto de lo que hay en el formulario (campos + servicios)."""
    return (ss.get(_k("cod")), ss.get(_k("ev")), ss.get(_k("cli")), str(ss.get(_k("fec"))), ss.get(_k("est")), ss.get(_k("inv")),
            json.dumps(ss.items_cot, sort_keys=True, default=str))


def hay_cambios():
    return ss.nav_menu == "Nueva cotización" and ss.cot_base is not None and estado_formulario() != ss.cot_base


def navegar(destino):
    """Callback de menú: si estás en una cotización con cambios sin guardar, pide confirmación antes de salir."""
    if hay_cambios():
        ss.confirmar_salida = True
        ss.destino_salida = destino
    else:
        ir(destino)


def dialogo_salida():
    st.write("Hiciste cambios en esta cotización que todavía no se guardaron. Si sales ahora, se perderán.")
    c1, c2 = st.columns(2)
    if c1.button("Salir sin guardar", key="exit_confirm", use_container_width=True):
        ir(ss.pop("destino_salida", "Panel de control"))
        st.rerun()
    if c2.button("Cancelar", key="exit_cancel", use_container_width=True):
        ss.pop("destino_salida", None)
        st.rerun()


def dialogo_editar(idx):
    it = ss.items_cot[idx]
    nombres = sorted({p["proveedor"] for p in ss.proveedores} | {it["proveedor"]})
    c1, c2 = st.columns(2)
    prov = c1.selectbox("Proveedor", nombres, index=nombres.index(it["proveedor"]), key=f"ed_prov_{idx}")
    serv = c2.text_input("Servicio", it["servicio"], key=f"ed_serv_{idx}")
    c3, c4, c5 = st.columns(3)
    ciudad = selector_ciudad(c3, "Ciudad", f"ed_ciu_{idx}", it["ciudad"])
    try:
        f0 = datetime.strptime(str(it["fecha"])[:10], "%Y-%m-%d")
    except ValueError:
        f0 = datetime.now()
    fecha = c4.date_input("Fecha de servicio", f0, key=f"ed_fec_{idx}")
    cant = c5.number_input("Cantidad", min_value=1, value=int(it["cantidad"]), step=1, key=f"ed_can_{idx}")
    c6, c7, c8 = st.columns(3)
    costo = c6.number_input("Costo unit. ($)", value=float(it["costo"]), format="%.2f", key=f"ed_cos_{idx}")
    ivas = [0.0, 0.15] if it["iva_prov"] in (0.0, 0.15) else [0.0, 0.15, it["iva_prov"]]
    iva = c7.selectbox("IVA prov.", ivas, index=ivas.index(it["iva_prov"]), format_func=lambda x: f"{int(x * 100)}%", key=f"ed_iva_{idx}")
    fee = c8.number_input("Margen (%)", value=float(it["fee_pct"]), step=5.0, format="%.2f", key=f"ed_fee_{idx}")
    base = cant * costo * (1 + iva)
    st.caption(f"Con estos valores: costo \\${base:,.2f} · margen \\${base * fee / 100:,.2f} · precio de venta \\${base * (1 + fee / 100):,.2f}")
    b1, b2 = st.columns(2)
    if b1.button("Guardar cambios", type="primary", use_container_width=True, key=f"ed_ok_{idx}"):
        if not serv.strip():
            st.error("El servicio no puede quedar vacío.")
        else:
            it.update({"proveedor": prov, "servicio": serv.strip(), "ciudad": ciudad, "fecha": fecha.strftime("%Y-%m-%d"),
                       "cantidad": int(cant), "costo": float(costo), "iva_prov": float(iva), "fee_pct": float(fee)})
            st.rerun()
    if b2.button("Cancelar", use_container_width=True, key=f"ed_no_{idx}"):
        st.rerun()


def encabezado_modulo(clave, html, unsafe_allow_html=True):
    """Encabezado de cada módulo: botón para volver al panel de control + el título."""
    c_vol, c_tit = st.columns([2.1, 8], vertical_alignment="center")
    c_vol.button("← Panel de control", key=f"volver_{clave}", on_click=navegar, args=("Panel de control",), help="Volver al panel de control")
    c_tit.markdown(html, unsafe_allow_html=True)


def encabezado_estandar(clave, titulo, subtitulo="", volver=True, derecha=None):
    """Encabezado igual en todos los módulos: [← Panel de control] título y subtítulo a la izquierda, acciones o dato a la derecha."""
    with st.container(border=True, key=f"card_h_{clave}"):
        if volver:
            c_vol, c_tit, c_der = st.columns([1.55, 3.6, 3], vertical_alignment="center")
            c_vol.button("← Panel de control", key=f"volver_{clave}", on_click=navegar, args=("Panel de control",), help="Volver al panel de control", use_container_width=True)
        else:
            c_tit, c_der = st.columns([1.6, 3.6], vertical_alignment="center")
        c_tit.markdown(f"<div class='hd-titulo'>{titulo}</div>" + (f"<div class='hd-sub'>{subtitulo}</div>" if subtitulo else ""), unsafe_allow_html=True)
        if derecha:
            with c_der:
                derecha()


def normalizar_multi(clave, todo):
    """Filtro múltiple con una opción "todo": al elegirla se desmarcan las demás; al elegir otra, se desmarca "todo"; si queda vacío, vuelve a "todo"."""
    val = list(ss.get(clave, []))
    antes = ss.get(clave + "_antes", [todo])
    if not val:
        val = [todo]
    elif todo in val and len(val) > 1:
        val = [v for v in val if v != todo] if todo in antes else [todo]
    ss[clave] = val
    ss[clave + "_antes"] = val


def fijar_estado(estado):
    """Selecciona la tarjeta; si ya estaba seleccionada, vuelve a 'Todas'."""
    ss.filtro_estado_tabla = "Todas" if ss.filtro_estado_tabla == estado else estado


def limpiar_filtros():
    """Borra TODAS las selecciones: tarjeta activa, filtros globales y buscador."""
    ss.filtro_estado_tabla = "Todas"
    ss.update(SIN_FILTRO)


def calcular_linea(item):
    """Devuelve (costo con IVA proveedor, margen en $, precio de venta) de una línea."""
    base = item["cantidad"] * item["costo"] * (1 + item["iva_prov"])
    fee = base * item["fee_pct"] / 100.0
    return base, fee, base + fee


def total_cliente(items):
    return sum(calcular_linea(i)[2] for i in items) * (1 + IVA_CLIENTE)


def siguiente_codigo():
    n = max((int(c["codigo"][-3:]) for c in ss.cotizaciones_guardadas if c["codigo"][-3:].isdigit()), default=0) + 1
    return f"KG-{datetime.now():%Y%m%d}-{n:03d}"


def guardar_cotizacion(activa, codigo, evento, cliente, fecha, estado, total, invitados=0):
    """Valida y guarda (o reemplaza en su misma posición) la cotización. Devuelve la cotización guardada o None."""
    lista = ss.cotizaciones_guardadas
    if not evento.strip():
        st.error("Ingrese el nombre del evento.")
    elif cliente == NUEVO_CLIENTE:
        st.error("Registre el cliente.")
    elif not ss.items_cot:
        st.error("Agregue al menos un servicio.")
    elif any(c["codigo"] == codigo and not (activa and activa["codigo"] == codigo) for c in lista):
        st.error("Ya existe una cotización con esa referencia.")
    else:
        nueva = {"codigo": codigo, "evento": evento, "cliente": cliente, "fecha": str(fecha),
                 "estado": estado, "total": total, "invitados": int(invitados), "items": [dict(i) for i in ss.items_cot]}
        pos = next((i for i, c in enumerate(lista) if activa and c["codigo"] == activa["codigo"]), None)
        if pos is None:
            lista.append(nueva)
        else:
            lista[pos] = nueva
        ss.cotizacion_activa = nueva          # los siguientes guardados reemplazan esta misma cotización
        ss.cot_base = estado_formulario()     # formulario "limpio": ya no hay cambios pendientes
        return nueva
    return None


def fmt_fecha(iso):
    try:
        return datetime.strptime(str(iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(iso)


def datos_empresa():
    """Datos de la empresa que salen en el encabezado de los documentos (se editan en Perfil de la empresa)."""
    return ss.empresa


def fecha_larga(d):
    """'miércoles, 30 de septiembre de 2026' a partir de una fecha o un texto AAAA-MM-DD."""
    if not hasattr(d, "year"):
        try:
            d = datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except ValueError:
            return str(d)
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}"


def dinero(x):
    try:
        v = float(str(x).replace("$", "").replace(" ", "").replace(",", "."))  if isinstance(x, str) else float(x)
    except ValueError:
        return str(x)
    return "$" + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def a_numero(x):
    try:
        return float(str(x).replace("$", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return 0.0


def agrupar_por_proveedor(cot):
    grupos = {}
    for it in cot["items"]:
        grupos.setdefault(it["proveedor"], []).append(it)
    return dict(sorted(grupos.items(), key=lambda kv: (kv[0] != EMPRESA, kv[0].lower())))   # Karkajadas primero


def cliente_de(cot):
    return next((c for c in ss.clientes_catalogo if c["empresa"] == cot["cliente"]), {})


def proveedor_de(nombre):
    return next((p for p in ss.proveedores if p["proveedor"] == nombre), {})


def evento_inicial(cot):
    """Datos del evento: se llenan una sola vez y alimentan todas las fichas y el pedido a bodega."""
    cli = cliente_de(cot)
    dirs, con = cli.get("direcciones", []), cli.get("contactos", [])
    return {
        "fecha_entrega": min(i["fecha"] for i in cot["items"]), "invitados": str(cot.get("invitados", "") or ""), "lugar": "",
        "direccion": dirs[0]["direccion"] if dirs else "", "ubicacion": "Pendiente", "horario": "", "tematica": cot["evento"],
        "recibe": con[0]["nombre"] if con else "", "telefono_recibe": con[0]["telefono"] if con else "",
        "montaje": "Sí", "hora_montaje": "", "desmontaje": "", "documento": "Cédula de identidad",
        "observacion": OBS_BASE,
    }


def proveedor_inicial(cot, prov, items):
    """Datos propios de cada proveedor en su ficha: servicio requerido, valores y condiciones."""
    cli = cliente_de(cot)
    lineas = []
    for i in items:
        desc = next((r["descripcion"] for r in ss.proveedores_catalogo if r["proveedor"] == prov and r["servicio"] == i["servicio"]), "")
        desc = "" if desc in ("", "Estándar", "Manual") else f"\n{desc}"
        lineas.append(f"{i['servicio']} - {i['ciudad']} - {fecha_larga(i['fecha'])}:\n{i['cantidad']} x {i['servicio']}{desc}")
    return {"servicio": "\n\n".join(lineas), "total": dinero(sum(calcular_linea(i)[0] for i in items)), "abono": dinero(0),
            "garantia": dinero(0), "transporte": "Incluido",
            "pago": f"A {cli['dias_credito']} días crédito" if cli.get("dias_credito") else "", "factura": "Factura"}


def texto_inclusion(ev, alimentacion=True):
    """Resumen de inclusión del evento para los documentos (solo cantidades, sin nombres). La alimentación puede omitirse por proveedor."""
    inc = ev.get("inclusion") or {}

    def lista(campos):
        return [f"{inc[c]} {t}" for c, t in campos if inc.get(c)]
    acc = lista([("movilidad", "con movilidad reducida o en silla de ruedas"), ("visual", "con discapacidad visual"),
                 ("auditiva", "con discapacidad auditiva"), ("otra_acc", "con otra necesidad de accesibilidad")])
    if str(inc.get("nota_acc", "")).strip():
        acc.append(inc["nota_acc"].strip())
    ali = lista([("vegetarianos", "vegetariano(s)"), ("veganos", "vegano(s)"), ("sin_gluten", "sin gluten"), ("alergias", "con alergia alimentaria")])
    if str(inc.get("nota_ali", "")).strip():
        ali.append(inc["nota_ali"].strip())
    partes = []
    if acc:
        partes.append("Accesibilidad: " + "; ".join(acc) + ".")
    if ali and alimentacion:
        partes.append("Alimentación: " + "; ".join(ali) + ".")
    if partes:
        return "\n".join(partes)
    return "No aplica a este servicio." if ali else "Sin necesidades especiales reportadas."


def firma_items(items):
    """Huella de los servicios de una cotización: sirve para avisar si cambió después de guardar una ficha."""
    return [[i["servicio"], i["cantidad"], i["fecha"], i["costo"]] for i in items]


def aprobadas_con(propio):
    """Cotizaciones aprobadas que tienen servicios propios (bodega) o de proveedores externos."""
    return [c for c in ss.cotizaciones_guardadas if c["estado"] == "Aprobada"
            and any((i["proveedor"] == EMPRESA) == propio for i in c["items"])]


def _a_fecha(txt, defecto):
    try:
        return datetime.strptime(str(txt)[:10], "%Y-%m-%d").date()
    except ValueError:
        return defecto


def _a_hora(txt, defecto):
    try:
        return datetime.strptime(str(txt)[:5], "%H:%M").time()
    except ValueError:
        return defecto


def _hh(t):
    """05:00 -> 05h00"""
    return f"{t:%H}h{t:%M}"


def selector_ciudad(contenedor, etiqueta, clave, valor=None):
    """Lista de ciudades con la opción "Otra...": si se elige, aparece un campo para escribirla
    y queda guardada en la lista para todo el ERP."""
    if valor and valor not in CIUDADES:
        ss.ciudades_extra.append(valor)
        CIUDADES.insert(len(CIUDADES) - 1, valor)
    opciones = CIUDADES + [OTRA]
    pos = CIUDADES.index(valor) if valor in CIUDADES else 0
    elegida = contenedor.selectbox(etiqueta, opciones, index=pos, key=clave)
    if elegida != OTRA:
        return elegida
    nueva = contenedor.text_input("Escribe la ciudad", key=f"{clave}_otra").strip()
    if nueva:
        nueva = nueva[:1].upper() + nueva[1:]
        if nueva not in CIUDADES:
            ss.ciudades_extra.append(nueva)
        return nueva
    return valor if valor in CIUDADES else CIUDADES[0]
