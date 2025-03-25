from .whatsapp_api import WhatsAppAPI

class MessageHandlers:
    def __init__(self):
        self.api = WhatsAppAPI()
    
    def handle_initial_state(self, user_id, message_text):
        """Fluxo inicial da conversa"""
        if "oi" in message_text.lower() or "olá" in message_text.lower():
            self.api.send_message(user_id, "Olá! Como posso ajudar? Escolha uma opção:\n1. Suporte\n2. Vendas\n3. Informações")
            return "AWAITING_RESPONSE"
        return "INITIAL"
    
    def handle_awaiting_response(self, user_id, message_text):
        """Trata a resposta do menu inicial"""
        if message_text == "1":
            self.api.send_message(user_id, "Ótimo! Por favor, descreva seu problema de suporte.")
            return "SUPPORT_DESCRIPTION"
        elif message_text == "2":
            self.api.send_message(user_id, "Você quer comprar qual produto?\nA. Produto X\nB. Produto Y")
            return "SALES_SELECTION"
        elif message_text == "3":
            self.api.send_message(user_id, "Nossos horários são:\nSeg-Sex: 9h-18h\nSáb: 9h-13h")
            return "INITIAL"
        else:
            self.api.send_message(user_id, "Opção inválida. Por favor, escolha 1, 2 ou 3.")
            return "AWAITING_RESPONSE"
    
    def handle_support_description(self, user_id, message_text):
        """Processa descrição de suporte"""
        self.api.send_message(user_id, "Recebemos sua solicitação! Um técnico entrará em contato em breve.")
        # Aqui você pode salvar no banco de dados
        return "INITIAL"
    
    def handle_sales_selection(self, user_id, message_text):
        """Processa seleção de produto"""
        if message_text.upper() == "A":
            self.api.send_message(user_id, "Produto X selecionado. Valor: R$ 99,90. Deseja finalizar? (sim/não)")
            return "CONFIRM_PURCHASE"
        elif message_text.upper() == "B":
            self.api.send_message(user_id, "Produto Y selecionado. Valor: R$ 149,90. Deseja finalizar? (sim/não)")
            return "CONFIRM_PURCHASE"
        else:
            self.api.send_message(user_id, "Opção inválida. Escolha A ou B.")
            return "SALES_SELECTION"
    
    def handle_confirm_purchase(self, user_id, message_text):
        """Confirmação de compra"""
        if message_text.lower() == "sim":
            self.api.send_message(user_id, "Compra confirmada! Enviaremos os detalhes por email.")
            return "INITIAL"
        elif message_text.lower() == "não":
            self.api.send_message(user_id, "Compra cancelada. Volte sempre!")
            return "INITIAL"
        else:
            self.api.send_message(user_id, "Por favor, responda com 'sim' ou 'não'.")
            return "CONFIRM_PURCHASE"