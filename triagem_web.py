import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from modulo.data_loader import carregar_dados_gsheets
from modulo.state_manager import inicializar_estado, resetar_estado, obter_estado
from modulo.busca_device import buscar_device


from modulo.flow import (
    runoff_flow
)

# Configurar o layout para "wide"
st.set_page_config(layout="wide", page_title="Minha Aplicação", page_icon="📊")

# Inicializa o estado se não estiver configurado
inicializar_estado()


SHEET_URL = "https://docs.google.com/spreadsheets/d/1B34FqK4aJWeJtm4RLLN2AqlBJ-n6AASRIKn6UrnaK0k/edit?gid=698133322#gid=698133322"
WORKSHEET = "Triagem"
USECOLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

#df = carregar_dados_gsheets(SHEET_URL, WORKSHEET, USECOLS)

try:
    df = carregar_dados_gsheets(SHEET_URL, WORKSHEET, USECOLS)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    raise


# Título principal
st.title("📋 Device Verification Workflow")

# Layout com colunas para incluir divisor vertical
col1, col2, col3 = st.columns([1, 0.1, 1])  # Ajustar proporções das colunas


# Primeira coluna: Buscar Modelo pelo Device
with col1:
    buscar_device(df)

# Divisor vertical na segunda coluna
with col2:
    st.markdown(
        """
        <div style="width: 2px; height: 100%; background-color: #ccc; margin: auto;"></div>
        """,
        unsafe_allow_html=True,
    )

# Terceira coluna: Triagem de Produtos
with col3:
    #st.subheader("⚙️ Triagem de Produtos")

    esteira = obter_estado("esteira")
    device_brand = obter_estado("marca")
    model = obter_estado("modelo")
    imei = obter_estado("imei")
    sr = obter_estado("sr")
    
    if esteira:
        st.subheader("📋 Triagem de Dispositivo")
        st.info(f"Esteira de Atendimento: **{esteira}**")
        st.info(f"Modelo: **{model}**")
        st.info(f"IMEI: **{imei}**")
        st.info(f"SR: **{sr}**")

        if esteira == "RUNOFF":
            
            runoff_flow(device_brand, sr)
            #st.session_state["fluxo_finalizado"] = True
        else:
            st.warning("⚠️ Fluxo não reconhecido ou não definido.")
    else:
        st.warning("⚠️ Nenhuma esteira foi selecionada. Realize uma busca do device no campo disponível.")


   # 🔹 Exibir botão "Reiniciar" apenas quando o fluxo terminar
    if st.session_state.get("fluxo_finalizado", False):  
        st.markdown("<br><br>", unsafe_allow_html=True)  # Adiciona espaçamento
        
        if st.button("🔄 Reiniciar"):
            # ✅ Reseta completamente os estados antes de atualizar a interface
            resetar_estado(grupo="fluxo")
            resetar_estado(grupo="dispositivo")

            # ✅ Garante que volte à primeira pergunta
            st.session_state["fluxo_finalizado"] = False  
            st.session_state.current_question = "Q1"
            st.session_state.responses = {}  # Limpa as respostas anteriores
            st.session_state["trocar_pergunta"] = False  # Remove qualquer trigger de atualização
            
            # 🚀 Atualiza a interface imediatamente após o reset
            st.rerun()
