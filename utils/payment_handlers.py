from .whatsapp_api import WhatsAppAPI
from dotenv import load_dotenv
import os
from .database_functions import get_user_debt_amount, update_payment_status
import logging

load_dotenv()

class PaymentHandlers:
    """
    Gerenciador de Pagamentos via WhatsApp
    
    Esta classe gerencia todas as operações relacionadas a pagamentos,
    incluindo geração de códigos PIX e confirmação de pagamentos.
    
    Atributos:
        api: Instância da API do WhatsApp para envio de mensagens
    """

    def __init__(self):
        """
        Inicializa o gerenciador de pagamentos configurando a API do WhatsApp
        """
        self.api = WhatsAppAPI()
        logging.debug("PaymentHandlers initialized.")

    def handle_pix_payment(self, user_id, message_text=None):
        """
        Processa uma solicitação de pagamento via PIX
        
        Gera um código PIX fictício e envia para o usuário através do WhatsApp.
        Em um ambiente real, este código seria gerado por uma API de pagamentos.
        
        Args:
            user_id: Identificador único do usuário no WhatsApp
            message_text: Texto da mensagem recebida (não utilizado atualmente)
            
        Returns:
            dict: Dicionário contendo o novo estado da conversa e a resposta
        """
        logging.debug(f"Initiating PIX payment for user {user_id}")
        try:
            mock_pix_code = "00020126580014BR.GOV.BCB.PIX0136random-key-mock-pix-example5204000053039865802BR5913Test merchant6008Sao Paulo62070503***6304E2CA"
            self.api.send_message(user_id, f"Por favor, use o seguinte código Pix para pagamento:\n{mock_pix_code}")
            return {'new_state': 'AWAITING_PIX_CONFIRMATION', 'reply': None}
        except Exception as e:
            print(f"Erro ao gerar Pix: {e}")
            return {'new_state': 'END_FLOW', 'reply': None}

    def handle_pix_confirmation(self, user_id, message_text):
        """
        Processa a confirmação de pagamento PIX enviada pelo usuário
        
        Verifica se o usuário confirmou o pagamento enviando a palavra 'PAGO'.
        Em um ambiente real, isso seria validado através de um webhook do banco.
        
        Args:
            user_id: Identificador único do usuário no WhatsApp
            message_text: Texto da mensagem de confirmação
            
        Returns:
            dict: Dicionário contendo o novo estado da conversa e a resposta
        """
        logging.debug(f"Received PIX confirmation input from user {user_id}: {message_text}")
        if message_text and message_text.lower() == "pago":
            self.handle_webhook_confirmation(user_id)
            return {'new_state': 'END_FLOW', 'reply': None}
        self.api.send_message(user_id, "Envie 'PAGO' para confirmar o pagamento.")
        return {'new_state': 'AWAITING_PIX_CONFIRMATION', 'reply': None}

    def handle_webhook_confirmation(self, user_id):
        """
        Simula o recebimento de uma confirmação de pagamento via webhook
        
        Em um ambiente real, este método seria chamado quando o banco
        notificasse o sistema sobre um pagamento recebido.
        
        Args:
            user_id: Identificador único do usuário no WhatsApp
            
        Returns:
            dict: Dicionário contendo o novo estado da conversa e a resposta
        """
        logging.debug(f"Confirming webhook payment for user {user_id}")
        update_payment_status(user_id, "MOCK_PAYMENT_" + str(hash(user_id)))
        self.api.send_message(user_id, "Pagamento confirmado! Muito obrigado!")
        return {'new_state': 'END_FLOW', 'reply': None}

    def check_payment_status(self, user_id):
        """
        Verifica o status do pagamento de um usuário
        
        Esta é uma implementação simulada que sempre retorna 'PAID'.
        Em um ambiente real, consultaria o status real no banco de dados.
        
        Args:
            user_id: Identificador único do usuário no WhatsApp
            
        Returns:
            str: Status do pagamento ('PAID' nesta simulação)
        """
        logging.debug(f"Checking payment status for user {user_id}")
        return "PAID"

    def get_user_debt_amount(self, user_id):
        """
        Obtém o valor da dívida de um usuário
        
        Esta é uma implementação simulada que sempre retorna R$ 100,00.
        Em um ambiente real, consultaria o valor real no banco de dados.
        
        Args:
            user_id: Identificador único do usuário no WhatsApp
            
        Returns:
            float: Valor da dívida (R$ 100,00 nesta simulação)
        """
        logging.debug(f"Retrieving debt amount for user {user_id}")
        return 100.0
