import socket
import threading
import datetime

#Server info
host = '127.0.0.1'# 127.0.0.1 for local
port = 9999# 9999 for local

#connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

#Socket list
clients = []
arduinos = []

#Socket class
class socketObj:
    def __init__(self, name, client, address):
        self.name = name
        self.client = client
        self.address = address


#message function
def sendClient(nick,message):
    for c in clients:
        if nick == c.name:
            c.client.send(message.encode('ascii'))


def sendArduino(sender,senderName, nick,message):
    token =  message.split()
    print("Client "+senderName+" requested to set led: "+ str(token[1])+"\n")
    if token[1] == '0':
        sendMess = str('a')
    elif token[1] == '1':
        sendMess = str('b')
    elif token[1] == "status":
        sendMess = str('c')
    for a in arduinos:
        if nick == a.name:
            a.client.send(sendMess.encode('ascii'))
    val = a.client.recv(1024)
    broadcastStr = "Led set "+ str(val)+"\n"
    print("Led set "+ str(val)+"\n")
    broadcastMessage(broadcastStr)

def broadcastMessage(message):
    print("("+message+") has been broadcasted\n")
    for c in clients:
            c.client.send(message.encode('ascii'))


def getTime():
    timeStr = datetime.datetime.now()
    timeStr += datetime.timedelta(hours=7)
    timeStr = datetime.datetime.strftime(timeStr, '%X')
    timeStr = str(timeStr)
    return timeStr


def eraseClient(client):
    for c in clients:
        if client == c.client:
            i = clients.index(c)
            clients.pop(i)
            client.close()


def recieveMessage(client,name):
    while True:
        try:
            message = client.recv(1024).decode('cp857')
            messageTokens = message.split()

            if messageTokens[0] == '-s':
                if messageTokens[1] == 'client':
                    clientCheck = False
                    for c in clients:
                        if messageTokens[2] == c.name:
                            clientCheck = True

                    if clientCheck == True:
                        index = message.find(messageTokens[2]) + len(messageTokens[2]) + 1
                        newMessage = name + ' says: ' + message[index:] + '.'
                        sendClient(messageTokens[2], newMessage)
                        client.send('Message has been sent\n'.encode('ascii'))
                    else:
                        client.send('Client not found\n'.encode('ascii'))
                elif messageTokens[1] == 'arduino':
                    clientCheck = False
                    for a in arduinos:
                        if messageTokens[2] == a.name:
                            clientCheck = True

                    if clientCheck == True:
                        index = message.find(messageTokens[2]) + len(messageTokens[2]) + 1
                        newMessage = 'client ' + name + ' has sent : ' + message[index:] + ' order to arduino '+ messageTokens[2]+"\n"
                        broadcastMessage(newMessage)
                        newMessage = message[index:]
                        sendArduino(client,name,messageTokens[2], newMessage)
                    else:
                        client.send('Client not found\n'.encode('ascii'))
            elif messageTokens[0] == '-t':
                client.send(getTime().encode('ascii'))

            elif messageTokens[0] == '-l':
                listStr = ''
                listStr += 'clients: \n'
                i=1
                for c in clients:
                    listStr += str(i) + '. ' + c.name + '\n'
                    i += 1
                listStr += 'arduinos: \n'
                i=1
                for a in arduinos:
                    listStr += str(i) + '. ' + a.name + '\n'
                    i += 1

                client.send(listStr.encode('ascii'))

            elif messageTokens[0] == '-q':
                eraseClient(client)
                print("client left "+name+"\n")
                break

            else:
                client.send('command not found\n'.encode('ascii'))

        except:
            eraseClient(client)
            print("client "+name+" left\n")
            break

print("Server started\n")
#a loop to accept clients and start threads
while True:
    client, address = server.accept()

    client.send('t'.encode('ascii'))
    type = client.recv(1024).decode('ascii')

    client.send('n'.encode('ascii'))
    name = client.recv(1024).decode('ascii')

    if type == 'c':
        clients.append(socketObj(name, client, address)) #save socket on the list
        thread = threading.Thread(target=recieveMessage, args=(client,name))
        thread.start()
        print("a new client " + name +" has joined\n")

    elif type == 'a':
        arduinos.append(socketObj(name, client, address))
        print("a new arduino " + name + " has joined\n")




