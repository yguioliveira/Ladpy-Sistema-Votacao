import random
import string
from datetime import datetime

from database.conexao import conectar
from utils.input_utils import ler_opcao
from utils.criptografia import cifra_hill, normalizar_chave, normalizar_numero
from utils.documentos import validar_titulo
from utils.logs import registrar_log
from utils.tela import limpar_tela


CHAVE_HILL = [[3, 3], [2, 5]]
STATUS_ABERTA = "ABERTA"
STATUS_FECHADA = "FECHADA"
MAPA_LETRA_NUMERO = {
    'A': '0', 'B': '1', 'C': '2', 'D': '3', 'E': '4',
    'F': '5', 'G': '6', 'H': '7', 'I': '8', 'J': '9'
}


def criptografar_chave_acesso(chave_acesso):
    """
    Criptografa uma chave de acesso usando a mesma regra aplicada no cadastro.

    Args:
        chave_acesso (str): Chave de acesso em texto claro.

    Returns:
        str: Chave de acesso criptografada pela Cifra de Hill.
    """
    chave_normalizada = normalizar_chave(chave_acesso)

    if not chave_normalizada:
        return ""

    controle = 1

    while controle != 0:
        if len(chave_normalizada) < 8:
            chave_normalizada += chave_normalizada[-1]
        else:
            controle = 0

    return cifra_hill(chave_normalizada, CHAVE_HILL)



def criptografar_protocolo(protocolo):
    """
    Criptografa o protocolo de votacao usando Cifra de Hill.

    Args:
        protocolo (str): Protocolo em texto claro gerado para o eleitor.

    Returns:
        str: Protocolo criptografado para armazenamento no banco de dados.
    """
    protocolo_normalizado = normalizar_chave(protocolo)

    if not protocolo_normalizado:
        return ""

    return cifra_hill(protocolo_normalizado, CHAVE_HILL)


def inverso_modular(valor, modulo):
    """
    Calcula o inverso modular de um valor.

    Args:
        valor (int): Valor que tera o inverso calculado.
        modulo (int): Modulo usado no calculo.

    Returns:
        int: Inverso modular encontrado.
    """
    valor = valor % modulo

    for candidato in range(1, modulo):
        if (valor * candidato) % modulo == 1:
            return candidato

    raise ValueError("Nao existe inverso modular para a chave informada.")


def matriz_inversa_hill(chave):
    """
    Calcula a matriz inversa 2x2 usada para descriptografar a Cifra de Hill.

    Args:
        chave (list): Matriz 2x2 usada na criptografia.

    Returns:
        list: Matriz inversa modular.
    """
    determinante = (chave[0][0] * chave[1][1]) - (chave[0][1] * chave[1][0])
    inverso_determinante = inverso_modular(determinante, 26)

    return [
        [(chave[1][1] * inverso_determinante) % 26,
         (-chave[0][1] * inverso_determinante) % 26],
        [(-chave[1][0] * inverso_determinante) % 26,
         (chave[0][0] * inverso_determinante) % 26]
    ]


def descriptografar_texto_hill(texto_criptografado, chave):
    """
    Descriptografa um texto criptografado pela Cifra de Hill.

    Args:
        texto_criptografado (str): Texto criptografado.
        chave (list): Matriz 2x2 usada na criptografia original.

    Returns:
        str: Texto normalizado descriptografado.
    """
    chave_inversa = matriz_inversa_hill(chave)

    return cifra_hill(texto_criptografado, chave_inversa)


def restaurar_formato_protocolo(protocolo_normalizado):
    """
    Restaura o formato exibido ao eleitor a partir do protocolo normalizado.

    Args:
        protocolo_normalizado (str): Protocolo descriptografado com digitos mapeados para letras.

    Returns:
        str: Protocolo em formato legivel.
    """
    if len(protocolo_normalizado) < 12:
        return protocolo_normalizado

    prefixo = protocolo_normalizado[:3]
    numeros = ""

    for letra in protocolo_normalizado[3:]:
        numeros += MAPA_LETRA_NUMERO.get(letra, letra)

    return prefixo + numeros


