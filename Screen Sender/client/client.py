import socket
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import os
import sys

# 配置：改成服务端IP
SERVER_PORT = 65432
BUFFER_SIZE = 65536

class ScreenClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Viewer")
        self.screen_label = QLabel()
        self.screen_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.screen_label)

        self.sock = None
        self.connect_server()

        # 持续接收画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

    def connect_server(self):
        """连接服务端"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_IP, SERVER_PORT))
            print("Connect To Server Successfully")
        except Exception as e:
            print(f"Connect Error: {e}")
            self.sock = None

    def recv_fixed(self, size):
        data = b""
        while len(data) < size:
            packet = self.sock.recv(min(BUFFER_SIZE, size - len(data)))
            if not packet:
                return None
            data += packet
        return data

    def update_frame(self):
        if not self.sock:
            return

        try:
            # 读取帧长度
            len_header = self.recv_fixed(8)
            if not len_header:
                self.close()
                return

            data_len = int(len_header.decode().strip())
            data = self.recv_fixed(data_len)

            # 解码显示
            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.screen_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.screen_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

        except:
            print("Disconnected.")
            self.sock = None

    def closeEvent(self, event):
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    SERVER_IP = str(input("Server IP:> "))
    app = QApplication(sys.argv)
    window = ScreenClient()
    window.resize(1280, 720)
    window.show()
    ret = app.exec_()
    os.system("pause")
    sys.exit(ret)