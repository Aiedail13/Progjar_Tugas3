import socket
import sys
import threading
import os

def read_msg(sock_cli):
    while True:
        data = sock_cli.recv(65535)

        datasplit = data.split(b'|', 1)
        header = datasplit[0]
        msg = datasplit[1]
        # print(header)
        # print(msg)
        if len(data) == 0:
            break
        
        if header == b"file":
            msgsplit = msg.split(b'|', 3)
            msgprint = msgsplit[0].decode('utf-8')
            file_name = msgsplit[1].decode('utf-8')
            file_size  = int(msgsplit[2].decode('utf-8'))
            file_data = msgsplit[3]

            with open(file_name, "wb") as f:
                f.write(file_data)
                while (file_size - len(file_data) > 0):
                    data = sock_cli.recv(65535)
                    file_data += data
                    f.write(data)
                
            
            print("menerima file {}".format(file_name))
        elif header == b"txt":
            print("\n" + msg.decode('utf-8'))
            
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
    cmd = input("<command list>\nbcast -> broadcast pesan ke semua teman\nmsg -> kirim pesan private ke teman\nadd -> request untuk jadi teman\nacc -> terima permintaan teman\nfile -> kirim file ke teman\nexit -> tutup program\n>>> ")

    if cmd == "bcast":
        dest = "bcast"
        msg = input("masukan pesan : ")
    elif cmd == "msg":
        dest = input("masukan username tujuan : ")
        msg = input("masukan pesan: ")
    elif cmd == "add":
        dest = input("masukan username untuk request friend : ")
        msg = "request friend"
    elif cmd == "acc":
        dest = input("masukan username untuk accept friend : ")
        msg = "accept friend"
    elif cmd == "file":
        dest = input("masukan username tujuan : ")
        file_name = input("masukan nama file : ")
        msg = "mengirim file {}".format(file_name)
    elif cmd == "exit":
        sock_cli.close()
        break
    else:
        print("command not found")
        continue

    if cmd == "file":
        if not os.path.exists(file_name):
            print('File tidak ditemukan.')
            continue

        file_data = b''
        file_size = 0
        with open(file_name, "rb") as f:
            file_data = f.read()
            file_size += len(file_data)

        sock_cli.sendall(bytes("{}|{}|{}|{}|{}|".format(cmd, dest, msg, file_name, file_size), "utf-8") + file_data)
    else: 
        sock_cli.send(bytes("{}|{}|{}".format(cmd, dest, msg), "utf-8"))