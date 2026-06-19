import os

def limpar_tela():
    """
    Limpa a tela do terminal de acordo com o sistema operacional.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    
    os.system("cls" if os.name == "nt" else "clear")
