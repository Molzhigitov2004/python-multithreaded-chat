import socket
import threading

SERVER_IP = "127.0.0.1"
PORT = 5001

nickname = input("Enter your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
stop = threading.Event() #This is basically a shared flag threads use to see if they need to terminate

def receiver():
    while not stop.is_set():
        try:
            data = client.recv(1024)
            if not data:
                print("Disconnected from the server")
                stop.set()
                break

            message = data.decode("utf-8", errors="replace").strip()

            if message == "BYE":
                print("BYE")
                stop.set()
                break
            elif message == "NICK": #Initial query for a nickname
                client.sendall(nickname.encode("utf-8"))
            else:
                print(message)
        except:
            print("Disconnected from the server")
            stop.set()
            break

    try:
        client.close()
    except:
        pass

def write():
    while not stop.is_set():
        try:
            message = input()
            if message.strip() == "QUIT":
                client.sendall(message.encode("utf-8"))
                continue
            client.sendall(message.encode("utf-8"))
        except:
            stop.set()
            break

#I declared those threads daemon so that user can get back into terminal after exit and those threads will shutdown independently
receive_thread = threading.Thread(target=receiver, args=(), daemon=True)
write_thread = threading.Thread(target=write, args=(), daemon=True)
receive_thread.start()
write_thread.start()

stop.wait()
