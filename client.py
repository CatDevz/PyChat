from commons import TermColors, decode, encode
import threading
import socket
import time


def handleMessages(sock):
    while True:
        message = decode(sock)

        msg_type = message["type"]
        msg_data = message["data"]

        if msg_type == "message":
            print(f"{TermColors[msg_data['color']].value}{msg_data['author']}: {TermColors.resetColor()}{msg_data['body']}")


def handleInput(sock):
    while True:
        message = input()
        sock.send(encode({
            "type": "message",
            "data": {
                "body": message
            }
        }))


def main(port=1337, ip="127.0.0.1"):
    # Creating a socket and connecting to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    identity = input(f"{TermColors.RED.value}[!]{TermColors.resetColor()} Choose your identitiy: ")
    sock.send(encode({
        "type": "modify-identity",
        "data": {
            "identity": identity
        }
    }))

    # Creating and starting 2 threads to handle I/O of the connection
    messagesThread = threading.Thread(target=handleMessages, args=[sock], daemon=True)
    inputThread = threading.Thread(target=handleInput, args=[sock], daemon=True)

    messagesThread.start()
    inputThread.start()

    while True:
        time.sleep(5)
        # howdy partner


if __name__ == "__main__":
    main()
