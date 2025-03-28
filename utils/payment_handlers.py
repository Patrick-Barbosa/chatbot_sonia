from .whatsapp_api import WhatsAppAPI
import mercadopago
from dotenv import load_dotenv
import os
from .database_functions import get_user_debt_amount, update_payment_status

load_dotenv()

class PaymentHandlers:
    def __init__(self):
        self.api = WhatsAppAPI()
        self.mp = mercadopago.SDK(os.getenv('MERCADO_PAGO_ACCESS_TOKEN'))

    def handle_pix_payment(self, user_id, message_text=None):
        """Inicia o processo de pagamento via Pix."""
        try:
            # Implement Mercado Pago Pix generation here
            payment_data = {
                "transaction_amount": float(self.get_user_debt_amount(user_id)),
                "payment_method_id": "pix",
                "payer": {
                    "email": "test@test.com"  # This should come from the database
                }
            }
            payment_response = self.mp.payment().create(payment_data)
            
            if payment_response["status"] == 201:
                pix_code = payment_response["response"]["point_of_interaction"]["transaction_data"]["qr_code"]
                self.api.send_message(user_id, f"Por favor, use o seguinte código Pix para pagamento:\n{pix_code}")
                return "AWAITING_PIX_CONFIRMATION"
            else:
                self.api.send_message(user_id, "Desculpe, houve um erro ao gerar o Pix. Tente novamente mais tarde.")
                return "END_FLOW"
        except Exception as e:
            print(f"Erro ao gerar Pix: {e}")
            self.api.send_message(user_id, "Desculpe, houve um erro ao gerar o Pix. Tente novamente mais tarde.")
            return "END_FLOW"

    def handle_pix_confirmation(self, user_id, message_text):
        """Confirmação do pagamento via Pix."""
        if message_text.lower() == "sim":
            self.api.send_message(user_id, "Aguardando confirmação do pagamento...")
            return "AWAITING_WEBHOOK"
        elif message_text.lower() == "não":
            self.api.send_message(user_id, "Pagamento cancelado. Volte sempre!")
            return "END_FLOW"
        else:
            self.api.send_message(user_id, "Por favor, responda com 'sim' ou 'não'.")
            return "AWAITING_PIX_CONFIRMATION"

    def handle_webhook_confirmation(self, user_id):
        """Aguarda a confirmação do pagamento via webhook."""
        payment_status = self.check_payment_status(user_id)
        if payment_status == "PAID":
            # Update payment status in database
            if update_payment_status(user_id, "MP_" + str(payment_status.get('id', ''))):
                self.api.send_message(user_id, "Pagamento confirmado! Muito obrigado!")
                return "END_FLOW"
            else:
                self.api.send_message(user_id, "Erro ao processar pagamento. Por favor, contate o suporte.")
                return "END_FLOW"
        elif payment_status == "FAILED":
            self.api.send_message(user_id, "Ocorreu um problema no pagamento. Tente novamente.")
            return "END_FLOW"
        else:
            self.api.send_message(user_id, "Ainda aguardando a confirmação do pagamento...")
            return "AWAITING_WEBHOOK"

    def check_payment_status(self, user_id):
        """Simula a verificação do status do pagamento via webhook."""
        # Replace this logic with actual webhook handling
        return "PAID"  # Simulated response: "PAID" or "FAILED"

    def get_user_debt_amount(self, user_id):
        """Simula a obtenção do valor devido pelo usuário."""
        # Replace this logic with actual database query
        return 100.0  # Simulated debt amount
