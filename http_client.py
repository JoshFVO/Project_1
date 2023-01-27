import socket
import sys
import re

#https://www.internalpointers.com/post/making-http-requests-sockets-python used this resource for help 

#grab get request
server = sys.argv[1]
port = ""

#if secure access, send error code
if server.find("https") != -1:
    sys.stderr.write("ERROR (1): secure website")
    exit(1)

#if it does not include a http hyper link, send error code
if server.find("http://") == -1:
    sys.stderr.write("ERROR (2): improper url")
    exit(2)

#remove http and nested url to get url host server
server = server.replace("http://","")
if server.endswith("/"):
    server = server[0:len(server)-1]

if server.find("/") != -1:
    server = server[0:server.find("/")]

#find reuqested port if included
while server[len(server)-1].isnumeric():
    port = server[len(server)-1] + port
    server = server[0:len(server)-1]

#if port is not specified, default to port 80
if port == "":
    port = "80"
else:
    server = server[0:len(server)-1]

port = int(port)

#connect socket to server at port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((""+server,port))

#send get request to host 
sock.send(bytes("GET " + sys.argv[1] + " HTTP/1.1\r\nHost:"  + server + "\r\nConnection: close\r\n\r\n", 'utf-8'))

#keep adding to response till there is no more data to receive 
response = b""
while True:
    chunk = sock.recv(4096)
    if len(chunk) == 0:     # No more data received, quitting
        break
    response = response + chunk


#if error code, return body of response if possible and non success exit
response = response.decode("utf-8","ignore")
code = response[9:12]
if int(code) >= 400:
    if response.find("<!DOCTYPE html>") != -1:
     sys.stdout.write(response[response.find("<!DOCTYPE html>"):len(response)])
    exit(3)

#if the content is not html, send non 0 exit code
if response.find("Content-Type: text/html") == -1:
    exit(4)

#form counter for redirects
counter = 0

#checks if there is a redirect found
while response.find("HTTP/1.1 302 Found") != -1 or response.find("HTTP/1.1 301 Moved Permanently") != -1:

    #if there is more than 10 redirects, send non 0 exit code
    counter += 1
    if counter > 10:
        exit(5)

    #finds redirected url and prints redirect url
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, response)
    url = url[0][0]
    url2 = url
    sys.stderr.write("Redirected To: " + url + '\n')

    #if secure url, exit with non 0 code
    if url.find("https") != -1:
        sys.stdout.write("ERROR (1): secure website\n")
        exit(1)
    
    #checks if the previous url is equal to the redirected, if so print same body and exit
    if url2.find("www.") != -1 and sys.argv[1].find("www.") == -1:
        url2 = url2.replace("www.","")

    if url2.endswith("/") == True and sys.argv[1].endswith("/") == False:
        url2 = url2[0:len(url2)-1]
    if url2 == sys.argv[1]:
        sys.stdout.write(response[response.find("<!DOCTYPE html>"):len(response)])
        exit(0)

    #reconnect socket to server and get redirected url data 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((""+server,port))
    sock.send(bytes("GET " + url + " HTTP/1.1\r\nHost:"  + server + "\r\nConnection: close\r\n\r\n", 'utf-8'))
    response = b""
    while True:
        chunk = sock.recv(4096)
        if len(chunk) == 0:     # No more data received, quitting
            break
        response = response + chunk

    response = response.decode("utf-8","ignore")

    if response.find("Content-Type: text/html") == -1:
        exit(4)

#print response body, end socket connection, and 0 exit
sys.stdout.write(response[response.find("<!DOCTYPE html>"):len(response)])
sock.close()
exit(0)
