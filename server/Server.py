import socket 
import time
from pynq import Overlay

s = None
# TODO: Change this to be correct filepath
overlay = Overlay('/home/xilinx/jupyter_notebooks/Checkers Project/Checkers7.bit')
addIP = overlay.checkersHLS_0
pad = [ 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 1, 0, 1, 0, 1, 0, 1,
        1, 0, 1, 0, 1, 0, 1, 0,
        0, 1, 0, 1, 0, 1, 0, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        2, 0, 2, 0, 2, 0, 2, 0,
        0, 2, 0, 2, 0, 2, 0, 2,
        2, 0, 2, 0, 2, 0, 2, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,]
startTime = 0
    
def sendBoard(startLocation, endLocation):
    #write parameters for gameOver check
    #print("1")
    startTime = time.process_time()
    for i in range(64):
        addIP.write(0x94+i*8, pad[i+24])

    #write parameters for validation check
    addIP.write(0x3c, startLocation)
    addIP.write(0x44, endLocation)
    addIP.write(0x4c, pad[startLocation+24])
    addIP.write(0x54, pad[startLocation+7+24])
    addIP.write(0x5c, pad[startLocation+9+24])
    addIP.write(0x64, pad[startLocation+14+24])
    addIP.write(0x6c, pad[startLocation+18+24])
    addIP.write(0x74, pad[startLocation-7+24])
    addIP.write(0x7c, pad[startLocation-9+24])
    addIP.write(0x84, pad[startLocation-14+24])
    addIP.write(0x8c, pad[startLocation-18+24])
    #enable hardware
    addIP.write(0x00, 1)
    
def updateBoard(startLocation):
    conditionCode = addIP.read(0x10)  # Read game state code

    #get updated board values
    pad[startLocation+24] = addIP.read(0x14) #current piece
    pad[startLocation+7+24] = addIP.read(0x18) #current piece + 7
    pad[startLocation+9+24] = addIP.read(0x1c) #current piece +9
    pad[startLocation+14+24] = addIP.read(0x20) #current piece +14
    pad[startLocation+18+24] = addIP.read(0x24) #current piece + 18
    pad[startLocation-7+24] = addIP.read(0x28) #current piece -7
    pad[startLocation-9+24] = addIP.read(0x2c) #current piece -9
    pad[startLocation-14+24] = addIP.read(0x30) #current piece -14
    pad[startLocation-18+24] = addIP.read(0x34) #current piece -18
    #print("2")
    print("ELAPSED TIME:", (time.process_time())-startTime)
    return conditionCode

def useInput(inputString):
    startTime = 0
    #print("4")
    inputSet = inputString.split("\n")
    #print(inputSet)
    startLocation = int(inputSet[0])
    #print(startLocation)
    endLocation = int(inputSet[1])
    #print(endLocation)
    gridList = inputSet[2]
    #print(gridList)
    gridList = gridList.split(",")
    #print(gridList)
    gridList = [int(i) for i in gridList]
    pad[24:87] = gridList
    sendBoard(startLocation, endLocation)
    conditionCode = updateBoard(startLocation)
    retString = str(conditionCode) + "\n"
    #print("3")
    for i in range(64):
        retString += str(pad[i + 24]) + ","
    return retString[0:-1]
    


def setup_socket():
    global s
    s = socket.socket()
    port = 12345
    host = '172.28.30.6'
    #'192.168.2.255'
    #'192.168.2.99'
    #'172.28.30.6'

    print(host, port)
    s.bind((host, port))
    
    
def runCheckersServer():
    global s
    setup_socket()
    s.listen(5)
    while True:
        print("Hosting")
        c, addr = s.accept()
        print("connected to", addr)
        receivedPacket = c.recv(10000).decode()
        print("Recieved, ", receivedPacket)
        outstring = useInput(receivedPacket)
        c.send(outstring.encode())
        c.close()

        
runCheckersServer()
            
         