import streamlit as st

def inicializar_estado():
    """
    Inicializa todas as variáveis de estado no `st.session_state`.
    """
    estados_padrao = {
        # Estados globais
        "inicializado": True,
        "fluxo_finalizado": False,
        # Estados do dispositivo
        "device_input": "",
        "esteira": None,
        "imei": None,
        "marca": None,
        "modelo": None,
        "sr": None,
        "status_sr": None,
        # Outros estados
        "observacao_cliente": "",
        # Estados do fluxo
        "current_question": "Q1",
        "responses": {},
    }
    for chave, valor in estados_padrao.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

def resetar_estado(grupo=None):
    """
    Reseta o estado para os valores padrão. Se um grupo for especificado, apenas esse grupo é resetado.
    """
    inicializar_estado()
    grupos = {
        "fluxo": ["current_question", "responses", "fluxo_finalizado"],
        "dispositivo": ["device_input", "esteira", "imei", "marca", "modelo", "status_sr"],
        "global": ["inicializado", "fluxo_finalizado"],
    }

    if grupo and grupo in grupos:
        for chave in grupos[grupo]:
            if chave in st.session_state:
                del st.session_state[chave]
    else:
        # Reseta todos os estados
        for chave in list(st.session_state.keys()):
            del st.session_state[chave]
    inicializar_estado()

def obter_estado(chave, valor_padrao=None):
    """
    Retorna o valor de uma variável de estado ou o valor padrão se não estiver definida.
    """
    return st.session_state.get(chave, valor_padrao)
