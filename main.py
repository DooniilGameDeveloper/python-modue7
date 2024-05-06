import os
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from enum import Enum
from urllib import parse


# Методы из модуля
def do_ping_sweep(ip, num_of_host):
    ip_parts = ip.split('.')
    network_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
    scanned_ip = network_ip + str(int(ip_parts[3]) + num_of_host)
    if int(scanned_ip.split('.')[-1]) > 255:
        return 'Incorrect IP'
    response = os.popen(f'ping -c 1 {scanned_ip}') 
    res = response.readlines()
    return f"[#] Result of scanning: {scanned_ip} [#]\n{res[1]}"


def sent_http_request(target, method, headers=None, payload=None):
    headers_dict = dict()
    if headers:
        for header in headers:
            header_name = header.split(':')[0]
            header_value = header.split(':')[1:]
            headers_dict[header_name] = ':'.join(header_value)
    if method == "GET":
        response = requests.get(target, headers=headers_dict)
    elif method == "POST":
        response = requests.post(target, headers=headers_dict, data=payload)
    return f"[#] Response status code: {response.status_code}\n" + \
        f"[#] Response headers: {json.dumps(dict(response.headers), indent=4, sort_keys=True)}\n" + \
        f"[#] Response content:\n {response.text}"


class Endpoint(str, Enum):
    Scan = '/scan'
    SendHTTP = '/sendhttp'


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = parse.urlparse(self.path) # парсинг URL
        keys = dict()
        if parsed_path.path == Endpoint.Scan.value:
            attributes: list = parsed_path.query.split('&') # парсинг параметров запроса по типу ?target=192.168.100.0&..=..
            for attribute in attributes:
                key, value = attribute.split('=')
                keys[key] = value
            
            message: str = do_ping_sweep(keys['target'], int(keys['count']))

            self.send_response(200, message.encode('utf-8'))
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))


    def do_POST(self):
        parsed_path = parse.urlparse(self.path)
        if parsed_path.path == Endpoint.SendHTTP.value:
            content_length = int(self.headers['Content-Length'])
            request_body: str = (self.rfile.read(content_length)).decode('utf-8')
            body = json.loads(request_body)

            message: str = sent_http_request(body.get('Target'), body.get('Method'), [f'{body.get("Header")}:{body.get("Header-value")}'])

            self.send_response(200, message.encode('utf-8'))
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))


if __name__ == '__main__':
    port = 8900
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Web Server running on port: {port}")
    print('Starting server, use <Ctrl-C> to stop')
    httpd.serve_forever()
