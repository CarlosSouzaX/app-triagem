import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def carregar_dados_gsheets(url, worksheet, usecols):
    """Carrega os dados do Google Sheets."""
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, worksheet=worksheet, usecols=usecols)
    df = pd.DataFrame(df)
    df.columns = df.columns.str.strip().str.lower()  # Normaliza as colunas
    return df
