from socket import *
import threading 
import ssl 
import time

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5) #5 here is the max number of connections in the queue waiting to be accepted.
print("Esmerelda is up and running!")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("BidCrafter-Auction-Engine/certs/server.crt", "BidCrafter-Auction-Engine/certs/server.key")

clients = []
auction_lock = threading.Lock() #lock ensures that only one thread can be in critical section at a time (OS cameo)

auctions = {
    1: {"name": "Saleena's Soul", "highest_bid": 100, "highest_bidder": None},
    2: {"name": "Zia's 970 day Duolingo Streak", "highest_bid": 50, "highest_bidder": None},
    3: {"name": "10 CGPA", "highest_bid": 500, "highest_bidder": None},
    4: {"name": "The Pyramids of Giza", "highest_bid": 10, "highest_bidder": None},
    5: {"name": "Sanju Samson", "highest_bid": 1000, "highest_bidder": None}
}

auction_duration = 120 #seconds
auction_start = time.time() #this can be used to track the duration of the auction 

def clientHandler(connectionSocket, addr): #this function handles client connection      
    usernames = {}          
    clients.append(connectionSocket)
    connectionSocket.send("Welcome! I'm Esmeralda, BidCrafter's server. Please enter your username:".encode())
    username = connectionSocket.recv(1024).decode().strip()
    usernames[connectionSocket] = username
    
    connectionSocket.send(f"Welcome to the auction, {username}! Use the command LIST to see items.\nTo bid, type in BID <item_id> <price>.\nUse the command STATUS to see the current value of an item.\nAnd of course, enter QUIT to leave (I'll be sad to see you go, though).\nHappy bidding, and may the odds be ever in your favour!".encode())
    
    while True:
        try: 
            message = connectionSocket.recv(1024).decode().strip() 
            # this is the msg that the client sends to esmerelda, with the auction information 
            
            if not message: 
                break #this is for when the client disconnects
            
            print(addr, "sent:", message) 
            
            parts = message.split()
            command = parts[0].upper()
            
            if command == "LIST":
                item_list = "Here's what's in store for you today:\n"
                for item_id, item_info in auctions.items():
                    item_list += f"{item_id}. {item_info['name']} - Current highest bid: {item_info['highest_bid']} by {item_info['highest_bidder']}\n"
                connectionSocket.send(item_list.encode())
            
            elif command == "BID":
                    item = int(parts[1])
                    bid_amount = int(parts[2]) #the [2] is the third part of the message which is bid amount 
                    with auction_lock: #critical section
                        
                        '''small theory section: critical section is the part of the code that accesses shared resources.
                        here, the resources are highest bid and bidder. we need to ensure that no two threads access this section at the same time 
                        so we can avoid inconsistencies in the auction state.'''
                        
                        if item in auctions:
                            if bid_amount > auctions[item]["highest_bid"]:
                                auctions[item]["highest_bid"] = bid_amount
                                auctions[item]["highest_bidder"] = usernames[connectionSocket]
                                connectionSocket.send(f"\nWOAHH CHECK THIS OUT- You're the highest bidder for {auctions[item]['name']} with a bid of {bid_amount}! Dude, that's sick.".encode())
                                broadcast(f"\nAttention please! {usernames[connectionSocket]} has placed a bid of {bid_amount} on {auctions[item]['name']}! Current highest bid is now {bid_amount}.")                           
                            else: 
                                connectionSocket.send(f"Bid is too low! Current bid is {auctions[item]['highest_bid']}. Don't be cheap, {usernames[connectionSocket]}! This item is worth a lot more than you think...".encode())
                        else: 
                            connectionSocket.send("Ruh Roh. Looks like this item isn't on the list. Don't try to play smart with me.".encode())
            
            elif command == "STATUS":
                item = int(parts[1])
                if item in auctions: 
                    connectionSocket.send(f"Current highest bid is {auctions[item]['highest_bid']} by {auctions[item]['highest_bidder']}. Keep going, this item is too precious to lose!".encode())
                else:
                    connectionSocket.send("Ruh Roh. Looks like this item isn't on the list. Don't try to play smart with me.".encode())

            elif command == "QUIT":
                connectionSocket.send("Thanks for coming! I hope it was worth your time :D".encode())
                break
            
            if time.time() - auction_start >= auction_duration: #i.e. if the auction time is upppp girlll sorry it's 11:30pm

                for item in auctions:

                    winner = auctions[item]["highest_bidder"]
                    price = auctions[item]["highest_bid"]

                    broadcast(
                        f"WINNER {item} -> {winner} with {price}"
                    )

                break  
        except:
            break
        
        
    print(addr, " disconnected") #when the client disconnects, this is printed
    clients.remove(connectionSocket) 
    connectionSocket.close()
    
def broadcast(message): 
    for client in clients:
        try:
            client.send((message + "\n").encode()) #HOLY ENCODING
        except:
            pass #pass is used to ignore exceptions
        
while True:
    new_socket, addr = serverSocket.accept()
    connectionSocket = context.wrap_socket(new_socket, server_side=True) #wrapping the socket up with SSL 
    print("Secure connection established with", addr)
    print("TLS version:", connectionSocket.version())
    print("Cipher:", connectionSocket.cipher()) 
    thread = threading.Thread(target=clientHandler, args = (connectionSocket,addr))
    #this is what creates the client thread for each client that connects to the server
    #a thread is a separate flow of execution that can run concurrently so that Esmerelda can handle multiple clients at the same time
    thread.start()