def descriptografar_protocolo(protocolo_criptografado):
    """
    Descriptografa o protocolo de votacao armazenado no banco de dados.

    Args:
        protocolo_criptografado (str): Protocolo criptografado.

    Returns:
        str: Protocolo restaurado para exibicao na auditoria.
    """
    protocolo_normalizado = descriptografar_texto_hill(protocolo_criptografado, CHAVE_HILL)

    return restaurar_formato_protocolo(protocolo_normalizado)


def cpf_criptografado_confere(cpf_criptografado, quatro_primeiros_digitos):
    """
    Confere os quatro primeiros digitos do CPF contra o CPF criptografado.

    Args:
        cpf_criptografado (str): CPF completo armazenado com criptografia.
        quatro_primeiros_digitos (str): Quatro primeiros digitos informados.

    Returns:
        str: Retorna "SIM" quando os quatro digitos conferem ou "NAO" caso contrario.
    """
    cpf_parcial = "".join(filter(str.isdigit, quatro_primeiros_digitos))

    if len(cpf_parcial) != 4:
        return "NAO"

    cpf_parcial_criptografado = cifra_hill(normalizar_numero(cpf_parcial), CHAVE_HILL)
    if cpf_criptografado.startswith(cpf_parcial_criptografado):
        return "SIM"

    return "NAO"


def valor_sim(valor):
    """
    Interpreta valores de texto usados para indicar resposta afirmativa.

    Args:
        valor (str): Texto que sera interpretado.

    Returns:
        str: Retorna "SIM" para respostas afirmativas ou "NAO" caso contrario.
    """
    if str(valor).strip().lower() in ("s", "sim", "1", "mesario"):
        return "SIM"

    return "NAO"


def autenticar_mesario(cursor):
    """
    Solicita e valida as credenciais de um eleitor com perfil de mesario.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        tuple | None: Dados do mesario autenticado ou None quando a validacao falhar.
    """
    controle_titulo = 1
    mesario = None

    while controle_titulo != 0:
        titulo = input("Titulo de eleitor: ").strip()
        titulo_limpo = "".join(filter(str.isdigit, titulo))

        if not validar_titulo(titulo_limpo):
            registrar_log("ALERTA: Tentativa de acesso negado ao mesario por titulo invalido")
            print("\nTitulo de eleitor incorreto. Digite novamente.\n")
            continue

        cursor.execute("""
            SELECT id, nome_completo, cpf_criptografado, titulo_eleitor,
                   e_mesario, chave_acesso_criptografada
            FROM eleitores
            WHERE titulo_eleitor = %s
        """, (titulo_limpo,))

        mesario = cursor.fetchone()

        if not mesario or valor_sim(mesario[4]) != "SIM":
            registrar_log("ALERTA: Tentativa de acesso negado ao mesario por usuario inexistente ou sem permissao")
            print("\nTitulo de eleitor incorreto ou usuario sem perfil de mesario.")
            print("Digite novamente.\n")
            continue

        controle_titulo = 0

    controle_cpf = 1

    while controle_cpf != 0:
        cpf_parcial = input("4 primeiros digitos do CPF: ").strip()

        if cpf_criptografado_confere(mesario[2], cpf_parcial) == "SIM":
            controle_cpf = 0
        else:
            registrar_log("ALERTA: Tentativa de acesso negado ao mesario por CPF incorreto")
            print("\nCPF incorreto. Digite novamente.\n")

    controle_chave = 1

    while controle_chave != 0:
        chave_acesso = input("Chave de acesso: ").strip()
        chave_criptografada = criptografar_chave_acesso(chave_acesso)

        if chave_criptografada == mesario[5]:
            controle_chave = 0
        else:
            registrar_log("ALERTA: Tentativa de acesso negado ao mesario por chave incorreta")
            print("\nChave de acesso incorreta. Digite novamente.\n")

    return mesario



def status_indica_voto_realizado(status_voto):
    """
    Verifica se o status do eleitor indica voto ja realizado.

    Args:
        status_voto (str): Status armazenado no cadastro do eleitor.

    Returns:
        str: Retorna "SIM" quando o eleitor ja votou ou "NAO" caso contrario.
    """
    status_normalizado = str(status_voto).strip().upper()

    if status_normalizado in ("JA_VOTOU", "JA VOTOU"):
        return "SIM"

    return "NAO"


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


