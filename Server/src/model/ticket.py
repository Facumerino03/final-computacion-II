from datetime import datetime

class Ticket():
    def __init__(self, title, author, description, status='pending', date_created=None):
        self.title = title
        self.author = author
        self.description = description
        self.status = status
        self.date_created = date_created or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'status': self.status,
            'date_created': self.date_created
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data['title'],
            author=data['author'],
            description=data['description'],
            status=data['status'],
            date_created=data['date_created']
        )

    def __repr__(self):
        return f"<Ticket(title={self.title}, author={self.author}, status={self.status}, description={self.description}, date_created={self.date_created})>"



# #prueba
# # Conectar a Redis
# redis_client = redis.Redis(host='localhost', port=6379, db=0)

# # Crear una instancia de TicketManager
# ticket_manager = TicketManager(redis_client)

# # Crear un nuevo ticket
# new_ticket = Ticket(title="Bug in login", author="John Doe", description="Unable to login with correct credentials")
# ticket_id = ticket_manager.create_ticket(new_ticket)
# print(f"Ticket created with ID: {ticket_id}")

# # Obtener un ticket
# retrieved_ticket = ticket_manager.get_ticket(ticket_id)
# print(f"Retrieved Ticket: {retrieved_ticket}")

# # Actualizar un ticket
# ticket_manager.update_ticket(ticket_id, {'status': 'resolved'})
# updated_ticket = ticket_manager.get_ticket(ticket_id)
# print(f"Updated Ticket: {updated_ticket}")

# # Eliminar un ticket
# ticket_manager.delete_ticket(ticket_id)
# deleted_ticket = ticket_manager.get_ticket(ticket_id)
# print(f"Deleted Ticket: {deleted_ticket}")