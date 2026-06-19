from database.resultado_db import (
    exibir_boletim_urna,
    exibir_estatistica_comparecimento,
    exibir_validacao_integridade,
    exibir_votos_por_partido
)
from database.votacao_db import abrir_sistema_votacao, exibir_protocolos_votacao, registrar_voto
from utils.input_utils import ler_opcao
from utils.logs import exibir_logs
from utils.tela import limpar_tela



def menu_auditoria():
    """
    Exibe o menu de auditoria da votacao.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    opcao = ""

    while opcao != "0":
        limpar_tela()
        print("\n=== AUDITORIA DA VOTACAO ===")
        print("1 - Exibir Logs de Ocorrencias")
        print("2 - Exibir Protocolos de Votacao")
        print("0 - Voltar")

        opcao = ler_opcao(["1", "2", "0"])

        if opcao == "1":
            exibir_logs()
        elif opcao == "2":
            exibir_protocolos_votacao()
            
def menu_resultados():
    """
    Exibe o menu de resultados consolidados da votacao.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    opcao = ""

    while opcao != "0":
        limpar_tela()
        print("\n=== RESULTADOS DA VOTACAO ===")
        print("1 - Boletim de Urna")
        print("2 - Estatistica de Comparecimento")
        print("3 - Votos por Partido")
        print("4 - Validacao de Integridade")
        print("0 - Voltar")

        opcao = ler_opcao(["1", "2", "3", "4", "0"])

        if opcao == "1":
            exibir_boletim_urna()
        elif opcao == "2":
            exibir_estatistica_comparecimento()
        elif opcao == "3":
            exibir_votos_por_partido()
        elif opcao == "4":
            exibir_validacao_integridade()

def menu_votacao():
    """
    Exibe o menu do modulo de votacao, auditoria e resultados.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    opcao = ""
    while opcao != "0":
        limpar_tela()
        print("\n=== VOTACAO ===")
        print("1 - Abrir Sistema de Votacao")
        print("2 - Auditoria")
        print("3 - Resultados")
        print("0 - Voltar")

        opcao = ler_opcao(["1", "2", "3", "0"])

        if opcao == "1":
            abrir_sistema_votacao()
        elif opcao == "2":
            menu_auditoria()
        elif opcao == "3":
            menu_resultados()
