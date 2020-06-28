from client import Client, MsgType


def message_handler(type, msg):
    if type == MsgType.CHAT:
        print(msg)


def main():
    pychat_cli = Client(host=input("IP address of server you would like to connect to: "), port=input("Port of the server you would like to connect to: "))
    pychat_cli.add_msg_handler(message_handler)

    while pychat_cli.connected:
        txt = input()
        pychat_cli.send(txt)


if __name__ == '__main__':
    main()