def autenticar_eleitor_para_voto(cursor):
    """
    Solicita e valida as credenciais do eleitor antes do voto.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        tuple: Retorna os dados do eleitor e o codigo da validacao realizada.
    """
    controle_titulo = 1
    eleitor = None

    while controle_titulo != 0:
        titulo = input("Titulo de eleitor: ").strip()
        titulo_limpo = "".join(filter(str.isdigit, titulo))

        if not validar_titulo(titulo_limpo):
            registrar_log("ALERTA: Tentativa de acesso negado ao eleitor por titulo invalido")
            print("\nTitulo de eleitor incorreto. Digite novamente.\n")
            continue

        cursor.execute("""
            SELECT id, nome_completo, cpf_criptografado, titulo_eleitor,
                   e_mesario, chave_acesso_criptografada, status_voto
            FROM eleitores
            WHERE titulo_eleitor = %s
        """, (titulo_limpo,))

        eleitor = cursor.fetchone()

        if not eleitor:
            registrar_log("ALERTA: Tentativa de acesso negado ao eleitor por titulo nao cadastrado")
            print("\nTitulo de eleitor incorreto. Digite novamente.\n")
            continue

        controle_titulo = 0

    if status_indica_voto_realizado(eleitor[6]) == "SIM":
        return None, "VOTO_DUPLO"

    controle_cpf = 1

    while controle_cpf != 0:
        cpf_parcial = input("4 primeiros digitos do CPF: ").strip()

        if cpf_criptografado_confere(eleitor[2], cpf_parcial) == "SIM":
            controle_cpf = 0
        else:
            registrar_log("ALERTA: Tentativa de acesso negado ao eleitor por CPF incorreto")
            print("\nCPF incorreto. Digite novamente.\n")

    controle_chave = 1

    while controle_chave != 0:
        chave_acesso = input("Chave de acesso: ").strip()
        chave_criptografada = criptografar_chave_acesso(chave_acesso)

        if chave_criptografada == eleitor[5]:
            controle_chave = 0
        else:
            registrar_log("ALERTA: Tentativa de acesso negado ao eleitor por chave incorreta")
            print("\nChave de acesso incorreta. Digite novamente.\n")

    return eleitor, "VALIDADO"



def buscar_candidato_por_numero(cursor, numero_candidato):
    """
    Busca um candidato pelo numero de votacao informado.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.
        numero_candidato (str): Numero digitado pelo eleitor.

    Returns:
        tuple | None: Dados do candidato encontrado ou None para voto nulo.
    """
    cursor.execute("""
        SELECT id, nome, numero, partido
        FROM candidatos
        WHERE numero = %s
    """, (numero_candidato,))

    return cursor.fetchone()


def gerar_protocolo_votacao(numero_candidato):
    """
    Gera o protocolo de confirmacao do voto.

    Args:
        numero_candidato (str): Numero do candidato ou "00" para voto nulo.

    Returns:
        str: Protocolo de votacao em texto claro para exibicao ao eleitor.
    """
    letras = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
    ano = datetime.now().strftime("%y")
    numero = "".join(filter(str.isdigit, str(numero_candidato))).zfill(2)[-2:]
    aleatorio = str(random.randint(10000, 99999))

    return f"V{letras}{ano}{numero}{aleatorio}"


