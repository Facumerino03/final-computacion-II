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
            print('\nClient disconnected!')
            self.sock.close()
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chat Client')
    parser.add_argument('--host', '-a', type=str, default='127.0.0.1', help='Server address')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Server port')
    args = parser.parse_args()

    print("""
    ¡Bienvenido al Sistema de Tickets!

    Este sistema le permite gestionar tickets fácilmente con los siguientes comandos:
          
    - create -t "Título" -a "Autor" -d "Descripción"                           -> Crea un ticket.
    - update -i ID [-t "Título"] [-a "Autor"] [-d "Descripción"] [-s "Estado"] -> Actualiza un ticket.
    - delete -i ID                                                             -> Elimina un ticket por su ID.
    - find -i ID                                                               -> Lista todos los tickets o busca por ID.
    - exit                                                                     -> Cierra el sistema.

    Ingrese un comando para empezar.
    """)

    Client(args.host, args.port)