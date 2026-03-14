# BidCrafter Auction Engine

A **secure real-time auction system** built using TCP sockets in Python.
The system allows multiple clients to connect to a central server and participate in live bidding for multiple auction items.

All communication between the server and clients is **encrypted using TLS (SSL)** to ensure secure transmission of auction commands and bid information.

---

## Features

* **Multi-client support** using threaded server architecture
* **TLS-encrypted communication** using Python's `ssl` module
* **Multiple auction items** with unique item IDs
* **Real-time bidding updates** broadcast to all connected clients
* **Thread-safe bidding logic** using locks to prevent race conditions
* **Username system** for bidder identification
* **Auction timer** that automatically declares winners
* **Custom application-layer protocol**

---

## System Architecture

```
Clients
   ↓
Secure TCP Connection (TLS)
   ↓
Auction Server
   ↓
Shared Auction State
```

Each connected client communicates with the server over a **secure TCP socket**.
The server maintains the auction state and ensures fair bidding using synchronization mechanisms.

---

## Project Structure

```
BidCrafter-Auction-Engine
│
├── certs/
│   ├── server.crt
│   └── server.key
│
├── clients/
│   └── client.py
│
├── server/
│   └── server.py
│
├── .gitignore
└── README.md
```

---

## Requirements

* Python 3.8+
* OpenSSL (for generating TLS certificates)

---

## Generating TLS Certificates

Before running the server, generate a self-signed certificate:

```
openssl req -new -x509 -days 365 -nodes -out certs/server.crt -keyout certs/server.key
```

This will create the TLS certificate and private key used for encrypted communication.

**Note:** The private key should not be committed to version control.

---

## Running the Auction Server

Navigate to the project directory and start the server:

```
python server/server.py
```

You should see output similar to:

```
Esmerelda is up and running!
Secure connection established with ('127.0.0.1', 53212)
TLS version: TLSv1.3
Cipher: TLS_AES_256_GCM_SHA384
```

---

## Connecting Clients

Open another terminal and run:

```
python clients/client.py
```

You can run multiple clients simultaneously to simulate concurrent bidders.

---

## Auction Commands

### View available items

```
LIST
```

### Place a bid

```
BID <item_id> <amount>
```

Example:

```
BID 2 500
```

### Check current item status

```
STATUS <item_id>
```

Example:

```
STATUS 3
```

### Leave the auction

```
QUIT
```
---

## Security

All client-server communication is secured using **TLS encryption** via Python's `ssl` module.
This ensures that auction commands and bid values cannot be intercepted or modified in transit.

---

## Concepts Demonstrated

This project demonstrates several important networking and systems concepts:

* TCP socket programming
* Threaded server architecture
* TLS encryption
* Application-layer protocol design
* Concurrency control with locks
* Real-time event broadcasting
* Client-server communication

---

## Future Improvements

* **Dynamic Auction Timer:**
  Introduce configurable or per-item timers so that each auction can have its own countdown instead of relying on a single fixed-duration timer.

* **Scalable Connection Handling:**
  Replace the current thread-per-client model with an **asynchronous event-driven architecture** using Python's `asyncio`. This would allow the server to handle a much larger number of simultaneous clients without creating a separate thread for each connection.

* **External Item Configuration:**
  Move auction items out of the source code and store them in a structured file such as **CSV or JSON**. This would allow items to be easily added, removed, or modifie


---

## Contributors
- Zia Kadijah
- Palla Tejeswar Reddy
- Mohammed Noor
