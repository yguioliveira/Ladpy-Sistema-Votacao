from database.conexao import conectar


def listar_candidatos():
    """
    Lista todos os candidatos cadastrados no banco de dados.

    Args:
        None.

    Returns:
        None: Esta funcao nao retorna valor.
    """

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, numero, partido
        FROM candidatos
    """)

    for (id, nome, numero, partido) in cursor.fetchall():
        print(f"ID: {id}")
        print(f"Nome: {nome}")
        print(f"Numero: {numero}")
        print(f"Partido: {partido}")
        print("-" * 30)

    input("\nPressione ENTER...")

    cursor.close()
    conexao.close()
