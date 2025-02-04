import streamlit as st
from modulo.data_processor import buscar_modelo_por_device

# Inicializa histórico de buscas no session_state
if "historico_buscas" not in st.session_state:
    st.session_state.historico_buscas = []

def normalizar_entrada(entrada):
    """ Remove espaços extras e mantém apenas números e letras. """
    return entrada.strip().replace(" ", "").upper()

def buscar_device(df):
    """
    Função aprimorada para buscar informações do Device e armazená-las no estado.
    """

    st.subheader("🔍 Buscar Modelo pelo Device")

    col1, col2 = st.columns([3, 1])

    with col1:
        device_input = st.text_input(
            "Digite o IMEI, Número do Device ou SR:",
            key="device_input",
            placeholder="Ex: 356939100123456 ou SR-00123"
        )
    
    with col2:
        buscar_agora = st.button("Buscar", key="buscar_device")

    # Normalizar a entrada
    device_input = normalizar_entrada(device_input)

    if buscar_agora:
        if not device_input:
            st.warning("⚠️ Digite um IMEI, número do device ou SR para continuar.")
            return

        # Evita buscas repetidas
        if device_input in st.session_state.historico_buscas:
            st.info(f"🔄 O dispositivo `{device_input}` já foi buscado recentemente.")

        # Chama a função de busca
        result = buscar_modelo_por_device(df, device_input)

        # Mapeamento de cores e ícones para o status_sr
        status_componentes = {
            "open": st.success,  # Verde
            "arrived": st.success,  # Verde
            "tracked": st.warning,  # Amarelo
            "swapped": st.warning,  # Amarelo
            "sent": st.warning,  # Amarelo
            "closed": st.info,  # Azul Claro
            "lost_in_delivery": st.error,  # Vermelho
            "rejected_documents": st.error,  # Vermelho
            "logistics_failure_from_pitzi": st.error,  # Vermelho
            "expired": st.error,  # Vermelho
            "rejected_closed": st.error,  # Vermelho
            "rejected_sent": st.error  # Vermelho
        }

        if result["status"] == "success":
            st.success("✅ Dispositivo encontrado com sucesso!")

            # Armazena os dados no session_state para persistência
            st.session_state["marca"] = result.get("marca", "")
            st.session_state["modelo"] = result.get("modelo", "")
            st.session_state["imei"] = result.get("imei", "")
            st.session_state["sr"] = result.get("sr", "")
            st.session_state["esteira"] = result.get("esteira", "")

            # Atualiza histórico de buscas
            if device_input not in st.session_state.historico_buscas:
                st.session_state.historico_buscas.append(device_input)

            # Exibe os detalhes do device
            st.subheader("📱 Dados do Device")
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"✅ Marca: **{st.session_state['marca']}**")
                st.success(f"✅ Modelo: **{st.session_state['modelo']}**")
            with col2:
                st.success(f"✅ IMEI: **{st.session_state['imei']}**")
                st.success(f"✅ SR: **{st.session_state['sr']}**")

            # Exibe o status da SR
            st.subheader("📄 Dados da SR")
            status_sr = result.get("status_sr", "Não informado")
            componente = status_componentes.get(status_sr, st.warning)
            componente(f"✅ **Status SR:** **{status_sr}**")

            # Exibir observação do cliente
            st.subheader("📌 Observação do Cliente")
            obs_cliente = result.get("obs_cliente", None)
            if obs_cliente:
                st.info(f"🔍 **Observação:** {obs_cliente}")
            else:
                st.warning("⚠️ **Sem observações registradas para este cliente.**")

        elif result["status"] == "warning":
            st.warning(f"⚠️ {result['message']}")
        elif result["status"] == "error":
            st.error(f"❌ {result['message']}")

    # Exibir o histórico de buscas recentes
    if st.session_state.historico_buscas:
        st.subheader("📜 Histórico de Buscas Recentes")
        for item in st.session_state.historico_buscas[-5:][::-1]:  # Mostra os últimos 5 dispositivos buscados
            st.text(f"🔹 {item}")
