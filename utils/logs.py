from datetime import datetime
from database.conexao import conectar
import os


ARQUIVO_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs_ocorrencias.txt")


def registrar_log(descricao):
    """
    Registra uma ocorrencia de auditoria em arquivo de texto e no banco MySQL.

    Args:
        descricao (str): Descricao da ocorrencia registrada pelo sistema.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{momento}] {descricao}\n")

    partes = descricao.split(":", 1)
    tipo = partes[0].strip().upper()
    descricao_banco = partes[1].strip() if len(partes) > 1 else descricao

    if tipo not in ("ABERTURA", "ALERTA", "SUCESSO", "ENCERRAMENTO"):
        tipo = "ALERTA"
        descricao_banco = descricao

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data_hora DATETIME NOT NULL,
                tipo ENUM('ABERTURA', 'ALERTA', 'SUCESSO', 'ENCERRAMENTO') NOT NULL,
                descricao TEXT NOT NULL
            )
        """)
        cursor.execute("""
            INSERT INTO logs (data_hora, tipo, descricao)
            VALUES (%s, %s, %s)
        """, (momento, tipo, descricao_banco))
        conexao.commit()

    except Exception:
        pass

    finally:
        try:
            cursor.close()
            conexao.close()
        except Exception:
            pass


def exibir_logs():
    """
    Exibe as ocorrencias de auditoria registradas no banco ou em arquivo.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT data_hora, tipo, descricao
            FROM logs
            ORDER BY id
        """)
        registros = cursor.fetchall()

        print("\n=== LOGS DE OCORRENCIAS ===\n")
        if registros:
            for data_hora, tipo, descricao in registros:
                momento = data_hora.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{momento}] {tipo}: {descricao}")
        else:
            print("Nenhum log de ocorrencia foi registrado.")

        input("\nPressione ENTER para continuar...")
        cursor.close()
        conexao.close()
        return

    except Exception:
        try:
            cursor.close()
            conexao.close()
        except Exception:
            pass

    if not os.path.exists(ARQUIVO_LOG):
        print("Nenhum log de ocorrencia foi registrado.")
        input("\nPressione ENTER para continuar...")
        return

    print("\n=== LOGS DE OCORRENCIAS ===\n")
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read().strip()

    print(conteudo if conteudo else "Nenhum log de ocorrencia foi registrado.")
    input("\nPressione ENTER para continuar...")
 
