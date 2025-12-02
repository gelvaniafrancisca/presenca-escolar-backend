import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',       # seu host MySQL
            user='root',            # usuário MySQL
            password='sua_senha',   # senha MySQL
            database='sistema_presenca'  # nome do banco
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None
