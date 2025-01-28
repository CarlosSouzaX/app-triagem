def verificar_imei(imei):
    """
    Verifica se um IMEI é válido usando o Algoritmo de Luhn.

    Args:
        imei (int or str): IMEI a ser verificado.

    Returns:
        bool: True se o IMEI for válido, False caso contrário.
    """
    imei = str(imei)  # Garantir que o IMEI seja tratado como string
    
    # Verifica se o IMEI tem exatamente 15 dígitos
    if len(imei) != 15 or not imei.isdigit():
        return False

    # Algoritmo de Luhn
    soma = 0
    for i, digito in enumerate(imei):
        n = int(digito)
        # Dobre os dígitos em posições pares (baseado em índice 0)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9  # Soma dos dígitos do resultado
        soma += n

    # O IMEI é válido se a soma for múltipla de 10
    return soma % 10 == 0
