import socket
import select
import sys
import os

#Starts the accept socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)

#Takes a Port
HOST, PORT = "", int(sys.argv[1])

#Binds the empty host list and port
s.bind((HOST, PORT))

#Listens for any connections
s.listen(5)

# Initialize list of open connections and their states
# This method of havind a list and dictionary to determine if a socket is a new connection 
# was taken from https://pymotw.com/3/select/
connections = []
connection_states = {}

while True:
    # Create the read list, including the accept socket
    read_list = connections + [s]

    # Use select to block until a socket is ready to be read
    # If socket has already been closed we throw an exception and reset the connections list
    try:
        readable, writable, xexception = select.select(read_list, [], [])
    except:
        read_list = []
        readable, writable, xexception = select.select(read_list, [], [])

    for sock in readable:
        # If the socket is the accept socket, accept the new connection
        if sock == s:
            new_connection, address = sock.accept()
            connections.append(new_connection)
            connection_states[new_connection] = "new"
        else:
            # Check the state of the connection
            state = connection_states[sock]

            if state == "new":
                
                # Reads a singular byte to see if the connection is available else parse the entire request
                data = sock.recv(1, socket.MSG_PEEK)
                if data:
                    # Read the whole request
                    request = sock.recv(4096)
                    # Process the request
                    lines = request.decode().split('\n')
                    parts = lines[0].split()
                    if (parts != []):
                        request = parts[1][1:]
                    else:
                        request = ""


                    if os.path.isfile(request) and request.endswith(('.htm', '.html')):

                        if request:
                            with open(request, 'r') as file:
                                response = file.read()
                        else:
                            response = ""

                        header = "HTTP/1.1 200 OK\r\n\r\n"
                        sock.send(header.encode())
                        sock.send(response.encode())

                    elif os.path.isfile(request):
                        header = "HTTP/1.1 403 Forbidden\r\n\r\n"
                        sock.send(header.encode())
                        sock.send(b"403 Forbidden")
        
                    else:
                        header = "HTTP/1.1 404 Not Found\r\n\r\n"
                        sock.send(header.encode())
                        sock.send(b"404 Not Found")
                
                    sock.close()
                   
