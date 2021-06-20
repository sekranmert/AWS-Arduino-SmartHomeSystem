import socket
import threading

helpMessage = '-q -- close connection\n-l -- list of connected devices\n-t -- server time \n-s "arduino/client ""reciever name" "message" -- send message (messages can be max 100 character) \nif reciever is an arduino board it can be controlled by this messsage:\n -s arduino "arduino name" led "0/1/status" \n'
print("connecting...\n for command list write '-h' \n"+helpMessage)
host = '127.0.0.1' # 127.0.0.1 for local
port = 9999 # 9999 for local

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))


def recvTh():
    while True:
        try:
            message = socket.recv(100).decode('ascii')
            if message == 't':
                socket.send("c".encode('ascii'))
            elif message == 'n':
                name = input("Enter your client name: ")
                socket.send(name.encode('ascii'))
            else:
                print(message+"\n")
        except ConnectionAbortedError:
            break
        except:
            print("connection error")
            socket.close()
            break

def sendTh():
    while True:
        message = input()
        if (len(message)<= 1024):
            tokens = message.split()
            if tokens[0] == '-h':
                print(helpMessage)
            elif tokens[0] == '-q':
                print("quiting")
                socket.send('-q'.encode('ascii'))
                socket.close()
                break
            else:
                socket.send(message.encode('ascii'))
        else:
            print("message must be under 1024 char")

recvThread = threading.Thread(target=recvTh)
sendThread = threading.Thread(target=sendTh)
recvThread.start()
sendThread.start()



