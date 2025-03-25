from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Removi o redirecionamento para HTTPS
@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        verify_token = os.getenv("VERIFY_TOKEN")
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print(f"Verificação recebida - Token: {token}, Challenge: {challenge}")
        
        if token == verify_token:
            return challenge, 200
        return "Token inválido", 403

    elif request.method == 'POST':
        data = request.get_json()
        print(f"Dados recebidos: {data}")
        
        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "value" in change and "messages" in change["value"]:
                        for message in change["value"]["messages"]:
                            print(f"Mensagem detalhada: {message}")
        return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    print("Servidor iniciando em HTTP...")
    # Rodando em HTTP simples na porta 7777
    app.run(host='0.0.0.0', port=7777, debug=True)