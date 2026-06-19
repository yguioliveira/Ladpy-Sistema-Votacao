from database.conexao import conectar


STATUS_FECHADA = "FECHADA"


def obter_status_votacao(cursor):
    """
    Consulta o status atual da votacao no banco de dados.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        str: Status atual da votacao.
    """
    cursor.execute("SELECT status FROM controle_votacao WHERE id = 1")
    resultado = cursor.fetchone()

    if not resultado:
        return STATUS_FECHADA

    return resultado[0]


def formatar_percentual(parte, total):
    """
    Calcula e formata um percentual com duas casas decimais.

    Args:
        parte (int): Quantidade parcial usada no calculo.
        total (int): Quantidade total usada como base do percentual.

    Returns:
        str: Percentual formatado com duas casas decimais.
    """
    if total == 0:
        return "0.00%"

    percentual = (parte / total) * 100

    return f"{percentual:.2f}%"


def votacao_esta_encerrada(cursor):
    """
    Verifica se a votacao ja foi encerrada antes de exibir resultados.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        str: Retorna "SIM" quando a votacao estiver fechada ou "NAO" caso contrario.
    """
    if obter_status_votacao(cursor) == STATUS_FECHADA:
        return "SIM"

    return "NAO"


def obter_total_eleitores(cursor):
    """
    Consulta a quantidade total de eleitores aptos cadastrados.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        int: Total de eleitores cadastrados.
    """
    cursor.execute("SELECT COUNT(*) FROM eleitores")

    return cursor.fetchone()[0]


def obter_total_eleitores_que_votaram(cursor):
    """
    Consulta a quantidade de eleitores marcados com status de voto realizado.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        int: Total de eleitores com status JA_VOTOU.
    """
    cursor.execute("""
        SELECT COUNT(*)
        FROM eleitores
        WHERE status_voto IN ('JA_VOTOU', 'JA VOTOU')
    """)

    return cursor.fetchone()[0]


def exibir_aviso_votacao_aberta(cursor):
    """
    Exibe um aviso quando os resultados forem acessados antes da apuracao.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        str: Retorna "SIM" se os resultados podem ser exibidos ou "NAO" caso contrario.
    """
    if votacao_esta_encerrada(cursor) == "SIM":
        return "SIM"

    print("\nVotacao ainda nao realizada.")

    return "NAO"


def exibir_boletim_urna():
    """
    Exibe o boletim de urna com votos por candidato e declaracao do vencedor.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        if exibir_aviso_votacao_aberta(cursor) == "NAO":
            return

        cursor.execute("""
            SELECT c.nome, c.numero, c.partido, COUNT(v.id) AS total_votos
            FROM candidatos c
            LEFT JOIN votos v ON v.candidato_id = c.id
            GROUP BY c.id, c.nome, c.numero, c.partido
            ORDER BY c.nome
        """)
        candidatos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM votos WHERE candidato_id IS NULL")
        votos_nulos = cursor.fetchone()[0]

        print("\n=== BOLETIM DE URNA ===\n")
        if not candidatos:
            print("Nenhum candidato cadastrado.")
        else:
            for nome, numero, partido, total_votos in candidatos:
                print(f"Nome: {nome}")
                print(f"Numero: {numero}")
                print(f"Partido: {partido}")
                print(f"Total de votos: {total_votos}")
                print("-" * 40)

            print(f"Votos nulos: {votos_nulos}")

            maior_votacao = max(candidato[3] for candidato in candidatos)
            vencedores = [
                candidato for candidato in candidatos
                if candidato[3] == maior_votacao
            ]

            print("\n=== VENCEDOR DA ELEICAO ===")
            if maior_votacao == 0:
                print("Nenhum candidato recebeu votos validos.")
            elif len(vencedores) > 1:
                print("Houve empate entre os candidatos mais votados:")
                for nome, numero, partido, total_votos in vencedores:
                    print(f"{nome} | Numero: {numero} | Partido: {partido} | Votos: {total_votos}")
            else:
                nome, numero, partido, total_votos = vencedores[0]
                print(f"Nome: {nome}")
                print(f"Numero: {numero}")
                print(f"Partido: {partido}")
                print(f"Total de votos: {total_votos}")

    except Exception as erro:
        print("Erro ao exibir boletim de urna:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    input("\nPressione ENTER para continuar...")


def exibir_estatistica_comparecimento():
    """
    Exibe a quantidade e o percentual de comparecimento dos eleitores.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        if exibir_aviso_votacao_aberta(cursor) == "NAO":
            return

        total_eleitores = obter_total_eleitores(cursor)
        total_votantes = obter_total_eleitores_que_votaram(cursor)

        print("\n=== ESTATISTICA DE COMPARECIMENTO ===\n")
        print(f"Eleitores aptos: {total_eleitores}")
        print(f"Pessoas que votaram: {total_votantes}")
        print(f"Percentual de comparecimento: {formatar_percentual(total_votantes, total_eleitores)}")

    except Exception as erro:
        print("Erro ao exibir estatistica de comparecimento:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    input("\nPressione ENTER para continuar...")


def exibir_votos_por_partido():
    """
    Exibe a somatoria de votos recebidos por cada partido.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        if exibir_aviso_votacao_aberta(cursor) == "NAO":
            return

        cursor.execute("""
            SELECT c.partido, COUNT(v.id) AS total_votos
            FROM candidatos c
            LEFT JOIN votos v ON v.candidato_id = c.id
            GROUP BY c.partido
            ORDER BY c.partido
        """)
        partidos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM votos WHERE candidato_id IS NULL")
        votos_nulos = cursor.fetchone()[0]

        print("\n=== VOTOS POR PARTIDO ===\n")
        if not partidos:
            print("Nenhum partido encontrado.")
        else:
            for partido, total_votos in partidos:
                print(f"Partido: {partido} | Votos: {total_votos}")

        print(f"Votos nulos: {votos_nulos}")

    except Exception as erro:
        print("Erro ao exibir votos por partido:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    input("\nPressione ENTER para continuar...")


def exibir_validacao_integridade():
    """
    Compara o total de votos registrados com o total de eleitores que votaram.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        if exibir_aviso_votacao_aberta(cursor) == "NAO":
            return

        cursor.execute("SELECT COUNT(*) FROM votos")
        total_votos = cursor.fetchone()[0]
        total_eleitores_ja_votaram = obter_total_eleitores_que_votaram(cursor)

        print("\n=== VALIDACAO DE INTEGRIDADE ===\n")
        print(f"Total de votos registrados na urna: {total_votos}")
        print(f"Eleitores com status JA_VOTOU: {total_eleitores_ja_votaram}")

        if total_votos == total_eleitores_ja_votaram:
            print("\nResultado: INTEGRO")
            print("O total de votos confere com a quantidade de eleitores que votaram.")
        else:
            print("\nResultado: INCONSISTENTE")
            print("Ha divergencia entre votos registrados e eleitores marcados como JA_VOTOU.")

    except Exception as erro:
        print("Erro ao exibir validacao de integridade:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    input("\nPressione ENTER para continuar...")
