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

def advance_to_next_question():
    """
    Avança para a próxima pergunta ou exibe o estado final.
    """

    current_question = st.session_state.current_question
    st.write("Estado atual:", st.session_state)

    questions = st.session_state.questions
    final_states = st.session_state.final_states

    response = st.session_state.responses.get(current_question)

    # Obter o próximo passo
    next_step = questions[current_question]["next"].get(response)
    if next_step in final_states:
        st.success(f"Estado Final: {final_states[next_step]}")
        st.session_state["fluxo_finalizado"] = True  # Marca o fluxo como finalizado
    else:
        st.session_state.current_question = next_step

def runoff_flow(device_brand):
    """
    Fluxo Funcional com avanço imediato no botão "Próximo" e validação do status SR.
    """

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
            "question": "O dispositivo está na Blacklist?",
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
                "Não": "Q4.2"
            }
        },
        "Q4.2": {
            "question": "Teve contato líquido?",
            "options": ["Sim", "Não"],
            "next": {
                "Sim": "END_Fabrica",
                "Não": "Q4.3"
            }
        },
        "Q4.3": {
            "question": "O sensor de umidade (gaveta do chip) está ativado?",
            "options": ["Sim", "Não"],
            "next": {
                "Sim": "END_Fabrica",
                "Não": "Q4.4"
            }
        },
        "Q4.4": {
            "question": "Tem evidências de carbonização?",
            "options": ["Sim", "Não"],
            "next": {
                "Sim": "END_Fabrica",
                "Não": "Q4.1"
            }
        },
        "Q4.1": {
            "question": "Teve dano por impacto?",
            "options": ["Sim", "Não"],
            "next": {
                "Sim": "END_Reparo_Mesmo",
                "Não": "Q4.5"
            }
        },
        "Q4.5": {
            "question": "O device está no período de garantia?",
            "options": ["Sim", "Não"],
            "next": {
                "Sim": "END_Garantia",
                "Não": "END_Reparo",
            }
        }
    }

    if "final_states" not in st.session_state:
        st.session_state.final_states = {
            "END_DevolverRecebimento": "Devolver para o Recebimento.",
            "END_AT": "Encaminhar para AT (Apple, Moto, Samsung, Infinix).",
            "END_DevolverPicking": "Devolver ao Picking e rejeitar SR.",
            "END_TriagemJuridico": "Manter em triagem e acionar jurídico.",
            "END_Bloqueio": "Bloquear IMEI e dispositivo (Blacklist).",
            "END_Fabrica": "Encaminhar para análise na fábrica.",
            "END_Reparo": "Encaminhar para Reparo Like New.",
            "END_Reparo_Mesmo": "Encaminhar para IN-HOUSE (Reparo do Mesmo).",
            "END_Garantia": "Encaminhar para garantia."
        }

    current_question = st.session_state.current_question
    questions = st.session_state.questions
    question_data = questions.get(current_question)

    if question_data:
        options = ["Selecione uma opção"] + question_data["options"]

        st.write(f"**{question_data['question']}**")
        response = st.radio(
            "Escolha uma opção:",
            options=options,
            index=0,
            key=f"q{current_question}"
        )

        if response != "Selecione uma opção":
            st.session_state.responses[current_question] = response

        is_next_enabled = response != "Selecione uma opção"

        st.button(
            "Próximo",
            disabled=not is_next_enabled,
            on_click=advance_to_next_question
        )
    else:
        st.warning("⚠️ Fluxo finalizado.")
        st.session_state["fluxo_finalizado"] = True  # Marca o fluxo como finalizado


"""
# Reinicializar estado
if "fluxo_finalizado" not in st.session_state:
    st.session_state["fluxo_finalizado"] = False

if st.session_state["fluxo_finalizado"]:
    if st.button("Reiniciar"):
        inicializar_estado()
        st.session_state["current_question"] = "Q1"
        st.session_state["responses"] = {}
        st.session_state["fluxo_finalizado"] = False
        st.success("Fluxo reiniciado!")
"""