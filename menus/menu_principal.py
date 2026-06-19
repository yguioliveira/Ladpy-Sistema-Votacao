from menus.menu_gerenciamento import menu_gerenciamento
from menus.menu_votacao import menu_votacao
from utils.input_utils import ler_opcao
from utils.tela import limpar_tela

def menu_principal():
    """
    Exibe o menu principal e direciona o usuario para os modulos do sistema.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    
    opcao = ""
    while opcao != "0":
        limpar_tela()
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Gerenciamento")
        print("2 - Votação")
        print("0 - Sair")

        opcao = ler_opcao(["1", "2", "0"])

        if opcao == "1":
            menu_gerenciamento()
        elif opcao == "2":
            menu_votacao()

    print("Encerrando sistema...")
 
