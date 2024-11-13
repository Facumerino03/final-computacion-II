import json

def parse_request(request):
    '''
    Función para parsear la respuesta recibida desde el servidor
    
    '''
    request = json.loads(request)
    return request['status_code'], request['response']
