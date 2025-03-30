import requests
import os
from datetime import datetime
from dotenv import load_dotenv

"""
Este módulo implementa uma interface para a API do WhatsApp Business.
Ele utiliza variáveis de ambiente para configuração e oferece métodos
para enviar e receber mensagens através da API oficial do WhatsApp.
"""

load_dotenv()

class WhatsAppAPI:
    """
    Classe que gerencia toda a comunicação com a API do WhatsApp Business.
    Permite enviar mensagens de texto e interativas, além de processar 
    dados recebidos através do webhook.
    """

    def __init__(self):
        """
        Inicializa a conexão com a API do WhatsApp carregando as credenciais necessárias:
        - api_url: Endereço base da API do WhatsApp
        - phone_number_id: Identificador único do número do WhatsApp Business
        - access_token: Token de autenticação para acessar a API
        """
        self.api_url = os.getenv("WHATSAPP_API_URL")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, to_number: str, message: str) -> dict:
        """
        Envia uma mensagem de texto simples para um número do WhatsApp.

        Args:
            to_number: Número do destinatário no formato internacional (ex: 5511999999999)
            message: Texto da mensagem a ser enviada

        Returns:
            dict: Resposta da API em caso de sucesso
            None: Em caso de falha no envio
        
        Exemplo de uso:
            api.send_message("5511999999999", "Olá, como posso ajudar?")
        """
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

    def send_payload(self, payload: dict) -> None:
        """
        Envia o payload para o endpoint da API do WhatsApp Business.

        Args:
            payload: Dicionário com a estrutura da mensagem conforme a documentação.
        """
        url = f"{self.api_url}{self.phone_number_id}/messages"
        requests.post(url, headers=self.headers, json=payload)


    def send_interactive_message(self, user_id: str, message: dict) -> None:
        """
        Envia mensagem interativa completa para a API do WhatsApp Business.
        
        Se o payload possuir a estrutura interativa, envia o objeto completo; 
        caso contrário, envia uma mensagem de texto simples.
        
        Args:
            user_id: Número do destinatário.
            message: Dicionário contendo a estrutura completa da mensagem.
        """
        # Se a mensagem já contém a estrutura interativa, envia o payload completo.
        if "interactive" in message:
            payload = {
                "messaging_product": "whatsapp",
                "to": user_id,
                **message  # Mescla o restante dos campos do payload
            }
        else:
            # Fallback: envia uma mensagem de texto simples
            payload = {
                "messaging_product": "whatsapp",
                "to": user_id,
                "type": "text",
                "text": {"body": message.get("text", "")}
            }
            
        self.send_payload(payload)
    
    def parse_webhook_data(self, data: dict) -> list:
        """
        Processa dados recebidos do webhook do WhatsApp e extrai as mensagens.
        
        Estrutura do processamento:
        1. Recebe dados brutos do webhook
        2. Navega através da estrutura: entry -> changes -> value -> messages
        3. Para cada mensagem, extrai:
           - Remetente (sender)
           - Horário (timestamp)
           - Tipo da mensagem (text, interactive, button)
           - Conteúdo da mensagem

        Args:
            data: Dicionário com os dados brutos do webhook

        Returns:
            list: Lista de mensagens processadas contendo:
                 - sender: Número do remetente
                 - timestamp: Momento do envio
                 - type: Tipo da mensagem
                 - text: Conteúdo da mensagem
        
        Exemplo de retorno:
        [
            {
                'sender': '5511999999999',
                'timestamp': '1234567890',
                'type': 'text',
                'text': 'Olá, tudo bem?'
            }
        ]
        """
        messages = []
        
        try:
            if "entry" in data and len(data["entry"]) > 0:
                for entry in data["entry"]:
                    if "changes" in entry and len(entry["changes"]) > 0:
                        for change in entry["changes"]:
                            if ("value" in change and "messages" in change["value"] and 
                                len(change["value"]["messages"]) > 0):
                                
                                for message in change["value"]["messages"]:
                                    msg_data = {
                                        "sender": message["from"],
                                        "timestamp": message["timestamp"],
                                        "type": message.get("type", "unknown")
                                    }

                                    # Extrai o texto baseado no tipo de mensagem
                                    if "text" in message:
                                        msg_data["text"] = message["text"]["body"]
                                    elif "interactive" in message:
                                        if "button_reply" in message["interactive"]:
                                            msg_data["text"] = message["interactive"]["button_reply"]["title"]
                                        elif "list_reply" in message["interactive"]:
                                            msg_data["text"] = message["interactive"]["list_reply"]["title"]
                                    elif "button" in message:
                                        msg_data["text"] = message["button"]["text"]
                                    else:
                                        msg_data["text"] = "[Mensagem não suportada]"

                                    messages.append(msg_data)
        except Exception as e:
            print(f"Erro ao processar dados do webhook: {e}")
            print(f"Dados recebidos: {data}")
            return []
        
        return messages