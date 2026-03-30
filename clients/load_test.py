import asyncio
import ssl
import random
import json
import os

HOST = "127.0.0.1"
PORT = 12000
NUM_CLIENTS = 1000

#loading the items dynamically from the .json file
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
items_path = os.path.join(BASE_DIR, "server", "items.json")

with open(items_path, "r") as f:
    items = json.load(f)

item_ids = [int(k) for k in items.keys()]

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

async def fake_client(id):
    # This spreads the 1000 connection attempts over 3 seconds.
    await asyncio.sleep(random.uniform(0, 3))
    
    try:
        reader, writer = await asyncio.open_connection(
            HOST, PORT, ssl=context
        )

        await reader.read(1024)

        writer.write(f"user{id}\n".encode())
        await writer.drain()

        await reader.read(1024)

        for _ in range(3):
            item = random.choice(item_ids)
            bid = random.randint(100, 1000)

            writer.write(f"BID {item} {bid}\n".encode())
            await writer.drain()

            await asyncio.sleep(random.uniform(0.5, 2))

        writer.write("QUIT\n".encode())
        await writer.drain()

        writer.close()
        await writer.wait_closed()
        
   
    except Exception as e:
        print(f"Bot {id} error: {e}")


async def main():
    tasks = [fake_client(i) for i in range(NUM_CLIENTS)]
    await asyncio.gather(*tasks)

asyncio.run(main())
