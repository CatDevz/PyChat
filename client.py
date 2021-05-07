# pylint: disable=no-member
from commons import TermColors, decode, encode
from dataclasses import dataclass, field
import curses
import threading
import socket
import time


@dataclass
class Client():
    # Connection related data
    socket: any
    server_port: int
    server_ip: str

    # Client's self related data
    message_buffer: str = ""

    # Data related to the room & other clients
    message_history: list = field(default_factory=lambda: [])


class Interface():
    def __init__(self, client):
        self.client = client
        self.inputHandlers = []

    def start(self):
        # Initilize ncurses
        self.stdscr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        self.stdscr.keypad(1)

        if curses.has_colors():
            curses.start_color()

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

        # Fill static lines
        self.stdscr.addstr(" PyChat V1.0 ", curses.A_BOLD | curses.A_REVERSE)
        self.stdscr.chgat(-1, curses.A_REVERSE)

        self.stdscr.addstr(curses.LINES-1, 0, "F1 Quit - F2 Change Identity - F5 Online Clients")

        self.stdscr.chgat(curses.LINES-1, 0, 2, curses.A_BOLD | curses.color_pair(1))
        self.stdscr.chgat(curses.LINES-1, 10, 2, curses.A_BOLD | curses.color_pair(2))
        self.stdscr.chgat(curses.LINES-1, 31, 2, curses.A_BOLD | curses.color_pair(3))

        # Creating main window
        self.chat_win = curses.newwin(curses.LINES-2, curses.COLS, 1, 0)

        # Creating & styling sub windows
        self.chat_stream_win = self.chat_win.subwin(curses.LINES-6, curses.COLS-4, 2, 2)
        self.chat_input_win = self.chat_win.subwin(1, curses.COLS-4, curses.LINES-3, 2)

    def refresh(self):
        # Clearing the main window
        self.chat_win.clear()

        # Styling main window & sub windows
        self.chat_win.box()
        self.chat_input_win.chgat(-1, curses.A_REVERSE)

        self.chat_win.addstr(curses.LINES-4, 2, " SEND: ", curses.A_BOLD | curses.A_REVERSE)
        self.chat_win.addstr(curses.LINES-4, 9, self.client.message_buffer, curses.A_REVERSE)

        for i, message in enumerate(self.client.message_history):
            self.chat_win.addstr(1+i, 2, "{}: {}".format(message["author"], message["body"]))

        # Refresh the windows & screen
        self.stdscr.noutrefresh()
        self.chat_win.noutrefresh()

        # Render it all
        curses.doupdate()

    def caputureKey(self):
        c = self.stdscr.getch()
        for handler in self.inputHandlers:
            handler(c)

    def kill(self):
        curses.echo()
        curses.nocbreak()
        curses.curs_set(1)

    def handleInput(self, func):
        #? @decorator for registering input handler
        self.inputHandlers.append(func)
        return func


def handleMessages(interface: Interface, client: Client):
    while True:
        message = decode(client.socket)

        msg_type = message["type"]
        msg_data = message["data"]

        if msg_type == "message":
            client.message_history.append(msg_data)
        
        interface.refresh()


def sendBuffer(client: Client):
    client.socket.send(encode({
        "type": "message",
        "data": {
            "body": client.message_buffer
        }
    }))


def main(port: int = 1337, ip: str = "45.32.228.139"):
    # Creating a socket and connecting to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    # Creating the Client & Interface objects
    client = Client(sock, port, ip)
    interface = Interface(client)

    # Creating and starting a thread to handle I/O of the connection
    messagesThread = threading.Thread(target=handleMessages, args=[interface, client], daemon=True)
    messagesThread.start()

    try:
        interface.start()

        # Adding a handler for handling interface input
        @interface.handleInput
        def inputHandler(c):
            if c == 265:
                return
            if c == 263:
                # Backspace
                client.message_buffer = client.message_buffer[:-1]
                return
            if c == 10:
                sendBuffer(client)
                client.message_buffer = ""
                interface.refresh()
                return
            client.message_buffer += chr(c)

        while True:
            interface.refresh()
            interface.caputureKey()
    finally:
        interface.kill()

    


if __name__ == "__main__":
    main()
