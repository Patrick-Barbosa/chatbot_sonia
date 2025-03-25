from flask import Flask, request, jsonify
from utils.session_manager import SessionManager
from utils.message_handlers import MessageHandlers
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente

app = Flask(__name__)
session_manager = SessionManager()
message_handlers = MessageHandlers()

def session_cleaner():
    """Limpa sessões expiradas periodicamente"""
    while True:
        time.sleep(60)  # Verifica a cada minuto
        cleaned = session_manager.clean_expired_sessions()
        if cleaned > 0:
            print(f"Limpeza: {cleaned} sessões expiradas removidas")

# Inicia a thread de limpeza
threading.Thread(target=session_cleaner, daemon=True).start()

@app.route('/webhook', methods=['GET', 'POST'])  # Adicionei o método GET
def webhook():
    # Verificação do token (GET request do Facebook)
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        if verify_token == os.getenv("VERIFY_TOKEN"):
            return request.args.get('hub.challenge'), 200
        return "Token inválido", 403
    
    # Processamento de mensagens (POST request)
    if request.method == 'POST':
        data = request.get_json()
        messages = message_handlers.api.parse_webhook_data(data)
        
        for msg in messages:
            user_id = msg['sender']
            text = msg['text']
            
            session = session_manager.get_session(user_id)
            current_state = session['state']
            
            state_handlers = {
                'INITIAL': message_handlers.handle_initial_state,
                'AWAITING_RESPONSE': message_handlers.handle_awaiting_response,
                'SUPPORT_DESCRIPTION': message_handlers.handle_support_description,
                'SALES_SELECTION': message_handlers.handle_sales_selection,
                'CONFIRM_PURCHASE': message_handlers.handle_confirm_purchase
            }
            
            new_state = state_handlers[current_state](user_id, text)
            session_manager.update_session(user_id, new_state)
        
        return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=7777, debug=True)