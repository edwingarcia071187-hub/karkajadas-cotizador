"""Karkajadas Group - ERP. Archivo principal: solo arma la pantalla y dirige cada opción del menú a su módulo."""
import streamlit as st

st.set_page_config(page_title="Karkajadas Group - ERP", layout="wide", initial_sidebar_state="expanded")

from constantes import CATALOGOS, MENU_BODEGA, MENU_CLIENTES, MENU_PERFIL, MENU_PRINCIPAL, MENU_PROV, MENU_PROVEEDORES, MENU_REPORTES, MENU_SOPORTE
from estilos import aplicar_estilos
from estado import iniciar_estado
from menu_lateral import dibujar_menu
import vista_bodega, vista_catalogos, vista_cotizacion, vista_directorios, vista_obra
import vista_ordenes, vista_panel, vista_perfil, vista_reportes

ss = st.session_state

aplicar_estilos()
iniciar_estado()
menu = dibujar_menu()

if ss.get("aviso_pendiente"):
    st.toast(ss.pop("aviso_pendiente"), icon="ℹ️")

if menu in [m for m in MENU_PRINCIPAL[1:] + MENU_SOPORTE if m != MENU_REPORTES]:
    vista_obra.mostrar(menu)
elif menu == MENU_REPORTES:
    vista_reportes.mostrar(menu)
elif menu == MENU_PERFIL:
    vista_perfil.mostrar(menu)
elif menu == "Panel de control":
    vista_panel.mostrar(menu)
elif menu == "Nueva cotización":
    vista_cotizacion.mostrar(menu)
elif menu in CATALOGOS:
    vista_catalogos.mostrar(menu)
elif menu == MENU_PROV:
    vista_ordenes.mostrar(menu)
elif menu == MENU_BODEGA:
    vista_bodega.mostrar(menu)
elif menu in (MENU_CLIENTES, MENU_PROVEEDORES):
    vista_directorios.mostrar(menu)
