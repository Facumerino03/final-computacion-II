from src.model import Ticket

class TicketManager:
    '''
    Clase que gestiona los tickets en redis
    
    '''
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def create_ticket(self, ticket: Ticket):
        '''
        Crea un nuevo ticket en redis

        '''
        ticket_id = self.redis_client.incr('ticket:id')
        self.redis_client.hset(f'ticket:{ticket_id}', mapping=ticket.to_dict())
        
        return ticket_id

    def get_ticket(self, ticket_id: int):
        '''
        Obtiene un ticket de redis por su id

        '''
        data = self.redis_client.hgetall(f'ticket:{ticket_id}')
        if data:
            return Ticket.from_dict({k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()})
        
        return None

    def update_ticket(self, ticket_id: int, data: dict):
        '''
        Actualiza un ticket en redis por su id y con los valores del diccionario data
        
        '''
        self.redis_client.hset(f'ticket:{ticket_id}', mapping=data)

    def delete_ticket(self, ticket_id: int):
        '''
        Elimina un ticket de redis por su id

        '''
        self.redis_client.delete(f'ticket:{ticket_id}')
