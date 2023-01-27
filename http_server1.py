import socket
import sys
import os

#Starts the accept socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)

#Takes a Port
HOST, PORT = "", int(sys.argv[1])

#Binds the empty host list and port
sock.bind((HOST, PORT))

#Listens for any connections
sock.listen(10)


#Addresses any accepted connections
while(True):

    connection, address = sock.accept()

    #Parses data for file content
    data = connection.recv(1024)
    lines = data.decode().split('\n')
    parts = lines[0].split()
    if (parts != []):
        request = parts[1][1:]
    else:
        request = ""

    #Checks if the file content exist and is the correct file type
    if os.path.isfile(request) and request.endswith(('.htm', '.html')):

        if request:
            with open(request, 'r') as file:
                response = file.read()
        else:
            response = ""

    #Sends the appropriate response to the connection depending on condition

        header = "HTTP/1.1 200 OK\r\n\r\n"
        connection.send(header.encode())
        connection.send(response.encode())

    elif os.path.isfile(request):
        header = "HTTP/1.1 403 Forbidden\r\n\r\n"
        connection.send(header.encode())
        connection.send(b"403 Forbidden")
        
    else:
        header = "HTTP/1.1 404 Not Found\r\n\r\n"
        connection.send(header.encode())
        connection.send(b"404 Not Found")

    #Closes the connection socket
    connection.close()
    



