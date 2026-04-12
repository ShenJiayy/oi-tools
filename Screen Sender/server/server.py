import socket
import threading
import mss
import numpy as np
import cv2
import time

# 配置
HOST = '0.0.0.0'
PORT = 65432
QUALITY = 70
FPS = 30

class ScreenServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)
        self.running = True
        self.client_socket = None
        print(f"Screen Sender Server Started, Port as {PORT}.\nWaiting for connection......")

    def handle_client(self, client_socket):
        """专门给一个客户端持续发送画面"""
        self.client_socket = client_socket
        sct = mss.mss()
        monitor = sct.monitors[1]
        interval = 1.0 / FPS

        while self.running:
            try:
                # 捕获屏幕
                img = sct.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                # 压缩
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY]
                _, img_encoded = cv2.imencode('.jpg', frame, encode_param)
                data = img_encoded.tobytes()

                # 发送
                client_socket.sendall(f"{len(data):<8}".encode())
                client_socket.sendall(data)

                # 帧率控制
                elapsed = time.time() - time.time()
                if elapsed < interval:
                    time.sleep(interval - elapsed)

            except:
                # 客户端断开，自动清理并退出线程
                print("Client Closed, Waiting For The Next Connection...")
                break

        # 安全关闭
        try:
            client_socket.close()
        except:
            pass
        self.client_socket = None

    def accept_connections(self):
        """持续等待新客户端连接"""
        while self.running:
            try:
                client, addr = self.server_socket.accept()
                print(f"New Client Connected: {addr}")

                # 已有连接则踢掉旧的
                if self.client_socket:
                    try:
                        self.client_socket.close()
                    except:
                        pass

                # 启动线程发送画面
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

            except:
                break

    def run(self):
        threading.Thread(target=self.accept_connections, daemon=True).start()
        while self.running:
            time.sleep(1)

if __name__ == "__main__":
    server = ScreenServer()
    server.run()