import streamlit as st
from modulo.data_processor import buscar_modelo_por_device

def buscar_device(df):
    """
    Função para buscar informações do Device e armazená-las no estado.
    """

    st.subheader("🔍 Buscar Modelo pelo Device")

    # Campo de entrada para buscar device
    device_input = st.text_input("Digite o número do Device:")
    
    if st.button("Buscar", key="buscar_device"):
        result = buscar_modelo_por_device(df, device_input)

        if result["status"] == "success":
            st.success("✅ Dispositivo encontrado com sucesso!")

            # Armazena os valores no estado para persistência
            st.session_state["marca"] = result.get("marca", "")
            st.session_state["modelo"] = result.get("modelo", "")
            st.session_state["imei"] = result.get("imei", "")
            st.session_state["sr"] = result.get("sr", "")
            st.session_state["esteira"] = result.get("esteira", "")

            # Exibir detalhes do device
            st.subheader("📱 Dados do Device")
            st.success(f"✅ Marca: **{st.session_state['marca']}**")
            st.success(f"✅ Modelo: **{st.session_state['modelo']}**")
            st.success(f"✅ IMEI: **{st.session_state['imei']}**")
            st.success(f"✅ SR: **{st.session_state['sr']}**")

        elif result["status"] == "warning":
            st.warning(f"⚠️ {result['message']}")
        elif result["status"] == "error":
            st.error(f"❌ {result['message']}")
