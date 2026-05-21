import socket
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = b'\x1f\x8a\x3c\x7b\x2e\x9d\x4f\x0a\x6c\x5b\x8e\x1a\x3d\x7f\x2c\x9b\x4e\x0f\x6a\x5c\x8d\x1b\x3e\x7a\x2d\x9c\x4d\x0b\x6b\x5a\x8f\x1c'

aesgcm = AESGCM(KEY)

def encrypt(message: str) -> bytes:
    nonce = os.urandom(12)
    
    ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
    
    return nonce + ciphertext

def decrypt(data: bytes) -> str:
    nonce = data[:12]
    ciphertext = data[12:]
    
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')

HOST = '127.0.0.1'
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"[SERVER] Listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()
print(f"[SERVER] Connection from {addr}")

while True:
    data = conn.recv(4096)
    if not data:
        break

    message = decrypt(data)
    print(f"[SERVER] Decrypted message: {message}")

    if message.lower() == 'exit':
        print("[SERVER] Client requested exit. Closing.")
        break

    reply = f"Server got: '{message}'"
    conn.send(encrypt(reply))

conn.close()
server_socket.close()
print("[SERVER] Closed.")