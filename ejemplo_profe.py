import argparse
import socket
import threading
"""
Este script configura un servidor de chat utilizando argparse para manejar los argumentos de línea de comandos.

Argumentos:
    --address, -a: Dirección IP en la que el servidor escuchará.
    --port, -p: Puerto en el que el servidor escuchará (por defecto es 8080).

Uso:
    python chat_server.py --address <direccion_ip> --port <numero_puerto>

Descripción paso a paso:
1. Importa el módulo argparse para manejar los argumentos de línea de comandos.
2. Crea un objeto ArgumentParser con una descripción del programa.
3. Define los argumentos de línea de comandos:
    - '--address' o '-a' para especificar la dirección IP.
    - '--port' o '-p' para especificar el puerto (por defecto 8080).
4. Analiza los argumentos proporcionados por el usuario.
5. Imprime la dirección y el puerto que se utilizarán para el servidor de chat.
"""

parser = argparse.ArgumentParser(description='Chat Server')

parser.add_argument('--address', '-a')
parser.add_argument('--port', '-p', type=int, default=8080)
args = parser.parse_args()

print("Address:", args.address, "Port:", args.port)

class ChatServer:
    #variables de clase
    running_servers = 0
    def __init__(self, host, port):
        if chat_server.running_servers != 0:
            print("Only one server can run at a time")
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Asocia el socket a la dirección y puerto especificados basado en INET, permitiendo conectarse a multiples protocolos.
        # SOCK_STREAM indica que se utilizará el protocolo TCP.
        self.socket.bind((host, port))
        # Habilita el socket para recibir conexiones y especifica el número máximo de conexiones pendientes (cuantos podemos escuchar sin aceptar).
        self.socket.listen(1)
        self.clients = []
        chat_server.running_servers += 1   

    def accept_connection(self):
        client_socket, client_address = self.socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        return client_socket, client_address
    
    def server_client(self, client_socket):
        while True:
            data = client_socket.recv(1024).decode()
            print(f"Received: {data}")
            if data.strip() == 'exit':
                break
            
            if client in chat_server.clients:
                if client != client_socket:
                    client.send(data.encode())
        
        client_socket.close()
    
    def start(self):
        print(f"Starting server on {self.host}:{self.port}")
        while True:
            client_socket = chat_server.accept_connection()
            chat_server.clients =
            print("Connection accepted")
            print(f"Client connected from: {client_socket.getpeername()}")
            threading.Thread(target=chat_server.server_client, args=(client_socket,)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat server")
    parser.add_argument("--address", type=str, default="localhost", help="Address to bind the server to")
    parser.add_argument("--port", type=int, required=True, help="Port to bind the server to")
    args = parser.parse_args()

    chat_server = ChatServer(args.address, args.port)
    chat_server.start()
    print("Waiting for connections...")
    
        
        # r = client_socket.recv(1024).decode()
        # print(f"Received", r)
        # if r.strip() == 'exit':
        #     print("Client disconnected")
        #     break
        # client_socket.close()
        



def crear_ticket(data):
    ticket = Ticket(
        title=data.get('title'),
        author=data.get('author'),
        description=data.get('description'),
        status='pending',
    )

    # Guardar el ticket en Redis
    ticket_id = client.incr('ticket:id')  # Incrementar ID para cada ticket
    client.hset(f'ticket:{ticket_id}', mapping=ticket.to_dict())

    return ticket_id


