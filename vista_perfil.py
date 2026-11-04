"""Perfil de la empresa."""
import streamlit as st
from html import escape as esc
from constantes import EMPRESA
from directorios import CFG_CUENTAS, COL_CUENTAS, editor_lista
from logo_datos import LOGO_B64
from utilidades import encabezado_estandar

ss = st.session_state


def mostrar(menu):
    encabezado_estandar("perfil", "Perfil de la empresa", "Se escribe una vez y sale en todos los documentos")
    emp = ss.empresa
    import base64 as _b64

    def _vista_encabezado():
        logo = emp.get("logo_b64") or LOGO_B64
        lineas = [x for x in (f"RUC {emp['ruc']}" if emp.get("ruc") else "", f"Tel. {emp['telefono']}" if emp.get("telefono") else "",
                              emp.get("correo", ""), emp.get("web", ""), emp.get("direccion", "")) if x]
        st.markdown(
            "<div style='display:flex; gap:22px; align-items:center; padding:6px 4px;'>"
            f"<img src='data:image/png;base64,{logo}' style='height:62px; max-width:190px; object-fit:contain;'/>"
            f"<div style='font-size:0.85rem; color:#475569; line-height:1.5;'><b style='color:#0F172A;'>{esc(emp.get('razon_social') or EMPRESA)}</b><br>"
            + " · ".join(esc(x) for x in lineas) + "</div></div>", unsafe_allow_html=True)

    t_dat, t_logo, t_cta, t_con, t_doc = st.tabs(["Datos generales", "Logo", "Cuentas bancarias", "Condiciones comerciales", "Documentación operativa"])

    with t_dat:
        with st.container(border=True, key="card_emp_prev"):
            st.markdown("<div class='sec-sub'>Así sale en los documentos</div>", unsafe_allow_html=True)
            _vista_encabezado()
        with st.container(border=True, key="card_emp_dat"):
            st.markdown("<div class='sec-sub'>Identificación</div>", unsafe_allow_html=True)
            a, b = st.columns(2)
            razon = a.text_input("Razón social", emp["razon_social"], key="emp_razon", placeholder="Nombre legal registrado en el SRI")
            ruc = b.text_input("RUC", emp["ruc"], key="emp_ruc", max_chars=13)
            a, b = st.columns(2)
            rep_n = a.text_input("Representante legal", emp["representante"], key="emp_rep")
            rep_c = b.text_input("Cargo", emp["cargo_representante"], key="emp_rep_c", placeholder="Gerente general")
            st.markdown("<div class='sec-sub'>Contacto y ubicación</div>", unsafe_allow_html=True)
            a, b = st.columns(2)
            tel = a.text_input("Teléfonos", emp["telefono"], key="emp_tel")
            correo = b.text_input("Correo", emp["correo"], key="emp_correo")
            a, b = st.columns(2)
            web = a.text_input("Sitio web", emp["web"], key="emp_web")
            ciudad_e = b.text_input("Ciudad", emp["ciudad"], key="emp_ciu")
            dire = st.text_input("Dirección", emp["direccion"], key="emp_dir")
            if st.button("Guardar datos", type="primary", key="emp_guardar"):
                if ruc.strip() and not (ruc.strip().isdigit() and len(ruc.strip()) == 13):
                    st.error("El RUC debe tener 13 números.")
                elif correo.strip() and "@" not in correo:
                    st.error("Revisa el correo: falta el @.")
                else:
                    emp.update({"razon_social": razon.strip(), "ruc": ruc.strip(), "representante": rep_n.strip(), "cargo_representante": rep_c.strip(),
                                "telefono": tel.strip(), "correo": correo.strip(), "web": web.strip(), "ciudad": ciudad_e.strip(), "direccion": dire.strip()})
                    st.toast("Datos de la empresa guardados", icon="✅")
                    st.rerun()

    with t_logo:
        with st.container(border=True, key="card_emp_logo"):
            st.markdown("<div class='sec-sub'>Logo de la empresa</div>", unsafe_allow_html=True)
            logo_actual = emp.get("logo_b64") or LOGO_B64
            st.markdown(f"<img src='data:image/png;base64,{logo_actual}' style='height:90px; max-width:300px; object-fit:contain; margin:4px 0 10px;'/>", unsafe_allow_html=True)
            arch = st.file_uploader("Subir un logo nuevo (PNG o JPG, de preferencia con fondo transparente)", type=["png", "jpg", "jpeg"], key="emp_logo_up")
            c1, c2 = st.columns([1, 1])
            if arch is not None and c1.button("Usar este logo", type="primary", key="emp_logo_ok"):
                emp["logo_b64"] = _b64.b64encode(arch.getvalue()).decode()
                st.rerun()
            if emp.get("logo_b64") and c2.button("Volver al logo original", key="emp_logo_reset"):
                emp["logo_b64"] = ""
                st.rerun()

    with t_cta:
        with st.container(border=True, key="card_emp_cta"):
            st.markdown("<div class='sec-sub'>Cuentas para recibir pagos</div>", unsafe_allow_html=True)
            st.caption("Salen al final de la cotización, en «Condiciones comerciales».")
            cuentas = editor_lista("emp_cuentas", emp["cuentas"], COL_CUENTAS, CFG_CUENTAS)
            if st.button("Guardar cuentas", type="primary", key="emp_cta_ok"):
                emp["cuentas"] = cuentas
                st.toast("Cuentas guardadas", icon="✅")
                st.rerun()

    with t_con:
        with st.container(border=True, key="card_emp_con"):
            st.markdown("<div class='sec-sub'>Condiciones que salen en la cotización</div>", unsafe_allow_html=True)
            a, b = st.columns([1, 3])
            validez = a.number_input("Validez de la oferta (días)", min_value=0, step=5, value=int(emp.get("validez_dias") or 0), key="emp_val")
            fpago = b.text_input("Forma de pago", emp.get("forma_pago", ""), key="emp_fpago", placeholder="Ej. 50% de anticipo y el saldo contra entrega")
            notas = st.text_area("Otras condiciones o notas", emp.get("notas_comerciales", ""), height=110, key="emp_notas",
                                 placeholder="Ej. Los precios no incluyen permisos municipales ni transporte fuera de la ciudad.")
            if st.button("Guardar condiciones", type="primary", key="emp_con_ok"):
                emp.update({"validez_dias": int(validez), "forma_pago": fpago.strip(), "notas_comerciales": notas.strip()})
                st.toast("Condiciones guardadas", icon="✅")
                st.rerun()

    with t_doc:
        with st.container(border=True, key="card_emp_doc"):
            st.markdown("<div class='sec-sub'>Documentación operativa</div>", unsafe_allow_html=True)
            st.info("Submódulo en construcción.")
            st.markdown("<div style='color:#475569; line-height:1.9;'>Lo que irá aquí:<br>"
                        "· Procedimientos paso a paso (montaje, bodega, atención al cliente)<br>"
                        "· Formatos y plantillas de la empresa<br>"
                        "· Normas de seguridad y checklists<br>"
                        "· Políticas internas y manual de funciones</div>", unsafe_allow_html=True)
