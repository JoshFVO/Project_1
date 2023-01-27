import socket
import sys
import json


#removes unnecessary chars from the strings to just get the operands
def removeLetters(remover):
    return remover[remover.find('=')+1:len(remover)]


#converts the strings into floats if possible 
def floatConverter(remover):
    try:
        return float(remover)
    except:
        return "no"

#mulitplies all the nums in the list
def mulitplyList(x):
    result = 1
    for num in x:
        result = result * num

    #checks if result is infinity or negative infinity
    if result == float('inf'):
        return "inf"

    if result == float('-inf'):
        return "-inf"

    return result



        
#setting up server to given host and port, ready to listen
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
HOST, PORT = "", int(sys.argv[1])
sock.bind((HOST, PORT))
sock.listen(10)


while(True):

    #if there is a connection request, accept it
    connection, address = sock.accept()

    #gets data from connect and splits it to the connection url 
    data = connection.recv(1024)
    lines = data.decode().split('\n')
    request = lines[0]
    request = request[0:len(request)-10]
    print(request)

    #check if the url is actually the /product request
    if request.find("GET /product") != 1:

        #check that the url has parameters, if not, send error code
        if request.endswith("product") or request.endswith("product?"):
            header = "HTTP/1.1 404 Not Found\r\n\r\n"
            connection.send(header.encode())
            connection.send(b"404 Not Found")

        
        #if it does, get these paramaters and attempt to convert them to float point numbers
        else:
            response = ""
            params = request[13:len(request)]
            params_list = params.split('&')
            params_list = list(map(removeLetters,params_list))
            params_list = list(map(floatConverter,params_list))
            print(params_list)
            #if there was a parameter that could not be converted to a float, send error code
            if params_list.count("no") != 0:
                header = "HTTP/1.1 404 Not Found\r\n\r\n"
                connection.send(header.encode())
                connection.send(b"404 Not Found")
            
            #if they all code, formulate json response with operands and product result
            else:

                header = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
                response = {"operation": "product",  "operands": params_list, "result": mulitplyList(params_list)}
                connection.send(header.encode())
                connection.send(json.dumps(response).encode())
    
    #if not the product url, send error code
    else:
        header = "HTTP/1.1 404 Not Found\r\n\r\n"
        connection.send(header.encode())
        connection.send(b"404 Not Found")


   #close connection once data is done sending
    connection.close()
    



