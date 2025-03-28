from .whatsapp_api import WhatsAppAPI
from .database_functions import check_phone_number, get_client_first_name, check_user_debts, get_user_debt_amount
from .payment_handlers import PaymentHandlers

class MessageHandlers:
    def __init__(self):
        self.api = WhatsAppAPI()
        self.payment_handlers = PaymentHandlers()

    def handle_initial_state(self, user_id, message_text):
        """Fluxo inicial da conversa"""
        if "oi" in message_text.lower() or "olá" in message_text.lower():
            # Consulta o banco de dados para verificar o número de telefone
            user_exists = check_phone_number(user_id)
            if user_exists:
                first_name = get_client_first_name(user_id)  # Retrieve the client's first name
                self.api.send_message(user_id, f"Olá, {first_name}! Tudo bem?")
                return "CHECK_DEBTS"  # Proceed to check debts
            else:
                self.api.send_message(user_id, "Olá, tudo bem? Não tenho seu número relacionado no soniatech!")
                self.api.send_message(user_id, "Para resolver isso, insira seu número no soniatech! Te espero na próxima!")
                return "END_FLOW"
        return "INITIAL"
    
    def handle_check_debts(self, user_id, message_text):
        """Consulta dívidas do usuário"""
        has_debts = check_user_debts(user_id)
        if has_debts:
            debt_amount = get_user_debt_amount(user_id)  # Retrieve the total debt amount
            self.api.send_message(user_id, f"Você possui dívidas pendentes no valor de R$ {debt_amount:.2f}. Deseja pagar as dívidas? (sim/não)")
            return "AWAITING_DEBT_PAYMENT"
        else:
            self.api.send_message(user_id, "Nenhuma dívida a ser paga!")
            return "AWAITING_ACTION"
    
    def handle_awaiting_debt_payment(self, user_id, message_text):
        """Processa decisão de pagamento de dívidas"""
        if message_text.lower() == "sim":
            return self.payment_handlers.handle_pix_payment(user_id)
        elif message_text.lower() == "não":
            self.api.send_message(user_id, "Entendido! Caso mude de ideia, estamos à disposição.")
            return "INITIAL"
        else:
            self.api.send_message(user_id, "Por favor, responda com 'sim' ou 'não'.")
            return "AWAITING_DEBT_PAYMENT"
    
    def handle_awaiting_action(self, user_id, message_text):
        """Trata ações após saudação"""
        self.api.send_message(user_id, "O que deseja fazer?")
        return "AWAITING_RESPONSE"