import streamlit as st
from modulo.data_processor import buscar_modelo_por_device


def buscar_device(df):
    """
    Função para buscar informações do Device e armazená-las no estado.
    """

    st.subheader("🔍 Buscar Modelo pelo Device")

    # Campo de texto vinculado ao estado
    device_input = st.text_input("Digite o número do Device:")
    
    if st.button("Buscar", key="buscar_device"):

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

        # Verifica o status geral
        if result["status"] == "success":

            # Exibe a validação da consulta
            st.success("✅ Dispositivo encontrado com sucesso!")

            # Armazenar a esteira no estado para uso posterior
            if isinstance(result, dict):
                st.session_state["esteira"] = result.get("esteira", "Não definida")
                esteira = result.get("esteira", "Não definida")

            
            
            for detalhe in result.get("detalhes", []):
                campo = detalhe["campo"]
                status = detalhe["status"]
                valor = detalhe["valor"]

                # Exibe dados do Device
                #st.subheader("📱 Dados do Device")
                 # Exibe o campo com base no status
                if campo == "marca":
                    if status == "success":
                        st.success(f"✅ {campo.capitalize()}: **{valor}**")
                        st.session_state["marca"] = valor
                    elif status == "warning":
                        st.warning(f"⚠️ {campo.capitalize()}: {valor}")
                    elif status == "error":
                        st.error(f"❌ {campo.capitalize()}: {valor}")
                if campo == "modelo":
                    if status == "success":
                        st.session_state["modelo"] = valor
                        st.success(f"✅ {campo.capitalize()}: **{valor}**")
                    elif status == "warning":
                        st.warning(f"⚠️ {campo.capitalize()}: {valor}")
                    elif status == "error":
                        st.error(f"❌ {campo.capitalize()}: {valor}")
                if campo == "imei":
                    if status == "success":
                        st.session_state["imei"] = valor
                        st.success(f"✅ {campo.capitalize()}: **{valor}**")
                    elif status == "warning":
                        st.warning(f"⚠️ {campo.capitalize()}: {valor}")
                    elif status == "error":
                        st.error(f"❌ {campo.capitalize()}: {valor}")
            
                # Exibe dados da SR
                #st.subheader("📄 Dados da SR")

                if campo == "sr":
                    if status == "success":
                        st.session_state["sr"] = valor
                        st.success(f"✅ **SR:** **{valor}**")
                    elif status == "warning":
                        st.warning(f"⚠️ **SR:** **{valor}**")
                    elif status == "error":
                        st.error(f"❌ **SR:** **{valor}**")
                if campo == "supplier":
                    if status == "success":
                        st.success(f"✅ **Supplier Device:** **{valor}**")
                    elif status == "warning":
                        st.warning(f"⚠️ **Supplier Device:** **{valor}**")
                    elif status == "error":
                        st.error(f"❌ **Supplier Device:** **{valor}**")
                if campo == "status_sr":
                    componente = status_componentes.get(valor)
                    st.session_state["status_sr"] = valor
                    if componente:  # Se o status estiver mapeado, exibe com o componente correspondente
                        componente(f"✅ **Status SR:** **{valor}**")
                    else:  # Caso o status não esteja no mapeamento, exibe um aviso genérico
                        st.warning(f"⚠️ **Status SR:** {valor} (Status não reconhecido)")

            # Mostrar a observação do cliente com destaque
            st.subheader("📌 Observação do Cliente")
            obs_cliente = result.get("obs_cliente", None)  # Obtém a observação do cliente do resultado
            if obs_cliente:
                st.info(f"🔍 **Observação:** {obs_cliente}")
            else:
                st.warning("⚠️ **Sem observações registradas para este cliente.**")    

        elif result["status"] == "warning":
            st.warning(f"⚠️ {result['message']}")
        elif result["status"] == "error":
            st.error(f"❌ {result['message']}")