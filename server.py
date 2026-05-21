import socket

# Configuration
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
    data = conn.recv(1024)
    
    if not data:
        break
    
    message = data.decode('utf-8')
    print(f"[SERVER] Received: {message}")
    
    if message.lower() == 'exit':
        print("[SERVER] Client requested exit. Closing.")
        break
    
    reply = f"Server got your message: '{message}'"
    conn.send(reply.encode('utf-8'))

conn.close()
server_socket.close()
print("[SERVER] Connection closed.")