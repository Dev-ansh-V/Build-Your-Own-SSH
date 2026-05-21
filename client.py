import socket
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def load_public_key(pem_data):
    return serialization.load_pem_public_key(pem_data)

def rsa_encrypt(public_key, data):
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def encrypt(aesgcm, message: str) -> bytes:
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
    return nonce + ciphertext

def decrypt(aesgcm, data: bytes) -> str:
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')

HOST = '127.0.0.1'
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"[CLIENT] Connected to {HOST}:{PORT}")

key_length_bytes = client_socket.recv(4)
key_length = int.from_bytes(key_length_bytes, 'big')

public_key_pem = client_socket.recv(key_length)
public_key = load_public_key(public_key_pem)
print(f"[CLIENT] Received server's public key ({key_length} bytes)")

session_key = os.urandom(32)
print(f"[CLIENT] Generated session key: {session_key.hex()}")

encrypted_session_key = rsa_encrypt(public_key, session_key)
client_socket.send(encrypted_session_key)
print(f"[CLIENT] Sent encrypted session key ({len(encrypted_session_key)} bytes)")

aesgcm = AESGCM(session_key)
print("[CLIENT]  Secure channel established!")

while True:
    message = input("[CLIENT] Enter message: ")
    client_socket.send(encrypt(aesgcm, message))

    if message.lower() == 'exit':
        break

    response = client_socket.recv(4096)
    print(f"[CLIENT] Server replied: {decrypt(aesgcm, response)}")

client_socket.close()