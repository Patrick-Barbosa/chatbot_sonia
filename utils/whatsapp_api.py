import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class WhatsAppAPI:
    def __init__(self):
        self.api_url = os.getenv("WHATSAPP_API_URL")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    
    def send_message(self, to_number, message):
        """Envia mensagem de texto"""
        url = f"{self.api_url}{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
            return None
    
    def parse_webhook_data(self, data):
        """Processa dados recebidos do webhook"""
        messages = []
        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    if "value" in change and "messages" in change["value"]:
                        for message in change["value"]["messages"]:
                            msg_data = {
                                "sender": message["from"],
                                "text": message["text"]["body"],
                                "timestamp": datetime.now(),
                                "message_id": message["id"]
                            }
                            messages.append(msg_data)
        return messages