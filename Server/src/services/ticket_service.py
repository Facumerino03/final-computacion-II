from src.model.ticket import Ticket

class TicketManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    def create_ticket(self, ticket: Ticket):
        '''
        Crea un nuevo ticket en redis
        params:
            ticket: Ticket
        '''
        
        # Incrementa contador de tickets para obtener un nuevo id
        ticket_id = self.redis_client.incr('ticket:id')
        
        # Guarda el ticket en redis y convierte el objeto ticket a un diccionario con to_dict
        self.redis_client.hset(f'ticket:{ticket_id}', mapping=ticket.to_dict())
        
        # Devuelve el id del ticket creado
        return ticket_id

    def get_ticket(self, ticket_id: int):
        '''
        Obtiene un ticket de redis por su id
        params:
            ticket_id: int
        '''
        
        #Obtiene todos los campos del ticker almacenados en redis con la el id ticket_id
        data = self.redis_client.hgetall(f'ticket:{ticket_id}')
        print(data)
        
        #Si hay datos, convierte el diccionario a un objeto Ticket utilizando from_dict
        if data:
            return Ticket.from_dict({k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()})
        
        #Si no hay datos, devuelve None
        return None

    def update_ticket(self, ticket_id: int, data: dict):
        '''
        Actualiza un ticket en redis
        params:
            ticket_id: int
            data: dict
        '''
        
        #Actualiza los campos del ticket en redis con el id ticket_id y los valores del diccionario data
        self.redis_client.hset(f'ticket:{ticket_id}', mapping=data)

    def delete_ticket(self, ticket_id: int):
        '''
        Elimina un ticket de redis por su id
        params:
            ticket_id: int
        '''
        
        #Elimina el ticket de redis con el id ticket_id
        self.redis_client.delete(f'ticket:{ticket_id}')
