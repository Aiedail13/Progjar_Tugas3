import socket
import sys
import threading


def read_cmd(clients, friend_list, sock_cli, addr_cli, username_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
        
        cmd, dest, msg = data.decode("utf-8").split("|")
        msg = "<{}>: {}".format(username_cli, msg)

        if cmd == "bcast":
            send_broadcast(clients, friend_list, addr_cli, username_cli, msg)
        elif cmd == "msg":
            send_msg(clients, friend_list, dest, sock_cli, username_cli, msg)
        elif cmd == "add":
            add_friend(clients, friend_list, dest, sock_cli, username_cli)
        elif cmd == "acc":
            accept_friend(clients, friend_list, dest, sock_cli, username_cli)
        elif cmd == "file":
            send_file(clients, friend_list, dest, addr_cli, msg)
        print(data)
    
    sock_cli.close()
    print("Connection closed", addr_cli)

def send_broadcast(clients, friend_list, sender_addr_cli, username_cli, msg):
   for key in list(clients.keys()):
        if not (sender_addr_cli[0] == clients[key][1][0] and sender_addr_cli[1] == clients[key][1][1]):
            if (key, username_cli) in friend_list and (username_cli, key) in friend_list:
                clients[key][0].send(bytes(msg, "utf-8"))

def send_msg(clients, friend_list, dest, sender_sock, username_cli, msg):
    #check friend
    if (dest, username_cli) in friend_list and (username_cli, dest) in friend_list:
        sock_cli = clients[dest][0]
        sock_cli.send(bytes(msg, "utf-8"))
    else:
        error_msg = "Not friend with {}".format(dest)
        sender_sock.send(bytes(error_msg, "utf-8"))
    

def add_friend(clients, friend_list, dest, sender_sock, username_cli):
    if (username_cli, dest) in friend_list and (dest, username_cli) in friend_list:
        msg = "already friend with {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    elif (username_cli, dest) in friend_list and (dest, username_cli) not in friend_list:
        msg = "already request friend to {}, but still not accepted".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    elif (dest, username_cli) in friend_list and (username_cli, dest) not in friend_list:
        msg = "{} already request to be friend with you, use accept_friend command to accept".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    else:
        friend_list.add((username_cli, dest))
        # send to sender
        msg = "request sent"
        sender_sock.send(bytes(msg, "utf-8"))
        # send to receiver
        sock_cli = clients[dest][0]
        msg = "{} send you a friend request".format(username_cli)
        sock_cli.send(bytes(msg, "utf-8"))
    
    #check friend list
    print(friend_list)

def accept_friend(clients, friend_list, dest, sender_sock, username_cli):
    if (username_cli, dest) in friend_list and (dest, username_cli) in friend_list:
        msg = "already friend with {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    elif (dest, username_cli) in friend_list and (username_cli, dest) not in friend_list:
        friend_list.add((username_cli, dest))
        # send to sender
        msg = "you are now friend with {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
        # send to receiver
        sock_cli = clients[dest][0]
        msg = "{} accepted your friend request".format(username_cli)
        sock_cli.send(bytes(msg, "utf-8"))
    else:
        msg = "you have no friend request from {}".format(dest)
        sender_sock.send(bytes(msg, "utf-8"))
    
    # check friend list
    print(friend_list)


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