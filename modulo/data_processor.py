import pandas as pd
from modulo.verificar_imei import verificar_imei
import os
import json


def carregar_modelos_ativos_json():
    """
    Carrega a lista de modelos ativos para reparo de um arquivo JSON localizado na pasta 'data'.

    Returns:
        list: Lista de modelos ativos.
    """
    # Caminho absoluto para o arquivo JSON
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório atual do data_processor.py
    caminho_modelos_ativos = os.path.join(base_dir, "../data/modelos_ativos.json")

    try:
        with open(caminho_modelos_ativos, "r", encoding="uft-8") as f:
            data = json.load(f)
        return data.get("modelos_ativos", [])  # Retorna a lista de modelos ativos
    except Exception as e:
        print(f"Erro ao carregar modelos ativos: {e}")
        return []


def buscar_modelo_por_device(df, device_input):
    """
    Realiza a busca do modelo e informações associadas ao número do Device e campos relacionados à SR.

    Args:
        df (pd.DataFrame): DataFrame com os dados.
        device_input (str): Número do Device fornecido pelo usuário.

    Returns:
        dict: Dicionário com status e informações da busca (marca, IMEI, modelo, SR, etc.).
    """
    try:
        # Valida a entrada
        if not device_input.strip():
            return {"status": "warning", "message": "Por favor, insira um valor válido para o Device."}

        # Converte para float
        device_input_float = float(device_input.strip())

        # Verifica se a coluna "device" existe
        if "device" not in df.columns:
            return {"status": "error", "message": "A coluna 'Device' não existe no DataFrame."}

        # Filtra pelo Device
        resultado = df.loc[df["device"] == device_input_float, df.columns[1:]]
        if resultado.empty:
            return {"status": "error", "message": f"Device '{device_input}' não encontrado no Banco de Dados."}

        # Inicializa o resultado parcial
        resultado_final = {"status": "success", "detalhes": []}

        # Verifica a marca
        marca = resultado.iloc[0, 1]  # Supondo que "marca" está na segunda coluna
        if pd.notnull(marca):
            resultado_final["detalhes"].append({"campo": "marca", "status": "success", "valor": marca})
        else:
            resultado_final["detalhes"].append({"campo": "marca", "status": "error", "valor": "Marca Não Disponível / Vazia"})

        # Verifica o IMEI
        imei = resultado.iloc[0, 3]  # Supondo que "imei" está na quarta coluna
        imei_status = "error"
        if pd.notnull(imei):
            try:
                imei_int = int(imei)  # Converte para inteiro
                if verificar_imei(imei_int):
                    imei_status = "success"
                    resultado_final["detalhes"].append({"campo": "imei", "status": "success", "valor": imei_int})
                else:
                    imei_status = "warning"
                    resultado_final["detalhes"].append({"campo": "imei", "status": "warning", "valor": "IMEI Não Válido"})
            except ValueError:
                imei_status = "warning"
                resultado_final["detalhes"].append({"campo": "imei", "status": "warning", "valor": "IMEI Não Válido"})
        else:
            resultado_final["detalhes"].append({"campo": "imei", "status": "error", "valor": "IMEI Não Disponível / Vazia"})

        # Verifica o Modelo
        modelo = resultado.iloc[0, 2]  # Supondo que "modelo" está na terceira coluna
        if pd.notnull(modelo):
            if imei_status == "success":
                resultado_final["detalhes"].append({"campo": "modelo", "status": "success", "valor": modelo})
            else:
                resultado_final["detalhes"].append({"campo": "modelo", "status": "warning", "valor": "Modelo Duvidoso"})
        else:
            resultado_final["detalhes"].append({"campo": "modelo", "status": "error", "valor": "Modelo Não Disponível / Vazio"})

        # Verifica a SR
        sr = resultado.iloc[0, 5]  # Supondo que "sr" está na sexta coluna
        if pd.notnull(sr):
            try:
                sr_int = int(sr)
                resultado_final["detalhes"].append({"campo": "sr", "status": "success", "valor": sr_int})
            except ValueError:
                resultado_final["detalhes"].append({"campo": "sr", "status": "warning", "valor": "SR contém caracteres inválidos."})
        else:
            resultado_final["detalhes"].append({"campo": "sr", "status": "warning", "valor": "Origem Duvidosa"})

        # Verifica o Status da SR
        status_sr = resultado.iloc[0, 6]  # Supondo que "status_sr" está na sétima coluna
        if pd.notnull(status_sr):
            resultado_final["detalhes"].append({"campo": "status_sr", "status": "success", "valor": status_sr})
        else:
            resultado_final["detalhes"].append({"campo": "status_sr", "status": "error", "valor": "Status Desconhecido"})

        # Verifica o Supplier
        supplier = resultado.iloc[0, 4]  # Supondo que "supplier" está na quinta coluna
        if pd.notnull(supplier):
            resultado_final["detalhes"].append({"campo": "supplier", "status": "warning", "valor": "Externo"})
        else:
            resultado_final["detalhes"].append({"campo": "supplier", "status": "success", "valor": "Pitzi"})
        
        # Verifica o Parceiro
        parceiro = resultado.iloc[0, 7]  # Supondo que "parceiro" está na oitava coluna
        if pd.notnull(parceiro):
            resultado_final["detalhes"].append({"campo": "parceiro", "status": "success", "valor": parceiro})
        else:
            resultado_final["detalhes"].append({"campo": "parceiro", "status": "error", "valor": "Status Desconhecido"})

       # Carrega os modelos ativos de um arquivo externo
        modelos_ativos = carregar_modelos_ativos_json()

        

        # Coleta os dados necessários
        origem = resultado.iloc[0, 8]  # Supondo que "origem" está na nona coluna
        resultado_final["origem"] = origem
        garantia_funcional = resultado.iloc[0, 9]  # Supondo que "garantia_funcional" está na décima coluna
        resultado_final["garantia_funcional"] = garantia_funcional
        reincidente = resultado.iloc[0, 10]  # Supondo que "reincidente" está na décima primeira coluna
        resultado_final["reincidente"] = reincidente
        runoff = resultado.iloc[0, 11]  # Supondo que a flag "runoff" está na décima segunda coluna
        resultado_final["runoff"] = runoff
        mdm_payjoy = resultado.iloc[0, 12]  # Supondo que "mdm_payjoy" está na décima terceira coluna
        resultado_final["mdm_payjoy"] = mdm_payjoy
        obs_cliente = resultado.iloc[0, 13]  # Supondo que "obs_cliente" está na décima quarta coluna
        resultado_final["obs_cliente"] = obs_cliente 

        # Determina a Esteira
        esteira = determinar_esteira(
            parceiro,
            origem,
            garantia_funcional,
            reincidente,
            runoff,
            mdm_payjoy,
            marca,
            modelo,
            imei,
            imei_status,
            status_sr,
            modelos_ativos
        )

        # Adiciona a Esteira ao resultado final
        resultado_final["esteira"] = esteira

        return resultado_final

    except ValueError:
        return {"status": "error", "message": "O valor inserido deve ser numérico."}


def determinar_esteira(parceiro, origem, garantia_funcional, reincidente, runoff, mdm_payjoy, marca, modelo, imei, imei_status, status_sr, modelos_ativos):

    # 1. Verifica IMEI inválido
    if (
        imei_status != "success" # IMEI deve estar válido
    ):
        return "DEVOLVER AO RECEBIMENTO / CHECAR IMEI PELA NF"
        
   # 2. Verifica RUNOFF
    if (
        #modelo in modelos_ativos and 
        status_sr in ["open", "arrived"] and  
        (runoff == "runoff" or parceiro == "Mercado Livre")
    ):
        return "RUNOFF"

    # Caso nenhuma condição específica seja atendida
    return "PADRÃO"
