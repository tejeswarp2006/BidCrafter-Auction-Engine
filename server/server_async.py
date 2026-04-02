import asyncio 
import ssl 
import time
import json
import os

#because our file paths kept going wishy washy:
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
cert = os.path.join(BASE_DIR,"certs","server.crt")
key = os.path.join(BASE_DIR,"certs","server.key")
items = os.path.join(BASE_DIR,"server","items.json")

#this is to test server throughput. FYI: throughput gets printed every 50 requests in the terminal
request_count = 0
start_time_metrics = time.time()
total_latency = 0
latency_count = 0

def print_final_metrics(): #stats!
    global request_count, start_time_metrics, total_latency, latency_count
    
    total_time = time.time() - start_time_metrics
    
    avg_throughput = request_count / total_time if total_time > 0 else 0
    avg_latency = total_latency / latency_count if latency_count > 0 else 0

    print("\nFINAL METRICS")
    print(f"Total Requests: {request_count}")
    print(f"Total Time: {total_time:.2f} sec")
    print(f"Average Throughput: {avg_throughput:.2f} req/sec")
    print(f"Average Latency: {avg_latency*1000:.2f} ms")
    print("\n")

#ssl implementation
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(cert,key)

#loading items from items.json into a dictionary called auctions
with open(items, "r") as f: 
    auctions = json.load(f)
#here's what's happening: the items are loaded from the items.json file into a python dictionary 
#fun fact:a dictionary in python is actually implemented using hashmaps! this is super efficient :D 
auctions = {int(k): v for k, v in auctions.items()} #json stores the item ids as strings, but our code wants them in int format

#values are being re-initialised every time the server starts up
for item in auctions.values(): 
    item["highest_bidder"]=None
    item["start_time"] = None
    item["ended"] = False

clients = set() #using a set to store clients because we don't want duplicates
usernames = {}

auction_lock = asyncio.Lock() #asyncio lock manages access to shared resources in an asynchronous environment

#async broadcast function
'''note: DO NOT get confused between readers/writers from the readers-writers problem and this particular readers and writer.
(I'm only saying that because I got confused the first time.)
In asyncio, the terms "reader" and "writer" typically refer to the StreamReader and StreamWriter objects, which are APIs used for asynchronous network I/O and communication with subprocesses. 
They enable writing concurrent code without using traditional callbacks.
'''
async def broadcast(message):
    for writer in clients:
        try:
            writer.write((message + "\n").encode())
            await writer.drain()
            #drain is used to ensure that the message is sent before we move on to the next one. 
            #it allows us to manage the flow of messages and prevent overwhelming the clients with too many messages at once.
        except:
            clients.discard(writer)
            
            
