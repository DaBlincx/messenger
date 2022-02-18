from faulthandler import disable
import os
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname
from threading import Thread
import time
from tkinter import Tk, END, Frame, Text, Scrollbar, Label, Entry, Button, VERTICAL, messagebox
import host_config

host_ip = host_config.host_ip
host_port = host_config.host_port

wwidth = 120
whight = 30

class ChatBox:
    user_socket = None
    latest_msg = None

    def msgTimestamp(objdd):
        tm = str(time.localtime())
        tmlist = tm.replace("time.struct_time(tm_","").replace(")","").split(", tm_")
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
        
        msg_timestamp = "<"+year+"."+month+"."+day+" | "+hour+":"+min+":"+sec+"> " #<
        return msg_timestamp

    def __init__(self, master):
        self.core = master
        self.transcript_box = None
        self.name_box = None
        self.text_box = None
        self.join_button = None
        self.socket_init()
        self.chatbox_init()
        self.message_listener()

    def socket_init(self):
        self.user_socket = socket(AF_INET, SOCK_STREAM)
        self.user_socket.connect((gethostbyname(host_ip), host_port))

    def chatbox_init(self):
        self.core.title("Socket Chat")
        self.core.resizable(0,0)
        self.chat_box()
        self.display_name_section()
        self.chat_area()

    def message_listener(self):
        Thread(target=self.msg_from_server, args=([self.user_socket])).start()

    def msg_from_server(self, so):
        while True:
            size = so.recv(256)
            if not size:
                break
            message = size.decode('utf-8')
            self.transcript_box.insert('end', message + '\n')
            if len(message) == 41:
                if message.endswith(" HostClient: /stop"):
                    print("Stopping server")
                    os._exit(0)
            self.transcript_box.yview(END)

        so.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text=' Name:', font=("Times", 16)).pack(side='left', padx=10)
        self.name_box = Entry(frame, width=round(120*1.06), borderwidth=2)
        self.name_box.pack(side='left', anchor='e')
        self.name_box.insert(0,"HostClient")
        self.name_box.config(state='disabled')
        self.join_button = Button(frame, text="Join", width=10, command=print("HostClient logged in successfully."), state='disabled').pack(side='left')
        frame.pack(side='top', anchor='nw')
        self.join_response

    def chat_box(self):
        frame = Frame()
        Label(frame, text='Live Transcript', font=("Times", 12)).pack(side='top', anchor='w')
        self.transcript_box = Text(frame, width=round(120*0.93), height=round(30*0.93), font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.transcript_box.yview, orient=VERTICAL)
        self.transcript_box.config(yscrollcommand=scrollbar.set)
        self.transcript_box.bind('<KeyPress>', lambda e: 'random')
        self.transcript_box.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def chat_area(self):
        frame = Frame()
        Label(frame, text='Message:', font=("Times", 12)).pack(side='left', anchor='w')
        self.text_box = Text(frame, width=round(120*0.87), height=1, font=("Serif", 12))
        self.text_box.pack(side='left', pady=15)
        self.text_box.bind('<Return>', self.enter_response)
        frame.pack(side='top')

    def join_response(self):
        if len(self.name_box.get()) == 0:
            messagebox.showerror(
                "Enter your name!", "Enter your name to join messenger!")
            return
        self.name_box.config(state='disabled')
        self.user_socket.send((self.name_box.get() + " has entered the chat.").encode('utf-8'))

    def enter_response(self, event):
        if len(self.name_box.get()) == 0:
            messagebox.showerror(
                "Enter your name!", "Enter your name to send a message!")
            return
        self.send_chat()
        self.remove_text()

    def remove_text(self):
        self.text_box.delete(1.0, 'end')

    def send_chat(self):
        msgTmst = self.msgTimestamp()
        sender = self.name_box.get().strip() + ": "
        data = self.text_box.get(1.0, 'end').strip()
        if data == "":
            messagebox.showerror("Empty message!","Please don not send empty messages!")
            return
        message = (msgTmst + sender + data).encode('utf-8')
        self.transcript_box.insert('end', message.decode('utf-8') + '\n')
        self.transcript_box.yview(END)
        self.user_socket.send(message)
        self.remove_text()
        if data == "/stop":
            self.close_response()
        if data == "/bbb":
            self.text_box.insert("HIII")
        return 'random'

    def close_response(self):
        
        try:
            self.user_socket.send((self.name_box.get() + " has left the chat.").encode('utf-8'))
        except ConnectionResetError:
            print('\nServer closed.\n')
        self.core.destroy()
        self.user_socket.close()
        os._exit(0)


if __name__ == '__main__':
    time.sleep(2)
    trigger = Tk()
    try:
        chat_win = ChatBox(trigger)
        trigger.protocol("WM_DELETE_WINDOW", disable())
        trigger.mainloop()
        
    except ConnectionRefusedError:
        os.system("start python server.py")
    
