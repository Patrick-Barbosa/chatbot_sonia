from datetime import datetime, timedelta
import logging

class SessionManager:
    """
    Gerenciador de Sessões para Chatbot
    
    Esta classe é responsável por gerenciar sessões de usuários no chatbot, mantendo
    o estado da conversa e dados temporários para cada usuário.
    
    Atributos:
        sessions (dict): Dicionário que armazena as sessões de todos os usuários
        timeout (timedelta): Tempo limite para uma sessão expirar
    """
    
    def __init__(self, timeout_minutes=3):
        """
        Inicializa o gerenciador de sessões
        
        Args:
            timeout_minutes (int): Tempo em minutos para uma sessão expirar
                                 Padrão é 3 minutos
        """
        self.sessions = {}
        self.timeout = timedelta(minutes=timeout_minutes)
    
    def get_session(self, user_id):
        """
        Recupera ou cria uma nova sessão para um usuário
        
        Esta função verifica se existe uma sessão válida para o usuário.
        Se não existir ou estiver expirada, cria uma nova sessão.
        
        Args:
            user_id: Identificador único do usuário
        
        Returns:
            dict: Sessão do usuário contendo:
                - state: Estado atual da conversa
                - data: Dados temporários da sessão
                - last_interaction: Momento da última interação
        """
        session = self.sessions.get(user_id)
        if not session or datetime.now() - session['last_interaction'] > self.timeout:
            logging.debug(f"Creating new session for user {user_id} or session expired.")
            self.sessions[user_id] = {
                'state': 'INITIAL',
                'data': {},
                'last_interaction': datetime.now()
            }
        return self.sessions[user_id]
    
    def update_session(self, user_id, state=None, data=None):
        """
        Atualiza os dados de uma sessão existente
        
        Esta função permite atualizar o estado da conversa e/ou adicionar
        novos dados à sessão do usuário. Também atualiza o momento da
        última interação.
        
        Args:
            user_id: Identificador único do usuário
            state (opcional): Novo estado da conversa
            data (opcional): Novos dados para adicionar à sessão
        
        Returns:
            dict: Sessão atualizada do usuário
        """
        session = self.get_session(user_id)
        if state:
            session['state'] = state
        if data:
            session['data'].update(data)
        session['last_interaction'] = datetime.now()
        logging.debug(f"Session updated for user {user_id}: {session}")
        return session
    
    def clean_expired_sessions(self):
        """
        Remove todas as sessões que ultrapassaram o tempo limite
        
        Esta função verifica todas as sessões existentes e remove aquelas
        que não tiveram interação dentro do período de timeout definido.
        
        Returns:
            int: Número de sessões que foram removidas
        """
        now = datetime.now()
        expired = [user_id for user_id, session in self.sessions.items() 
                  if now - session['last_interaction'] > self.timeout]
        logging.debug(f"Cleaning expired sessions at {now}. Expired users: {expired}")
        for user_id in expired:
            del self.sessions[user_id]
        return len(expired)
    
    def clean_session(self, user_id: str, misterio) -> bool:
        """
        Remove a sessão específica de um usuário, se existir.

        Args:
            user_id (str): Identificador único do usuário.

        Returns:
            bool: True se a sessão foi removida com sucesso, False se não houver sessão para esse usuário.
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
            return True
        else:
            return False