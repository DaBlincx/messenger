from os import system
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gethostbyname
from sys import exit
from threading import Thread
import time
import host_config
from tkinter import messagebox

host_ip = host_config.host_ip
host_port = host_config.host_port

class ChatServer:
    audience_list = []
    latest_msg = ""

    def msgTimestamp(objdd):
        tm = str(time.localtime())
        tmlist = tm.replace("time.struct_time(tm_","").replace(")","").split(", tm_")
        ##print(tmlist)
        for det in tmlist:
            if det.startswith("year="):
                year  = str(det.replace("year=",""))
            elif det.startswith("mon="):
                month = str(det.replace("mon=",""))
                if len(month) == 1:
                    month = "0"+month
            elif det.startswith("mday="):
                day   = str(det.replace("mday=",""))
                if len(day) == 1:
                    day = "0"+day
            elif det.startswith("hour="):
                hour  = str(det.replace("hour=",""))
                if len(hour) == 1:
                    hour = "0"+hour
            elif det.startswith("min="):
                min   = str(det.replace("min=",""))
                if len(min) == 1:
                    min = "0"+min
            elif det.startswith("sec="):
                sec   = str(det.replace("sec=",""))
                if len(sec) == 1:
                    sec = "0"+sec
            else:
                pass
            ##print(det)
        
        msg_timestamp = "<"+year+"."+month+"."+day+" | "+hour+":"+min+":"+sec+"> "
        return msg_timestamp

    def __init__(self):
        self.socket_fd = None
        self.listener()

    def listener(self):
        self.socket_fd = socket(AF_INET, SOCK_STREAM)
        self.socket_fd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket_fd.bind((gethostbyname(host_ip), host_port))
        print(f"Listener on {host_ip}:{str(host_port)} activated. Awaiting connections..")
        self.socket_fd.listen(5)
        self.threaded_message()

    def receiver_list(self, client):
        if client not in self.audience_list:
            self.audience_list.append(client)

    def receive_messages(self, so):
        while True:
            try:
                message_buff = so.recv(256)
                # empty messages will not be delivered to the receiver
                msg_checker = (message_buff.decode("utf-8")).split(':')[-1]
                if not message_buff or len(msg_checker) < 2:
                    break
                self.latest_msg = message_buff.decode('utf-8')
                self.show_to_audience(so)  # send to all clients
            except OSError as os_error:
                if str(os_error) == '[Errno 9] Bad file descriptor':
                    print(f"Origin: {':'.join(str(raddr) for raddr in so.getsockname())} "
                          f"has been attempted to access from an unsupported gateway. "
                          f"Socket: {':'.join(str(raddr) for raddr in so.getpeername())}")
        so.close()

    def show_to_audience(self, senders_socket):
        for client in self.audience_list:
            so, _ = client
            if so is not senders_socket:
                printmsg = self.latest_msg.encode('utf-8')
                so.sendall(printmsg)
                print(str(printmsg)[2:-1])

    def threaded_message(self):
        while True:
            client = so, (ip, port) = self.socket_fd.accept()
            self.receiver_list(client)
            print(f'\nConnection accepted from {ip}:{port}')
            Thread(target=self.receive_messages, args=([so])).start()


if __name__ == "__main__":
    ChatServer()
