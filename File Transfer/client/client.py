import socket
import os
import struct

def send_file(server_ip, server_port=8888, file_path=''):
    if not os.path.isfile(file_path):
        print(f"Fatal Error: {file_path} Doesn't Exist!")
        return
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print(f"Connect Successfully to  {server_ip}:{server_port}")
    except Exception as e:
        print(f"Connect Error: {str(e)}")
        return
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        client_socket.send(struct.pack('128s', str(len(file_name)).encode()))
        client_socket.send(file_name.encode())
        client_socket.send(struct.pack('Q', file_size))
        print(f"Sending File {file_name} | Size: {file_size} byte(s)")
        sent_size = 0
        with open(file_path, 'rb') as f:
            while sent_size < file_size:
                data = f.read(4096)
                client_socket.send(data)
                sent_size += len(data)
                progress = sent_size / file_size * 100
                print(f"\rProgress {progress:.2f}%", end='')

        print(f"\n Send File Successfully")

    except Exception as e:
        print(f"\nSend Error: {str(e)}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    ip = str(input("Server IP Here.\n> "))
    fp = str(input("File Path Here.\n> "))
    send_file(ip, 8888, fp)
    print("Press Any Key To Continue.", end="")
    os.system("pause 1>nul 2>nul")