import socket
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_rsa_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    return private_key

def get_public_key_pem(private_key):
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def rsa_decrypt(private_key, ciphertext):
    return private_key.decrypt(
        ciphertext,
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

print("[SERVER] Generating RSA-2048 keypair...")
private_key = generate_rsa_keypair()
public_key_pem = get_public_key_pem(private_key)
print(f"[SERVER] Keypair ready. Public key is {len(public_key_pem)} bytes.")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"[SERVER] Listening on {HOST}:{PORT}...")

conn, addr = server_socket.accept()
print(f"[SERVER] Connection from {addr}")

key_length = len(public_key_pem)
conn.send(key_length.to_bytes(4, 'big'))  # 4 bytes = the length
conn.send(public_key_pem)                  # the actual key
print(f"[SERVER] Sent public key ({key_length} bytes)")

encrypted_session_key = conn.recv(256)
session_key = rsa_decrypt(private_key, encrypted_session_key)
print(f"[SERVER] Session key received and decrypted: {session_key.hex()}")

aesgcm = AESGCM(session_key)
print("[SERVER] Secure channel established!")

while True:
    data = conn.recv(4096)
    if not data:
        break

    message = decrypt(aesgcm, data)
    print(f"[SERVER] Decrypted: {message}")

    if message.lower() == 'exit':
        break

    reply = f"Server got: '{message}'"
    conn.send(encrypt(aesgcm, reply))

conn.close()
server_socket.close()
print("[SERVER] Closed.")