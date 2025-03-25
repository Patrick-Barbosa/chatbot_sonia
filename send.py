import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

# Configurações da API
API_URL = os.getenv("WHATSAPP_API_URL")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

def send_whatsapp_message(to_number, message):
    """Envia mensagem pelo WhatsApp Business API"""
    
    url = f"{API_URL}{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {str(e)}")
        return None

@app.route('/send-message', methods=['POST'])
def send_message_endpoint():
    """Endpoint para enviar mensagem via POST"""
    
    data = request.get_json()
    if not data or 'number' not in data or 'message' not in data:
        return jsonify({"error": "Número e mensagem são obrigatórios"}), 400
    
    result = send_whatsapp_message(data['number'], data['message'])
    
    if result:
        return jsonify({"status": "success", "response": result}), 200
    else:
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(port=7777, debug=True)