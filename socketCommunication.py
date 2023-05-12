import socket


def attempt_connection():
    s = socket.socket()
    host = '192.168.2.255'
    port = 12340
    s.connect((host, port))
    return s


def sendAGrid(moveString):
    s = socket.socket()
    host = '172.28.30.6'
    port = 12345
    print(host, port)
    s.connect((host, port))

    s.send(moveString.encode())
    result = s.recv(10000).decode("UTF-8")
    s.close()
    return result



