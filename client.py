import socket

HOST = '127.0.0.1'
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))
print(f"[CLIENT] Connected to {HOST}:{PORT}")

while True:
    
    message = input("[CLIENT] Enter message: ")
    client_socket.send(message.encode('utf-8'))
    
    if message.lower() == 'exit':
        print("[CLIENT] Exiting.")
        break
    
    response = client_socket.recv(1024)
    print(f"[CLIENT] Server replied: {response.decode('utf-8')}")

client_socket.close()
print("[CLIENT] Socket closed.")