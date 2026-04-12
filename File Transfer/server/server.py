import socket
import os
import struct

def receive_file(host='0.0.0.0', port=8888, save_dir='received_files'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print(f"Server Started, Listening {host}:{port}")
    print(f"File Save to {save_dir}")
    print("Waiting......")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"\nClient Connected: {addr}")

        try:
            file_name_len = struct.unpack('128s', client_socket.recv(128))[0].decode().strip('\x00')
            file_name = client_socket.recv(int(file_name_len)).decode()

            file_size = struct.unpack('Q', client_socket.recv(8))[0]
            print(f"Reciving Files{file_name} | Size: {file_size} bytes")

            save_path = os.path.join(save_dir, file_name)
            received_size = 0
            with open(save_path, 'wb') as f:
                while received_size < file_size:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    received_size += len(data)
                    progress = received_size / file_size * 100
                    print(f"\rProcess {progress:.2f}%", end='')

            print(f"\nSaved Compelete, Path: {save_path}")

        except Exception as e:
            print(f"\nRecived Error: {str(e)}")
        finally:
            client_socket.close()

if __name__ == '__main__':
    receive_file(port=8888, save_dir='Saved Files')