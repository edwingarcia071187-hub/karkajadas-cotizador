"""Documentos PDF: cotización, orden de servicios, ficha, pedido y checklist de bodega."""
import streamlit as st
from datetime import datetime
from constantes import EMPRESA, IVA_CLIENTE
from logo_datos import LOGO_B64
from utilidades import a_numero, calcular_linea, datos_empresa, dinero, fecha_larga, fmt_fecha, proveedor_de, texto_inclusion

ss = st.session_state


def generar_pdf(cot, cliente):
    """PDF de la cotización para el cliente. Incluye los datos del evento y del cliente y, por cada servicio,
    proveedor, servicio, fecha, ciudad, cantidad y subtotal. NO incluye costo unitario, IVA del proveedor,
    margen % ni margen $, ni los totales internos (costos operativos / rentabilidad). Requiere reportlab."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    AZUL, VERDE = colors.HexColor("#1E3A8A"), colors.HexColor("#059669")
    TINTA, GRIS = colors.HexColor("#0F172A"), colors.HexColor("#64748B")
    LINEA, FONDO = colors.HexColor("#CBD5E1"), colors.HexColor("#F1F5F9")

    def est(size, bold=False, color=TINTA, align=0, leading=None):
        return ParagraphStyle("x", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                              leading=leading or size * 1.3, textColor=color, alignment=align)

    def P(texto, **kw):
        return Paragraph(escape(str(texto)), est(**kw))

    cliente = cliente or {}
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2.2 * cm,
                            title=f"Cotización {cot['codigo']}", author="Karkajadas Group")
    ancho = doc.width
    historia = []

    # Encabezado
    cab = Table([[P("Karkajadas Group", size=22, bold=True, color=AZUL),
                  [P("COTIZACIÓN", size=9, bold=True, color=GRIS, align=TA_RIGHT),
                   P(cot["codigo"], size=15, bold=True, align=TA_RIGHT)]]], colWidths=[ancho * 0.55, ancho * 0.45])
    cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, 0), 2.5, VERDE),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    de = datos_empresa()
    linea_emp = " · ".join(x for x in (f"RUC {de['ruc']}" if de.get("ruc") else "", f"Tel. {de['telefono']}" if de.get("telefono") else "",
                                       de.get("correo", ""), de.get("web", ""), de.get("direccion", "")) if x)
    historia += [cab, Spacer(1, 4), P(linea_emp, size=8, color=GRIS), Spacer(1, 12)]

    # Datos del evento y del cliente
    def ficha(filas):
        filas = [(a, b) for a, b in filas if str(b).strip()]
        t = Table([[P(a.upper(), size=7, bold=True, color=GRIS), P(b, size=9.5)] for a, b in filas], colWidths=[3.0 * cm, None])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return t

    dias = cliente.get("dias_credito")
    evento = [("Referencia", cot["codigo"]), ("Evento", cot["evento"]), ("Fecha del evento", fmt_fecha(cot["fecha"])), ("Estado", cot["estado"])]
    datos_cli = [("Empresa", cot["cliente"]), ("RUC", cliente.get("ruc", "")), ("Ciudad", cliente.get("ciudad", "")),
                 ("Dirección", cliente.get("direccion", "")), ("Contacto", cliente.get("contacto", "")), ("Correo", cliente.get("email", "")),
                 ("Teléfono", cliente.get("telefono", "")), ("Sitio web", cliente.get("web", "")),
                 ("Pago", "Contado" if dias == 0 else f"{dias} días de crédito" if dias else "")]
    w = (ancho - 0.6 * cm) / 2
    info = Table([[P("DATOS DEL EVENTO", size=8.5, bold=True, color=AZUL), "", P("DATOS DEL CLIENTE", size=8.5, bold=True, color=AZUL)],
                  [ficha(evento), "", ficha(datos_cli)]], colWidths=[w, 0.6 * cm, w])
    info.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), FONDO), ("BACKGROUND", (2, 0), (2, -1), FONDO),
                              ("BOX", (0, 0), (0, -1), 0.6, LINEA), ("BOX", (2, 0), (2, -1), 0.6, LINEA),
                              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, -1), 10), ("LEFTPADDING", (2, 0), (2, -1), 10),
                              ("RIGHTPADDING", (0, 0), (0, -1), 8), ("RIGHTPADDING", (2, 0), (2, -1), 8),
                              ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, -1), (-1, -1), 8)]))
    historia += [info, Spacer(1, 16), P("SERVICIOS", size=10, bold=True, color=AZUL), Spacer(1, 5)]

    # Servicios (sin costo unitario, IVA del proveedor, margen % ni margen $)
    cols = [0.8, 5.6, 3.0, 2.6, 1.5, 3.5]
    filas = [[P(t, size=8, bold=True, color=colors.white, align=a) for t, a in
              [("#", TA_CENTER), ("SERVICIO", 0), ("FECHA", 0), ("CIUDAD", 0), ("CANT.", TA_RIGHT), ("SUBTOTAL", TA_RIGHT)]]]
    subtotal = 0.0
    for n, it in enumerate(cot["items"], 1):
        p_ven = calcular_linea(it)[2]
        subtotal += p_ven
        filas.append([P(n, size=9, align=TA_CENTER), P(it["servicio"], size=9, bold=True),
                      P(fmt_fecha(it["fecha"]), size=9), P(it["ciudad"], size=9), P(it["cantidad"], size=9, align=TA_RIGHT),
                      P(f"${p_ven:,.2f}", size=9, bold=True, align=TA_RIGHT)])
    tabla = Table(filas, colWidths=[c * cm for c in cols], repeatRows=1)
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
                               ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINEA), ("BOX", (0, 0), (-1, -1), 0.6, LINEA),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    historia += [tabla, Spacer(1, 12)]

    # Totales
    iva = subtotal * IVA_CLIENTE
    tot = Table([[P("Subtotal", size=9.5, color=GRIS), P(f"${subtotal:,.2f}", size=9.5, align=TA_RIGHT)],
                 [P(f"IVA {int(IVA_CLIENTE * 100)}%", size=9.5, color=GRIS), P(f"${iva:,.2f}", size=9.5, align=TA_RIGHT)],
                 [P("TOTAL INVERSIÓN", size=11, bold=True, color=AZUL), P(f"${subtotal + iva:,.2f}", size=13, bold=True, color=AZUL, align=TA_RIGHT)]],
                colWidths=[4.3 * cm, 3.2 * cm], hAlign="RIGHT")
    tot.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FONDO), ("BOX", (0, 0), (-1, -1), 0.6, LINEA), ("LINEABOVE", (0, 2), (-1, 2), 1, LINEA),
                             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                             ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    historia += [tot, Spacer(1, 14), P("Valores expresados en dólares americanos (USD).", size=8, color=GRIS)]
    cond = []
    if de.get("validez_dias"):
        cond.append(f"Validez de la oferta: {de['validez_dias']} días.")
    if str(de.get("forma_pago", "")).strip():
        cond.append(f"Forma de pago: {de['forma_pago'].strip()}")
    if str(de.get("notas_comerciales", "")).strip():
        cond.append(de["notas_comerciales"].strip())
    for c in de.get("cuentas", []):
        cond.append(f"Cuenta {c.get('tipo', '').lower()} {c.get('banco', '')} N.º {c.get('numero', '')} - {c.get('titular', '')}")
    if cond:
        historia += [Spacer(1, 10), P("CONDICIONES COMERCIALES", size=8.5, bold=True, color=AZUL), Spacer(1, 3)]
        historia += [P(x, size=8.5, color=GRIS) for x in cond]

    def pie(canvas, d):
        canvas.saveState()
        canvas.setStrokeColor(LINEA); canvas.setLineWidth(0.5)
        canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        canvas.setFont("Helvetica", 8); canvas.setFillColor(GRIS)
        canvas.drawString(2 * cm, 1.1 * cm, f"Karkajadas Group  ·  Cotización {cot['codigo']}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Página {d.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()


def _logo(ancho_cm):
    import base64
    from io import BytesIO
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Image
    datos = base64.b64decode(ss.empresa.get("logo_b64") or LOGO_B64)
    w, h = ImageReader(BytesIO(datos)).getSize()
    return Image(BytesIO(datos), width=ancho_cm * cm, height=ancho_cm * cm * h / w)


def pdf_documento(titulo, ref, subtitulo, bloques):
    """PDF con el estilo del ERP. bloques: ("info", [(etiqueta, valor)]) | ("seccion", texto) | ("nota", texto) |
    ("tabla", titulos, filas, anchos_relativos, columnas_casilla). En columnas de casilla, True = marcada."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    AZUL, VERDE = colors.HexColor("#1E3A8A"), colors.HexColor("#059669")
    TINTA, GRIS = colors.HexColor("#0F172A"), colors.HexColor("#64748B")
    LINEA, FONDO = colors.HexColor("#CBD5E1"), colors.HexColor("#F1F5F9")

    def P(texto, size=9.5, bold=False, color=TINTA, align=0):
        txt = escape(str(texto)).replace("\n", "<br/>")
        return Paragraph(txt, ParagraphStyle("x", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                                             leading=size * 1.3, textColor=color, alignment=align))

    def casilla(marcada):
        caja = Table([[P("X" if marcada else "", 8, True, colors.white, 1)]], colWidths=[0.5 * cm], rowHeights=[0.5 * cm])
        caja.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, VERDE if marcada else GRIS),
                                  ("BACKGROUND", (0, 0), (-1, -1), VERDE if marcada else colors.white),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                  ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        return caja

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.4 * cm,
                            bottomMargin=2.0 * cm, title=titulo, author=EMPRESA)
    ancho = doc.width
    d = datos_empresa()
    lineas_emp = [x for x in (f"RUC {d['ruc']}" if d.get("ruc") else "", f"Tel. {d['telefono']}" if d.get("telefono") else "",
                              d.get("correo", ""), d.get("web", ""), d.get("direccion", "")) if x]
    izq = [_logo(3.4), Spacer(1, 3)] + [P(x, 7.5, False, GRIS) for x in lineas_emp]
    cab = Table([[izq, [P(titulo.upper(), 9, True, GRIS, TA_RIGHT), P(ref, 15, True, TINTA, TA_RIGHT)]]], colWidths=[ancho * 0.55, ancho * 0.45])
    cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, 0), 2.5, VERDE),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    h = [cab]
    if subtitulo:
        h += [Spacer(1, 6), P(subtitulo, 10, False, GRIS)]
    h += [Spacer(1, 12)]

    for b in bloques:
        if b[0] == "info":
            filas = [(a, v) for a, v in b[1] if str(v).strip()]
            t = Table([[P(a.upper(), 7, True, GRIS), P(v, 9.5)] for a, v in filas], colWidths=[4.0 * cm, None])
            t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
            h += [t, Spacer(1, 12)]
        elif b[0] == "seccion":
            h += [Spacer(1, 4), P(b[1], 11, True, AZUL), Spacer(1, 4)]
        elif b[0] == "nota":
            h += [Spacer(1, 6), P(b[1], 8, False, GRIS)]
        elif b[0] == "tabla":
            _, titulos, filas, rel, cols_cas = b
            datos = [[P(x, 7.5, True, colors.white) for x in titulos]]
            for f in filas:
                datos.append([casilla(v) if i in cols_cas else P(v, 9) for i, v in enumerate(f)])
            tot = sum(rel)
            t = Table(datos, colWidths=[ancho * r / tot for r in rel], repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
                                   ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINEA),
                                   ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
            h += [t, Spacer(1, 10)]

    def pie(canvas, d):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(1.8 * cm, 1.0 * cm, f"{EMPRESA} · {ref}")
        canvas.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, f"Página {d.page}")
        canvas.restoreState()

    doc.build(h, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()


def pdf_ficha(cot, prov, ev, fp):
    """Ficha de contratación para el proveedor: lo más importante (fecha, horario, lugar y servicio) arriba y en grande;
    el resto, ordenado por bloques."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    AZUL, VERDE = colors.HexColor("#1E3A8A"), colors.HexColor("#059669")
    TINTA, GRIS = colors.HexColor("#0F172A"), colors.HexColor("#64748B")
    LINEA, FONDO, SUAVE = colors.HexColor("#CBD5E1"), colors.HexColor("#F1F5F9"), colors.HexColor("#EEF2FF")

    def P(t, size=9.5, bold=False, color=TINTA, align=0, lead=None, raw=False):
        txt = t if raw else escape(str(t)).replace("\n", "<br/>")
        return Paragraph(txt, ParagraphStyle("x", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                                             leading=lead or size * 1.3, textColor=color, alignment=align))

    def etiqueta(t):
        return P(t.upper(), 7, True, GRIS)

    saldo = a_numero(fp["total"]) - a_numero(fp["abono"])
    d = datos_empresa()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.3 * cm, bottomMargin=1.8 * cm,
                            title=f"Ficha de contratación {cot['codigo']} - {prov}", author=EMPRESA)
    w = doc.width - 12   # el área útil de la página descuenta 6 pt de relleno por lado
    sin_pad = [("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]

    # 1. Encabezado: logo y datos de la empresa a la izquierda; tipo de documento, referencia y proveedor a la derecha
    lineas_emp = [x for x in (f"RUC {d['ruc']}" if d.get("ruc") else "", f"Tel. {d['telefono']}" if d.get("telefono") else "",
                              d.get("correo", ""), d.get("web", ""), d.get("direccion", "")) if x]
    izq = [_logo(3.4), Spacer(1, 3)] + [P(x, 7.5, False, GRIS) for x in lineas_emp]
    der = [P("FICHA DE CONTRATACIÓN", 9, True, GRIS, TA_RIGHT), P(cot["codigo"], 15, True, TINTA, TA_RIGHT), Spacer(1, 4),
           P("PROVEEDOR", 7, True, GRIS, TA_RIGHT), P(prov, 11, True, AZUL, TA_RIGHT)]
    cab = Table([[izq, der]], colWidths=[w * 0.55, w * 0.45])
    cab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, 0), 2.5, VERDE), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))

    # 2. Datos clave, en grande: fecha, horario del evento y lugar
    lineas_h = [l for l in str(ev.get("horario", "")).split("\n") if l.strip()]
    h_evento = next((l.split(" - ", 1)[1] for l in lineas_h if l.startswith("Evento") and " - " in l), lineas_h[0] if lineas_h else "Por confirmar")
    lugar = ev.get("lugar") or ev.get("direccion") or "Por confirmar"
    clave = Table([[etiqueta("Fecha del servicio"), etiqueta("Horario del evento"), etiqueta("Lugar")],
                   [P(fecha_larga(ev["fecha_entrega"]), 12.5, True, AZUL, lead=15), P(h_evento, 12.5, True, AZUL, lead=15), P(lugar, 12.5, True, AZUL, lead=15)]],
                  colWidths=[w * 0.40, w * 0.25, w * 0.35])
    clave.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SUAVE), ("LINEABOVE", (0, 0), (-1, 0), 2, AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                               ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                               ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 10)]))

    # 3. Servicio contratado (lo más importante para el proveedor)
    serv = Table([[etiqueta("Servicio contratado")], [P(fp["servicio"], 11, True, TINTA, lead=14.5)]], colWidths=[w])
    serv.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, LINEA), ("LINEBEFORE", (0, 0), (0, -1), 4, VERDE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                              ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                              ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 10)]))

    # bloques con título y filas etiqueta / valor
    def bloque(titulo, filas, ancho):
        filas = [(a, v) for a, v in filas if str(v).strip()]
        t = Table([[P(a.upper(), 7, True, GRIS), v if not isinstance(v, str) else P(v, 9.5)] for a, v in filas], colWidths=[ancho * 0.34, ancho * 0.66])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINEA), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]))
        return [P(titulo, 10.5, True, AZUL), Spacer(1, 3), t]

    def dos(izq_, der_):
        t = Table([[izq_, "", der_]], colWidths=[w * 0.485, w * 0.03, w * 0.485])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")] + sin_pad))
        return t
    c = w * 0.485

    horas = []
    for l in lineas_h:
        if l.startswith("Nota:"):
            horas.append(("Nota", P(l[5:].strip(), 9, False, GRIS)))
        else:
            e, _, r = l.partition(" ")
            horas.append((e, r))
    montaje = ev.get("montaje")
    b_hor = bloque("Horarios", horas, c)
    b_evento = bloque("El evento", [("Cliente", cot["cliente"]), ("Temática", ev["tematica"]), ("Invitados", ev["invitados"]),
                                    ("Montaje", "No hay montaje" if montaje == "No" else "")], c)
    mapa = ev.get("enlace", "")
    b_ubi = bloque("Ubicación", [("Dirección", ev["direccion"]), ("Referencia", ev.get("referencia", "")),
                                 ("Mapa", P(f'<link href="{escape(mapa, {chr(34): "&quot;"})}" color="#1E3A8A">Abrir la ubicación en el mapa</link>', 9.5, raw=True) if mapa else ""),
                                 ("Ubicación enviada", ev["ubicacion"])], c)
    b_rec = bloque("Quién recibe y acceso", [("Persona que recibe", ev["recibe"]), ("Teléfono", ev["telefono_recibe"]),
                                              ("Documento de ingreso", ev["documento"])], c)

    # Condiciones económicas: total y saldo resaltados
    def cifra(et, valor, grande=False, color=TINTA):
        return [etiqueta(et), P(valor, 12 if grande else 10, True, color)]
    eco = Table([[cifra("Total", dinero(fp["total"]), True), cifra("Abono", dinero(fp["abono"])),
                  cifra("Saldo pendiente", dinero(saldo), True, colors.HexColor("#B91C1C") if saldo < 0 else AZUL), cifra("Garantía", dinero(fp["garantia"]))],
                 [cifra("Transporte", fp["transporte"]), cifra("Forma de pago", fp["pago"]), cifra("Factura", fp["factura"]), ""]],
                colWidths=[w * 0.25] * 4)
    eco.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, LINEA), ("LINEBELOW", (0, 0), (-1, 0), 0.3, LINEA), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                             ("BACKGROUND", (0, 0), (-1, 0), FONDO), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))

    inclusion = Table([[etiqueta("Inclusión y accesibilidad")], [P(texto_inclusion(ev, fp.get("alimentacion", True)), 9.5)]], colWidths=[w])
    inclusion.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FONDO), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, 0), 6),
                                   ("BOTTOMPADDING", (0, 0), (-1, 0), 1), ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 7)]))

    aviso = Table([[P("Su servicio es contratado por Karkajadas Group. Usted no está autorizado a dar información de precios, números de teléfono, "
                      "correos electrónicos ni ninguna información referente a su servicio.", 8.5, False, colors.white, lead=11)]], colWidths=[w])
    aviso.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINTA), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                               ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))

    historia = [cab, Spacer(1, 10), clave, Spacer(1, 8), serv, Spacer(1, 12), dos(b_hor, b_evento), Spacer(1, 10), dos(b_ubi, b_rec), Spacer(1, 10), inclusion,
                Spacer(1, 12), P("Condiciones económicas", 10.5, True, AZUL), Spacer(1, 3), eco]
    if str(ev.get("observacion", "")).strip():
        historia += [Spacer(1, 12), P("Observaciones", 10.5, True, AZUL), Spacer(1, 3), P(ev["observacion"], 9, False, GRIS, lead=12)]
    historia += [Spacer(1, 12), KeepTogether([aviso])]

    def pie(canvas, dd):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawString(1.8 * cm, 1.0 * cm, f"{EMPRESA} · Ficha de contratación · {cot['codigo']} · Emitida el {fecha_larga(datetime.now())}")
        canvas.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, f"Página {dd.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()


def pdf_orden(cot, prov, items):
    p = proveedor_de(prov)
    con = p.get("contactos", [])
    filas = [[False, i["servicio"], fecha_larga(i["fecha"]), i["ciudad"], str(i["cantidad"]), ""] for i in items]
    bloques = [("info", [("Proveedor", prov), ("Contacto", f"{con[0]['nombre']} - {con[0]['telefono']}" if con else ""),
                         ("Cotización aprobada", cot["codigo"]), ("Evento", cot["evento"]), ("Cliente", cot["cliente"]),
                         ("Fecha de emisión", fecha_larga(datetime.now()))]
                        + ([("Inclusión y accesibilidad", texto_inclusion(ss.eventos[cot["codigo"]]))] if cot["codigo"] in ss.eventos else [])),
               ("seccion", "Servicios a contratar"),
               ("tabla", ["", "SERVICIO", "FECHA", "CIUDAD", "CANT.", "OBSERVACIONES"], filas, [0.5, 3.6, 2.8, 1.5, 0.9, 2.4], {0}),
               ("nota", "Marque cada servicio al confirmarlo con el proveedor.")]
    return pdf_documento("Orden de servicios", cot["codigo"], None, bloques)


def _info_evento(cot, ev):
    return [("Cotización aprobada", cot["codigo"]), ("Evento", cot["evento"]), ("Cliente", cot["cliente"]),
            ("Fecha de entrega", fecha_larga(ev["fecha_entrega"])), ("Lugar", ev["lugar"]), ("Dirección", ev["direccion"]), ("Referencia", ev.get("referencia", "")), ("Mapa", ev.get("enlace", "")),
            ("Horario", ev["horario"]), ("Montaje", f"{ev['montaje']} - {ev['hora_montaje']}".strip(" -")), ("Desmontaje", ev["desmontaje"]),
            ("Recibe", f"{ev['recibe']} - {ev['telefono_recibe']}".strip(" -")),
            ("Inclusión y accesibilidad", texto_inclusion(ev)), ("Observación", ev["observacion"])]


def pdf_pedido_bodega(cot, items, ev):
    """Pedido a bodega generado desde la cotización: solo servicios propios, sin proveedores ni precios."""
    filas = [[i["servicio"], str(i["cantidad"]), fmt_fecha(i["fecha"]), i["ciudad"], ""] for i in items]
    bloques = [("info", _info_evento(cot, ev)), ("seccion", "Servicios a despachar"),
               ("tabla", ["SERVICIO", "CANT.", "FECHA", "CIUDAD", "OBSERVACIONES"], filas, [4.2, 1.0, 1.8, 1.8, 2.8], set()),
               ("nota", "El bodeguero detalla las piezas de cada servicio en su checklist.")]
    return pdf_documento("Pedido a bodega", cot["codigo"], None, bloques)


def pdf_hoja_bodega(cot, items, ev):
    """Checklist detallado del bodeguero: piezas de cada servicio, con salida y retorno."""
    bloques = [("info", _info_evento(cot, ev))]
    for it in items:
        bloques.append(("seccion", f"{it['servicio']} - {it['cantidad']} unidad(es) - {fmt_fecha(it['fecha'])}"))
        hoja = ss.hojas.get(cot["codigo"], {}).get(it["servicio"], [])
        if not hoja:
            bloques.append(("nota", "El bodeguero aún no ha detallado las piezas de este servicio."))
            continue
        filas = [[p["pieza"], str(p["cantidad"]), bool(p["salio"]), bool(p["regreso"]), p.get("obs", "")] for p in hoja]
        bloques.append(("tabla", ["PIEZA", "CANT.", "SALIÓ", "REGRESÓ", "OBSERVACIONES"], filas, [3.8, 0.9, 1.0, 1.1, 3.2], {2, 3}))
    return pdf_documento("Checklist de bodega", cot["codigo"], "Revisión de piezas a la salida y al regreso", bloques)
