from socket import * #this is that stuff from CN slides- socket library is used for socket creation 
import threading #new library! what it do? 
#we can run multiple threads at the same time WOWOWOWOW

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5) #we'll take 5 connections

print("Esmerelda is ready to help the good people of Carnesia")

clients = [] #this is an array of clients 

def clientHandler(connectionSocket, addr): #this function handles client connection
    print("I'm connected to: ", addr)
    clients.append(connectionSocket) #once esmerelda is connected to a carnesian citizen ill add them to the array i made earlier
    
    while True:
        try: 
            message = connectionSocket.recv(1024).decode()
            # this is the msg that the client sends to esmerelda, with the auction information 
            
            if not message: 
                break #this is for when the client disconnects
            
            print(addr, "sent: ", message) #prints the message esmerelda receives 
            broadcast(message) 
            
        except:
            break
        
    print(addr, "disconnected") #when the client disconnects, this is printed
    clients.remove(connectionSocket) #the citizen then gets removed from array 
    connectionSocket.close()
    
def broadcast(message): #as mentioned in line 27 
    for client in clients:
        try:
            client.send(message.encode()) #HOLY END TO END ENCRYPTION 
        except:
            pass #pass is used to ignore exceptions
        
while True:
    connectionSocket, addr = serverSocket.accept()
    thread = threading.Thread(target=clientHandler, args = (connectionSocket,addr))
    #this is what creates the client thread for each client that connects to the server
    #a thread is a separate flow of execution that can run concurrently so that Esmerelda can handle multiple citizens at the same time
    thread.start()
