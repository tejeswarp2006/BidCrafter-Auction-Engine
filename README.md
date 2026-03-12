# BidCrafter-Auction-Engine
**BidCrafter** is a real-time online auction platform supporting multiple bidders and items.

## Features
- **Multi-client Model:** It can handle multiple connections(Bidders) at the same time without blocking other connections.
- **Real-Time Bidding:** Notifies all connected bidders instantaneously when a new highest bid is placed.
- **Connection-Oriented** Built on TCP connection for efficient and reliable data transfer for high-stake auctions.
- **Session Management:** Tracks connected users and gracefully handles client disconnects or timeouts.
---

## Architecture
* **Language:** Python 3.8+
* **Networking:** Raw TCP Sockets via Python's built-in `socket` library.
* **Concurrency Model:** Multi-threading via the `threading` library.
---

## Prerequisites

Before you begin, ensure you have met the following requirements:
* Python `3.8` or higher installed on your system.
* A terminal or command prompt to run the server and client instances.
* Atleast two Virtual Machines if you are running it on the same system

## Contributors
- Zia Kadijah
- Palla Tejeswar Reddy
- Mohammed Noor
## you are free to change the name and description of the repo if you guys want to!!
