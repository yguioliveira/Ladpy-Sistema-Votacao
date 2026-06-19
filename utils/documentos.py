def validar_cpf(cpf):
    """
    Valida matematicamente um numero de CPF.

    Args:
        cpf (str): CPF informado pelo usuario, com ou sem pontuacao.

    Returns:
        bool: Retorna True se o CPF for valido, False caso contrario.
    """

    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    multiplicador = 10

    for i in range(9):
        soma += int(cpf[i]) * multiplicador
        multiplicador -= 1

    resto = soma % 11

    if resto < 2:
        dig1 = 0
    else:
        dig1 = 11 - resto

    if dig1 != int(cpf[9]):
        return False

    soma = 0
    multiplicador = 11

    for i in range(10):
        soma += int(cpf[i]) * multiplicador
        multiplicador -= 1

    resto = soma % 11

    if resto < 2:
        dig2 = 0
    else:
        dig2 = 11 - resto

    if dig2 != int(cpf[10]):
        return False

    return True


def validar_titulo(titulo):
    """
    Valida matematicamente um numero de titulo de eleitor.

    Args:
        titulo (str): Titulo de eleitor informado pelo usuario.

    Returns:
        bool: Retorna True se o titulo for valido, False caso contrario.
    """

    titulo = ''.join(filter(str.isdigit, titulo))

    if len(titulo) != 12:
        return False

    if titulo == titulo[0] * 12:
        return False

    soma = 0

    for i in range(8):
        soma += int(titulo[i]) * (2 + i)

    resto = soma % 11

    if resto == 10:
        dig1 = 0
    else:
        dig1 = resto

    if dig1 != int(titulo[10]):
        return False

    soma = 0
    soma += int(titulo[8]) * 7
    soma += int(titulo[9]) * 8
    soma += dig1 * 9

    resto = soma % 11

    if resto == 10:
        dig2 = 0
    else:
        dig2 = resto

    if dig2 != int(titulo[11]):
        return False

    return True
