import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Karkajadas Group - ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS AVANZADOS Y COLORIMETRÍA SEMÁNTICA ---
st.markdown("""
    <style>
    /* Tipografía y fondos principales */
    .stApp, .main, header { background-color: #F8FAFC !important; color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* Contenedores blancos estilo tarjeta */
    .card-container {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .filter-container {
        background-color: #FFFFFF;
        padding: 15px 24px;
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        margin-bottom: 20px;
    }
    
    /* Títulos de Sección */
    .section-title {
        color: #0F172A;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #E2E8F0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ----------------------------------------------------
       BOTONES: VERDE (Avanzar/Crear), AZUL (Neutro), ROJO (Borrar)
       ---------------------------------------------------- */
    /* Botones PRIMARIOS (Azul por defecto) */
    button[kind="primary"] {
        background-color: #1E3A8A !important; 
        color: #FFFFFF !important;
        border-radius: 4px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        border: none !important; 
        box-shadow: 0 2px 4px rgba(30, 58, 138, 0.2);
        transition: all 0.2s ease;
    }
    button[kind="primary"]:hover { background-color: #1E40AF !important; transform: translateY(-1px); }

    /* Botones SECUNDARIOS (Fondo blanco, borde/texto azul) */
    button[kind="secondary"] {
        background-color: #FFFFFF !important; 
        color: #1E3A8A !important;
        border-radius: 4px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #CBD5E1 !important; 
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover { background-color: #F1F5F9 !important; border-color: #1E3A8A !important; }

    /* BOTONES DE
