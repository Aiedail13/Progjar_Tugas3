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
   

def send_msg(clients, friend_list, dest, sender_sock, username_cli, msg):
    
    

def add_friend(clients, friend_list, dest, sender_sock, username_cli):
    

def accept_friend(clients, friend_list, dest, sender_sock, username_cli):
    


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