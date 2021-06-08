import socket
import sys
import threading


def read_cmd(clients, friend_list, sock_cli, addr_cli, username_cli):
    while True:
        data = sock_cli.recv(65535)

        print(data)
        # print("\n\n\n LOOOP BARUUUU \n\n\n")

        if len(data) == 0:
            break
        
        cmd, dest, msg = data.split(b"|", 2)
        cmd = cmd.decode('utf-8')
        dest = dest.decode('utf-8')

        if cmd == "bcast":
            msg = msg.decode('utf-8')
            msg = "<{}>: {}".format(username_cli, msg)
            send_broadcast(clients, friend_list, addr_cli, username_cli, msg)
        elif cmd == "msg":
            msg = msg.decode('utf-8')
            msg = "<{}>: {}".format(username_cli, msg)
            send_msg(clients, friend_list, dest, sock_cli, username_cli, msg)
        elif cmd == "add":
            msg = msg.decode('utf-8')
            msg = "<{}>: {}".format(username_cli, msg)
            add_friend(clients, friend_list, dest, sock_cli, username_cli)
        elif cmd == "acc":
            msg = msg.decode('utf-8')
            msg = "<{}>: {}".format(username_cli, msg)
            accept_friend(clients, friend_list, dest, sock_cli, username_cli)
        elif cmd == "file":
            filemsg = msg.split(b"|", 3)
            msg = filemsg[0].decode('utf-8')
            file_name = filemsg[1].decode('utf-8')
            file_size = int(filemsg[2].decode('utf-8'))
            file_data = filemsg[3]
    
            while (file_size - len(file_data) > 0):
                data = sock_cli.recv(65535)
                file_data += data

            send_file(clients, friend_list, dest, sock_cli, username_cli, msg, file_name, file_size, file_data)
        
    sock_cli.close()
    print("Connection closed", addr_cli)

def send_broadcast(clients, friend_list, sender_addr_cli, username_cli, msg):
   for key in list(clients.keys()):
        if not (sender_addr_cli[0] == clients[key][1][0] and sender_addr_cli[1] == clients[key][1][1]):
            if (key, username_cli) in friend_list and (username_cli, key) in friend_list:
                bcastmsg = "txt|{}".format(msg)
                clients[key][0].send(bytes(bcastmsg, "utf-8"))

def send_msg(clients, friend_list, dest, sender_sock, username_cli, msg):
    #check friend
    if (dest, username_cli) in friend_list and (username_cli, dest) in friend_list:
        sock_cli = clients[dest][0]
        msg = "txt|{}".format(msg)
        sock_cli.send(bytes(msg, "utf-8"))
    else:
        error_msg = "txt|Not friend with {}".format(dest)
        sender_sock.send(bytes(error_msg, "utf-8"))
    
def add_friend(clients, friend_list, dest, sender_sock, username_cli):
    if (username_cli, dest) in friend_list and (dest, username_cli) in friend_list:
        msg = "txt|already friend with {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    elif (username_cli, dest) in friend_list and (dest, username_cli) not in friend_list:
        msg = "txt|already request friend to {}, but still not accepted".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    elif (dest, username_cli) in friend_list and (username_cli, dest) not in friend_list:
        msg = "txt|{} already request to be friend with you, use accept_friend command to accept".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    else:
        friend_list.add((username_cli, dest))
        # send to sender
        msg = "txt|request sent"
        sender_sock.send(bytes(msg, "utf-8"))
        # send to receiver
        sock_cli = clients[dest][0]
        msg = "txt|{} send you a friend request".format(username_cli)
        sock_cli.send(bytes(msg, "utf-8"))
    
    #check friend list
    print(friend_list)

def accept_friend(clients, friend_list, dest, sender_sock, username_cli):
    if (username_cli, dest) in friend_list and (dest, username_cli) in friend_list:
        msg = "txt|already friend with {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    elif (dest, username_cli) in friend_list and (username_cli, dest) not in friend_list:
        friend_list.add((username_cli, dest))
        # send to sender
        msg = "txt|you are now friend with {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
        # send to receiver
        sock_cli = clients[dest][0]
        msg = "txt|{} accepted your friend request".format(username_cli)
        sock_cli.send(bytes(msg, "utf-8"))
    else:
        msg = "txt|you have no friend request from {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    
    # check friend list
    print(friend_list)

def send_file(clients, friend_list, dest, sender_sock, username_cli, msg, file_name, file_size, file_data):
    #check friend
    if (dest, username_cli) in friend_list and (username_cli, dest) in friend_list:
        sock_cli = clients[dest][0]
        sock_cli.sendall(bytes("file|{}|{}|{}|".format(msg, file_name, file_size), "utf-8") + file_data)
    else:
        error_msg = "txt|Not friend with {}".format(dest)
        sender_sock.send(bytes(error_msg, "utf-8"))

sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("0.0.0.0", 6666))
sock_server.listen(5)

clients = {}
friend_list = set()

while True:
    sock_cli, addr_cli = sock_server.accept()

    username_cli = sock_cli.recv(65535).decode("utf-8")
    print(username_cli, " joined")

    thread_cli = threading.Thread(target=read_cmd, args=(clients, friend_list, sock_cli, addr_cli, username_cli))
    thread_cli.start()

    clients[username_cli] = (sock_cli, addr_cli, thread_cli)