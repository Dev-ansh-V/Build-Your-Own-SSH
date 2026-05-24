# Build Your Own SSH

A simplified SSH system built from scratch using Python — no high-level SSH libraries, just raw sockets and cryptographic primitives.
The goal: make two programs communicate securely over a network, the same way real SSH does.

## The Problem We're Solving

When two computers talk over a network, anyone watching the network can read the messages, like passing notes in class where the teacher can read everything. This project builds a secure channel so only the two intended parties can read what's being sent.

## Phase 1 — Raw Sockets (Making Two Programs Talk)

### What we did
Wrote a `server.py` and a `client.py` that exchange messages over TCP. No security at all, just raw communication.

### How it works
- The **server** opens a "door" (port 9999) on the machine and waits
- The **client** knocks on that door and connects
- Once connected, they can send messages back and forth in a loop
- TCP handles making sure every message arrives correctly and in order

### The problem this reveals
When we opened Wireshark (a tool that watches network traffic), every message was visible in plain text. Anyone on the same network could read everything being said. This is the problem the next phases solve.
Client sends:  "hello"
Network sees:  "hello"   ← anyone can read this
Server sees:   "hello"

## Phase 2 — Symmetric Encryption (Adding a Secret Code)

### What we did
Before sending any message, we now **encrypt** it using AES-GCM. After receiving, we **decrypt** it. Both sides use the same secret key.

### How it works
- **AES** is the encryption algorithm — it scrambles data mathematically so it looks like random garbage without the key
- **GCM** mode adds a safety check — it also guarantees nobody tampered with the message in transit
- A fresh random **nonce** (a one-time number) is generated for every single message, so even if you send the same message twice it looks completely different on the network
- The nonce is sent along with the encrypted message so the receiver can decrypt it

### What actually travels over the network now
Client sends:  [random nonce] + [encrypted garbage]
Network sees:  "x9#kP!2@..."  ← unreadable
Server sees:   "hello"  (after decrypting)

Wireshark now shows pure gibberish instead of readable text.

### The problem this reveals
The secret key is hardcoded — it's the same fixed value written directly in the code on both sides. If anyone sees the source code, they can decrypt every message. The key needs to be generated dynamically, which is what Phase 3 solves.

## Phase 3 — RSA Key Exchange (Sharing the Secret Safely)

### What we did
Removed the hardcoded key. Instead, the two programs now **negotiate a fresh key every time they connect**, without ever sending the key in plain text.

### How it works
RSA gives you two mathematically linked keys — a **public key** and a **private key**.

- What the public key encrypts, only the private key can decrypt
- The public key can be shared with anyone safely — it's useless without the private key

The key exchange works like this:
1. Server generates an RSA keypair on startup

2. Server sends its public key to the client
   (this is fine — public key is meant to be shared)

3. Client generates a fresh random 32-byte session key

4. Client encrypts that session key using the server's public key
   and sends it over

5. Server decrypts it using its private key
   → Now both sides have the same session key

6. This session key is used for AES-GCM encryption (same as Phase 2)
   but now it was never hardcoded anywhere

### Why this is secure
Even if Dr. Ganguly intercepts step 4, he only sees encrypted bytes. Without the server's private key — which never left the server — he cannot decrypt the session key. And without the session key, he cannot read any messages.

### What Wireshark shows
Server → Client:  -----BEGIN PUBLIC KEY-----  (visible, intentional)
Client → Server:  [256 bytes of RSA-encrypted garbage]  (the session key, unreadable)
After that:       [AES-GCM encrypted messages]  (unreadable)

Each phase builds directly on the previous one. The socket code from Phase 1 never changed — we just wrapped it in more security each time.

## Tools Used
- **Python** — socket, os, json
- **cryptography** pip package — for AES-GCM and RSA primitives
- **Wireshark** — to inspect network traffic and verify encryption is working
