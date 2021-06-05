import socket
import sys
import threading

def read_msg(sock_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
            
        print(data)

# check input username
if len(sys.argv) != 2:
    sys.exit()

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_cli.connect(("127.0.0.1", 6666))
sock_cli.send(bytes(sys.argv[1], "utf-8"))

thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

while True:
    # input command
    cmd = input("masukan perintah(bcast untuk broadcast, add untuk add friend, send_file untuk send file, send)")

    if cmd == "bcast":
        dest = "bcast"
        msg = input("masukan pesan :")
    elif cmd == "msg":
        dest = input("masukan username tujuan :")
        msg = input("masukan pesan:")
    elif cmd == "add":
        dest = input("masukan username untuk request friend :")
        msg = "request friend"
    elif cmd == "acc":
        dest = input("masukan username untuk accept friend :")
        msg = "accept friend"
    elif cmd == "file":
        dest = input("masukan username tujuan :")
        nama_file = input("masukan nama file :")
        msg = "data file"
    else:
        print("command not found")
        continue
  

    if msg == "exit":
        sock_cli.close()
        break

    sock_cli.send(bytes("{}|{}|{}".format(cmd, dest, msg), "utf-8"))