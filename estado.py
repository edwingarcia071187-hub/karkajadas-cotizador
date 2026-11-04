"""Datos de ejemplo y estado inicial de la sesión."""
import streamlit as st
from constantes import CIUDADES, CIUDADES_BASE, CIUDADES_DEMO, EMPRESA_DATOS, EMPRESA_PROPIA, IVA_CLIENTE, SERVICIOS_PROPIOS, SIN_FILTRO

ss = st.session_state


def _item(servicio, fecha, cant, costo, iva, fee):
    return {"servicio": servicio, "proveedor": "Pro", "ciudad": "Quito", "fecha": fecha,
            "cantidad": cant, "costo": costo, "iva_prov": iva, "fee_pct": fee}


def migrar_datos():
    """Pone al día los datos de la sesión (también los creados con versiones anteriores de la app)."""
    for c in ss.cotizaciones_guardadas:
        c.setdefault("invitados", 100)
    for n, c in enumerate(ss.clientes_catalogo, 1):
        c.setdefault("id", f"CLI-{n:03d}")
        c.setdefault("contactos", [{"nombre": c.get("contacto", ""), "cargo": "", "correo": c.get("email", ""), "telefono": c.get("telefono", "")}]
                     if any(c.get(k) for k in ("contacto", "email", "telefono")) else [])
        c.setdefault("direcciones", [{"etiqueta": "Principal", "direccion": c.get("direccion", ""), "ciudad": c.get("ciudad", "")}] if c.get("direccion") else [])
        c.setdefault("web", "")
        c.setdefault("dias_credito", 30)
    for r in ss.proveedores_catalogo:
        r.pop("banco", None)
        r.pop("cuenta", None)
        r.setdefault("categoria", "")
        r.setdefault("descripcion", "")
    if "proveedores" not in ss:
        vistos = {}
        for r in ss.proveedores_catalogo:
            vistos.setdefault(r["proveedor"], r)
        ss.proveedores = [{"id": f"PRV-{n:03d}", "proveedor": nom, "ruc": "", "categoria": r["categoria"], "ciudad": r["ciudad"],
                           "observaciones": "", "contactos": [], "direcciones": [], "cuentas": []}
                          for n, (nom, r) in enumerate(vistos.items(), 1)]
    for n, p in enumerate(ss.proveedores, 1):
        p.setdefault("id", f"PRV-{n:03d}")
        for k in ("contactos", "direcciones", "cuentas"):
            p.setdefault(k, [])
        for k in ("ruc", "categoria", "observaciones"):
            p.setdefault(k, "")


def asegurar_proveedor_propio():
    if not any(p["proveedor"] == EMPRESA_PROPIA for p in ss.proveedores):
        ss.proveedores.append({"id": f"PRV-{len(ss.proveedores) + 1:03d}", "proveedor": EMPRESA_PROPIA, "ruc": "", "categoria": "Propio",
                               "ciudad": "Quito", "observaciones": "Servicios propios (salen de bodega)", "contactos": [], "direcciones": [], "cuentas": []})
    for nombre, precio in SERVICIOS_PROPIOS:
        if not any(r["proveedor"] == EMPRESA_PROPIA and r["servicio"] == nombre for r in ss.proveedores_catalogo):
            ss.proveedores_catalogo.append({"servicio": nombre, "proveedor": EMPRESA_PROPIA, "categoria": "Propio", "ciudad": "Quito",
                                            "precio_base": precio, "iva": 0.15, "descripcion": "Servicio propio"})


