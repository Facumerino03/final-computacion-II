import json

def parse_request(request):
    request = json.loads(request)
    return request['status_code'], request['response']
