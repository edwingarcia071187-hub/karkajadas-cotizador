"""Logística: datos de ejemplo, reglas de stock, órdenes de despacho, movimientos, códigos QR y PDF."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
import streamlit as st
from constantes import EMPRESA, IVA_CLIENTE, MENU_LOGISTICA
from documentos import pdf_documento

ss = st.session_state

ESTADOS_ORDEN = ["Preparación", "Despachada", "En evento", "Recibida", "Cerrada"]
ESTADOS_EN_USO = ("Despachada", "En evento")
ESTADOS_HISTORIAL = ("Recibida", "Cerrada")
CATEGORIAS = ["Juegos gigantes", "Decoración", "Audio", "Iluminación", "Mobiliario", "Carpas y estructuras", "Electricidad", "Papelería y consumibles", "Otros"]
UNIDADES = ["unidad", "juego", "par", "rollo", "caja", "metro", "paquete"]
TIPOS = ["Retornable", "Consumible"]
TIPOS_SERVICIO = {"Material": "Material (sale de bodega)", "Mixto": "Mixto (material y personal)", "Servicio": "Servicio (no sale de bodega)"}
URL_APP_DEFECTO = "https://karkajadas-cotizador-57ytrjr2isrqcnqecqfugq.streamlit.app"


def ahora():
    """Fecha y hora de Ecuador (UTC-5), sin importar dónde corra el servidor."""
    return datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M")


# ------------------------------------------------------------------ datos de ejemplo
# (código, nombre, categoría, unidad, tipo, stock, mínimo, valor unitario, ubicación)
_INVENTARIO = [
    ("INV-001", "Jenga gigante de madera", "Juegos gigantes", "juego", "Retornable", 4, 2, 180.0, "Estante A-1"),
    ("INV-002", "Cuatro en raya gigante", "Juegos gigantes", "juego", "Retornable", 4, 2, 150.0, "Estante A-2"),
    ("INV-003", "Rompecabezas gigante", "Juegos gigantes", "juego", "Retornable", 3, 1, 200.0, "Estante A-3"),
    ("INV-004", "Globos de látex surtidos", "Decoración", "unidad", "Consumible", 2000, 600, 0.08, "Estante B-1"),
    ("INV-005", "Cinta adhesiva de embalaje", "Papelería y consumibles", "rollo", "Consumible", 40, 12, 1.5, "Estante B-3"),
    ("INV-006", "Parlante activo 15 pulgadas", "Audio", "unidad", "Retornable", 6, 2, 420.0, "Estante C-1"),
    ("INV-007", "Pedestal para parlante", "Audio", "unidad", "Retornable", 6, 2, 45.0, "Estante C-2"),
    ("INV-008", "Micrófono inalámbrico", "Audio", "unidad", "Retornable", 8, 3, 160.0, "Estante C-3"),
    ("INV-009", "Pilas AA", "Papelería y consumibles", "unidad", "Consumible", 120, 60, 0.45, "Estante B-2"),
    ("INV-010", "Extensión eléctrica de 10 metros", "Electricidad", "unidad", "Retornable", 12, 4, 14.0, "Estante D-1"),
    ("INV-011", "Regleta de 6 tomas", "Electricidad", "unidad", "Retornable", 10, 4, 9.0, "Estante D-2"),
    ("INV-012", "Mesa plegable de 1,80 m", "Mobiliario", "unidad", "Retornable", 20, 6, 38.0, "Bodega principal"),
    ("INV-013", "Mantel blanco", "Mobiliario", "unidad", "Retornable", 30, 10, 7.5, "Estante E-1"),
    ("INV-014", "Carpa de 3 x 3 m", "Carpas y estructuras", "unidad", "Retornable", 6, 2, 260.0, "Bodega principal"),
]

# servicio de Karkajadas -> tipo y qué sale de bodega por cada unidad vendida: [(código, cantidad)]
_RECETAS = {
    "Jenga gigante de madera": ("Material", [("INV-001", 1), ("INV-005", 1)]),
    "Cuatro en raya gigante": ("Material", [("INV-002", 1)]),
    "Rompecabezas gigante": ("Material", [("INV-003", 1), ("INV-005", 1)]),
    "Alquiler de parlante con micrófonos": ("Material", [("INV-006", 1), ("INV-007", 1), ("INV-008", 2), ("INV-009", 4), ("INV-010", 1)]),
    "Decoración con globos": ("Material", [("INV-004", 150), ("INV-005", 1)]),
    "Coach de liderazgo": ("Servicio", []),
}


def _cot_demo(cod, evento, cliente, fecha, invitados, lineas):
    """lineas: (servicio, proveedor, ciudad, cantidad, costo, iva, margen %)"""
    items = [{"servicio": s, "proveedor": p, "ciudad": ciu, "fecha": fecha, "cantidad": c, "costo": k, "iva_prov": v, "fee_pct": f}
             for s, p, ciu, c, k, v, f in lineas]
    total = sum(c * k * (1 + v) * (1 + f / 100) for _, _, _, c, k, v, f in lineas) * (1 + IVA_CLIENTE)
    return {"codigo": cod, "evento": evento, "cliente": cliente, "fecha": fecha, "estado": "Aprobada",
            "total": round(total, 2), "items": items, "invitados": invitados}


def iniciar_logistica():
    """Crea los datos de ejemplo de Logística la primera vez (el inventario real se cargará después)."""
    if "inventario" in ss:
        return
    ahora_ = ahora()
    ss.inventario = [{"codigo": c, "nombre": n, "categoria": cat, "unidad": u, "tipo": t, "total": s, "minimo": m, "valor": v,
                      "ubicacion": ub, "foto": None, "notas": "", "actualizado": ahora_} for c, n, cat, u, t, s, m, v, ub in _INVENTARIO]
    ss.recetas = {s: {"tipo": t, "componentes": [{"item": i, "cantidad": q} for i, q in comp]} for s, (t, comp) in _RECETAS.items()}
    ss.kardex = [{"fecha": ahora_, "item": it["codigo"], "tipo": "Ingreso inicial", "cantidad": it["total"], "saldo": it["total"],
                  "orden": "", "detalle": "Carga inicial del inventario (datos de ejemplo)"} for it in ss.inventario]
    ss.ordenes_log = {}
    ss.setdefault("url_app", URL_APP_DEFECTO)

    # cotizaciones aprobadas de ejemplo con servicios de Karkajadas
    ss.cotizaciones_guardadas.append(_cot_demo(
        "KG-20261106-014", "Aniversario Siemens", "Siemens Ecuador S.A.", "2026-11-06", 80,
        [("Jenga gigante de madera", EMPRESA, "Quito", 1, 60.0, 0.15, 0.0), ("Alquiler de parlante con micrófonos", EMPRESA, "Quito", 1, 90.0, 0.15, 0.0),
         ("Decoración con globos", EMPRESA, "Quito", 2, 120.0, 0.15, 0.0)]))
    ss.cotizaciones_guardadas.append(_cot_demo(
        "KG-20261120-015", "Día de la familia", "Hilton Colón Quito", "2026-11-20", 150,
        [("Jenga gigante de madera", EMPRESA, "Quito", 2, 60.0, 0.15, 0.0), ("Cuatro en raya gigante", EMPRESA, "Quito", 1, 50.0, 0.15, 0.0),
         ("Alquiler de parlante con micrófonos", EMPRESA, "Quito", 2, 90.0, 0.15, 0.0), ("Decoración con globos", EMPRESA, "Quito", 3, 120.0, 0.15, 0.0),
         ("Coach de liderazgo", EMPRESA, "Quito", 1, 200.0, 0.15, 0.0), ("Catering premium", "ProAlimentos QUI", "Quito", 80, 25.0, 0.15, 20.0)]))
    # una orden de ejemplo que ya salió, para ver "dónde está" cada artículo
    cot = next(c for c in ss.cotizaciones_guardadas if c["codigo"] == "KG-20261106-014")
    lineas, _, _ = lineas_para(cot)
    for l in lineas:
        l["preparado"], l["listo"] = l["requerido"], True
    o = nueva_orden(cot, lineas)
    o.update(responsable="Carlos Moreno", vehiculo="Camioneta blanca · PBX-1234", chofer="Luis Andrade", hora_salida="08:30")
    despachar(o, "2026-11-03 07:50")


# ------------------------------------------------------------------ inventario y stock
def item_por_codigo(cod):
    return next((i for i in ss.inventario if i["codigo"] == cod), None)


def nombre_item(cod):
    it = item_por_codigo(cod)
    return it["nombre"] if it else cod


def siguiente_codigo_item():
    n = max([int(i["codigo"].split("-")[1]) for i in ss.inventario if i["codigo"].startswith("INV-") and i["codigo"][4:].isdigit()] or [0])
    return f"INV-{n + 1:03d}"


def _lineas_de(cod, estados, excepto=None):
    return [(o, l) for o in ss.ordenes_log.values() if o["estado"] in estados and o["codigo"] != excepto for l in o["lineas"] if l["item"] == cod]


def fuera(cod):
    """Unidades retornables que están en eventos (despachadas y aún no recibidas)."""
    it = item_por_codigo(cod)
    if not it or it["tipo"] != "Retornable":
        return 0
    return sum(l["preparado"] for _, l in _lineas_de(cod, ESTADOS_EN_USO))


def reservado(cod, excepto=None):
    """Unidades apartadas en órdenes que todavía se están preparando."""
    return sum(l["requerido"] for _, l in _lineas_de(cod, ("Preparación",), excepto))


def disponible(cod, excepto=None):
    it = item_por_codigo(cod)
    return (it["total"] - fuera(cod) - reservado(cod, excepto)) if it else 0


def donde_esta(cod):
    """Órdenes que tienen parte de este artículo (apartado o en un evento)."""
    filas = []
    for o, l in _lineas_de(cod, ("Preparación",) + ESTADOS_EN_USO):
        cant = l["requerido"] if o["estado"] == "Preparación" else l["preparado"]
        filas.append({"Orden": o["codigo"], "Evento": o["evento"], "Empresa": o["cliente"], "Fecha del evento": o["fecha_evento"],
                      "Estado": "Apartado" if o["estado"] == "Preparación" else o["estado"], "Cantidad": cant})
    return filas


def mover(cod, tipo, cantidad, detalle, orden="", fecha=None):
    """Escribe una línea en el kardex (historial de movimientos) con el saldo que queda."""
    it = item_por_codigo(cod)
    ss.kardex.append({"fecha": fecha or ahora(), "item": cod, "tipo": tipo, "cantidad": cantidad, "saldo": it["total"] if it else 0,
                      "orden": orden, "detalle": detalle})


def ajustar_stock(cod, delta, tipo, detalle):
    it = item_por_codigo(cod)
    it["total"] = max(it["total"] + delta, 0)
    it["actualizado"] = ahora()
    mover(cod, tipo, delta, detalle)


# ------------------------------------------------------------------ recetas (kits) y órdenes
def lineas_para(cot):
    """Arma la lista de bodega de una cotización: solo los servicios de Karkajadas que son material, con todo lo que cada uno lleva.
    Devuelve (líneas, servicios sin configurar, servicios que no salen de bodega)."""
    acum, sin_config, solo_servicio = {}, [], []
    for it in cot["items"]:
        if it["proveedor"] != EMPRESA:
            continue
        r = ss.recetas.get(it["servicio"])
        if r is None:
            if it["servicio"] not in sin_config:
                sin_config.append(it["servicio"])
            continue
        if r["tipo"] == "Servicio":
            solo_servicio.append(it["servicio"])
            continue
        for comp in r["componentes"]:
            base = item_por_codigo(comp["item"])
            if not base:
                continue
            cant = int(round(comp["cantidad"] * float(it["cantidad"])))
            d = acum.setdefault(comp["item"], {"item": comp["item"], "articulo": base["nombre"], "unidad": base["unidad"], "requerido": 0,
                                                "preparado": 0, "listo": False, "origen": [], "adicional": False})
            d["requerido"] += cant
            d["origen"].append(f"{it['servicio']} ×{int(it['cantidad']) if float(it['cantidad']).is_integer() else it['cantidad']}")
    lineas = list(acum.values())
    for l in lineas:
        l["origen"] = " · ".join(l["origen"])
    return lineas, sin_config, solo_servicio


def codigo_orden(cot):
    return "OD-" + cot["codigo"].split("-", 1)[-1]


def nueva_orden(cot, lineas):
    o = {"codigo": codigo_orden(cot), "cot": cot["codigo"], "evento": cot["evento"], "cliente": cot["cliente"],
         "fecha_evento": min(i["fecha"] for i in cot["items"]), "estado": "Preparación", "lineas": lineas, "responsable": "",
         "vehiculo": "", "chofer": "", "hora_salida": "", "obs": "", "creada": ahora(), "fecha_despacho": "", "ver": 0}
    ss.ordenes_log[o["codigo"]] = o
    return o


def despachar(o, fecha=None):
    """Pasa la orden a 'Despachada': los consumibles bajan del stock y todo queda escrito en el kardex."""
    fecha = fecha or ahora()
    o["estado"], o["fecha_despacho"] = "Despachada", fecha
    for l in o["lineas"]:
        it = item_por_codigo(l["item"])
        if it["tipo"] == "Consumible":
            it["total"] = max(it["total"] - l["preparado"], 0)
        it["actualizado"] = fecha
        mover(l["item"], "Salida a evento", -l["preparado"], f"{o['evento']} · {o['cliente']}", o["codigo"], fecha)


def estado_stock(it):
    d = disponible(it["codigo"])
    if d <= 0:
        return "Sin disponible"
    return "Bajo el mínimo" if d < it["minimo"] else "Normal"


# ------------------------------------------------------------------ códigos QR
def _qr_widget(texto):
    from reportlab.graphics.barcode.qr import QrCodeWidget
    return QrCodeWidget(texto, barLevel="M")


def qr_dibujo(texto, tam):
    """QR como dibujo de reportlab (para los PDF). tam en puntos."""
    from reportlab.graphics.shapes import Drawing
    w = _qr_widget(texto)
    x0, y0, x1, y1 = w.getBounds()
    d = Drawing(tam, tam, transform=[tam / (x1 - x0), 0, 0, tam / (y1 - y0), 0, 0])
    d.add(w)
    return d


def qr_svg(texto, px=150):
    """QR en SVG para mostrarlo en pantalla."""
    from reportlab.graphics import renderSVG
    svg = renderSVG.drawToString(qr_dibujo(texto, px))
    return svg[svg.find("<svg"):]


def _base_url():
    return str(ss.get("url_app", URL_APP_DEFECTO)).strip().rstrip("/")


def url_item(cod):
    return f"{_base_url()}/?item={cod}"


def url_orden(cod):
    return f"{_base_url()}/?orden={cod}"


def atender_enlace_qr():
    """Si alguien escaneó un QR, la app abre directo ese artículo u orden."""
    qp = st.query_params
    if "item" in qp:
        ss.nav_menu, ss.log_seccion, ss.log_item = MENU_LOGISTICA, "Inventario", str(qp["item"])
        qp.clear()
    elif "orden" in qp:
        ss.nav_menu, ss.log_seccion, ss.log_orden = MENU_LOGISTICA, "Órdenes de despacho", str(qp["orden"])
        ss.log_filtro = "Todas"
        qp.clear()


# ------------------------------------------------------------------ PDF
def pdf_despacho(o):
    ev = ss.eventos.get(o["cot"], {})
    info = [("Evento", o["evento"]), ("Empresa", o["cliente"]), ("Cotización", o["cot"]), ("Fecha del evento", _f(o["fecha_evento"])),
            ("Lugar", ev.get("lugar", "")), ("Dirección", ev.get("direccion", "")), ("Montaje", ev.get("hora_montaje", "")),
            ("Quién recibe", " · ".join(x for x in (ev.get("recibe", ""), ev.get("telefono_recibe", "")) if x)),
            ("Estado de la orden", o["estado"]), ("Responsable de bodega", o["responsable"]),
            ("Despachada el", o["fecha_despacho"]), ("Vehículo", o["vehiculo"]), ("Chofer", o["chofer"]), ("Hora de salida", o["hora_salida"])]
    filas = [[l["articulo"], l["origen"] or "Adicional", l["unidad"], str(l["requerido"]), str(l["preparado"]), bool(l["listo"])] for l in o["lineas"]]
    bloques = [("info", info), ("seccion", "Artículos que salen de bodega"),
               ("tabla", ["ARTÍCULO", "PARA", "UNIDAD", "PEDIDO", "SALIÓ", "VERIF."], filas, [3.6, 3.6, 1.2, 1.1, 1.1, 1.1], {5})]
    retorn = [l["articulo"] for l in o["lineas"] if (item_por_codigo(l["item"]) or {}).get("tipo") == "Retornable"]
    if retorn:
        bloques.append(("nota", "Los artículos retornables deben volver a bodega al terminar el evento y se revisan con la orden de recepción."))
    if o["obs"].strip():
        bloques += [("seccion", "Observaciones"), ("nota", o["obs"])]
    bloques += [("firmas", ["Entrega · bodeguero", "Recibe · transporte", "Recibe · cliente"]),
                ("qr", url_orden(o["codigo"]), "Escanea con la cámara del celular para abrir esta orden en el ERP.")]
    return pdf_documento("Orden de despacho", o["codigo"], f"{o['evento']} · {o['cliente']}", bloques)


def _f(iso):
    try:
        return datetime.strptime(str(iso)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(iso)


def pdf_etiquetas(items):
    """Hoja de etiquetas con el QR de cada artículo (3 columnas por 8 filas)."""
    from reportlab.graphics import renderPDF
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfgen import canvas
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Etiquetas QR de inventario")
    cols, filas, mx, my = 3, 8, 1.1 * cm, 1.3 * cm
    w, h = (A4[0] - 2 * mx) / cols, (A4[1] - 2 * my) / filas
    for n, it in enumerate(items):
        k = n % (cols * filas)
        if n and k == 0:
            c.showPage()
        x, y = mx + (k % cols) * w, A4[1] - my - (k // cols + 1) * h
        c.setStrokeColorRGB(0.8, 0.84, 0.88)
        c.rect(x + 2, y + 2, w - 4, h - 4)
        lado = h - 1.0 * cm
        renderPDF.draw(qr_dibujo(url_item(it["codigo"]), lado), c, x + 0.35 * cm, y + 0.5 * cm)
        tx, ancho_t = x + lado + 0.6 * cm, w - lado - 0.9 * cm
        c.setFillColorRGB(0.06, 0.09, 0.16)
        c.setFont("Helvetica-Bold", 8.5)
        yy = y + h - 0.9 * cm
        for linea in simpleSplit(it["nombre"], "Helvetica-Bold", 8.5, ancho_t)[:3]:
            c.drawString(tx, yy, linea)
            yy -= 10.5
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.39, 0.45, 0.55)
        c.drawString(tx, yy - 2, it["codigo"])
        if it.get("ubicacion"):
            c.drawString(tx, yy - 13, it["ubicacion"][:26])
    c.save()
    return buf.getvalue()
