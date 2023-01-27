import socket
import sys

HOST, PORT = "", int(sys.argv[1])

def handle_request(client_connection):
    request = client_connection.recv(1024).decode()
    request_lines = request.split("\r\n")
    file_requested = request_lines[0].split()[1]

    if file_requested.endswith(".html") or file_requested.endswith(".htm"):
        try:
            with open(file_requested[1:], "rb") as file:
                response = file.read()
                header = "HTTP/1.1 200 OK\r\n\r\n"
                client_connection.send(header.encode())
                client_connection.send(response)
        except:
            header = "HTTP/1.1 404 Not Found\r\n\r\n"
            client_connection.send(header.encode())
            client_connection.send(b"404 Not Found")
    else:
        header = "HTTP/1.1 400 Bad Request\r\n\r\n"
        client_connection.send(header.encode())
        client_connection.send(b"400 Bad Request")

    client_connection.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Serving HTTP on port {PORT}...")
    while True:
        client_connection, client_address = server_socket.accept()
        handle_request(client_connection)