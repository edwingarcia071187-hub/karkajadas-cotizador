"""Módulos en construcción."""
import streamlit as st
from utilidades import encabezado_estandar


def mostrar(menu):
    encabezado_estandar("obra", menu, "Módulo en construcción")
    st.info("Módulo en construcción.")
