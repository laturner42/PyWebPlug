# This file runs the websockets.

import string, cgi, time

from wsserver import *

from time import sleep

def setupMessages():
    return


class Client:

    def __init__(self, socket):
        self.socket = socket
        self.needsConfirmation = True
    
    def handle(self):
        data = self.socket.readRaw()
        if len(data) > 0:
            print(data)
        if self.needsConfirmation:
            code = data[0:4]
            if code == "0000":
                self.becomeHost()
            else:
                self.host = findHost(code)
                if self.host:
                    confirm(self)
        else:
            if self.host.socket:
                self.host.socket.send(self.sID + data)
            else:
                print("Host's socket is closed.")

    # This is called to confirm to the client that they have been accepted,
    # after they send us their details.
    def confirm(self):
        self.pID = self.host.getNextpID()
        self.host.players[self.pID] = self
        needsConfirmation = False
        self.socket.send("999")
        self.sID = extend(self.pID, 2)
        self.host.send("998" + self.sID)

    def becomeHost(self):
        host = Host(self.socket, newHostCode())
        clients.remove(self)
        hosts.add(host)

    def disconnect(self):
        print("Lost client.")
        clients.remove(self)
        self.socket = None
        return

class Host:
    
    def __init__(self, socket, hostCode):
        self.socket = socket
        self.hostCode = hostCode
        self.players = {}
        self.pID = 0
        self.socket.send("999" + str(self.hostCode))

    def getNextpID(self):
        self.pID += 1
        return self.pID

    def handle(self):
        data = self.socket.readRaw()
        pID = int(data[0:2])
        if players[pID]:
            if players[pID].socket:
                players[pID].send(data[2:])
            else:
                print("Client's socket is closed.")
        else:
            print("Host", self.hostCode," tried to send a messaged to non-existant player", pID)
        
    def disconnect(self):
        print("Lost host.")
        hosts.remove(self)
        self.socket = None
        return

def findHost(code):
    for host in hosts:
        if host.hostCode == code:
            return host
    return None

def newHostCode():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code = ''.join(chars[int(random.random()*26)] for _ in range(4))
    if findHost(code):
        return newHostCode()
    return code

def extend(v, l):
    out = str(v)
    while len(out) < l:
        out = "0" + out
    return out

# This handles a new client.
# We need to hand them to an object
# so that we can read and write from it
def handle(socket):
    global clients
    client = Client(socket)
    clients.append(client)

def main():
    global gameStarted
    global stage
    try:
        setupMessages()
        server = startServer()
        while True:
            newClient = handleNetwork()
            if newClient:
                handle(newClient)
            for client in clients:
                client.handle()
            for host in hosts:
                host.handle()
            sleep(0.001)
    except KeyboardInterrupt:
        print(' received, closing server.')
        server.close()
    
clients = []
hosts = []
pID = 0

if __name__ == '__main__':
    main()
