import argparse
import socket
import uuid
import threading
import redis #type: ignore
from dotenv import load_dotenv
from src.logs import Logger
from src.model import Ticket
from src.utils import parse_message, make_response
from src.services import TicketManager
import os

load_dotenv()

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_db = os.getenv('REDIS_DB')
redis_password = os.getenv('REDIS_PASSWORD')

ticket_manager = TicketManager(redis.Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password))

class ClientHandler:
    '''
    Clase para manejar las conexiones de los clientes, procesar mensajes y comandos.
    
    '''
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.user_id = None
        self.commands = {
            'login': self.login,
            'create': self.create,
            'find': self.find,
            'update': self.update,
            'delete': self.delete,
            'exit': self.exit,
        }
        
        self.main()

    def has_permission(self, ticket_data):
        '''
        Verifica si el usuario tiene permiso para acceder al ticket en base al user_id del ticket.
        
        '''
        return ticket_data.user_id == self.user_id

    def login(self, args):
        '''
        Iniciar sesión o registrar un nuevo usuario.
        
        '''
        if self.user_id:
            response = make_response(400, f'Ya estás autenticado con el ID de usuario: {self.user_id}')
            self.socket.send(response.encode())
            return

        parser = argparse.ArgumentParser(description='Iniciar sesión o registrar un nuevo usuario.')
        parser.add_argument('-i', '--id', required=False, help='ID del usuario')
        
        
        try:
            parsed_args = parser.parse_args(args)
            if parsed_args.id:
                self.user_id = parsed_args.id
                response = make_response(200, f'Inicio de sesión exitoso. User ID: {self.user_id}')
                self.socket.send(response.encode()) 
            else:
                self.user_id = str(uuid.uuid4())
                response = make_response(200, f'Registro exitoso, guarda el siguiente ID para iniciar sesión: {self.user_id}')
                self.socket.send(response.encode()) 
                
        except SystemExit:
            logger.error('Has ingresado el comando login de forma incorrecta. Uso: login [-i <ID>] para iniciar sesión o login sin argumentos para registrarte')
            response = make_response(400, 'Has ingresado el comando login de forma incorrecta. Uso: login [-i <ID>] para iniciar sesión o login sin argumentos para registrarte')
            self.socket.send(response.encode())
            return
    
    def create(self, args):
        '''
        Crear un nuevo ticket.
        
        '''
        parser = argparse.ArgumentParser(description='Crear un nuevo ticket.')
        parser.add_argument('-t', '--title', required=True, help='Título del ticket')
        parser.add_argument('-a', '--author', required=True, help='Autor del ticket')
        parser.add_argument('-d', '--description', required=True, help='Descripción del ticket')

        if not self.user_id:
            response = make_response(404, 'Debes iniciar sesión o registrarte primero para ejecutar este comando')
            self.socket.send(response.encode())
            return

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            logger.error('Has ingresado el comando create de forma incorrecta. Uso: create -t <título> -a <autor> -d <descripción>')
            response = make_response(400, 'Has ingresado el comando create de forma incorrecta. Uso: create -t <título> -a <autor> -d <descripción>')
            self.socket.send(response.encode())
            return
        
        new_ticket = Ticket(
            user_id = self.user_id,
            title = parsed_args.title,
            author = parsed_args.author,
            description = parsed_args.description,
            status = 'pending'
        )
        
        ticket_id = ticket_manager.create_ticket(new_ticket)
        
        logger.info(f"Ticket creado exitosamente con ID: {ticket_id} por {self.address[0]}:{self.address[1]}!")
        response = make_response(201, f'Ticket creado exitosamente con ID: {ticket_id}')
        self.socket.send(response.encode())

    def find(self, args):
        '''
        Buscar un ticket por id.
        
        '''
        parser = argparse.ArgumentParser(description='Buscar un ticket por id.')
        parser.add_argument('-i', '--id', help='ID del ticket', required=True)

        if not self.user_id:
            response = make_response(400, 'Debes iniciar sesión o registrarte primero para ejecutar este comando')
            self.socket.send(response.encode())
            return
        
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            logger.error("Has ingresado el comando find de forma incorrecta. Uso: find -i <id>")
            response = make_response(400, "Has ingresado el comando find de forma incorrecta. Uso: find -i <id>")
            self.socket.send(response.encode())
            return
        
        ticket_id = parsed_args.id
        ticket_data = ticket_manager.get_ticket(ticket_id)

        if not ticket_data:
            logger.error(f'Ticket no encontrado por id {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'Ticket no encontrado, intenta con otro ID.')
            self.socket.send(response.encode())
            return
        
        if not self.has_permission(ticket_data):
            logger.error(f'Acceso denegado para el ticket {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, 'No tienes permiso para acceder este ticket')
            self.socket.send(response.encode())
            return

        ticket_data = ticket_data.to_dict()

        response = make_response(200, ticket_data)
        self.socket.send(response.encode())
        logger.info(f'Ticket con ID {ticket_id} enviado al cliente exitosamente.')

    def update(self, args):
        '''
        Actualizar un ticket por id.
        
        '''
        parser = argparse.ArgumentParser(description="Actualizar un ticket")
        parser.add_argument('-i', '--id', required=True, help="ID del ticket")
        parser.add_argument('-t', '--title', help="Nuevo título del ticket")
        parser.add_argument('-d', '--description', help="Nueva descripción del ticket")
        parser.add_argument('-s', '--status', help="Nuevo estado del ticket")

        if not self.user_id:
            response = make_response(401, 'Debes iniciar sesión o registrarte primero para ejecutar este comando')
            self.socket.send(response.encode())
            return

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            logger.error('Has ingresado el comando update de forma incorrecta. Uso: update -i <id> [-t <título>] [-d <descripción>] [-s <estado>]')
            response = make_response(400, 'Has ingresado el comando update de forma incorrecta. Uso: update -i <id> [-t <título>] [-d <descripción>] [-s <estado>]')
            self.socket.send(response.encode())
            return

        ticket_id = parsed_args.id
        ticket_data = ticket_manager.get_ticket(int(ticket_id))

        if not ticket_data:
            logger.error(f'Ticket no encontrado por id {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'Ticket no encontrado, intenta con otro ID.')
            self.socket.send(response.encode())
            return
        
        if not self.has_permission(ticket_data):
            logger.error(f'Acceso denegado para el ticket {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, 'No tienes permiso para actualizar este ticket')
            self.socket.send(response.encode())
            return
        
        data = {}
        if parsed_args.title:
            data['title'] = parsed_args.title
        if parsed_args.description:
            data['description'] = parsed_args.description
        if parsed_args.status:
            data['status'] = parsed_args.status
        
        if data:
            ticket_manager.update_ticket(int(ticket_id), data)
            logger.info(f'Ticket con ID {ticket_id} actualizado exitosamente por {self.address[0]}:{self.address[1]}!')
            response = make_response(200, f'Ticket actualizado exitosamente.')
            self.socket.send(response.encode())
        else:
            logger.error(f'Intento de actualización fallido por {self.address[0]}:{self.address[1]}, no se encontraron campos para actualizar.')
            response = make_response(404, 'No se encontraron campos para actualizar.')
            self.socket.send(response.encode())

    def delete(self, args):
        '''
        Eliminar un ticket por id.
        
        '''
        parser = argparse.ArgumentParser(description="Eliminar un ticket")
        parser.add_argument('-i', '--id', required=True, help="ID del ticket a eliminar")

        if not self.user_id:
            response = make_response(404, 'Debes iniciar sesión o registrarte primero para ejecutar este comando')
            self.socket.send(response.encode())
            return

        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            logger.error('Has ingresado el comando delete de forma incorrecta. Uso: delete -i <id>')
            response = make_response(400, 'Has ingresado el comando delete de forma incorrecta. Uso: delete -i <id>')
            self.socket.send(response.encode())
            return
        
        ticket_id = parsed_args.id

        ticket_data = ticket_manager.get_ticket(int(ticket_id))

        if not ticket_data:
            logger.error(
                f'Ticket no encontrado por id {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, 'Ticket no encontrado!')
            self.socket.send(response.encode())
            return

        if not self.has_permission(ticket_data):
            logger.error(f'Acceso denegado para el ticket {ticket_id} por {self.address[0]}:{self.address[1]}!')
            response = make_response(404, 'No tienes permiso para eliminar este ticket')
            self.socket.send(response.encode())
            return
        
        ticket_manager.delete_ticket(int(ticket_id))
        
        logger.info(f'Ticket con ID {ticket_id} eliminado exitosamente por {self.address[0]}:{self.address[1]}!')
        response = make_response(200, f'Ticket eliminado exitosamente.')
        self.socket.send(response.encode())

    def exit(self, _):
        '''
        Cierra la conexión con el cliente y finaliza el programa.
        
        '''
        logger.info(f'Cliente {self.address} desconectado!')
        response = make_response(499, '¡Cliente desconectado!')
        self.socket.send(response.encode())
        self.socket.close()

        raise SystemExit

    def main(self):
        '''
        Mantiene el servidor en ejecución, recibe mensajes de los clientes y los procesa.
        
        '''
        try:
            while True:
                message = self.socket.recv(1024).decode()
                command, args = parse_message(message)
                if command == 'login':
                    self.login(args)
                elif command in self.commands:
                    if not self.user_id:
                        response = make_response(400, 'Debes iniciar sesión o registrarte primero')
                        self.socket.send(response.encode())
                    else:
                        logger.info(f'Executing command: {command}')
                        self.commands[command](args)
                else:
                    logger.error(f'Comando no encontrado: {command}. Inténtalo de nuevo!')
                    response = make_response(404, f'Comando no encontrado: {command}. Inténtalo de nuevo!')
                    self.socket.send(response.encode())
                    
        except IndexError:
            logger.info('Cliente desconectado!')
            
        except Exception as e:
            logger.error(f'Error inesperado: {e}')
            response = make_response(500, 'Error interno del servidor')
            self.socket.send(response.encode())



class Server:
    '''
    Clase para manejar la creación de un servidor.
    
    '''
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.create_socket()
        self.handle_accept()

    def create_socket(self):
        '''
        Crea un socket en el host y puerto especificados.
        '''
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        logger.info(f'Socket creado correctamente en {self.host}:{self.port}')
        
        self.server.bind((self.host, self.port))
        
        #Configura el socket para escuchar conexiones entrantes, con una cola de hasta 5 conexiones pendientes.
        self.server.listen(5)

    def handle_accept(self):
        '''
        Acepta conexiones entrantes y crea un hilo para manejar cada conexión.
        
        '''
        try:
            logger.info('Aceptando conexiones entrantes...')
            while True:
                client, address = self.server.accept()
                logger.info(f'Conexión establecida con {address[0]}:{address[1]}')
                thread = threading.Thread(target=ClientHandler, args=(client, address))
                thread.start()
                
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt: el servidor se cerrará...')
            self.server.close()
            raise SystemExit

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(add_help=False, description='Servidor de Tickets')
    parser.add_argument('-h', '--host', default='127.0.0.1', help='Host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')
    parser.add_argument('-d', '--debug', type=bool, default=False, help='Debug mode')
    parser.add_argument('--help', action='help', default=argparse.SUPPRESS, help='Muestra este mensaje de ayuda y sale del programa')

    args = parser.parse_args()

    logger = Logger(debug=args.debug)
    Server(args.host, args.port)