def iniciar_estado():
    """Crea los datos de ejemplo y el estado de la sesión la primera vez que se abre la app."""
    ss.setdefault("ciudades_extra", [])   # ciudades que se escriben con la opción "Otra..."
    CIUDADES[:] = CIUDADES_BASE + [c for c in ss.ciudades_extra if c not in CIUDADES_BASE] + ["Varias ciudades"]
    ss.setdefault("nav_menu", "Panel de control")
    ss.setdefault("items_cot", [])
    ss.setdefault("cotizacion_activa", None)
    ss.setdefault("filtro_estado_tabla", "Todas")
    ss.setdefault("cot_sid", 0)       # se incrementa en cada navegación: así los campos de la cotización arrancan limpios
    ss.setdefault("cot_base", None)   # "foto" del formulario al abrirlo / guardarlo, para detectar cambios sin guardar
    for _k, _v in SIN_FILTRO.items():
        ss.setdefault(_k, _v)
    if "proveedores_catalogo" not in ss:
        servicios_base = [
            ("Cabina fotográfica 360", "Entretenimiento", 300.0, 0.0),
            ("Carpa estructural 6x6", "Estructuras", 50.0, 0.15),
            ("Animador corporativo", "Animación", 150.0, 0.15),
            ("Catering premium", "Alimentos", 25.0, 0.15),
            ("Sonido profesional", "Audiovisual", 180.0, 0.15),
        ]
        ss.proveedores_catalogo = [
            {"servicio": s, "proveedor": f"Pro{cat} {ciu[:3].upper()}", "categoria": cat, "ciudad": ciu,
             "precio_base": precio, "iva": iva, "descripcion": "Estándar"}
            for ciu in CIUDADES_DEMO for s, cat, precio, iva in servicios_base
        ]
    if "cotizaciones_guardadas" not in ss:
        ss.cotizaciones_guardadas = [
            {"codigo": "KG-20261215-001", "evento": "Fiesta corporativa", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-12-15", "estado": "Aprobada", "total": 1414.00, "items": [_item("Cabina fotográfica", "2026-12-15", 1, 300.0, 0.0, 20.0)]},
            {"codigo": "KG-20261110-002", "evento": "Lanzamiento de marca", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-11-10", "estado": "Enviada", "total": 2248.40, "items": [_item("Sonido profesional", "2026-11-10", 1, 180.0, 0.15, 20.0)]},
            {"codigo": "KG-20261020-003", "evento": "Cena de directivos", "cliente": "Hilton Colón Quito", "fecha": "2026-10-20", "estado": "Borrador", "total": 834.50, "items": [_item("Catering premium", "2026-10-20", 1, 25.0, 0.15, 20.0)]},
            {"codigo": "KG-20260905-004", "evento": "Capacitación anual", "cliente": "Siemens Ecuador S.A.", "fecha": "2026-09-05", "estado": "Aprobada", "total": 3150.00, "items": [_item("Logística", "2026-09-05", 1, 1000.0, 0.0, 15.0)]},
            {"codigo": "KG-20260812-005", "evento": "Activación BTL", "cliente": "Corrugadora Nacional Cransa S.A.", "fecha": "2026-08-12", "estado": "Aprobada", "total": 1850.00, "items": [_item("Animador corporativo", "2026-08-12", 5, 150.0, 0.15, 20.0)]},
            {"codigo": "KG-20261006-007", "evento": "Feria cultural", "cliente": "Hilton Colón Quito", "fecha": "2026-10-06", "estado": "Aprobada", "total": 545.10, "items": [
                {"servicio": "Carpa 6x6 con 4 paredes", "proveedor": "Mario Mora - Bizion", "ciudad": "Guayaquil", "fecha": "2026-10-06", "cantidad": 1, "costo": 300.0, "iva_prov": 0.15, "fee_pct": 20.0},
                {"servicio": "Jenga gigante de madera", "proveedor": "Karkajadas Group", "ciudad": "Guayaquil", "fecha": "2026-10-06", "cantidad": 2, "costo": 30.0, "iva_prov": 0.0, "fee_pct": 0.0}]},
            {"codigo": "KG-20261005-006", "evento": "Feria de exposición", "cliente": "Hilton Colón Quito", "fecha": "2026-10-05", "estado": "Aprobada", "total": 2200.00, "items": [_item("Carpa", "2026-10-05", 2, 50.0, 0.15, 20.0)]},
        ]

        def _cot(cod, evento, cliente, fecha, estado, lineas):
            """lineas: (servicio, categoría, ciudad, cantidad, costo, iva, margen %). El proveedor sale del catálogo de ejemplo."""
            items = [{"servicio": sv, "proveedor": f"Pro{cat} {ciu[:3].upper()}", "ciudad": ciu, "fecha": fecha,
                      "cantidad": cant, "costo": costo, "iva_prov": iva, "fee_pct": fee} for sv, cat, ciu, cant, costo, iva, fee in lineas]
            total = sum(c * k * (1 + v) * (1 + f / 100) for _, _, _, c, k, v, f in lineas) * (1 + IVA_CLIENTE)
            return {"codigo": cod, "evento": evento, "cliente": cliente, "fecha": fecha, "estado": estado, "total": round(total, 2), "items": items}

        ss.cotizaciones_guardadas += [
            _cot("KG-20260918-008", "Convención anual de ventas", "Importadora Austral S.A.", "2026-09-18", "Aprobada",
                 [("Sonido profesional", "Audiovisual", "Cuenca", 1, 180.0, 0.15, 20.0), ("Catering premium", "Alimentos", "Cuenca", 120, 25.0, 0.15, 20.0)]),
            _cot("KG-20261003-009", "Fiesta de fin de año", "Hotel Costa Azul S.A.", "2026-10-03", "Enviada",
                 [("Carpa estructural 6x6", "Estructuras", "Manta", 3, 220.0, 0.15, 20.0), ("Animador corporativo", "Animación", "Manta", 2, 150.0, 0.15, 20.0)]),
            _cot("KG-20261112-010", "Lanzamiento de producto", "Grupo Litoral Cía. Ltda.", "2026-11-12", "Aprobada",
                 [("Cabina fotográfica 360", "Entretenimiento", "Guayaquil", 1, 300.0, 0.0, 20.0), ("Sonido profesional", "Audiovisual", "Guayaquil", 1, 180.0, 0.15, 20.0)]),
            _cot("KG-20260825-011", "Feria de emprendedores", "Importadora Austral S.A.", "2026-08-25", "Borrador",
                 [("Carpa estructural 6x6", "Estructuras", "Ambato", 4, 220.0, 0.15, 15.0)]),
            _cot("KG-20261205-012", "Gala empresarial", "Hotel Costa Azul S.A.", "2026-12-05", "Cancelada",
                 [("Catering premium", "Alimentos", "Manta", 200, 25.0, 0.15, 20.0), ("Animador corporativo", "Animación", "Manta", 1, 150.0, 0.15, 20.0)]),
            _cot("KG-20261022-013", "Activación de marca", "Grupo Litoral Cía. Ltda.", "2026-10-22", "Enviada",
                 [("Cabina fotográfica 360", "Entretenimiento", "Guayaquil", 2, 300.0, 0.0, 20.0), ("Animador corporativo", "Animación", "Guayaquil", 3, 150.0, 0.15, 20.0)]),
        ]
    if "clientes_catalogo" not in ss:
        ss.clientes_catalogo = [
            {"empresa": "Corrugadora Nacional Cransa S.A.", "ruc": "1791179382001", "ciudad": "Quito", "direccion": "Av. Galo Plaza", "web": "www.cransa.com", "contacto": "Compras", "email": "compras@cransa.com", "telefono": "02-2123-456", "dias_credito": 30},
            {"empresa": "Siemens Ecuador S.A.", "ruc": "1790151234001", "ciudad": "Quito", "direccion": "Av. República", "web": "www.siemens.ec", "contacto": "Logística", "email": "eventos@siemens.ec", "telefono": "02-393-2000", "dias_credito": 60},
            {"empresa": "Hilton Colón Quito", "ruc": "1790012345001", "ciudad": "Quito", "direccion": "Av. Patria", "web": "www.hilton.com", "contacto": "Eventos", "email": "eventos@hiltonquito.com", "telefono": "02-256-0666", "dias_credito": 15},
            {"empresa": "Importadora Austral S.A.", "ruc": "0190123456001", "ciudad": "Cuenca", "direccion": "Av. Ordóñez Lasso", "web": "www.austral.ec", "contacto": "Marketing", "email": "eventos@austral.ec", "telefono": "07-410-2233", "dias_credito": 30},
            {"empresa": "Hotel Costa Azul S.A.", "ruc": "1391234567001", "ciudad": "Manta", "direccion": "Malecón de Manta", "web": "www.costaazul.ec", "contacto": "Eventos", "email": "eventos@costaazul.ec", "telefono": "05-262-1100", "dias_credito": 15},
            {"empresa": "Grupo Litoral Cía. Ltda.", "ruc": "0991234567001", "ciudad": "Guayaquil", "direccion": "Av. Francisco de Orellana", "web": "www.grupolitoral.ec", "contacto": "Gerencia", "email": "gerencia@grupolitoral.ec", "telefono": "04-268-5500", "dias_credito": 45},
        ]
    ss.setdefault("fichas", {})
    ss.setdefault("eventos", {})
    ss.setdefault("hojas", {})        # checklist del bodeguero: {cotización: {servicio: [piezas]}}
    ss.setdefault("plantillas", {})   # piezas por servicio (por unidad), para no escribirlas otra vez
    migrar_datos()
    asegurar_proveedor_propio()
    ss.setdefault("empresa", {**EMPRESA_DATOS, "razon_social": "", "representante": "", "cargo_representante": "", "ciudad": "Quito",
                              "logo_b64": "", "cuentas": [], "validez_dias": 15, "forma_pago": "", "notas_comerciales": ""})
