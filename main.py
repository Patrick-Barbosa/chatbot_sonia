"""
Este script configura uma aplicação web Flask para lidar com webhooks recebidos,
especificamente projetada para um chatbot. Ele utiliza variáveis de ambiente para
configuração, gerencia sessões de usuário e processa mensagens com base em estados
predefinidos. A aplicação inclui registro (logging) para depuração e monitoramento,
e uma thread em segundo plano para limpar sessões expiradas.
"""
import os  # Importa o módulo 'os' para interagir com o sistema operacional (ex: manipular arquivos e diretórios).
import time  # Importa o módulo 'time' para adicionar pausas e gerenciar tempo.
import threading  # Importa o módulo 'threading' para permitir a execução de tarefas em paralelo.
import logging  # Importa o módulo 'logging' para registrar eventos e erros.
from datetime import datetime  # Importa a classe 'datetime' do módulo 'datetime' para trabalhar com datas e horários.
from flask import Flask, request, jsonify  # Importa classes do framework Flask para criar a aplicação web.
from dotenv import load_dotenv  # Importa a função 'load_dotenv' do módulo 'dotenv' para carregar variáveis de ambiente de um arquivo '.env'.
from utils.session_manager import SessionManager  # Importa a classe 'SessionManager' do módulo 'utils.session_manager' para gerenciar sessões de usuário.
from utils.message_handlers import MessageHandlers  # Importa a classe 'MessageHandlers' do módulo 'utils.message_handlers' para lidar com mensagens recebidas.

load_dotenv()  # Carrega as variáveis de ambiente do arquivo '.env' para o ambiente de execução.

os.makedirs('.temp', exist_ok=True)  # Cria o diretório '.temp' se ele não existir. 'exist_ok=True' evita erros se o diretório já existir.

file_handler = logging.FileHandler('.temp/logs.txt')  # Cria um handler para gravar logs em um arquivo chamado 'logs.txt' dentro do diretório '.temp'.
file_handler.setLevel(logging.INFO)  # Define o nível mínimo de log para INFO (informações, avisos, erros).
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))  # Define o formato das mensagens de log (data/hora - mensagem).

console_handler = logging.StreamHandler()  # Cria um handler para exibir logs no console.
console_handler.setLevel(logging.INFO)  # Define o nível mínimo de log para INFO.

console_logger = logging.getLogger('console')  # Cria um logger específico para mensagens que devem ser exibidas no console.
console_logger.addHandler(console_handler)  # Adiciona o handler de console ao logger 'console'.

logging.getLogger('werkzeug').disabled = True  # Desabilita o logger 'werkzeug' (usado pelo Flask) para evitar logs de debug no console.

app = Flask(__name__)  # Cria uma instância do aplicativo Flask. '__name__' é o nome do módulo atual.
session_manager = SessionManager()  # Cria uma instância do gerenciador de sessões.
message_handlers = MessageHandlers()  # Cria uma instância do gerenciador de mensagens.

def session_cleaner():
    """
    Limpa sessões expiradas periodicamente.

    Esta função é executada em uma thread separada e verifica a cada 60 segundos
    se há sessões expiradas. Remove as sessões expiradas e imprime uma mensagem
    no console indicando o número de sessões removidas.
    """
    while True:  # Loop infinito para executar a limpeza periodicamente.
        time.sleep(60)  # Pausa a execução por 60 segundos.
        cleaned = session_manager.clean_expired_sessions()  # Chama o método para limpar sessões expiradas.
        if cleaned > 0:  # Verifica se alguma sessão foi removida.
            print(f"Limpeza: {cleaned} sessões expiradas removidas")  # Imprime a mensagem no console.


