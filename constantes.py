"""Constantes del ERP: listas, nombres de menú y datos fijos de la empresa."""



ESTADOS = ["Aprobada", "Enviada", "Borrador", "Cancelada"]


MENU_CLIENTES = "Directorio de clientes"


MENU_PROVEEDORES = "Directorio de proveedores"


COLORES = {   # paleta de datos sobria: distinta a los botones (verde = confirmar, azul = neutro)
    "Aprobada": "#2C8C84",   # verde azulado
    "Enviada": "#7A68B5",    # lavanda
    "Borrador": "#B8913F",   # arena
    "Cancelada": "#B85C78",  # rosa antiguo
}


MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


CIUDADES_DEMO = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Varias ciudades"]   # solo para el catálogo de ejemplo


CIUDADES_BASE = ["Quito", "Guayaquil", "Cuenca", "Santo Domingo de los Tsáchilas", "Machala", "Manta", "Portoviejo", "Ambato",
                 "Riobamba", "Loja", "Ibarra", "Esmeraldas", "Latacunga"]


OTRA = "Otra..."


CIUDADES = CIUDADES_BASE + ["Varias ciudades"]


NUEVO_CLIENTE = "+ Registrar nuevo cliente..."


IVA_CLIENTE = 0.15


SIN_FILTRO = {"f_emp": "Todas", "f_mes": "Todos", "f_ciu": "Todas", "b_u": ""}


# --- Datos del módulo de órdenes de servicio: Karkajadas como proveedor propio, eventos, fichas y pedido a bodega
EMPRESA_PROPIA = "Karkajadas Group"


SERVICIOS_PROPIOS = [("Jenga gigante de madera", 60.0), ("Cuatro en raya gigante", 50.0), ("Rompecabezas gigante", 75.0),
                     ("Alquiler de parlante con micrófonos", 90.0), ("Decoración con globos", 120.0), ("Coach de liderazgo", 200.0)]


EMPRESA = "Karkajadas Group"


EMPRESA_DATOS = {"web": "www.karkajadasgroup.com", "ruc": "1713272845001", "telefono": "0998526514 / 02 3076303",
                 "correo": "edwin.garcia@karkajadasgroup.com", "direccion": "La Victoria Baja, Calle D, Lote 50 B"}


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


OBS_BASE = ("El equipo de Karkajadas Group estará en constante coordinación con el cliente y el proveedor.\n\n"
            "El personal debe llevar los implementos de seguridad industrial básicos para el montaje.")


DOCUMENTOS_INGRESO = ["Cédula de identidad", "Cédula y RUC de la empresa", "Pasaporte", "Credencial del proveedor", "Ninguno"]


MENU_PRINCIPAL = ["Panel de control", "Reportes financieros", "Proyecciones de ventas", "Noticias corporativas"]


MENU_SOPORTE = ["Centro de ayuda"]


MENU_PERFIL = "Perfil de la empresa"


CATALOGOS = {"Catálogo regular": "regular", "Catálogo navideño": "navidad"}   # menú -> catálogo del cotizador


MENU_PROV = "Órdenes a proveedores"


MENU_BODEGA = "Bodega"
MENU_LOGISTICA = "Logística"


MENU_REPORTES = "Reportes financieros"


# Cada sección tiene un tono propio y apagado (franja izquierda, etiqueta y fondo muy tenue); la opción activa se resalta
SECCIONES = [
    ("pri", None, MENU_PRINCIPAL, "#94A3B8"),
    ("cat", "COTIZADOR DE CATÁLOGOS", list(CATALOGOS), "#5FA8A0"),
    ("dir", "DIRECTORIOS", [MENU_CLIENTES, MENU_PROVEEDORES], "#9B8EC9"),
    ("ope", "OPERACIONES", [MENU_PROV, MENU_BODEGA, MENU_LOGISTICA], "#C9A961"),
    ("emp", "MI EMPRESA", [MENU_PERFIL], "#7C9CBF"),
    ("sop", "SOPORTE Y PROCESOS", MENU_SOPORTE, "#C28A9B"),
]