#async client handler function 
async def handle_client(reader, writer):
    
    addr = writer.get_extra_info('peername') #this is the asyncio way of getting the client's address
    #asyncio is lowkey a pain but we gotta do what we gotta do 
    ssl_object = writer.get_extra_info('ssl_object')
    if ssl_object:
        print("Secure connection established with", addr)
        print("TLS version:", ssl_object.version())
        print("Cipher:", ssl_object.cipher())
        print("New client connected! Address:", addr)
    clients.add(writer) #add the writer to the set of clients
    
    #getting username from the client
    writer.write("Welcome! I'm Esmeralda, BidCrafter's server. Please enter your username:".encode())
    await writer.drain()
    username = (await reader.read(1024)).decode().strip()
    usernames[writer] = username
    
    #general instructions
    writer.write(f"Welcome to the auction, {username}! Use the command LIST to see items.\nTo bid, type in BID <item_id> <price>.\nUse the command STATUS <item_id> to see the current value of an item.\nAnd of course, enter QUIT to leave (I'll be sad to see you go, though).\nHappy bidding, and may the odds be ever in your favour!".encode())
    await writer.drain()
    
    #handling all forms of requests
    while True:
        try:
            message = (await reader.read(1024)).decode().strip()
            
            if not message:
                break

            start_latency = time.time()
            global request_count 
            request_count+=1
            
            if request_count % 50 == 0:
                elapsed = time.time() - start_time_metrics
                avg_throughput = request_count / elapsed
                print(f"Average Throughput: {avg_throughput:.2f} req/sec")
            
            print(addr, "sent you a message! It reads:\n", message)
            parts = message.split()
            command = parts[0].upper()
            
            if command == "LIST":
                item_list = "Here's what's in store for you today:\n"
                for item_id, item_info in auctions.items():
                    status = "ENDED" if item_info["ended"] else "ACTIVE"
                    item_list += f"{item_id}. {item_info['name']} [{status}] - Current highest bid: {item_info['highest_bid']} by {item_info['highest_bidder']}\n"
                writer.write(item_list.encode())
                await writer.drain()
                
            elif command == "BID":
                try:
                    item = int(parts[1])
                    bid_amount = int(parts[2])
                except:
                    writer.write("Invalid BID format. Use: BID <item_id> <amount>\n".encode())
                    await writer.drain()
                    continue

                async with auction_lock: #critical section
                    if item in auctions:
                        if auctions[item]["ended"]:
                            writer.write(f"\nOh no! Bidding for {auctions[item]['name']} has ended. Learn to read, silly!\n".encode())
                            await writer.drain()
                            continue
                        
                        if auctions[item]["start_time"] is None:
                            auctions[item]["start_time"] = time.time()

                        if bid_amount > auctions[item]["highest_bid"]: 
                            auctions[item]["highest_bid"] = bid_amount
                            auctions[item]["highest_bidder"] = usernames[writer]
                            writer.write(f"\nWOAHH CHECK THIS OUT- You're the highest bidder for {auctions[item]['name']} with a bid of {bid_amount}! Dude, that's sick.".encode())
                            await writer.drain()
                            await broadcast(f"\nAttention please! {usernames[writer]} has placed a bid of {bid_amount} on {auctions[item]['name']}! Current highest bid is now {bid_amount}.")
                        else:
                            writer.write(f"Bid is too low! Current bid is {auctions[item]['highest_bid']}. Don't be cheap, {usernames[writer]}! This item is worth a lot more than you think...".encode())
                            await writer.drain()
                    else:
                        writer.write("Ruh Roh. Looks like this item isn't on the list. Don't try to play smart with me.".encode())
                        await writer.drain()
                        
            elif command == "STATUS":
                try:
                    item = int(parts[1])
                except:
                    writer.write("Invalid STATUS format. Use: STATUS <item_id>\n".encode())
                    await writer.drain()
                    continue

                if item in auctions:
                    if auctions[item]["ended"]:
                        writer.write(f"Oh no! The bidding for this item has ended. Learn to read, silly!\n".encode())
                        await writer.drain()
                    else:
                        writer.write(f"Current highest bid is {auctions[item]['highest_bid']} by {auctions[item]['highest_bidder']}. Keep going, this item is too precious to lose!".encode())
                        await writer.drain()
                else:
                    writer.write("Ruh Roh. Looks like this item isn't on the list. Don't try to play smart with me.".encode())
                    await writer.drain()
            
            elif command == "QUIT":
                writer.write("Thanks for coming! I hope it was worth your time :D".encode())
                await writer.drain()
                break

            latency = time.time() - start_latency

            global total_latency, latency_count
            total_latency += latency
            latency_count += 1

            print(f"Latency: {latency:.4f}s")

            if latency_count % 50 == 0:
                avg_latency = total_latency / latency_count
                print(f"Average Latency: {avg_latency:.4f}s")
        except:
            break
        
    print(addr, " disconnected") 
    clients.discard(writer)
    usernames.pop(writer, None) 
        
    writer.close()
    try:
        await writer.wait_closed()
    except:
        pass
    
#how we're ending the auction- time basis
async def timer_task(): 
    while True:
        to_remove = []

        for item_id, item_data in auctions.items():
            if item_data["start_time"] is not None and not item_data["ended"]:
                
                elapsed = time.time() - item_data["start_time"]

                if elapsed >= item_data["duration"]:

                    winner = item_data["highest_bidder"]
                    price = item_data["highest_bid"]

                    await broadcast(
                        f"Ding ding ding!! Time's up!\n {item_data['name']} → {winner} with {price}"
                    )

                    to_remove.append(item_id)

        for item_id in to_remove:
            auctions[item_id]["ended"] = True

        await asyncio.sleep(1)
        

async def main():
    server = await asyncio.start_server(
        handle_client, 
        '0.0.0.0',
        12000, 
        ssl = context
    )
        
    print("Esmerelda is running on port 12000!!! <3")
    asyncio.create_task(timer_task())
    async with server:
        await server.serve_forever()
        
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nShutting down server...")
    print_final_metrics()