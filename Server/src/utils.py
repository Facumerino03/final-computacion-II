import json
import shlex

def parse_message(message):
    '''
    Función para parsear el mensaje recibido desde el cliente
    '''
    args = shlex.split(message)
    command = args.pop(0)
    return command, args

def make_response(status_code, response):
    '''
    Función para crear una respuesta en formato JSON
    '''
    return json.dumps({
        'status_code': status_code,
        'response': response,
    })