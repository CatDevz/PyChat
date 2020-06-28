import socket, threading, time

HEADER_SIZE = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


class MsgType:
    CHAT,SYSTEM,DISCONNECT = range(3)


class Server:
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=5080):
        # Setting class scope variables
        self.host = str(host)
        self.port = int(port)
        self.addr = (self.host, self.port)
        self.names = {}
        self.connections = []
        self.commands = {}

        # Setting some basic commands
        def help_command(conn):
            cmd_msg = "\"{}\" ".format(DISCONNECT_MESSAGE)
            for i in self.commands.keys():
                cmd_msg += "\"{}\" ".format(i)
            self.send(conn, "[SERVER] Currently advaible commands: {}".format(cmd_msg))
        def members_command(conn):
            self.send(conn, "[SERVER] Current members online: {}".format([self.names[i] for i in self.names]))
        self.register_command('!HELP', help_command)
        self.register_command('!MEMBERS', members_command)

        # Creating the socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)

        # Creating a thread for timeout checks
        threading.Thread(target=self.__give_user_count).start()

        # Creating a thread for listening to new connections
        threading.Thread(target=self.__new_connections).start()


    def send_all(self, msg):
        """Send a message to all users connected to the current server instance"""
        for usr in self.connections:
            try:
                self.send(usr, msg)
            except BrokenPipeError:
                self.connections.remove(usr)


    def send(self, conn, msg, msgtype=0):
        """Send a message to a specific user connected to the current server instance"""
        msg = (str(msgtype)+str(msg)).encode(FORMAT)   # 0=Chat Message, 1=System Message, 2=Disconnect
        msg_length = len(msg)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER_SIZE - len(send_length))

        conn.send(send_length)
        conn.send(msg)


    def register_command(self, command, command_listener):
        """Register a new command to the server."""
        self.commands[command] = command_listener


    def handle_client(self, conn, addr):
        """Handles data recieved from clients and sends data back to clients"""
        self.send(conn,"[SERVER] Welcome to the server! What would you like to be called?")
        while conn in self.connections:
            msg_length = conn.recv(HEADER_SIZE).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)

                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    self.send(conn, "[SERVER] Your connection has now been successfully closed.")
                    self.send(conn, "LOGOUT", msgtype=2)
                    self.connections.remove(conn)
                elif addr not in self.names:
                    self.names[addr] = msg
                    self.send(conn,"[SERVER] Your name has been successfully set to {}, you may now start chatting freely!".format(msg))
                elif msg in self.commands:
                    try:
                        self.commands[msg](conn)
                    except TypeError:
                        print("[ERROR] {} is not a function".format(self.commands[msg]))
                else:
                    self.send_all("[{}] {}".format(self.names[addr], msg))
                    print("[{}] {}".format(self.names[addr], msg))
        self.names[addr] = None
        print("[CLOSED CONNECTION] Connection to {} has been closed".format(addr))


    def __new_connections(self):
        # Accepting new connections from anywhere
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            self.connections.append(conn)
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()


    def __give_user_count(self):
        while True:
            for usr in self.connections:
                try:
                    self.send(usr,"USR_CNT:{}".format(len(self.connections)),msgtype=MsgType.SYSTEM)
                except BrokenPipeError:
                    self.connections.remove(usr)
            time.sleep(5)


if __name__ == '__main__':
    print("Starting server")
    serv = Server(port=6080)
