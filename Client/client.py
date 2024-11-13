import sys
import socket
import argparse
from utils import parse_request

class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.sock.connect((host, port))
        self.main()

    def main(self):
        '''
        Función principal del cliente que recibe los comandos del usuario
        
        '''
        try:
            while True:
                message = input('\n-> ')
                if not message:
                    continue
                self.sock.send(message.encode())
                data = self.sock.recv(4096).decode()
                status_code, response = parse_request(data)

                if status_code in [200, 201]:
                    print(response)
                if status_code in [400, 404]:
                    print(response)
                if status_code in [499]:
                    print(response)
                    break
        
        except KeyboardInterrupt:
            print('\nCliente desconectado.')
            self.sock.close()
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cliente para el Sistema de Tickets')
    parser.add_argument('--host', '-a', type=str, default='127.0.0.1', help='Server address')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Server port')
    args = parser.parse_args()
    
    print("""
¡Bienvenido al Sistema de Gestión de Tickets!

Este sistema le permite gestionar tickets con los siguientes comandos:

Comandos de Usuario:
- login [-i "ID"]
  -> Inicia sesión con un ID de usuario.
- login
  -> Registra un nuevo usuario y obtiene un ID.

Comandos de Ticket:
- create -t "Título" -a "Autor" -d "Descripción"
  -> Crea un nuevo ticket.
          
- update -i ID [-t "Título"] [-a "Autor"] [-d "Descripción"] [-s "Estado"]
  -> Actualiza un ticket existente.
          
- delete -i ID
  -> Elimina un ticket por su ID.
          
- find -i ID
  -> Busca un ticket por su ID o lista todos los tickets.

Comando de Salida:
- exit
  -> Cierra el sistema.

IMPORTANTE: Debes iniciar sesión o registrarte antes de gestionar tickets.

Ingrese un comando para empezar:
""")

    Client(args.host, args.port)