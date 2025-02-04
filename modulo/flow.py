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
    base_dir = os.path.dirname(__file__)  # Diretório atual
    caminho_modelos_ativos = os.path.join(base_dir, "../data/modelos_ativos_ln.json")

    try:
        with open(caminho_modelos_ativos, "r") as f:
            data = json.load(f)
        return data.get("modelos_ativos_ln", [])
    except Exception as e:
        print(f"Erro ao carregar modelos ativos: {e}")
        return []


def carregar_final_states():
    """
    Retorna um dicionário com os estados finais do fluxo.
    """
    return {
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


def carregar_perguntas(device_brand):
    """
    Retorna um dicionário com as perguntas do fluxo de triagem.
    """
    return {
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


def runoff_flow(device_brand):
    """
    Inicia o fluxo de triagem do dispositivo, carregando perguntas e controlando a navegação.
    """

    # Inicializa estados da sessão se não existirem
    st.session_state.setdefault("current_question", "Q1")
    st.session_state.setdefault("responses", {})
    st.session_state.setdefault("final_states", carregar_final_states())
    st.session_state.setdefault("questions", carregar_perguntas(device_brand))

    exibir_pergunta()


def exibir_pergunta():
    """
    Exibe a pergunta atual no fluxo e permite avançar.
    """
    current_question = st.session_state.current_question
    questions = st.session_state.questions
    question_data = questions.get(current_question)

    if question_data:
        st.subheader("📋 Triagem de Dispositivo")
        st.write(f"**{question_data['question']}**")

        response = st.selectbox(
            "Escolha uma opção:",
            question_data["options"],
            key=f"q{current_question}"
        )

        if st.button("Próximo"):
            if response:
                st.session_state.responses[current_question] = response
                advance_to_next_question()
                st.experimental_rerun()
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
