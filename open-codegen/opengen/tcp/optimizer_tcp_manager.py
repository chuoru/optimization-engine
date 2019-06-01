import yaml
import os
import subprocess
import socket
from threading import Thread
from retry import retry
import time


class OptimizerTcpManager:

    def __init__(self, optimizer_path):
        self.__optimizer_path = optimizer_path
        self.__tcp_details = None

    def __load_tcp_details(self):
        yaml_file = os.path.join(self.__optimizer_path, "optimizer.yml")
        with open(yaml_file, 'r') as stream:
            self.__tcp_details = yaml.safe_load(stream)

    def __threaded_start(self):
        command = ['cargo', 'run']
        p = subprocess.Popen(command, cwd=self.__optimizer_path)
        p.wait()

    @retry(tries=10, delay=1)
    def __obtain_socket_connection(self):
        print("connecting...")
        tcp_data = self.__tcp_details
        ip = tcp_data['tcp']['ip']
        port = tcp_data['tcp']['port']
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        print("CONNECTED :-)")
        return s

    def __ping(self, s):
        ping_message = b'{"Ping" : 1}'
        s.sendall(ping_message)
        data = s.recv(256)  # 256 is more than enough
        return data.decode()

    def ping(self):
        with self.__obtain_socket_connection() as s:
            data = self.__ping(s)
        return data

    def start(self):
        self.__load_tcp_details()
        thread = Thread(target=self.__threaded_start)

        # start the server
        thread.start()

        # ping the server until it responds so that we know it's
        # up and running
        pong = self.ping()
        print(pong)

    def call(self, p):
        em = b'{"Run" : {"parameter", [1.0, 2.0]}}'

        # ---- WIP
