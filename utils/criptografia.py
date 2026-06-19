ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def normalizar_numero(texto):
    """
    Converte digitos numericos em letras para uso na Cifra de Hill.

    Args:
        texto (str): Texto contendo numeros a serem normalizados.

    Returns:
        str: Texto formado pelas letras equivalentes aos digitos informados.
    """

    mapa = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E',
            '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J'}
    return ''.join(mapa[c] for c in texto if c.isdigit())


def normalizar_chave(texto):
    """
    Normaliza letras e numeros de uma chave para o alfabeto usado na cifra.

    Args:
        texto (str): Texto original contendo letras e numeros.

    Returns:
        str: Texto normalizado apenas com letras maiusculas.
    """

    mapa = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E',
            '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J'}

    resultado = ""
    for c in texto.upper():
        if c.isalpha():
            resultado += c
        elif c.isdigit():
            resultado += mapa[c]

    return resultado


def texto_para_numeros(texto):
    """
    Converte um texto alfabetico em uma lista de indices numericos.

    Args:
        texto (str): Texto composto por letras presentes no alfabeto da cifra.

    Returns:
        list: Lista de numeros correspondentes as posicoes das letras.
    """

    return [ALFABETO.index(c) for c in texto]


def numeros_para_texto(numeros):
    """
    Converte uma lista de numeros em texto alfabetico.

    Args:
        numeros (list): Lista de numeros gerados pela Cifra de Hill.

    Returns:
        str: Texto convertido a partir dos indices numericos.
    """

    return ''.join(ALFABETO[n % 26] for n in numeros)


def cifra_hill(texto, chave):
    """
    Criptografa um texto usando a Cifra de Hill com matriz 2x2.

    Args:
        texto (str): Texto claro a ser criptografado.
        chave (list): Matriz 2x2 usada como chave de criptografia.

    Returns:
        str: Texto criptografado.
    """

    texto = ''.join(c for c in texto.upper() if c.isalpha())

    if len(texto) == 0:
        return ""

    if len(texto) % 2 != 0:
        texto += texto[-1]

    numeros = texto_para_numeros(texto)
    resultado = []

    for i in range(0, len(numeros), 2):
        a, b = numeros[i], numeros[i + 1]

        c1 = (chave[0][0] * a + chave[0][1] * b) % 26
        c2 = (chave[1][0] * a + chave[1][1] * b) % 26

        resultado.extend([c1, c2])

    return numeros_para_texto(resultado)
