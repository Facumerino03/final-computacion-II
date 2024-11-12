import redis #type: ignore
from Server.src.model.ticket import Ticket
from Server.src.services.ticket_service import TicketManager

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Crear una instancia de TicketManager
ticket_manager = TicketManager(redis_client)

# Crear un nuevo ticket
new_ticket = Ticket(title="Bug in login", author="John Doe", description="Unable to login with correct credentials")
ticket_id = ticket_manager.create_ticket(new_ticket)
print(f"Ticket created with ID: {ticket_id}")

# Obtener un ticket
retrieved_ticket = ticket_manager.get_ticket(ticket_id)
print(f"Retrieved Ticket: {retrieved_ticket}")

# Actualizar un ticket
ticket_manager.update_ticket(ticket_id, {'status': 'resolved'})
updated_ticket = ticket_manager.get_ticket(ticket_id)
print(f"Updated Ticket: {updated_ticket}")

# Eliminar un ticket
ticket_manager.delete_ticket(ticket_id)
deleted_ticket = ticket_manager.get_ticket(ticket_id)
print(f"Deleted Ticket: {deleted_ticket}")