import mysql.connector
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def conectar():
    """
    Cria uma conexao com o banco de dados MySQL do projeto.

    Args:
        None.

    Returns:
        mysql.connector.connection.MySQLConnection: Conexao ativa com o banco.
    """
    
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "projetointegrador_db"))
