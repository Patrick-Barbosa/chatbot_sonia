import logging  # Importa a biblioteca logging, utilizada para registrar eventos e informações do sistema.
from typing import Dict, Any  # Importa Dict e Any do módulo typing para ajudar na definição de tipos de dados.
from .whatsapp_api import WhatsAppAPI  # Importa a classe WhatsAppAPI do módulo whatsapp_api no mesmo diretório. Essa classe provavelmente lida com a comunicação com a API do WhatsApp.
from .database_functions import check_phone_number, get_client_first_name, check_user_debts, get_user_debt_amount  # Importa funções do módulo database_functions para interagir com o banco de dados, como verificar um número de telefone, obter o primeiro nome de um cliente, verificar dívidas e obter o valor da dívida.
from .payment_handlers import PaymentHandlers  # Importa a classe PaymentHandlers do módulo payment_handlers, que provavelmente contém a lógica para lidar com pagamentos.
import time  # Importa o módulo time, que fornece funções relacionadas ao tempo, como pausas na execução do código.

# Configuração de Logging
logger = logging.getLogger(__name__)  # Cria um objeto logger com o nome do módulo atual. Isso ajuda a identificar de onde as mensagens de log estão vindo.
logger.setLevel(logging.INFO)  # Define o nível de log para INFO, o que significa que mensagens de log com nível INFO ou superior (WARNING, ERROR, CRITICAL) serão registradas.

if not logger.handlers:  # Verifica se o logger já possui algum handler configurado. Isso evita adicionar handlers duplicados.
    console_handler = logging.StreamHandler()  # Cria um handler que envia as mensagens de log para o console (saída padrão).
    console_handler.setLevel(logging.INFO)  # Define o nível de log para o handler do console como INFO.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Cria um formatador para as mensagens de log. Ele define o formato da mensagem, incluindo a data e hora, o nome do logger, o nível da mensagem e a mensagem em si.
    console_handler.setFormatter(formatter)  # Define o formatador para o handler do console.
    logger.addHandler(console_handler)  # Adiciona o handler do console ao logger. Agora, as mensagens de log serão exibidas no console.

