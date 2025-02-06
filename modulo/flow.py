import streamlit as st
import os
import json
from modulo.state_manager import inicializar_estado


def carregar_modelos_ativos_json():
    """
    Carrega a lista de modelos ativos para reparo de um arquivo JSON localizado na pasta 'data'.

    Returns:
        list: Lista de modelos ativos.
    """
    base_dir = os.path.dirname(__file__)  # Diretório atual do data_processor.py
    caminho_modelos_ativos = os.path.join(base_dir, "../data/modelos_ativos_ln.json")

    try:
        with open(caminho_modelos_ativos, "r") as f:
            data = json.load(f)
        return data.get("modelos_ativos_ln", [])
    except Exception as e:
        print(f"Erro ao carregar modelos ativos: {e}")
        return []


def runoff_flow(device_brand, sr, device):
    """
    Fluxo Funcional com avanço imediato no botão "Próximo" e validação do status SR.
    """

    # Inicializa estados da sessão se não existirem
    if "current_question" not in st.session_state:
        st.session_state.current_question = "Q1"

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    if "final_states" not in st.session_state:
        st.session_state.final_states = {
            "END_DevolverRecebimento": "Devolver para o Recebimento para correção de IMEI / MODELO",
            "END_AT": "Encaminhar para AT (Apple, Moto, Samsung, Infinix).",
            "END_DevolverPicking": "Devolver ao Picking e rejeitar SR.",
            "END_TriagemJuridico": "Manter em triagem e acionar jurídico.",
            "END_Bloqueio": "Bloquear IMEI e dispositivo (Blacklist).",
            "END_Fabrica": "Encaminhar para análise na Engenharia",
            "END_Reparo": "Encaminhar para Reparo Like New.",
            "END_Reparo_Mesmo": "Encaminhar para IN-HOUSE (Reparo do Mesmo).",
            "END_Garantia": "Encaminhar para garantia.",
            "END_SCRAP": "Enviar device para Scrap.",
            "END_CX": "Atendimento Técnico. Entrar em contato com o cliente para remover FMiP/FMD"
        }

    if "questions" not in st.session_state:
        st.session_state.questions = {
            "Q1": {
                "question": "É possível identificar o IMEI?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "Q2",
                    "Não": "END_SCRAP"
                }
            },
            "Q2": {
                "question": "O IMEI está correto?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "Q3",
                    "Não": "END_DevolverRecebimento"
                }
            },
            "Q3": {
                "question": "O dispositivo está listado como 'Blocklist'? [Link](https://ui.prologmobile.com/Home)",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_DevolverPicking",
                    "Não": "Q4_FMiP" if device_brand in ["Apple", "Xiaomi"] else "Q4"
                }
            },
            "Q4_FMiP": {
                "question": "O dispositivo está com FMiP ativo? [Apple](https://ui.prologmobile.com/Home), [Xiaomi](https://mifirm.net/)",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_CX",
                    "Não": "Q4"
                }
            },
            "Q4": {
                "question": "O Modelo está correto?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "Q4.1",
                    "Não": "END_DevolverRecebimento"
                },
                "prev": "Q1"
            },
            "Q4.1": {
                "question": "O dispositivo apresenta danos irreversíveis por LÍQUIDO, impossibilitando o reparo?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_SCRAP",
                    "Não": "Q4.2"
                }
            },
            "Q4.2": {
                "question": "O dispositivo apresenta danos irreversíveis na PLACA, impossibilitando o reparo?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_SCRAP",
                    "Não": "END_Reparo_Mesmo"
                }
            }
        }

    current_question = st.session_state.current_question
    questions = st.session_state.questions
    question_data = questions.get(current_question)

    if question_data:
        
        st.markdown(f"**{question_data['question']}**")

        key_response = f"q{current_question}"

        # ✅ Inicializa a resposta no session_state
        if key_response not in st.session_state:
            st.session_state[key_response] = "Selecione uma opção"

        # ✅ Captura a resposta do usuário
        response = st.selectbox(
            "Escolha uma opção:",
            ["Selecione uma opção"] + question_data["options"],  # Placeholder
            key=key_response
        )

        # ✅ Atualiza o estado imediatamente após seleção
        st.session_state["botao_habilitado"] = response != "Selecione uma opção"

        espaco = st.empty()
        espaco.write("\n" * 10)  # Adiciona 10 linhas em branco


        if "prev" in question_data and isinstance(question_data["prev"], str):  
            if st.button("⬅ Voltar", key=f"prev_{current_question}"):
                st.session_state["trocar_pergunta"] = True  # Ativa o trigger para a mudança
                st.session_state.current_question = question_data["prev"]


        # ✅ Botão "Próximo" agora avança corretamente
        if st.button("➡ Próximo", key=f"next_{current_question}", disabled=not st.session_state["botao_habilitado"]):
            st.session_state.responses[current_question] = response
            next_question = question_data["next"][response]

            # ✅ Se for um estado final, exibe a mensagem e para o fluxo
            if next_question.startswith("END_"):
                st.session_state["fluxo_finalizado"] = True
                # Obtém a mensagem final do dicionário
                final_message = st.session_state.final_states[next_question]
                st.warning(f"⚠️ Fluxo finalizado: {final_message}")
                if next_question == "END_SCRAP":
                    st.markdown(f"🔗 [Acesse a SR {sr}](https://admin.pitzi.com.br/admin/service_requests/{sr}/edit) e anote: ***RUNOFF REJEITADO***")
                if next_question == "END_Reparo_Mesmo":

                    st.markdown(f"🔗 [Acesse o Device {device}](https://admin.pitzi.com.br/operations_admin/arrived_device_verifications/review?device_id={device}&from=%2Foperations_admin%2Farrived_device_verifications%2Fdevices")


            else:
                st.session_state.current_question = next_question
                st.session_state["trocar_pergunta"] = True  # Ativa o trigger para atualização


        # ✅ Aplica a troca de pergunta automaticamente
        if st.session_state.get("trocar_pergunta", False):
            st.session_state["trocar_pergunta"] = False  # Reseta o trigger
            st.rerun()  # 🚀 Atualiza a interface corretamente
               
    else:
        st.warning("⚠️ Fluxo finalizado.")
        st.session_state["fluxo_finalizado"] = True  # Marca o fluxo como finalizado


'''def advance_to_next_question():
    """Avança para a próxima pergunta no fluxo baseado na resposta do usuário."""
    current_question = st.session_state.current_question
    response = st.session_state.responses.get(current_question)

    if response:
        next_question = st.session_state.questions[current_question]["next"].get(response)

        if next_question:
            # Atualiza para a próxima pergunta ou finaliza o fluxo
            if next_question.startswith("END_"):
                st.session_state["fluxo_finalizado"] = True
                final_message = st.session_state.final_states[next_question]
                st.markdown(f"[🔗 Fluxo finalizado: {final_message}")

                #st.warning(f"⚠️ Fluxo finalizado: {final_message}")                      
            else:
                st.session_state.current_question = next_question
        else:
            st.error("Erro: Opção inválida no fluxo!")'''
   