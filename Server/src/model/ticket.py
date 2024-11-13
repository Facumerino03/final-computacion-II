from datetime import datetime

class Ticket():
    '''
    Clase que representa un ticket
    
    '''
    def __init__(self, title, author, description, user_id, status='pending', date_created=None):
        self.title = title
        self.author = author
        self.description = description
        self.status = status
        self.user_id = user_id
        self.date_created = date_created or datetime.now().isoformat()
    
    def to_dict(self):
        '''
        Devuelve un diccionario con los atributos del ticket
        
        '''
        return {
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'status': self.status,
            'user_id': self.user_id,
            'date_created': self.date_created
        }
    
    @classmethod
    def from_dict(cls, data):
        '''
        Crea una instancia de Ticket a partir de un diccionario
        
        '''
        return cls(
            title=data['title'],
            author=data['author'],
            description=data['description'],
            user_id=data['user_id'],
            status=data['status'],
            date_created=data['date_created']
        )

    def __repr__(self):
        return f"<Ticket(title={self.title}, author={self.author}, status={self.status}, description={self.description}, user_id={self.user_id}, date_created={self.date_created})>"