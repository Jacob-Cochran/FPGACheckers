import socket
import time

s = None


def setup_socket():
    global s
    s = socket.socket()
    hostname = socket.gethostname()
    port = 12345
    host = socket.gethostbyname(hostname)
    print(host)
    s.bind((host, port))


def sendAGrid(moveString):
    global s
    setup_socket()
    s.listen(5)
    while True:
        c, addr = s.accept()
        print("connected to", addr)
        break
    message = moveString
    c.send(message.encode())
    result = c.recv(10000).decode()
    c.close()
    return result