threading.Thread(target=session_cleaner, daemon=True).start()  # Inicia a thread de limpeza de sessões. 'daemon=True' faz com que a thread termine quando o programa principal terminar.

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Lida com requisições de webhook.

    Esta rota é o ponto de entrada para processar eventos de webhook. Ela lida com
    requisições GET para verificação do webhook e requisições POST contendo dados
    de eventos.

    Requisições GET:
        - Usadas pelo Facebook para verificar o webhook.
        - Compara o 'hub.verify_token' com a variável de ambiente 'VERIFY_TOKEN'.
        - Retorna o valor de 'hub.challenge' se os tokens coincidirem, caso contrário retorna erro 403.

    Requisições POST:
        - Contêm os dados reais do evento.
        - Analisa os dados para extrair mensagens, identifica o usuário e processa a mensagem com base no estado da sessão do usuário.
        - Usa os manipuladores de mensagens para determinar a resposta apropriada e atualiza o estado da sessão.

    Retorna:
        Uma resposta JSON com status de sucesso e código 200.
    """
    if request.method == 'GET':  # Verifica se a requisição é do tipo GET (usada para verificação do webhook).
        verify_token = request.args.get('hub.verify_token')  # Obtém o valor do parâmetro 'hub.verify_token' da URL.
        if verify_token == os.getenv("VERIFY_TOKEN"):  # Compara o token recebido com o token armazenado na variável de ambiente.
            return request.args.get('hub.challenge'), 200  # Retorna o valor do parâmetro 'hub.challenge' e o código 200 (OK) se os tokens coincidirem.
        return "Token inválido", 403  # Retorna uma mensagem de erro e o código 403 (Forbidden) se os tokens não coincidirem.
    
    if request.method == 'POST':  # Verifica se a requisição é do tipo POST (contém os dados do evento).
        data = request.get_json()  # Obtém os dados da requisição no formato JSON.
        try:
            status = data['entry'][0]['changes'][0]['value']['statuses'][0]['status']
            if status != None:
                return jsonify({"status": "success"}), 200  # Retorna uma resposta JSON com o status de sucesso e o código 200 (OK) se o status não for nulo.
        except:
            pass

        messages = message_handlers.api.parse_webhook_data(data)  # Usa o 'message_handlers' para analisar os dados do webhook e extrair as mensagens.
        
        for msg in messages:  # Itera sobre cada mensagem extraída.
            user_id = msg['sender']  # Extrai o ID do remetente da mensagem.
            text = msg.get('interactive', {}).get('button_reply', msg['text'])  # Extrai o texto da mensagem. Se for uma resposta interativa (botão), pega o texto da resposta, senão pega o texto da mensagem.
            text = text.strip().lower()  # Remove espaços em branco extras e converte o texto para minúsculas para normalizar a entrada.
            sender_name = msg.get('sender_name', user_id)  # Obtém o nome do remetente, se disponível, senão usa o ID do usuário.
            timestamp = datetime.now().strftime("[%I:%M %p, %m/%d/%Y]")  # Obtém a data e hora atual e formata como string.
            
            console_logger.info(f"{timestamp} {sender_name}: {text}")  # Imprime a mensagem formatada no console.
            console_logger.info(f"Full message - From: {user_id}, Text: {text}")  # Registra a mensagem completa no arquivo de log.
            
            session = session_manager.get_session(user_id)  # Obtém a sessão do usuário usando o ID do usuário.
            current_state = session['state']  # Obtém o estado atual da sessão do usuário.
            
            state_handlers = {  # Define um dicionário que mapeia estados para funções de tratamento.
                'INITIAL': message_handlers.handle_initial_state,  # Estado inicial.
                'AWAITING_DEBT_PAYMENT': message_handlers.handle_awaiting_debt_payment,  # Aguardando pagamento da dívida.
                'AWAITING_PIX_CONFIRMATION': message_handlers.handle_pix_confirmation,  # Aguardando confirmação do PIX.
                'END_FLOW': None  # Estado final.
            }
            
            handler = state_handlers.get(current_state)  # Obtém a função de tratamento para o estado atual.
            response = handler(user_id, text)  # Chama a função de tratamento com o ID do usuário e o texto da mensagem.
            new_state = response.get('new_state', current_state)  # Obtém o novo estado da resposta. Se não houver novo estado, mantém o estado atual.
            reply = response.get('reply')  # Obtém a mensagem de resposta da resposta.
            
            if reply:  # Verifica se há uma mensagem de resposta.
                console_logger.info(f"{timestamp} Bot: {reply}")  # Imprime a mensagem de resposta no console.
            
            if new_state == 'END_FLOW':  # Verifica se o novo estado é o final do fluxo.
                session_manager.clean_session(user_id)  # Remove a sessão do usuário se o fluxo foi encerrado.
            else:
                session_manager.update_session(user_id, new_state)  # Atualiza o estado da sessão do usuário.
    
        return jsonify({"status": "success"}), 200  # Retorna uma resposta JSON com o status de sucesso e o código 200 (OK).

if __name__ == '__main__':  # Verifica se o script está sendo executado diretamente (não importado como um módulo).
    app.run(host='0.0.0.0', port=os.getenv("PORT"), debug=True)  # Inicia o aplicativo Flask. 'host='0.0.0.0'' permite que o aplicativo seja acessado de qualquer endereço IP. 'port=os.getenv("PORT")' define a porta a partir da variável de ambiente 'PORT'. 'debug=True' habilita o modo de depuração (não recomendado para produção).