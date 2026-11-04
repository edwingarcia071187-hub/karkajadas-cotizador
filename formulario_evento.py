"""Formulario de los datos del evento (fechas, ubicación con mapa, inclusión, quién recibe)."""
import streamlit as st
from datetime import date
from datetime import datetime
from html import escape as esc
from urllib.parse import quote_plus
from constantes import DOCUMENTOS_INGRESO
from ubicacion import buscar_lugar, resolver_ubicacion, reverse_punto
from utilidades import _a_fecha, _a_hora, _hh, cliente_de, evento_inicial, fecha_larga

ss = st.session_state


def bloque_evento(cot, sufijo):
    """Datos del evento (se llenan una vez por cotización; los usan las fichas y bodega). Fechas con calendario y horas con reloj."""
    cod, cli = cot["codigo"], cliente_de(cot)
    ev = {**evento_inicial(cot), **ss.eventos.get(cod, {})}
    contactos = cli.get("contactos", [])
    k = f"{sufijo}_{cod}"
    ev["fecha_entrega"] = min(i["fecha"] for i in cot["items"])   # vienen de la cotización aprobada: no se editan aquí
    ev["tematica"] = cot["evento"]
    ev["invitados"] = str(cot.get("invitados", "") or "")
    f_base = _a_fecha(ev["fecha_entrega"], date.today())

    with st.container(border=True, key=f"card_ev_{k}"):
        st.markdown("<div class='sec-sub'>El evento</div>", unsafe_allow_html=True)
        a, b, c3 = st.columns([1.1, 1.3, 1])
        f_ent = a.date_input("Fecha de entrega del servicio", value=f_base, key=f"ev_f_{k}", disabled=True, help="Viene de la cotización aprobada")
        inv = c3.number_input("Invitados (aprox.)", min_value=0, value=int(cot.get("invitados", 0) or 0), key=f"ev_i_{k}", disabled=True,
                              help="Viene de la cotización aprobada")
        tema = b.text_input("Temática", ev["tematica"], key=f"ev_t_{k}", disabled=True, help="Viene de la cotización aprobada")
        pkey = f"pto_{k}"
        if pkey not in ss and ev.get("lat"):
            ss[pkey] = {"ok": True, "lat": ev["lat"], "lng": ev["lng"], "nombre": ev["lugar"], "calles": ev["direccion"], "aceptada": True}
        lugar = ss.get(f"lug_{k}", ev["lugar"])

        def _aceptar(k=k, pkey=pkey):
            u = ss.get(pkey)
            if u and u.get("ok"):
                ss[f"ev_d_{k}"] = u["calles"]
                ss[f"ev_e_{k}"] = f"https://www.google.com/maps?q={u['lat']:.6f},{u['lng']:.6f}"   # enlace del punto elegido
                ss[f"lug_{k}"] = u.get("nombre", "")
                ss[pkey] = {**u, "aceptada": True}

        st.markdown("<div class='sec-sub'>Ubicación</div>", unsafe_allow_html=True)
        def _buscar(k=k, pkey=pkey):
            texto = (ss.get(f"ev_q_{k}") or "").strip()
            ss.pop(f"err_{k}", None)
            ss.pop(f"res_{k}", None)
            ss.pop(f"sel_{k}", None)
            if not texto:
                return
            if texto.startswith("http"):
                r = resolver_ubicacion(texto)
                lista = [r] if r.get("ok") else None
                if not lista:
                    ss[f"err_{k}"] = r["error"]
            else:
                lista, falla = buscar_lugar(texto)
                if falla:
                    ss[f"err_{k}"] = f"No pude consultar el buscador de lugares ({falla}). Elige el punto en el mapa o inténtalo de nuevo en un momento."
                elif not lista:
                    ss[f"err_{k}"] = f"No encontré «{texto}». Prueba con otras palabras (por ejemplo, el sector y la ciudad) o haz clic en el mapa."
                    lista = None
            if lista:
                ss[pkey] = lista[0]
                ss[f"zm_{k}"] = 17
                if len(lista) > 1:
                    ss[f"res_{k}"] = lista

        def _elegir_resultado(k=k, pkey=pkey):
            lista = ss.get(f"res_{k}") or []
            i = ss.get(f"sel_{k}")
            if i is not None and 0 <= i < len(lista):
                ss[pkey] = lista[i]
                ss[f"zm_{k}"] = 17

        e1, e2 = st.columns([4, 1], vertical_alignment="bottom")
        e1.text_input("Buscar un lugar o pegar un enlace de Google Maps o Waze", key=f"ev_q_{k}", on_change=_buscar,
                      placeholder="Ej. Rincón de Puembo, o pega aquí el enlace que te compartieron")
        e2.button("Buscar", key=f"ev_bu_{k}", use_container_width=True, type="secondary", on_click=_buscar)
        if ss.get(f"err_{k}"):
            st.warning(ss[f"err_{k}"])
        if ss.get(f"res_{k}"):
            lista = ss[f"res_{k}"]
            st.selectbox("Se encontraron varios lugares: elige el correcto", range(len(lista)), format_func=lambda i: f"{lista[i]['nombre']} - {lista[i]['etiqueta']}",
                         key=f"sel_{k}", on_change=_elegir_resultado)
        u = ss.get(pkey)
        try:
            import folium
            from streamlit_folium import st_folium
        except ImportError:
            folium = None
        m1, m2 = st.columns([1.7, 1])
        with m1:
            if folium is None:
                st.warning("Falta instalar el componente del mapa para poder hacer clic en él: sube el archivo requirements.txt a GitHub y reinicia la app. Mientras tanto se muestra una vista previa.")
                st.iframe(f"https://maps.google.com/maps?q={u['lat']},{u['lng']}&z=17&output=embed&hl=es" if u else "https://maps.google.com/maps?q=Quito,Ecuador&z=12&output=embed&hl=es", height=300)
            else:
                centro = [u["lat"], u["lng"]] if u else [-0.1807, -78.4678]
                mapa = folium.Map(location=centro, zoom_start=ss.get(f"zm_{k}") or (17 if u else 12), tiles="OpenStreetMap", control_scale=True)
                if u:
                    folium.Marker(centro, icon=folium.Icon(color="darkblue", icon="map-marker", prefix="fa")).add_to(mapa)
                res = st_folium(mapa, height=330, use_container_width=True, key=f"mapa_{k}", returned_objects=["last_clicked", "zoom"])
                if res and res.get("zoom"):
                    ss[f"zm_{k}"] = res["zoom"]
                cl = res.get("last_clicked") if res else None
                if cl and (round(cl["lat"], 7), round(cl["lng"], 7)) != ss.get(f"clk_{k}"):
                    ss[f"clk_{k}"] = (round(cl["lat"], 7), round(cl["lng"], 7))
                    rr = reverse_punto(cl["lat"], cl["lng"])
                    ss[pkey] = {"ok": True, "lat": cl["lat"], "lng": cl["lng"], "nombre": rr["nombre"], "calles": rr["calles"]}
                    st.rerun()
        with m2:
            if not u:
                st.markdown("<div class='col-head'>Cómo elegir el punto</div><div style='color:#475569; line-height:1.6; margin-top:4px;'>"
                            "Escribe el nombre del lugar arriba, haz clic en el mapa donde será el evento, o pega el enlace que te compartieron.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='col-head'>Punto elegido</div>"
                            f"<div style='font-weight:700; margin:2px 0 10px;'>{esc(u.get('nombre') or '') or 'Sin nombre'}</div>"
                            "<div class='col-head'>Dirección aproximada</div>"
                            f"<div style='margin:2px 0 12px;'>{esc(u.get('calles') or '') or 'No se pudo obtener; escríbela abajo'}</div>", unsafe_allow_html=True)
                if u.get("aceptada"):
                    st.success("Dirección aceptada")
                else:
                    st.button("Aceptar dirección", type="primary", key=f"ev_ac_{k}", on_click=_aceptar, use_container_width=True)
                    st.caption("Al aceptar se completan la dirección y el enlace. Si no es el punto exacto, haz clic en otro lugar del mapa.")

        d1, d2, d3 = st.columns([1.4, 1.2, 1.2])
        direccion = d1.text_area("Dirección", ev["direccion"], height=96, key=f"ev_d_{k}")
        referencia = d2.text_area("Referencia (opcional)", ev.get("referencia", ""), height=96, key=f"ev_rf_{k}",
                                  placeholder="Ej. Portón azul, frente al parque, preguntar por Juan en recepción")
        enlace = d3.text_area("Enlace de la ubicación", ev.get("enlace", ""), height=96, key=f"ev_e_{k}",
                              placeholder="Se completa solo al aceptar la dirección")
        texto_mapa = " ".join(x for x in (lugar.strip(), direccion.strip()) if x)
        if texto_mapa:
            q = quote_plus(texto_mapa + ", Ecuador")
            b1, b2, b3 = st.columns([1, 1, 1])
            b1.link_button("Buscar en Google Maps", f"https://www.google.com/maps/search/?api=1&query={q}", use_container_width=True)
            if enlace.strip().startswith("http"):
                b2.link_button("Abrir el enlace de la ubicación", enlace.strip(), use_container_width=True)

        st.markdown("<div class='sec-sub'>Horarios</div>", unsafe_allow_html=True)
        # cuadrícula: el evento y, en una sola fila, el montaje y el desmontaje (se bloquean si no hay montaje)
        g = [1.0, 1.5, 1.0, 1.0, 1.3]
        hd = st.columns(g)
        for col, t in zip(hd, ["", "Fecha", "Desde", "Hasta", ""]):
            col.markdown(f"<span class='col-head'>{t}</span>", unsafe_allow_html=True)
        r = st.columns(g, vertical_alignment="center")
        r[0].markdown("<b>Evento</b>", unsafe_allow_html=True)
        f_eve = r[1].date_input("Fecha del evento", value=_a_fecha(ev.get("f_evento", ""), f_base), key=f"ev_fe_{k}", label_visibility="collapsed")
        h_ini = r[2].time_input("Evento desde", value=_a_hora(ev.get("h_ini", ""), datetime.strptime("09:00", "%H:%M").time()), step=900, key=f"ev_hi_{k}", label_visibility="collapsed")
        h_fin = r[3].time_input("Evento hasta", value=_a_hora(ev.get("h_fin", ""), datetime.strptime("12:00", "%H:%M").time()), step=900, key=f"ev_hf_{k}", label_visibility="collapsed")
        t1, t2 = st.columns([1.0, 4.8], vertical_alignment="center")
        t1.markdown("<b>Montaje y desmontaje</b>", unsafe_allow_html=True)
        mon = t2.segmented_control("¿Hay montaje?", ["Sí", "No"], default="Sí" if ev["montaje"] != "No" else "No", key=f"ev_m_{k}", label_visibility="collapsed") or "Sí"
        sin = mon == "No"
        g2 = [1.0, 1.5, 1.0, 1.5, 1.0]
        m = st.columns(g2)
        t_mon, t_des = datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("13:00", "%H:%M").time()
        if sin:   # sin montaje: no hay nada que llenar (se muestran apagados)
            for col, t in zip(m[1:], ["Fecha del montaje", "Hora del montaje", "Fecha del desmontaje", "Hora del desmontaje"]):
                col.markdown(f"<div style='font-size:0.875rem; color:#94A3B8; margin-bottom:6px;'>{t}</div>"
                             "<div style='background:#F1F5F9; border:1px solid #E2E8F0; border-radius:8px; height:40px; line-height:40px; padding:0 12px; color:#94A3B8;'>No aplica</div>",
                             unsafe_allow_html=True)
            f_mon = f_des = f_base
            h_mon, h_des = t_mon, t_des
        else:
            f_mon = m[1].date_input("Fecha del montaje", value=_a_fecha(ev.get("f_montaje", ""), f_base), key=f"ev_fm_{k}")
            h_mon = m[2].time_input("Hora del montaje", value=_a_hora(ev.get("h_montaje", ""), t_mon), step=900, key=f"ev_hm_{k}")
            f_des = m[3].date_input("Fecha del desmontaje", value=_a_fecha(ev.get("f_desm", ""), f_base), key=f"ev_fd_{k}")
            h_des = m[4].time_input("Hora del desmontaje", value=_a_hora(ev.get("h_desm", ""), t_des), step=900, key=f"ev_hd_{k}")
        obs_h = st.text_input("Nota sobre los horarios (opcional)", ev.get("obs_horario", ""),
                              placeholder="Ej. El horario del desmontaje puede variar según el cierre del evento", key=f"ev_oh_{k}")
        if h_fin <= h_ini:
            st.warning("La hora de fin del evento debe ser posterior a la de inicio.")

        st.markdown("<div class='sec-sub'>Inclusión y necesidades especiales</div>", unsafe_allow_html=True)
        st.caption("Solo cantidades de personas, sin nombres. Sale en las fichas de los proveedores para que se preparen.")
        inc0 = ev.get("inclusion") or {}
        hay = any(v for v in inc0.values())
        tiene_inc = st.segmented_control("¿El evento tiene personas con necesidades especiales?", ["Sí", "No"], default="Sí" if hay else "No", key=f"in_si_{k}") or "No"
        vegt = vega = glut = aler = movi = visu = audi = otra = 0
        nota_ali = nota_acc = ""
        if tiene_inc == "Sí":
            st.markdown("<span class='col-head'>Alimentación</span>", unsafe_allow_html=True)
            i1, i2, i3, i4 = st.columns(4)
            vegt = i1.number_input("Vegetarianos", min_value=0, step=1, value=int(inc0.get("vegetarianos", 0)), key=f"in_v_{k}")
            vega = i2.number_input("Veganos", min_value=0, step=1, value=int(inc0.get("veganos", 0)), key=f"in_vg_{k}")
            glut = i3.number_input("Sin gluten (celíacos)", min_value=0, step=1, value=int(inc0.get("sin_gluten", 0)), key=f"in_g_{k}")
            aler = i4.number_input("Con alergias alimentarias", min_value=0, step=1, value=int(inc0.get("alergias", 0)), key=f"in_a_{k}")
            nota_ali = st.text_input("Detalle de alergias u otras restricciones (opcional)", inc0.get("nota_ali", ""), key=f"in_na_{k}",
                                     placeholder="Ej. Alergia a mariscos y maní; una persona sin lactosa")
            st.markdown("<span class='col-head'>Accesibilidad</span>", unsafe_allow_html=True)
            j1, j2, j3, j4 = st.columns(4)
            movi = j1.number_input("Movilidad reducida o silla de ruedas", min_value=0, step=1, value=int(inc0.get("movilidad", 0)), key=f"in_m_{k}")
            visu = j2.number_input("Discapacidad visual", min_value=0, step=1, value=int(inc0.get("visual", 0)), key=f"in_vi_{k}")
            audi = j3.number_input("Discapacidad auditiva", min_value=0, step=1, value=int(inc0.get("auditiva", 0)), key=f"in_au_{k}")
            otra = j4.number_input("Otra necesidad", min_value=0, step=1, value=int(inc0.get("otra_acc", 0)), key=f"in_o_{k}")
            nota_acc = st.text_input("Qué se necesita (opcional)", inc0.get("nota_acc", ""), key=f"in_nc_{k}",
                                     placeholder="Ej. Rampa en el ingreso, espacio frente al escenario, intérprete de lengua de señas")

        st.markdown("<div class='sec-sub'>Quién recibe y requisitos</div>", unsafe_allow_html=True)
        c2, c3 = st.columns(2)
        recibe = c2.text_input("Persona que recibe", ev["recibe"], key=f"ev_n_{k}")
        tel = c3.text_input("Teléfono de quien recibe", ev["telefono_recibe"], key=f"ev_p_{k}")
        u1, u2 = st.columns([1, 2])
        ubic = u1.segmented_control("Ubicación enviada", ["Pendiente", "Enviada"], default="Enviada" if ev["ubicacion"] == "Enviada" else "Pendiente", key=f"ev_u_{k}") or "Pendiente"
        docs = DOCUMENTOS_INGRESO if ev["documento"] in DOCUMENTOS_INGRESO or not ev["documento"] else DOCUMENTOS_INGRESO + [ev["documento"]]
        doc_in = u2.selectbox("Documento requerido para el ingreso", docs, index=docs.index(ev["documento"]) if ev["documento"] in docs else 0,
                              accept_new_options=True, key=f"ev_di_{k}")
        obs = st.text_area("Observaciones generales", ev["observacion"], height=110, key=f"ev_ob_{k}")

        if st.button("Guardar datos del evento", type="primary", key=f"ev_save_{k}"):
            fm = lambda d: d.strftime("%d/%m/%Y")
            lineas = []
            if mon == "Sí":
                lineas.append(f"Montaje {fm(f_mon)} - A partir de las {_hh(h_mon)}")
            lineas.append(f"Evento {fm(f_eve)} - {h_ini:%H:%M} a {h_fin:%H:%M}")
            if mon == "Sí":
                lineas.append(f"Desmontaje {fm(f_des)} - A partir de las {_hh(h_des)}")
            if obs_h.strip():
                lineas.append(f"Nota: {obs_h.strip()}")
            ss.eventos[cod] = {
                "fecha_entrega": f_ent.strftime("%Y-%m-%d"), "invitados": str(inv) if inv else "", "lugar": lugar, "direccion": direccion, "lat": (ss.get(pkey) or {}).get("lat"), "lng": (ss.get(pkey) or {}).get("lng"),
                "ubicacion": ubic, "horario": "\n".join(lineas), "tematica": tema, "recibe": recibe, "telefono_recibe": tel,
                "montaje": mon,
                "inclusion": {"vegetarianos": int(vegt), "veganos": int(vega), "sin_gluten": int(glut), "alergias": int(aler), "nota_ali": nota_ali.strip(),
                              "movilidad": int(movi), "visual": int(visu), "auditiva": int(audi), "otra_acc": int(otra), "nota_acc": nota_acc.strip()}, "enlace": enlace.strip(), "referencia": referencia.strip(),
                "hora_montaje": f"{fecha_larga(f_mon)} a partir de las {_hh(h_mon)}" if mon == "Sí" else "No aplica",
                "desmontaje": f"{fecha_larga(f_des)} a partir de las {_hh(h_des)}" if mon == "Sí" else "No aplica", "documento": doc_in, "observacion": obs,
                "f_montaje": f_mon.strftime("%Y-%m-%d"), "h_montaje": f"{h_mon:%H:%M}",
                "f_evento": f_eve.strftime("%Y-%m-%d"), "h_ini": f"{h_ini:%H:%M}", "h_fin": f"{h_fin:%H:%M}",
                "f_desm": f_des.strftime("%Y-%m-%d"), "h_desm": f"{h_des:%H:%M}", "obs_horario": obs_h.strip()}
            st.rerun()
    return {**evento_inicial(cot), **ss.eventos.get(cod, {})}
