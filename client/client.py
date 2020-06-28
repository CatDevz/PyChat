import socket, threading

HEADER_SIZE = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


class MsgType:
    CHAT,SYSTEM,DISCONNECT = range(3)


class Client:
    def __init__(self, msg_handlers=None, host=socket.gethostbyname(socket.gethostname()), port=5080):
        # Setting class scope variables
        if msg_handlers is None:
            msg_handlers = []
        self.host = str(host)
        self.port = int(port)
        self.addr = (self.host, self.port)
        self.msg_history = []
        self.msg_handlers = msg_handlers

        # Connecting to the server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.addr)
        self.connected = True

        # Creating a thread to handle incoming messages
        threading.Thread(target=self.__recv_data).start()


    def send(self, msg):
        msg = msg.encode(FORMAT)
        msg_len = len(msg)
        send_len = str(msg_len).encode(FORMAT)
        send_len += b' ' * (HEADER_SIZE - len(send_len))

        self.socket.send(send_len)
        self.socket.send(msg)


    def disconnect(self):
        self.send(DISCONNECT_MESSAGE)


    def get_msg_history(self):
        return self.msg_history


    def add_msg_handler(self, handler):
        self.msg_handlers.append(handler)


    def __recv_data(self):
        while self.connected:
            msg_len = self.socket.recv(HEADER_SIZE).decode(FORMAT)
            if msg_len:
                msg_len = int(msg_len)

                msg = self.socket.recv(msg_len).decode(FORMAT)

                if msg[0] == '2':
                    self.connected = False
                else:
                    for handler in self.msg_handlers:
                        try:
                            handler(int(msg[0]), msg[1:])
                        except Exception:
                            pass
                    if msg[0] == '0':
                        self.msg_history.insert(0, msg[1:])


if __name__ == '__main__':
    def print_msg(msg):
        print(msg)
    client = Client(print_msg, port=5082)