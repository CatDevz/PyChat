import curses, threading, time, sys
from client import Client, MsgType


running = True
current_scene = None
client = None
message = ""
online = 0


class ChatWin:
    def __init__(self, win):
        self.win = win

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, 231, 235)    # BACKGROUND     231, 235
        curses.init_pair(2, 231, 240)    # INFO BAR       231, 240
        curses.init_pair(3, 248, 236)    # ONLINE USERS   248, 236
        curses.init_pair(4, 248, 238)    # BINDINGS       248, 238

        curses.init_pair(5, 248, 236)    # SEND AREA      248, 236

        threading.Thread(target=self.input).start()


    def draw(self):
        self.win.clear()

        # Drawing the background of the application
        for x in range(curses.COLS - 1):
            for y in range(curses.LINES):
                self.win.addstr(y, x, ' ', curses.color_pair(1))
        for x in range(curses.COLS - 1):
            self.win.addstr(0, x, ' ', curses.color_pair(2))
            self.win.addstr(curses.LINES - 3, x, ' ', curses.color_pair(5))
            self.win.addstr(curses.LINES - 2, x, ' ', curses.color_pair(5))
            self.win.addstr(curses.LINES - 1, x, ' ', curses.color_pair(5))

        # Drawing the top menu bar of the application
        self.win.addstr(0, 0, ' Online: {} '.format(online), curses.color_pair(3))
        self.win.addstr(' View Bindings: \'CTRL+B\' ', curses.color_pair(4))

        # Drawing all the text of the application
        for k,v in enumerate(client.get_msg_history()):
            self.win.addstr(curses.LINES - 5 - k, 4, v, curses.color_pair(1))
        self.win.addstr(curses.LINES - 2, 2, ': {}'.format(message), curses.color_pair(5))


    def input(self):
        global message, client

        while running:
            in_chr = self.win.getch()
            if in_chr != 0:
                if in_chr == 2:
                    pass # OPEN UP A HELP DIALOG
                elif in_chr == 10:
                    client.send(message)
                    message = ""
                elif in_chr == 263:
                    message = message[:len(message)-1]
                elif in_chr in range(32,127):
                    message += chr(in_chr)
                else:
                    message = str(in_chr) + " - " + chr(in_chr)


def msg_listener(type, msg):
    global online
    if type == MsgType.SYSTEM:
        if 'USR_CNT' in msg:
            online = int(msg[len(msg)-1])


def main():
    global current_scene, client

    server_ip = input("SERVER IP: ")
    server_port = input("SERVER PORT: ")
    try:
        client = Client(host=server_ip, port=server_port)
        client.add_msg_handler(msg_listener)

        print("Client successfully connected to server")
        time.sleep(0.4)
    except ConnectionRefusedError:
        print("Connection to server failed, maybe you inputted a wrong address?")
        sys.exit(0)
    except Exception as e:
        print("Unknown error occurred, '{}'".format(e))
        sys.exit(0)

    stdscr = None
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        curses.mousemask(True)

        current_scene = ChatWin(stdscr)
        while running:
            current_scene.draw()
            stdscr.refresh()
            time.sleep(0.025)
    finally:
        curses.mousemask(False)
        stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


if __name__ == '__main__':
    main()