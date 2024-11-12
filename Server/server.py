import argparse
import socket
import json
import threading
import redis #type: ignore
from logger import Logger
from src.model.ticket import Ticket
from src.utils import parse_message, make_response
from src.services.ticket_service import TicketManager

ticket_manager = TicketManager(redis.Redis(host='localhost', port=6379, db=0, password = 2037))

class ClientHandler:
    
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.client_id = f"{address[0]}:{address[1]}"
        self.commands = {
            'create': self.create,
            'find': self.find,
            'update': self.update,
            'delete': self.delete,
            'exit': self.exit,
        }
        
        self.main()

    def has_permission(self, ticket_data):
        '''
        Verificar si el cliente tiene permiso para realizar operaciones en el ticket.
        '''
        return ticket_data.owner_address == self.client_id
    
    def create(self, args):
        '''
        Crear un nuevo ticket.
        '''
        parser = argparse.ArgumentParser(description='Crear un nuevo ticket.')
        parser.add_argument('-t', '--title', required=True, help='Título del ticket')
        parser.add_argument('-a', '--author', required=True, help='Autor del ticket')
        parser.add_argument('-d', '--description', required=True, help='Descripción del ticket')

        # Intentar analizar los argumentos
        try:
            parsed_args = parser.parse_args(args)
        except argparse.ArgumentError as e:
            logger.error(f'Error al analizar los argumentos: {e}')
            response = make_response(404, f'Error al analizar los argumentos: {e}')
            self.socket.send(response.encode())
            return
        
        # Crear una instancia de Ticket con los argumentos analizados
        new_ticket = Ticket(
            title=parsed_args.title,
            author=parsed_args.author,
            description=parsed_args.description,
            owner_address=self.client_id,
            status='pending'
        )
        
        # Crear un nuevo ticket en redis
        ticket_id = ticket_manager.create_ticket(new_ticket)
        
        logger.info(f"Ticket created with ID: {ticket_id}")
        
        logger.info(
            f'Ticket creado exitosamente por {self.address[0]}:{self.address[1]}!')
        response = make_response(201, '¡Ticket creado exitosamente!')
        self.socket.send(response.encode())

    def find(self, args):
        '''
        Buscar un ticket por id.
        '''
        
        # Debug: Listar todas las keys de tickets
        all_keys = ticket_manager.redis_client.keys('ticket:*')
        logger.info(f"Tickets disponibles en Redis: {[k.decode('utf-8') for k in all_keys]}")

        # Configurar el parser de argumentos
        parser = argparse.ArgumentParser(description='Listar tickets por id.')
        parser.add_argument('-i', '--id', help='Filtrar por id del ticket')

        # Intentar analizar los argumentos
        try:
            parsed_args = parser.parse_args(args)
        except argparse.ArgumentError as e:
            logger.error(f'Error al analizar los argumentos: {e}')
            response = make_response(404, f'Error al analizar los argumentos: {e}')
            self.socket.send(response.encode())
            return
        
        ticket_id = parsed_args.id
        ticket_data = ticket_manager.get_ticket(ticket_id)

        # Verificar si el ticket existe
        if not ticket_data:
            logger.error(
                f'Ticket no encontrado por id {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'Ticket no encontrado!')
            self.socket.send(response.encode())
            return
        
        if not self.has_permission(ticket_data):
            logger.error(f'Access denied for ticket {ticket_id}')
            response = make_response(403, 'No tienes permiso para ver este ticket')
            self.socket.send(response.encode())
            return

        # Convertir el objeto Ticket a un diccionario
        ticket_data = ticket_data.to_dict()

        response = make_response(200, ticket_data)
        self.socket.send(response.encode())
        logger.info(f'Ticket con ID {ticket_id} enviado al cliente.')

    def update(self, args):
        '''
        Actualizar un ticket por id.
        '''

        # Configurar argparse para manejar los argumentos
        parser = argparse.ArgumentParser(description="Actualizar un ticket")
        parser.add_argument('-i', '--id', required=True, help="ID del ticket")
        parser.add_argument('-t', '--title', help="Nuevo título del ticket")
        parser.add_argument('-d', '--description', help="Nueva descripción del ticket")
        parser.add_argument('-s', '--status', help="Nuevo estado del ticket")

        # Parsear los argumentos
        try:
            parsed_args = parser.parse_args(args)
        except argparse.ArgumentError as e:
            logger.error(f"Error en los argumentos: {str(e)}")
            response = make_response(400, f"Argumentos inválidos. Error: {str(e)}")
            self.socket.send(response.encode())
            return

        ticket_id = parsed_args.id
        ticket_data = ticket_manager.get_ticket(int(ticket_id))

        # Verificar si el ticket existe
        if not ticket_data:
            logger.error(
                f'Ticket no encontrado por id {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'Ticket no encontrado!')
            self.socket.send(response.encode())
            return
        
        if not self.has_permission(ticket_data):
            logger.error(f'Access denied for ticket {ticket_id}')
            response = make_response(403, 'No tienes permiso para actualizar este ticket')
            self.socket.send(response.encode())
            return
        
        # Actualizar los campos del ticket
        data = {}
        if parsed_args.title:
            data['title'] = parsed_args.title
        if parsed_args.description:
            data['description'] = parsed_args.description
        if parsed_args.status:
            data['status'] = parsed_args.status
        
        # Si hay datos para actualizar, guardarlos en Redis
        if data:
            ticket_manager.update_ticket(int(ticket_id), data)
            logger.info(f'Ticket con ID {ticket_id} actualizado exitosamente por {self.address[0]}:{self.address[1]}!')
            response = make_response(200, f'Ticket actualizado exitosamente.')
            self.socket.send(response.encode())
        else:
            logger.error(f'No hay datos para actualizar para el ticket con ID {ticket_id}.')
            response = make_response(400, 'No se encontraron campos para actualizar.')
            self.socket.send(response.encode())

    def delete(self, args):
        '''
        Eliminar un ticket por id.
        '''

        # Configurar argparse para manejar los argumentos
        parser = argparse.ArgumentParser(description="Eliminar un ticket")
        parser.add_argument('-i', '--id', required=True, help="ID del ticket a eliminar")

        # Parsear los argumentos
        try:
            parsed_args = parser.parse_args(args)
        except argparse.ArgumentError as e:
            logger.error(f"Error en los argumentos: {str(e)}")
            response = make_response(400, f"Argumentos inválidos. Error: {str(e)}")
            self.socket.send(response.encode())
            return
        
        ticket_id = parsed_args.id

        ticket_data = ticket_manager.get_ticket(int(ticket_id))

        # Verificar si el ticket existe
        if not ticket_data:
            logger.error(
                f'Ticket no encontrado por id {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'Ticket no encontrado!')
            self.socket.send(response.encode())
            return

        if not self.has_permission(ticket_data):
            logger.error(f'Access denied for ticket {ticket_id}')
            response = make_response(403, 'No tienes permiso para eliminar este ticket')
            self.socket.send(response.encode())
            return
        
        # Intentar eliminar el ticket desde Redis
        ticket = ticket_manager.delete_ticket(int(ticket_id))

        # Verificar si el ticket fue eliminado correctamente
        if ticket:
            logger.error(f'Ticket con ID {ticket_id} no encontrado.')
            response = make_response(404, f'Ticket con ID {ticket_id} no encontrado.')
            self.socket.send(response.encode())
            return
        
        logger.info(f'Ticket con ID {ticket_id} eliminado exitosamente por {self.address[0]}:{self.address[1]}!')
        response = make_response(200, f'Ticket eliminado exitosamente.')
        self.socket.send(response.encode())

    def exit(self, _):
        # Registra un mensaje informativo indicando que el cliente con la dirección self.address se ha desconectado.
        logger.info(f'Cliente {self.address} desconectado!')
        # Llama a make_response para crear una respuesta con el código de estado 499 y el mensaje '¡Cliente desconectado!'.
        response = make_response(499, '¡Cliente desconectado!')
        # Envía la respuesta al cliente a través del socket.
        self.socket.send(response.encode())
        # Cierra el socket para finalizar la conexión con el cliente.
        self.socket.close()
        #Lanza una excepción SystemExit para terminar el programa.
        raise SystemExit

    def main(self):
        '''
        Mantiene el servidor en ejecución, recibe mensajes de los clientes y los procesa.
        '''
        try:
            # Entra en un bucle infinito para mantener el servidor en ejecución y listo para recibir mensajes continuamente.
            while True:
                # Recibe un mensaje del cliente y lo decodifica.
                message = self.socket.recv(1024).decode()
                # Divide el mensaje en comando y argumentos.
                command, args = parse_message(message)
                # Verifica si el comando está en la lista de comandos definidos en el diccionario de comandos.
                if command in self.commands:
                    # Registra un mensaje de información (logger.info) indicando que el comando se está ejecutando y llama a la función correspondiente en self.commands pasando los argumentos (args).
                    logger.info(f'Executing command: {command}')
                    self.commands[command](args)
                else:
                    # Si el comando no está en la lista de comandos, registra un mensaje de error (logger.error) indicando que el comando no se encontró y envía un mensaje de respuesta al cliente indicando que el comando no se encontró.
                    logger.error(f'Command not found: {command}')
                    response = make_response(
                        404, f'Command not found: {command}. Try again!')
                    self.socket.send(response.encode())
        
        # Si se produce una excepción IndexError (lo que puede ocurrir si el cliente se desconecta de manera inesperada), registra un mensaje de información (logger.info) indicando que el cliente se ha desconectado
        except IndexError:
            logger.info('Client disconnected!')



class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.create_socket()
        self.handle_accept()

    def create_socket(self):
        '''
        Crea un socket en el host y puerto especificados.
        '''
        
        # Crea un socket utilizando la familia de direcciones AF_INET (IPv4) y el tipo de socket SOCK_STREAM (TCP).
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        
        # Habilita la reutilización de la dirección del socket.
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Registra un mensaje de información (logger.info) indicando que el socket se ha creado correctamente en el host y puerto especificados.
        logger.info(
            f'Socket created successfully on {(self.host)}:{self.port}!')
        
        #Enlaza el socket al host y puerto especificados.
        self.server.bind((self.host, self.port))
        
        #Configura el socket para escuchar conexiones entrantes, con una cola de hasta 5 conexiones pendientes.
        self.server.listen(5)

    def handle_accept(self):
        try:
            logger.info('Accepting connections')
            # Entra en un bucle infinito para aceptar conexiones entrantes continuamente.
            while True:
                # Acepta una conexión entrante y almacena el socket del cliente y la dirección del cliente.
                client, address = self.server.accept()
                # Registra un mensaje de información (logger.info) indicando que se ha establecido una conexión con el cliente en la dirección address.
                logger.info(f'Connection from {address[0]}:{address[1]}')
                # Crea un hilo para manejar la conexión con el cliente, pasando el socket del cliente y la dirección del cliente como argumentos.
                thread = threading.Thread(
                    target=ClientHandler, args=(client, address))
                thread.start()
                
        # Si se produce una excepción KeyboardInterrupt (lo que puede ocurrir si se presiona Ctrl + C para detener el servidor), registra un mensaje de información (logger.info) indicando que se ha presionado Ctrl + C y cierra el socket del servidor.        
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt')
            self.server.close()
            # Lanza una excepción SystemExit para finalizar el programa.
            raise SystemExit

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--host', default='127.0.0.1', help='Host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')
    parser.add_argument('-d', '--debug', type=bool, default=False, help='Debug mode')

    parser.add_argument('--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')

    args = parser.parse_args()

    logger = Logger(debug=args.debug)
    Server(args.host, args.port)
