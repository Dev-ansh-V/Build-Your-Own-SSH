import socket

# Configuration
HOST = '127.0.0.1'   
PORT = 9999        

# creating the socket (AF_INET- specifies the IP family-IPv4)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# for preventing "address already in use" error - reuseaddr->allows reusing address
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# attach socket to our address and port
server_socket.bind((HOST, PORT))
# listen
server_socket.listen(1)

print(f"[SERVER] Listening on {HOST}:{PORT}...")

#waits for client connection (blocks till connects)
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