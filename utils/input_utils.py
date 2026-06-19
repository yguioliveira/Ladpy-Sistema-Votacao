def ler_opcao(opcoes_validas):
    """
    Le uma opcao do usuario ate que ela esteja entre as opcoes validas.

    Args:
        opcoes_validas (list): Lista de opcoes aceitas pelo menu atual.

    Returns:
        str: Opcao valida escolhida pelo usuario.
    """
    
    opcao = input("Escolha uma opção: ")
    while opcao not in opcoes_validas:
        print("Opção inválida!")
        opcao = input("Escolha uma opção: ")
    return opcao
