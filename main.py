import socket 
from EventLoop import EventLoop

eventloop = EventLoop()

client, server = socket.socketpair()

def on_data(sock):
    data = sock.recv(1024)

    print("Received:", data.decode())

    eventloop.unregister_socket(sock)
    eventloop.stop()

eventloop.register_socket(server, on_data)

eventloop.call_later(
    2, 
    lambda: client.send(b"Bounce!")
)

print("Event Loop starting!")

eventloop.run()

client.close()
server.close()

print("Event Loop stopped!")