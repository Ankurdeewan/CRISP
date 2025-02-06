import socket
import threading
import time

intercept_status = False
intercept_queue = []
intercept_lock = threading.Lock

def forward_request(host, port, request_data, client_socket):
    try:
        print(f"[+] Forwarding request to {host}:{port}")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, port))
        
        server_socket.sendall(request_data)
        response = server_socket.recv(4096)

        if client_socket:
            client_socket.sendall(response)

        server_socket.close()
    except Exception as e:
        print(f"[!] Error forwarding request: {e}")



def handle_client_request(client_socket):
    global intercept_status, intercept_queue

    print("Received request:")
    request = b''
    client_socket.setblocking(False)

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            request += data
            print(data.decode('utf-8'), end='')
        except BlockingIOError:
            break

    host, port = extract_host_port_from_request(request.decode('utf-8'))

    with intercept_lock:
        if intercept_status:
            print("\n[+] Intercepting request. Pausing execution...")
            intercept_queue.append((host, port, request, client_socket))  
            
            while intercept_status: 
                time.sleep(0.5)

   
    forward_request(host, port, request, client_socket)


def extract_host_port_from_request(request):
    host_string_start = request.find('Host: ') + len('Host: ')
    host_string_end = request.find('\r\n', host_string_start)
    host_string = request[host_string_start:host_string_end]
    port = 80
    if ':' in host_string:
        host, port = host_string.split(':')
        port = int(port)
    else:
        host = host_string
    return host, port

def start_proxy_server(port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    print(f"Proxy server running on port {port}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Accepted connection from {client_address}")
        client_handler = threading.Thread(target=handle_client_request, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_proxy_server()