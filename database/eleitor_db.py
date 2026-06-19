import random

from database.conexao import conectar
from utils.criptografia import cifra_hill, normalizar_chave, normalizar_numero
from utils.documentos import validar_cpf, validar_titulo
from utils.tela import limpar_tela


CHAVE_HILL = [[3, 3],
              [2, 5]]


def gerar_chave_acesso(nome_completo):
    """
    Gera uma chave de acesso individual para o eleitor.

    Args:
        nome_completo (str): Nome completo do eleitor.

    Returns:
        str | None: Chave gerada ou None se o nome for invalido.
    """
    nomes = nome_completo.strip().upper().split()

    if len(nomes) < 2:
        return None

    return nomes[0][:2] + nomes[1][0] + str(random.randint(1000, 9999))


def criptografar_chave_acesso(chave_gerada):
    """
    Criptografa uma chave de acesso usando Cifra de Hill.

    Args:
        chave_gerada (str): Chave de acesso em texto claro.

    Returns:
        str: Chave de acesso criptografada.
    """
    chave_normalizada = normalizar_chave(chave_gerada)

    if not chave_normalizada:
        return ""

    while len(chave_normalizada) < 8:
        chave_normalizada += chave_normalizada[-1]

    return cifra_hill(chave_normalizada, CHAVE_HILL)


def criptografar_cpf(cpf):
    """
    Criptografa um CPF normalizado usando Cifra de Hill.

    Args:
        cpf (str): CPF informado pelo usuario.

    Returns:
        str: CPF criptografado para armazenamento no banco de dados.
    """

    return cifra_hill(normalizar_numero(cpf), CHAVE_HILL)


def buscar_eleitor_por_id(cursor, id_eleitor):
    """
    Busca um eleitor pelo identificador unico.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.
        id_eleitor (str): Identificador do eleitor pesquisado.

    Returns:
        tuple | None: Dados do eleitor encontrado ou None caso nao exista.
    """

    cursor.execute("""
        SELECT id, nome_completo, cpf_criptografado, titulo_eleitor, e_mesario
        FROM eleitores
        WHERE id = %s
    """, (id_eleitor,))

    return cursor.fetchone()


def ler_cpf_unico(cursor, id_ignorado=""):
    """
    Le, valida e garante a unicidade de um CPF.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.
        id_ignorado (str): ID ignorado durante edicao de eleitor.

    Returns:
        str: CPF valido e ainda nao cadastrado para outro eleitor.
    """
    
    cpf = ""
    while cpf == "":
        cpf_digitado = input("CPF: ")

        if not validar_cpf(cpf_digitado):
            print("CPF invalido. Tente novamente.")
            continue

        cpf_cripto = criptografar_cpf(cpf_digitado)
        cursor.execute("""
            SELECT id
            FROM eleitores
            WHERE cpf_criptografado = %s AND id <> %s
        """, (cpf_cripto, id_ignorado))

        if cursor.fetchone():
            print("CPF ja cadastrado! Digite outro.")
            continue

        cpf = cpf_digitado

    return cpf


def ler_titulo_unico(cursor, id_ignorado=""):
    """
    Le, valida e garante a unicidade de um titulo de eleitor.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.
        id_ignorado (str): ID ignorado durante edicao de eleitor.

    Returns:
        str: Titulo valido e ainda nao cadastrado para outro eleitor.
    """

    titulo_limpo = ""
    while titulo_limpo == "":
        titulo = input("Titulo de eleitor: ")

        if not validar_titulo(titulo):
            print("Titulo invalido. Tente novamente.")
            continue

        titulo_digitado = ''.join(filter(str.isdigit, titulo))
        cursor.execute("""
            SELECT id
            FROM eleitores
            WHERE titulo_eleitor = %s AND id <> %s
        """, (titulo_digitado, id_ignorado))

        if cursor.fetchone():
            print("Titulo ja cadastrado! Digite outro.")
            continue

        titulo_limpo = titulo_digitado

    return titulo_limpo


def inserir_eleitor():
    """
    Cadastra um novo eleitor no banco de dados.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        nome = input("Nome completo: ")
        cpf = ler_cpf_unico(cursor)
        titulo_limpo = ler_titulo_unico(cursor)

        mesario = input("Deseja ser mesario? (s/n): ").lower()
        e_mesario = "Sim" if mesario == "s" or mesario == "sim" else "Nao"

        chave_gerada = gerar_chave_acesso(nome)
        if not chave_gerada:
            print("Nome invalido.")
            return

        cursor.execute("""
            INSERT INTO eleitores
            (nome_completo, cpf_criptografado, titulo_eleitor, e_mesario,
             chave_acesso_criptografada, status_voto, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            nome,
            criptografar_cpf(cpf),
            titulo_limpo,
            e_mesario,
            criptografar_chave_acesso(chave_gerada),
            "NAO_VOTOU"
        ))
        conexao.commit()

        print("Eleitor cadastrado com sucesso!")
        print("SUA CHAVE DE ACESSO:", chave_gerada)

    except Exception as e:
        print("Erro:", e)

    finally:
        cursor.close()
        conexao.close()
        input("Pressione ENTER...")


