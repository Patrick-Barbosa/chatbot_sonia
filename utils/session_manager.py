from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, timeout_minutes=3):
        self.sessions = {}
        self.timeout = timedelta(minutes=timeout_minutes)
    
    def get_session(self, user_id):
        """Obtém ou cria uma sessão para o usuário"""
        session = self.sessions.get(user_id)
        if not session or datetime.now() - session['last_interaction'] > self.timeout:
            self.sessions[user_id] = {
                'state': 'INITIAL',
                'data': {},
                'last_interaction': datetime.now()
            }
        return self.sessions[user_id]
    
    def update_session(self, user_id, state=None, data=None):
        """Atualiza o estado da sessão"""
        session = self.get_session(user_id)
        if state:
            session['state'] = state
        if data:
            session['data'].update(data)
        session['last_interaction'] = datetime.now()
        return session
    
    def clean_expired_sessions(self):
        """Remove sessões inativas"""
        now = datetime.now()
        expired = [user_id for user_id, session in self.sessions.items() 
                  if now - session['last_interaction'] > self.timeout]
        for user_id in expired:
            del self.sessions[user_id]
        return len(expired)