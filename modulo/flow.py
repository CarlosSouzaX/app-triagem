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


def runoff_flow(device_brand):
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
            "END_DevolverRecebimento": "Devolver para o Recebimento.",
            "END_AT": "Encaminhar para AT (Apple, Moto, Samsung, Infinix).",
            "END_DevolverPicking": "Devolver ao Picking e rejeitar SR.",
            "END_TriagemJuridico": "Manter em triagem e acionar jurídico.",
            "END_Bloqueio": "Bloquear IMEI e dispositivo (Blacklist).",
            "END_Fabrica": "Encaminhar para análise na Engenharia",
            "END_Reparo": "Encaminhar para Reparo Like New.",
            "END_Reparo_Mesmo": "Encaminhar para IN-HOUSE (Reparo do Mesmo).",
            "END_Garantia": "Encaminhar para garantia."
        }

    if "questions" not in st.session_state:
        st.session_state.questions = {
            "Q1": {
                "question": "O IMEI está correto?",
                "options": ["Sim", "Não", "Não Sei"],
                "next": {
                    "Sim": "Q2",
                    "Não": "END_DevolverRecebimento",
                    "Não Sei": "END_AT"
                }
            },
            "Q2": {
                "question": "O Modelo está correto?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "Q3",
                    "Não": "END_DevolverRecebimento"
                }
            },
            "Q3": {
                "question": "O dispositivo está listado como 'Blocklist'?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_DevolverPicking",
                    "Não": "Q4_FMiP" if device_brand in ["Apple", "Xiaomi"] else "Q4.2"
                }
            },
            "Q4_FMiP": {
                "question": "O dispositivo está com FMiP ativo?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_DevolverPicking",
                    "Não": "Q4.1"
                }
            },
            "Q4.1": {
                "question": "O sensor de umidade (gaveta do chip) está ativado ou teve contato com líquido?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_Fabrica",
                    "Não": "Q4.2"
                }
            },
            "Q4.2": {
                "question": "Tem evidências de carbonização?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_Fabrica",
                    "Não": "Q4.3"
                }
            },
            "Q4.3": {
                "question": "Teve dano por impacto?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_Reparo_Mesmo",
                    "Não": "Q4.4"
                }
            },
            "Q4.4": {
                "question": "O device está no período de garantia?",
                "options": ["Sim", "Não"],
                "next": {
                    "Sim": "END_Garantia",
                    "Não": "END_Reparo",
                }
            }
        }

    current_question = st.session_state.current_question
    questions = st.session_state.questions
    question_data = questions.get(current_question)

    if question_data:
        st.subheader("📋 Triagem de Dispositivo")
        
        st.write(f"**{question_data['question']}**")

        # ✅ Define a chave do selectbox no session_state para garantir persistência
        if f"q{current_question}" not in st.session_state:
            st.session_state[f"q{current_question}"] = "Selecione uma opção"

        # ✅ Selectbox primeiro para capturar a resposta
        response = st.selectbox(
            "Escolha uma opção:",
            ["Selecione uma opção"] + question_data["options"],  # Placeholder como primeira opção
            key=f"q{current_question}"
        )

        # ✅ Atualiza o session_state para ativar o botão apenas quando necessário
        st.session_state["botao_habilitado"] = response != "Selecione uma opção"

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if "prev" in question_data and st.button("⬅ Voltar", key=f"prev_{current_question}"):
                voltar_pergunta()

        with col2:
            # ✅ Botão "Próximo" agora é ativado corretamente após a seleção
            if st.button("➡ Próximo", key=f"next_{current_question}", disabled=not st.session_state["botao_habilitado"]):
                st.session_state.responses[current_question] = response
                advance_to_next_question()

        

        
    else:
        st.warning("⚠️ Fluxo finalizado.")
        st.session_state["fluxo_finalizado"] = True  # Marca o fluxo como finalizado


def advance_to_next_question():
    """Avança para a próxima pergunta no fluxo baseado na resposta do usuário."""
    current_question = st.session_state.current_question
    response = st.session_state.responses.get(current_question)

    if response:
        next_question = st.session_state.questions[current_question]["next"].get(response)

        if next_question:
            # Atualiza para a próxima pergunta ou finaliza o fluxo
            if next_question.startswith("END_"):
                st.session_state["fluxo_finalizado"] = True
                st.warning(f"⚠️ Fluxo finalizado: {st.session_state.final_states[next_question]}")
            else:
                st.session_state.current_question = next_question
        else:
            st.error("Erro: Opção inválida no fluxo!")
   