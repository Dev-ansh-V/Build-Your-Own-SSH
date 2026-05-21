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

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"[CLIENT] Connected to {HOST}:{PORT}")

while True:
    message = input("[CLIENT] Enter message: ")
    
    client_socket.send(encrypt(message))

    if message.lower() == 'exit':
        break

    response = client_socket.recv(4096)
    print(f"[CLIENT] Server replied: {decrypt(response)}")

client_socket.close()