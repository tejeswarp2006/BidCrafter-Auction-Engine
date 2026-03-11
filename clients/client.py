#The client can type in commands like BID, STATUS, AND QUIT. 

from socket import *
import threading 
import ssl

context = ssl.create_default_context() #default SSL context that is used to wrap the client socket
context.check_hostname = False 
#the above line is included because we're using "self-signed certificates"
#this means that the certificate is not signed by a certificate authority, so the client can't verify the server's identity
#by setting the above line to false, we're telling the client not to check at all. 
context.verify_mode = ssl.CERT_NONE


serverName = "localhost" #really wanted to name it esmerelda but that's not how sockets work :( 
serverPort = 12000
rawSocket = socket(AF_INET, SOCK_STREAM)
clientSocket = context.wrap_socket(rawSocket, server_hostname=serverName) #wrapping the client socket with SSL
clientSocket.connect((serverName,serverPort))

print("Connected to Esmerelda!")

def receive_messages():
    while True:
        try:
            message = clientSocket.recv(1024).decode()
            if message:
                print("\n" + message)
        except:
            break


receive_thread = threading.Thread(target=receive_messages) #this is a thread that runs the receive_messages function
receive_thread.start() 
#now the client can receive messages and simultaneously send bids 

while True:
    message = input()
    clientSocket.send(message.encode())
    
    if message.upper() == "QUIT":
        #reason i did this is because without this, the client took 2 input messages to quit everytime i entered QUIT. 
        #also we need to make sure that the client socket is closed when the client quits, or the server may try to send 
        #messages to a closed socket. 
        clientSocket.close()
        break 
    