from utils.input_utils import ler_opcao
from utils.tela import limpar_tela
from database.candidato_db import listar_candidatos
from database.eleitor_db import inserir_eleitor, listar_eleitores, buscar_eleitor, editar_eleitor, remover_eleitor

def menu_gerenciamento():
    """
    Exibe o menu administrativo de gerenciamento do sistema.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    opcao = ""
    while opcao != "0":
        limpar_tela()
        print("\n=== GERENCIAMENTO ===")
        print("1 - Eleitores")
        print("2 - Candidatos")
        print("0 - Voltar")

        opcao = ler_opcao(["1", "2", "0"])

        if opcao == "1":
            menu_eleitores()
        elif opcao == "2":
            menu_candidatos()

def menu_eleitores():
    """
    Exibe o submenu de operacoes para gerenciamento de eleitores.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    opcao = ""
    while opcao != "0":
        limpar_tela()
        print("\n--- ELEITORES ---")
        print("1 - Cadastrar")
        print("2 - Editar")
        print("3 - Remover")
        print("4 - Buscar")
        print("5 - Listar")
        print("0 - Voltar")

        opcao = ler_opcao(["1","2","3","4","5","0"])

        if opcao == "1":
            inserir_eleitor()
        elif opcao == "2":
            editar_eleitor()
        elif opcao == "3":
            remover_eleitor()
        elif opcao == "5":
            listar_eleitores()
        elif opcao == "4":
            buscar_eleitor()
        elif opcao != "0":
            ler_opcao()

def menu_candidatos():
    """
    Exibe o submenu de operacoes para gerenciamento de candidatos.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    opcao = ""
    while opcao != "0":
        limpar_tela()
        print("\n--- CANDIDATOS ---")
        print("1 - Listar")
        print("0 - Voltar")

        opcao = ler_opcao(["1","0"])
        if opcao == "1":
           listar_candidatos()
        
