import socket
import threading #1 thread for each client

HOST = "0.0.0.0"
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = [] 
nicknames = []

def get_users():
    users_list = "USERS "
    for user in nicknames:
        users_list = users_list + " " + "<" + user + ">"
    return users_list

def broadcast(message, sender): #Dont broadcast to the sender
    for client in clients:
        if sender != client:
            client.sendall(message)

def broadcastone(message, sender):
    for client in clients:
        if sender == client:
            client.sendall(message)

def first_word(text): #used to extract command
    if text:
        return text.split()[0]     
    else: 
        return ""

def remove_before_first_space(text): #used to remove command from the message
    if text and " " in text:
        return text.split(maxsplit=1)[1]
    else:
        return ""

def find_client_by_nickname(name):
    if name in nicknames:
        return clients[nicknames.index(name)]
    return None

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        nicknames.remove(nickname)
        try:
            client.close()
        except:
            pass
        broadcast(f"<{nickname}> left the chat!\n".encode("utf-8"), None)
        print(f"Client <{nickname}> disconnected!")

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            decoded = message.decode("utf-8", errors="replace").strip()
            command = first_word(decoded)
            if command == "LIST":
                users = get_users().encode("utf-8")
                broadcastone(users, client)
            elif command == "MSG":
                index = clients.index(client)
                nickname = nicknames[index]
                decoded = remove_before_first_space(decoded)
                decoded = f"FROM <{nickname}> <{decoded}>"
                encoded = decoded.encode("utf-8")
                broadcast(encoded, client)
            elif command == "PM":
                parts = decoded.split(maxsplit=2)
                if len(parts) < 3:
                    broadcastone("Error BadFormat".encode("utf-8"), client)
                    continue
                target_user = parts[1]
                pm_text = parts[2]

                sender_index = clients.index(client)
                sender_name = nicknames[sender_index]

                target_client = find_client_by_nickname(target_user)

                if target_client is None:
                    broadcastone("Error NoSuchUser".encode("utf-8"), client)
                else:
                    out = f"PMFROM <{sender_name}> <{pm_text}>".encode("utf-8")
                    broadcastone(out, target_client)
            elif command == "QUIT":
                broadcastone(b"BYE\n", client)
                remove_client(client)
                break
            else:
                broadcastone('Error Unknown Command'.encode("utf-8"), client)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"<{nickname}> left the chat!".encode("utf-8"), None)
            print(f"Client <{nickname}> disconnected!")
            nicknames.remove(nickname)
            break
def main():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        client.sendall('NICK'.encode("utf-8"))
        nickname = client.recv(1024).decode("utf-8")
        while nickname in nicknames:
            client.sendall(f'{nickname} is already taken\nEnter your nickname:'.encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")         
        nicknames.append(nickname)
        clients.append(client)
        print(f'Nickname of the client is <{nickname}>!') 
        broadcast(f"WELCOME <{nickname}>".encode("utf-8"), None)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is ON")
main()