# Definição da Classe MessageHandlers
class MessageHandlers:  # Define a classe MessageHandlers, que contém métodos para lidar com diferentes tipos de mensagens e interações com o usuário.
    def __init__(self):  # Define o método construtor da classe. Ele é chamado quando um objeto da classe é criado.
        self.api = WhatsAppAPI()  # Cria uma instância da classe WhatsAppAPI e a atribui ao atributo api da classe MessageHandlers. Isso permite que a classe MessageHandlers envie mensagens via WhatsApp.
        self.payment_handlers = PaymentHandlers()  # Cria uma instância da classe PaymentHandlers e a atribui ao atributo payment_handlers. Isso permite que a classe MessageHandlers lide com pagamentos.
    
    # Método para Lidar com o Estado Inicial do Usuário
    def handle_initial_state(self, user_id: str, text: str) -> Dict:  # Define o método handle_initial_state, que lida com o estado inicial de um usuário. Ele recebe o ID do usuário e o texto da mensagem como entrada e retorna um dicionário.
        user_exists = check_phone_number(user_id)  # Chama a função check_phone_number para verificar se o número de telefone do usuário existe no banco de dados.
        if user_exists:  # Se o usuário existir no banco de dados:
            first_name = get_client_first_name(user_id)  # Obtém o primeiro nome do cliente usando a função get_client_first_name.
            self.api.send_message(user_id, f"Olá, {first_name}! Tudo bem?")  # Envia uma mensagem de saudação personalizada para o usuário.
            time.sleep(6)  # Pausa a execução do código por 6 segundos. Isso pode ser usado para evitar sobrecarregar a API do WhatsApp ou para dar tempo ao usuário para ler a mensagem.
            result = self.handle_check_debts(user_id, text)  # Chama o método handle_check_debts para verificar se o usuário possui dívidas.
            return result  # Retorna o resultado do método handle_check_debts.
        else:  # Se o usuário não existir no banco de dados:
            self.api.send_message(user_id, "Olá, tudo bem? Não tenho seu número relacionado no soniatech!")  # Envia uma mensagem informando que o número do usuário não está cadastrado.
            time.sleep(6)  # Pausa a execução do código por 6 segundos.
            self.api.send_message(user_id, "Para resolver isso, insira seu número no soniatech! Te espero na próxima!")  # Envia uma mensagem instruindo o usuário a inserir seu número no sistema.
            result = {'new_state': 'END_FLOW', 'reply': None}  # Define o resultado como um dicionário indicando que o fluxo deve ser encerrado.
            return result  # Retorna o resultado.
    
    # Define o método handle_check_debts, que verifica se o usuário tem dívidas e oferece a opção de pagar.
    def handle_check_debts(self, user_id, message_text) -> Dict:
        has_debts = check_user_debts(user_id)  # Chama a função check_user_debts para verificar se o usuário tem dívidas.
        if has_debts:  # Se o usuário tiver dívidas:
            debt_amount = get_user_debt_amount(user_id)  # Obtém o valor total das dívidas do usuário.
            message = {  # Define a mensagem interativa a ser enviada ao usuário.
                "type": "interactive",  # Define o tipo da mensagem como interativa.
                "interactive": {  # Define o conteúdo da mensagem interativa.
                    "type": "button",  # Define o tipo de interatividade como botões.
                    "body": {  # Define o corpo da mensagem.
                        "text": f"Você possui dívidas pendentes no valor de R$ {debt_amount:.2f}. Deseja pagar as dívidas?"  # Define o texto da mensagem, informando o valor da dívida e perguntando se o usuário deseja pagar.
                    },
                    "action": {  # Define as ações que o usuário pode realizar.
                        "buttons": [  # Define os botões que serão exibidos.
                            {
                                "type": "reply",  # Define o tipo do botão como uma resposta.
                                "reply": {  # Define a resposta associada ao botão.
                                    "id": "pay_yes",  # Define o ID da resposta (para identificar a ação).
                                    "title": "Sim"  # Define o título do botão como "Sim".
                                }
                            },
                            {
                                "type": "reply",  # Define o tipo do botão como uma resposta.
                                "reply": {  # Define a resposta associada ao botão.
                                    "id": "pay_no",  # Define o ID da resposta (para identificar a ação).
                                    "title": "Não"  # Define o título do botão como "Não".
                                }
                            }
                        ]
                    }
                }
            }
            self.api.send_interactive_message(user_id, message)  # Envia a mensagem interativa para o usuário.
            result = {'new_state': 'AWAITING_DEBT_PAYMENT', 'reply': None}  # Define o novo estado como "AWAITING_DEBT_PAYMENT" (aguardando a decisão de pagamento) e a resposta como None.
            return result  # Retorna o resultado.
        else:  # Se o usuário não tiver dívidas:
            self.api.send_message(user_id, "Nenhuma dívida a ser paga!")  # Envia uma mensagem informando que não há dívidas.
            result = {'new_state': 'END_FLOW', 'reply': None}  # Define o novo estado como "END_FLOW" (fim do fluxo) e a resposta como "Nenhuma dívida a ser paga!".
            return result  # Retorna o resultado.
    
    # Define o método handle_awaiting_debt_payment, que lida com a resposta do usuário sobre o pagamento da dívida.
    def handle_awaiting_debt_payment(self, user_id, message_text) -> Dict:
        logger.info(f"User {user_id} sent message: {message_text}")  # Registra a mensagem enviada pelo usuário.
        logger.info(f"Processing debt payment decision for user {user_id} with message: {message_text}")  # Registra que está processando a decisão do usuário sobre o pagamento da dívida.
        if isinstance(message_text, str):  # Verifica se a mensagem do usuário é uma string.
            if message_text in ["sim", "yes"]:  # Se a mensagem for "sim" ou "yes" (em português ou inglês):
                result = self.payment_handlers.handle_pix_payment(user_id)  # Chama o método handle_pix_payment para iniciar o processo de pagamento via PIX.
                return result  # Retorna o resultado do processo de pagamento.
            elif message_text in ["nao", "não", "no"]:  # Se a mensagem for "nao", "não" ou "no" (em português ou inglês):
                self.api.send_message(user_id, "Entendido! Caso mude de ideia, estamos à disposição.")  # Envia uma mensagem informando que entendeu a decisão do usuário.
                result = {'new_state': 'INITIAL', 'reply': None}  # Define o novo estado como "INITIAL" (estado inicial) e a resposta como None.
                return result  # Retorna o resultado.
            else:  # Se a mensagem não for "sim", "yes", "nao", "não" ou "no":
                debt_amount = self.payment_handlers.get_user_debt_amount(user_id)  # Obtém o valor da dívida do usuário.
                interactive_message = {  # Define a mensagem interativa a ser enviada ao usuário.
                    "messaging_product": "whatsapp",  # Especifica que a mensagem é para o WhatsApp.
                    "to": user_id,  # Define o destinatário da mensagem (o ID do usuário).
                    "type": "interactive",  # Define o tipo da mensagem como interativa.
                    "interactive": {  # Define o conteúdo da mensagem interativa.
                        "type": "button",  # Define o tipo de interatividade como botões.
                        "body": {  # Define o corpo da mensagem.
                            "text": f"Você possui dívidas pendentes no valor de R$ {debt_amount:.2f}. Deseja pagar as dívidas?"  # Define o texto da mensagem, informando o valor da dívida e perguntando se o usuário deseja pagar.
                        },
                        "action": {  # Define as ações que o usuário pode realizar.
                            "buttons": [  # Define os botões que serão exibidos.
                                {
                                    "type": "reply",  # Define o tipo do botão como uma resposta.
                                    "reply": {  # Define a resposta associada ao botão.
                                        "id": "pay_yes",  # Define o ID da resposta (para identificar a ação).
                                        "title": "Sim"  # Define o título do botão como "Sim".
                                    }
                                },
                                {
                                    "type": "reply",  # Define o tipo do botão como uma resposta.
                                    "reply": {  # Define a resposta associada ao botão.
                                        "id": "pay_no",  # Define o ID da resposta (para identificar a ação).
                                        "title": "Não"  # Define o título do botão como "Não".
                                    }
                                }
                            ]
                        }
                    }
                }
                self.api.send_interactive_message(user_id, interactive_message)  # Envia a mensagem interativa para o usuário.
                result = {'new_state': 'AWAITING_DEBT_PAYMENT', 'reply': None}  # Define o novo estado como "AWAITING_DEBT_PAYMENT" (aguardando a decisão de pagamento) e a resposta como None.
                return result  # Retorna o resultado.
        elif isinstance(message_text, dict) and 'id' in message_text:  # Verifica se a mensagem do usuário é um dicionário e contém o campo 'id'.
            if message_text.get('id') == "pay_yes":  # Se o campo 'id' for "pay_yes":
                result = self.payment_handlers.handle_pix_payment(user_id)  # Chama o método handle_pix_payment para iniciar o processo de pagamento via PIX.
                return result  # Retorna o resultado do processo de pagamento.
            elif message_text.get('id') == "pay_no":  # Se o campo 'id' for "pay_no":
                self.api.send_message(user_id, "Entendido! Caso mude de ideia, estamos à disposição.")  # Envia uma mensagem informando que entendeu a decisão do usuário.
                result = {'new_state': 'INITIAL', 'reply': None}  # Define o novo estado como "INITIAL" (estado inicial) e a resposta como None.
                return result  # Retorna o resultado.
            else:  # Se o campo 'id' não for "pay_yes" ou "pay_no":
                self.api.send_message(user_id, "Por favor, selecione uma das opções disponíveis.")  # Envia uma mensagem solicitando que o usuário selecione uma das opções disponíveis.
                result = {'new_state': 'AWAITING_DEBT_PAYMENT', 'reply': None}  # Define o novo estado como "AWAITING_DEBT_PAYMENT" (aguardando a decisão de pagamento) e a resposta como None.
                return result  # Retorna o resultado.
        else:  # Se a mensagem do usuário não for uma string ou um dicionário válido:
            debt_amount = self.payment_handlers.get_user_debt_amount(user_id)  # Obtém o valor da dívida do usuário.
            interactive_message = {  # Define a mensagem interativa a ser enviada ao usuário.
                "messaging_product": "whatsapp",  # Especifica que a mensagem é para o WhatsApp.
                "to": user_id,  # Define o destinatário da mensagem (o ID do usuário).
                "type": "interactive",  # Define o tipo da mensagem como interativa.
                "interactive": {  # Define o conteúdo da mensagem interativa.
                    "type": "button",  # Define o tipo de interatividade como botões.
                    "body": {  # Define o corpo da mensagem.
                        "text": f"Você possui dívidas pendentes no valor de R$ {debt_amount:.2f}. Deseja pagar as dívidas?"  # Define o texto da mensagem, informando o valor da dívida e perguntando se o usuário deseja pagar.
                    },
                    "action": {  # Define as ações que o usuário pode realizar.
                        "buttons": [  # Define os botões que serão exibidos.
                            {
                                "type": "reply",  # Define o tipo do botão como uma resposta.
                                "reply": {  # Define a resposta associada ao botão.
                                    "id": "pay_yes",  # Define o ID da resposta (para identificar a ação).
                                    "title": "Sim"  # Define o título do botão como "Sim".
                                }
                            },
                            {
                                "type": "reply",  # Define o tipo do botão como uma resposta.
                                "reply": {  # Define a resposta associada ao botão.
                                    "id": "pay_no",  # Define o ID da resposta (para identificar a ação).
                                    "title": "Não"  # Define o título do botão como "Não".
                                }
                            }
                        ]
                    }
                }
            }
            self.api.send_interactive_message(user_id, interactive_message)  # Envia a mensagem interativa para o usuário.
            result = {'new_state': 'AWAITING_DEBT_PAYMENT', 'reply': None}  # Define o novo estado como "AWAITING_DEBT_PAYMENT" (aguardando a decisão de pagamento) e a resposta como None.
            return result  # Retorna o resultado.
    
    def handle_pix_confirmation(self, user_id, message_text):
        logger.info(f"User {user_id} sent message: {message_text}")
        result = self.payment_handlers.handle_pix_confirmation(user_id, message_text)
        return result
