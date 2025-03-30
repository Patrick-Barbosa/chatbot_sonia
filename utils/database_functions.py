import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Global variable for schema
SCHEMA = os.getenv("schema")

def get_db_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados PostgreSQL.
    
    A função utiliza variáveis de ambiente armazenadas em um arquivo .env para 
    configurar a conexão de forma segura, evitando expor credenciais no código.
    
    Retorna:
        psycopg2.connection: Objeto de conexão com o banco de dados PostgreSQL
    """
    return psycopg2.connect(
        dbname=os.getenv("database"),
        user=os.getenv("username"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port")
    )

def format_phone_number(phone_number: str) -> str:
    """
    Formata um número de telefone removendo o prefixo '55' se presente.
    
    Args:
        phone_number (str): Número de telefone que pode conter o prefixo '55'
    
    Retorna:
        str: Número de telefone sem o prefixo '55'
    """
    if phone_number.startswith('55'):
        return phone_number[2:]
    return phone_number

def check_phone_number(phone_number: str) -> bool:
    """
    Verifica se um número de telefone está cadastrado na tabela de clientes.
    
    Args:
        phone_number (str): Número de telefone para verificação
    
    Retorna:
        bool: True se o número existe no banco, False caso contrário ou em caso de erro
    
    Exemplo:
        >>> check_phone_number("5511999999999")
        True
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        formatted_phone = format_phone_number(phone_number)
        query = f"SELECT EXISTS(SELECT 1 FROM {SCHEMA}.dclientes WHERE telefone = %s);"
        cursor.execute(query, (formatted_phone,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_client_first_name(phone_number: str) -> str:
    """
    Obtém o primeiro nome do cliente a partir do número de telefone.
    
    Args:
        phone_number (str): Número de telefone do cliente
    
    Retorna:
        str: Primeiro nome do cliente ou None se não encontrado
    
    Exemplo:
        >>> get_client_first_name("5511999999999")
        'Maria'
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        formatted_phone = format_phone_number(phone_number)
        query = f"SELECT nome FROM {SCHEMA}.dclientes WHERE telefone = %s;"
        cursor.execute(query, (formatted_phone,))
        result = cursor.fetchone()
        if result and result[0]:
            # Split the full name and get the first part
            first_name = result[0].split()[0]
            return first_name
        return None
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()

def check_user_debts(phone_number: str) -> bool:
    """
    Verifica se um cliente possui dívidas pendentes.
    
    Esta função realiza um JOIN entre as tabelas de vendas e clientes para
    verificar se existem vendas não pagas associadas ao número de telefone.
    
    Args:
        phone_number (str): Número de telefone do cliente
    
    Retorna:
        bool: True se existem dívidas, False caso contrário
    
    Exemplo:
        >>> check_user_debts("5511999999999")
        True
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        formatted_phone = format_phone_number(phone_number)
        query = f"SELECT EXISTS(SELECT 1 FROM {SCHEMA}.fvendas as f LEFT JOIN {SCHEMA}.dclientes as cli ON UPPER(f.nome) = UPPER(cli.nome) WHERE cli.telefone = %s AND f.pago = FALSE);"
        cursor.execute(query, (formatted_phone,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_user_debt_amount(phone_number: str) -> float:
    """
    Calcula o valor total das dívidas pendentes de um cliente.
    
    Esta função soma todos os valores das vendas não pagas do cliente,
    identificado pelo número de telefone.
    
    Args:
        phone_number (str): Número de telefone do cliente
    
    Retorna:
        float: Soma total das dívidas ou 0.0 se não houver dívidas
    
    Exemplo:
        >>> get_user_debt_amount("5511999999999")
        150.50
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        formatted_phone = format_phone_number(phone_number)
        query = f"SELECT SUM(f.valor) FROM {SCHEMA}.fvendas as f LEFT JOIN {SCHEMA}.dclientes as cli ON UPPER(f.nome) = UPPER(cli.nome) WHERE cli.telefone = %s AND f.pago = FALSE;"
        cursor.execute(query, (formatted_phone,))
        result = cursor.fetchone()
        return result[0] if result[0] else 0.0  # Return 0.0 if no debts are found
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return 0.0
    finally:
        if connection:
            cursor.close()
            connection.close()

def update_payment_status(phone_number: str, payment_id: str) -> bool:
    """
    Atualiza o status de pagamento das dívidas de um cliente.
    
    Esta função marca todas as vendas não pagas do cliente como pagas,
    registra a data do pagamento e associa um ID de pagamento à transação.
    A operação é realizada dentro de uma transação para garantir a integridade
    dos dados.
    
    Args:
        phone_number (str): Número de telefone do cliente
        payment_id (str): Identificador único do pagamento
    
    Retorna:
        bool: True se a atualização foi bem-sucedida, False caso contrário
    
    Exemplo:
        >>> update_payment_status("5511999999999", "PAY123")
        True
    """
    try:
        connection = get_db_connection()
        connection.autocommit = False  # Start transaction
        cursor = connection.cursor()
        formatted_phone = format_phone_number(phone_number)
        
        # Update all unpaid debts for this user
        query = f"""
                UPDATE {SCHEMA}.fvendas f
                SET 
                    pago = TRUE,
                    data_pagamento = CURRENT_TIMESTAMP,
                    id_pagamento = %s
                FROM {SCHEMA}.dclientes cli
                WHERE 
                    UPPER(f.nome) = UPPER(cli.nome)
                    AND cli.telefone = %s
                    AND f.pago = FALSE;
        """
        cursor.execute(query, (payment_id, formatted_phone))
        
        connection.commit()
        return True
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Erro ao atualizar status de pago: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()
