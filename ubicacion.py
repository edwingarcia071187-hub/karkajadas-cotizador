"""Búsqueda de lugares y direcciones (OpenStreetMap)."""



def _coords_en_texto(t):
    """Busca latitud y longitud dentro de un enlace de Google Maps o Waze."""
    import re
    from urllib.parse import unquote
    t = unquote(t)
    for patron in (r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", r"@(-?\d+\.\d+),(-?\d+\.\d+)", r"[?&](?:q|ll|query|center|destination|daddr)=(-?\d+\.\d+)[ ,]\s*(-?\d+\.\d+)"):
        m = re.search(patron, t)
        if m:
            return float(m.group(1)), float(m.group(2))
    return None


def _nombre_en_enlace(url):
    import re
    from urllib.parse import unquote_plus
    m = re.search(r"/place/([^/@?]+)", url)
    if m:
        n = unquote_plus(m.group(1)).strip()
        return "" if _coords_en_texto(n) else n
    return ""


def _http(url, leer=0):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "KarkajadasERP/1.0 (sistema interno de gestion de eventos)", "Accept-Language": "es"})
    with urllib.request.urlopen(req, timeout=8) as r:
        cuerpo = r.read(leer).decode("utf-8", "ignore") if leer else ""
        return r.geturl(), cuerpo


def _memoria():
    return {}


_MEM = _memoria()   # respuestas buenas de los buscadores (las fallas no se guardan, para poder reintentar)


def _json_de(url):
    import json as _json
    _, cuerpo = _http(url, leer=400000)
    return _json.loads(cuerpo)


def _arma_calles(via, num, zona, ciudad, respaldo=""):
    via = " ".join(x for x in (via, num) if x)
    return ", ".join(x for x in (via, zona, ciudad) if x) or respaldo


def reverse_punto(lat, lng):
    """Nombre del lugar y dirección aproximada (calle, sector, ciudad) de un punto del mapa. OpenStreetMap, con respaldo en Photon."""
    clave = ("rev", round(lat, 5), round(lng, 5))
    if clave in _MEM:
        return _MEM[clave]
    try:
        d = _json_de(f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=18&addressdetails=1&accept-language=es&lat={lat}&lon={lng}")
        a = d.get("address", {})
        r = {"nombre": d.get("name", ""), "falla": False,
             "calles": _arma_calles(a.get("road") or a.get("pedestrian") or "", a.get("house_number", ""),
                                    a.get("suburb") or a.get("neighbourhood") or a.get("quarter") or "",
                                    a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or "", d.get("display_name", ""))}
        _MEM[clave] = r
        return r
    except Exception:
        pass
    try:
        d = _json_de(f"https://photon.komoot.io/reverse?lat={lat}&lon={lng}")
        p = d["features"][0]["properties"]
        r = {"nombre": p.get("name", ""), "falla": False,
             "calles": _arma_calles(p.get("street", ""), p.get("housenumber", ""), p.get("district") or p.get("locality") or "", p.get("city") or p.get("county") or "")}
        _MEM[clave] = r
        return r
    except Exception:
        return {"nombre": "", "calles": "", "falla": True}


def buscar_lugar(texto):
    """Busca un lugar por palabras (ej. «Rincón de Puembo») en Ecuador. Devuelve (lista de hasta 5 resultados, error)."""
    from urllib.parse import quote_plus as _q
    clave = ("bus", texto.lower())
    if clave in _MEM:
        return _MEM[clave], ""
    sal, errores = [], []
    try:
        for d in _json_de(f"https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&countrycodes=ec&addressdetails=1&accept-language=es&q={_q(texto)}"):
            a = d.get("address", {})
            dn = d.get("display_name", "")
            sal.append({"ok": True, "lat": float(d["lat"]), "lng": float(d["lon"]), "nombre": d.get("name") or dn.split(",")[0],
                        "calles": _arma_calles(a.get("road") or a.get("pedestrian") or "", a.get("house_number", ""),
                                               a.get("suburb") or a.get("neighbourhood") or a.get("quarter") or a.get("village") or "",
                                               a.get("city") or a.get("town") or a.get("municipality") or a.get("county") or "", dn),
                        "etiqueta": ", ".join(dn.split(",")[:3])})
    except Exception as e:
        errores.append(f"OpenStreetMap: {type(e).__name__} {e}")
    if not sal:
        try:   # respaldo: Photon, limitado a Ecuador
            for f in _json_de(f"https://photon.komoot.io/api/?limit=5&bbox=-81.1,-5.1,-75.1,1.5&q={_q(texto)}")["features"]:
                p, (lng, lat) = f["properties"], f["geometry"]["coordinates"]
                zona = p.get("district") or p.get("locality") or ""
                ciudad = p.get("city") or p.get("county") or ""
                sal.append({"ok": True, "lat": lat, "lng": lng, "nombre": p.get("name", ""),
                            "calles": _arma_calles(p.get("street", ""), p.get("housenumber", ""), zona, ciudad, p.get("name", "")),
                            "etiqueta": ", ".join(x for x in (p.get("name", ""), zona or ciudad, p.get("state", "")) if x)})
        except Exception as e:
            errores.append(f"Photon: {type(e).__name__} {e}")
    if sal:
        _MEM[clave] = sal
        return sal, ""
    return [], ("; ".join(errores) if errores else "")


def resolver_ubicacion(enlace):
    """Del enlace (Google Maps, Waze, acortado o largo) saca el punto, el nombre del lugar y la dirección aproximada."""
    from urllib.parse import quote_plus as _q
    try:
        url, cuerpo = _http(enlace, leer=300000)
    except Exception:
        return {"ok": False, "error": "No pude abrir el enlace. Revisa que esté completo o escribe el nombre del lugar."}
    punto = _coords_en_texto(url) or _coords_en_texto(cuerpo[:300000])
    nombre = _nombre_en_enlace(url)
    if not punto and nombre:   # el enlace solo trae el nombre: se busca el punto
        lista, _ = buscar_lugar(nombre)
        if lista:
            punto = (lista[0]["lat"], lista[0]["lng"])
    if not punto:
        return {"ok": False, "error": "No encontré el punto en ese enlace. Prueba con el enlace de «Compartir» de la ubicación o elige el punto en el mapa."}
    r = reverse_punto(punto[0], punto[1])
    return {"ok": True, "lat": punto[0], "lng": punto[1], "nombre": nombre or r["nombre"], "calles": r["calles"]}