def realizar_zerezima(cursor):
    """
    Limpa registros de votacao anteriores e exibe candidatos com zero votos.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    cursor.execute("DELETE FROM votos")
    cursor.execute("UPDATE eleitores SET status_voto = 'NAO_VOTOU'")

    cursor.execute("""
        SELECT nome, numero, partido
        FROM candidatos
        ORDER BY nome
    """)

    candidatos = cursor.fetchall()

    print("\n=== ZEREZIMA ===")
    if not candidatos:
        print("Nenhum candidato cadastrado.")
        return

    for candidato in candidatos:
        print(
            f"Nome: {candidato[0]} | "
            f"Numero: {candidato[1]} | "
            f"Partido: {candidato[2]} | "
            "Votos: 0"
        )


def exibir_protocolos_votacao():
    """
    Exibe todos os protocolos de votacao registrados para auditoria.

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

        cursor.execute("""
            SELECT v.protocolo_criptografado, v.data_hora, c.numero, c.nome
            FROM votos v
            LEFT JOIN candidatos c ON c.id = v.candidato_id
        """)

        registros = []
        for protocolo_criptografado, data_hora, numero_candidato, nome_candidato in cursor.fetchall():
            protocolo = descriptografar_protocolo(protocolo_criptografado)
            registros.append((protocolo, data_hora, numero_candidato, nome_candidato))

        registros.sort(key=lambda item: item[0])

        print("\n=== PROTOCOLOS DE VOTACAO ===\n")
        if not registros:
            print("Nenhum protocolo de votacao foi registrado.")
        else:
            for protocolo, data_hora, numero_candidato, nome_candidato in registros:
                if hasattr(data_hora, "strftime"):
                    momento = data_hora.strftime("%Y-%m-%d %H:%M:%S")
                elif data_hora:
                    momento = str(data_hora)
                else:
                    momento = "Data nao registrada"

                candidato = "Voto nulo"
                if numero_candidato and nome_candidato:
                    candidato = f"{numero_candidato} - {nome_candidato}"

                print(f"Protocolo: {protocolo}")
                print(f"Data/hora: {momento}")
                print("-" * 40)

    except Exception as erro:
        print("Erro ao exibir protocolos de votacao:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

        input("\nPressione ENTER para continuar...")


def atualizar_status_votacao(cursor, status):
    """
    Atualiza o estado oficial da urna no banco de dados.

    Args:
        cursor (mysql.connector.cursor.MySQLCursor): Cursor ativo do banco de dados.
        status (str): Novo status da urna.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if status == STATUS_ABERTA:
        cursor.execute("""
            UPDATE controle_votacao
            SET status = %s, aberto_em = %s, encerrado_em = NULL
            WHERE id = 1
        """, (status, agora))
    else:
        cursor.execute("""
            UPDATE controle_votacao
            SET status = %s, encerrado_em = %s
            WHERE id = 1
        """, (status, agora))


def registrar_voto():
    """
    Registra o voto do eleitor autenticado no banco de dados.

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

        if obter_status_votacao(cursor) != STATUS_ABERTA:
            print("\nERRO: A votacao ainda nao foi aberta pelo mesario.")
            input("\nPressione ENTER para continuar...")
            return

        limpar_tela()
        print("=== IDENTIFICACAO DO ELEITOR ===\n")
        eleitor, status_validacao = autenticar_eleitor_para_voto(cursor)

        if status_validacao == "VOTO_DUPLO":
            registrar_log("ALERTA: Tentativa de voto duplo")
            print("\nERRO: Este eleitor ja votou. Nao e permitido votar novamente.")
            input("\nPressione ENTER para continuar...")
            return

        if not eleitor:
            registrar_log("ALERTA: Tentativa de acesso negado")
            print("\nValidacao falhou. Dados invalidos.")
            input("\nPressione ENTER para continuar...")
            return

        controle_voto = 1
        candidato = None
        numero_digitado = ""

        while controle_voto != 0:
            limpar_tela()
            print("=== REGISTRO DO VOTO ===\n")
            numero_digitado = input("Numero do candidato: ").strip()
            candidato = buscar_candidato_por_numero(cursor, numero_digitado)

            if candidato:
                print("\nConfira seu voto:")
                print(f"Nome: {candidato[1]}")
                print(f"Numero: {candidato[2]}")
                print(f"Partido: {candidato[3]}")
            else:
                print("\nNumero nao encontrado.")
                print("Ao confirmar, o voto sera registrado como NULO.")

            confirmar = input("\nConfirmar voto? (Sim/Nao): ").strip()

            if valor_sim(confirmar) == "SIM":
                controle_voto = 0

        candidato_id = candidato[0] if candidato else None
        numero_protocolo = candidato[2] if candidato else "00"
        protocolo = gerar_protocolo_votacao(numero_protocolo)
        protocolo_criptografado = criptografar_protocolo(protocolo)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO votos (candidato_id, protocolo_criptografado, data_hora)
            VALUES (%s, %s, %s)
        """, (candidato_id, protocolo_criptografado, data_hora))

        cursor.execute("""
            UPDATE eleitores
            SET status_voto = 'JA_VOTOU'
            WHERE id = %s
        """, (eleitor[0],))

        conexao.commit()
        registrar_log("SUCESSO: Voto realizado com sucesso")

        print("\nVoto registrado com sucesso!")
        print(f"Protocolo de votacao: {protocolo}")
        input("\nPressione ENTER para continuar...")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao registrar voto:", erro)
        input("\nPressione ENTER para continuar...")

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def abrir_sistema_votacao():
    """
    Abre o sistema de votacao apos validar o mesario e executar a zerezima.

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

        if obter_status_votacao(cursor) == STATUS_ABERTA:
            limpar_tela()
            print("=== SISTEMA DE VOTACAO ABERTO ===")
            print("\nSistema ja em funcionamento.")
            print("Informe os dados do mesario para acessar a operacao da urna.\n")
            mesario = autenticar_mesario(cursor)

            if not mesario:
                registrar_log("ALERTA: Tentativa de acesso negado")
                print("\nValidacao falhou. Dados invalidos ou usuario sem perfil de mesario.")
                input("\nPressione ENTER para continuar...")
                return

            input("\nValidacao realizada com sucesso. Pressione ENTER para continuar...")
            menu_operacao_urna()
            return

        limpar_tela()
        print("=== ABERTURA DO SISTEMA DE VOTACAO ===\n")
        mesario = autenticar_mesario(cursor)

        if not mesario:
            registrar_log("ALERTA: Tentativa de acesso negado")
            print("\nValidacao falhou. Dados invalidos ou usuario sem perfil de mesario.")
            input("\nPressione ENTER para continuar...")
            return

        realizar_zerezima(cursor)
        atualizar_status_votacao(cursor, STATUS_ABERTA)
        conexao.commit()
        registrar_log("ABERTURA: Votacao iniciada com sucesso. Total de votos zerado.")

        print("\nSistema de votacao aberto com sucesso.")
        input("\nPressione ENTER para acessar a operacao da urna...")
        menu_operacao_urna()

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao abrir sistema de votacao:", erro)
        input("\nPressione ENTER para continuar...")

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def encerrar_sistema_votacao():
    """
    Encerra a votacao apos validar o mesario e exigir dupla confirmacao.

    Args:
        None.

    Returns:
        str: Retorna "ENCERRADA" quando a votacao foi encerrada ou "CANCELADA" caso contrario.
    """
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        limpar_tela()
        print("=== ENCERRAMENTO DO SISTEMA DE VOTACAO ===\n")
        mesario = autenticar_mesario(cursor)

        if not mesario:
            registrar_log("ALERTA: Tentativa de acesso negado")
            print("\nValidacao falhou. Dados invalidos ou usuario sem perfil de mesario.")
            input("\nPressione ENTER para continuar...")
            return "CANCELADA"

        confirmar = input("\nDeseja realmente encerrar a votacao? (Sim/Nao): ").strip()
        if valor_sim(confirmar) != "SIM":
            print("\nEncerramento cancelado.")
            input("\nPressione ENTER para continuar...")
            return "CANCELADA"

        controle_chave = 1

        while controle_chave != 0:
            segunda_chave = input("Digite novamente a chave de acesso: ").strip()

            if criptografar_chave_acesso(segunda_chave) == mesario[5]:
                controle_chave = 0
            else:
                registrar_log("ALERTA: Chave negada no encerramento")
                print("\nChave negada. Tente novamente.\n")

        atualizar_status_votacao(cursor, STATUS_FECHADA)
        conexao.commit()
        registrar_log("ENCERRAMENTO: Votacao finalizada com sucesso.")

        print("\nSistema de votacao encerrado com sucesso.")
        print("Resultados consolidados e urna fechada para novos votos.")
        input("\nPressione ENTER para continuar...")
        return "ENCERRADA"

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao encerrar sistema de votacao:", erro)
        input("\nPressione ENTER para continuar...")
        return "CANCELADA"

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()



def menu_operacao_urna():
    """
    Exibe o menu liberado apos a zerezima com opcoes de votar ou encerrar.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    opcao = -1

    while opcao != 0:
        limpar_tela()
        print("\n=== OPERACAO DA URNA ===")
        print("1 - Votar")
        print("2 - Encerrar Sistema de Votacao")

        opcao = int(ler_opcao(["1", "2"]))

        if opcao == 1:
            registrar_voto()
        elif opcao == 2:
            if encerrar_sistema_votacao() == "ENCERRADA":
                opcao = 0