def buscar_eleitor():
    """
    Busca e exibe um eleitor por CPF ou titulo de eleitor.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        limpar_tela()
        print("=== BUSCAR ELEITOR ===")
        print("1 - CPF")
        print("2 - Titulo de eleitor")
        opcao = input("\nEscolha: ")
        limpar_tela()

        if opcao == "1":
            cpf = input("Digite o CPF: ")
            if not validar_cpf(cpf):
                print("CPF invalido.")
                return

            cursor.execute("""
                SELECT id, nome_completo, cpf_criptografado, titulo_eleitor,
                       e_mesario, status_voto, criado_em
                FROM eleitores
                WHERE cpf_criptografado = %s
            """, (criptografar_cpf(cpf),))

        elif opcao == "2":
            titulo = input("Digite o titulo: ")
            if not validar_titulo(titulo):
                print("Titulo invalido.")
                return

            titulo_limpo = ''.join(filter(str.isdigit, titulo))
            cursor.execute("""
                SELECT id, nome_completo, cpf_criptografado, titulo_eleitor,
                       e_mesario, status_voto, criado_em
                FROM eleitores
                WHERE titulo_eleitor = %s
            """, (titulo_limpo,))

        else:
            print("Opcao invalida.")
            return

        resultado = cursor.fetchone()
        limpar_tela()

        if resultado:
            id, nome, cpf, titulo, mesario, status, criado_em = resultado
            print("ELEITOR ENCONTRADO\n")
            print(f"ID: {id}")
            print(f"Nome: {nome}")
            print(f"CPF (criptografado): {cpf}")
            print(f"Titulo: {titulo}")
            print(f"Mesario: {mesario}")
            print(f"Status do voto: {status}")
            print(f"Criado em: {criado_em}")
        else:
            print("Eleitor nao encontrado.")

    except Exception as e:
        print("Erro:", e)

    finally:
        cursor.close()
        conexao.close()
        input("\nPressione ENTER para continuar...")


def editar_eleitor():
    """
    Edita os dados cadastrais de um eleitor existente.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        limpar_tela()
        print("=== EDITAR ELEITOR ===\n")

        id_eleitor = input("Digite o ID do eleitor: ").strip()
        if not id_eleitor.isdigit():
            print("ID invalido.")
            return

        eleitor = buscar_eleitor_por_id(cursor, id_eleitor)
        if not eleitor:
            print("Eleitor nao encontrado.")
            return

        print("\nDados atuais:")
        print(f"ID: {eleitor[0]}")
        print(f"Nome: {eleitor[1]}")
        print(f"CPF criptografado: {eleitor[2]}")
        print(f"Titulo: {eleitor[3]}")
        print(f"Mesario: {eleitor[4]}")

        nome = input("\nNovo nome completo (ENTER para manter): ").strip()
        nome = eleitor[1] if nome == "" else nome

        cpf = input("Alterar CPF? (s/n): ").strip().lower()
        cpf_cripto = eleitor[2]
        if cpf == "s" or cpf == "sim":
            cpf_cripto = criptografar_cpf(ler_cpf_unico(cursor, id_eleitor))

        titulo = input("Alterar titulo? (s/n): ").strip().lower()
        titulo_limpo = eleitor[3]
        if titulo == "s" or titulo == "sim":
            titulo_limpo = ler_titulo_unico(cursor, id_eleitor)

        mesario = input("Deseja ser mesario? (s/n ou ENTER para manter): ").strip().lower()
        if mesario == "":
            e_mesario = eleitor[4]
        elif mesario == "s" or mesario == "sim":
            e_mesario = "Sim"
        else:
            e_mesario = "Nao"

        cursor.execute("""
            UPDATE eleitores
            SET nome_completo = %s,
                cpf_criptografado = %s,
                titulo_eleitor = %s,
                e_mesario = %s
            WHERE id = %s
        """, (nome, cpf_cripto, titulo_limpo, e_mesario, id_eleitor))

        conexao.commit()
        print("\nEleitor atualizado com sucesso!")

    except Exception as e:
        print("Erro:", e)

    finally:
        cursor.close()
        conexao.close()
        input("\nPressione ENTER para continuar...")


def remover_eleitor():
    """
    Remove um eleitor cadastrado apos confirmacao do usuario.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        limpar_tela()
        print("=== REMOVER ELEITOR ===\n")

        id_eleitor = input("Digite o ID do eleitor: ").strip()
        if not id_eleitor.isdigit():
            print("ID invalido.")
            return

        eleitor = buscar_eleitor_por_id(cursor, id_eleitor)
        if not eleitor:
            print("Eleitor nao encontrado.")
            return

        print("\nEleitor encontrado:")
        print(f"ID: {eleitor[0]}")
        print(f"Nome: {eleitor[1]}")
        print(f"Titulo: {eleitor[3]}")

        confirmar = input("\nDeseja realmente remover este eleitor? (s/n): ").strip().lower()
        if confirmar != "s" and confirmar != "sim":
            print("Remocao cancelada.")
            return

        cursor.execute("DELETE FROM eleitores WHERE id = %s", (id_eleitor,))
        conexao.commit()
        print("\nEleitor removido com sucesso!")

    except Exception as e:
        print("Erro:", e)

    finally:
        cursor.close()
        conexao.close()
        input("\nPressione ENTER para continuar...")


def listar_eleitores():
    """
    Lista todos os eleitores cadastrados no banco de dados.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome_completo, cpf_criptografado, titulo_eleitor,
               e_mesario, status_voto, criado_em
        FROM eleitores
    """)

    for (id, nome, cpf_hash, titulo, mesario, status, criado_em) in cursor.fetchall():
        print(f"ID: {id}")
        print(f"Nome: {nome}")
        print(f"CPF: {cpf_hash}")
        print(f"Titulo: {titulo}")
        print(f"Mesario: {mesario}")
        print(f"Status do voto: {status}")
        print(f"Criado em: {criado_em}")
        print("-" * 30)

    input("\nPressione ENTER...")

    cursor.close()
    conexao.close()
