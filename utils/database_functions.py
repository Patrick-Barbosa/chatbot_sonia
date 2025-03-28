import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Global variable for schema
SCHEMA = os.getenv("schema")

def get_db_connection():
    """Retorna uma conexão com o banco de dados usando variáveis do .env."""
    return psycopg2.connect(
        dbname=os.getenv("database"),
        user=os.getenv("username"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port")
    )

def check_phone_number(phone_number):
    """Consulta a tabela clientes para verificar se o número de telefone existe."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"SELECT EXISTS(SELECT 1 FROM {SCHEMA}.clientes WHERE telefone = %s);"
        cursor.execute(query, (phone_number,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_client_first_name(phone_number):
    """Consulta a tabela clientes para obter o primeiro nome do cliente."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"SELECT primeiro_nome FROM {SCHEMA}.clientes WHERE telefone = %s;"
        cursor.execute(query, (phone_number,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()

def check_user_debts(phone_number):
    """Consulta a tabela de vendas para verificar se o usuário possui dívidas."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"SELECT EXISTS(SELECT 1 FROM {SCHEMA}.f_vendas WHERE telefone = %s AND pagamento = FALSE);"
        cursor.execute(query, (phone_number,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_user_debt_amount(phone_number):
    """Consulta a tabela de vendas para calcular o valor total das dívidas do usuário."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"SELECT SUM(valor) FROM {SCHEMA}.f_vendas WHERE telefone = %s AND pagamento = FALSE;"
        cursor.execute(query, (phone_number,))
        result = cursor.fetchone()
        return result[0] if result[0] else 0.0  # Return 0.0 if no debts are found
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return 0.0
    finally:
        if connection:
            cursor.close()
            connection.close()

def update_payment_status(phone_number, payment_id):
    """Atualiza o status de pagamento das dívidas do usuário."""
    try:
        connection = get_db_connection()
        connection.autocommit = False  # Start transaction
        cursor = connection.cursor()
        
        # Update all unpaid debts for this user
        query = f"""
            UPDATE {SCHEMA}.f_vendas 
            SET pagamento = TRUE,
                data_pagamento = CURRENT_TIMESTAMP,
                id_transacao = %s
            WHERE telefone = %s AND pagamento = FALSE;
        """
        cursor.execute(query, (payment_id, phone_number))
        
        connection.commit()
        return True
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao atualizar status de pagamento: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()
