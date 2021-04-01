from commons import MalformedPacketException, TermColors, decode, encode
from dataclasses import dataclass
import threading
import socket
import time

running = False


@dataclass
class Server:
    socket: any
    clients: list
    handlers: dict

    def addHandler(self, msg_type, func):
        self.handlers[msg_type] = func

    def handler(self, msg_type):
        def wrap(func):
            self.addHandler(msg_type, func)
        return wrap


@dataclass
class Client:
    connection: any
    address: tuple
    identity: str
    color: TermColors


def awaitConnections(server: Server):
    # This function will be responsible for obtaining new connections
    # and opening up a handleConnection thread for them
    global running
    
    server.socket.listen()
    while running:
        # Accepting new requests to connect
        connection, address = server.socket.accept()

        # Creating the client object & appending it
        # to the list of clients in the server object
        client = Client(connection, address, str(address[1]), TermColors.randomColor())
        server.clients.append(client)

        connectionThread = threading.Thread(target=handleConnection, args=[server, client])
        connectionThread.start()


def handleConnection(server: Server, client: Client):
    # This function will be responsible for handling connections
    # once they have actually been aquired
    global running

    while running:
        # Attempt to get a message from the connection
        try:
            message = decode(client.connection)

            msg_type = message.get("type", None)
            msg_data = message.get("data", None)
            if msg_type == None or msg_data == None:
                raise MalformedPacketException("Malformed packet receved from client")

            if not msg_type in server.handlers:
                print("Could not find handler for packet type of {}".format(msg_type))
                continue

            handler = server.handlers.get(msg_type)
            handler(server, client, msg_data)        
        except MalformedPacketException:
            print("Client with identity {} sent a malformed packet".format(client.identity))
            client.send(encode({
                "type": "error",
                "data": {
                    "body": "A Malformed Packet was sent"
                }
            }))
        except Exception:
            # Removing the client from the list of clients
            server.clients.remove(client)
            print("Lost client with identity {}".format(client.identity))
            return


def main(port=1337, ip="127.0.0.1"):
    global running

    # Set running to true
    running = True

    # Creating a socket and binding it to the ip/port combo
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))

    # Creating a server object
    server = Server(sock, [], {})

    awaitThread = threading.Thread(target=awaitConnections, args=[server])
    awaitThread.start()

    @server.handler("modify-identity")
    def identityHandler(server, client, message):
        new_identity = message["identity"]
        client.identity = new_identity

        encoded_message = encode({
            "type": "success",
            "data": {
                "body": "Changing identity was successful"
            }
        })

        client.connection.send(encoded_message)

    @server.handler("message")
    def messageHandler(server, client, message):
        body = message["body"]

        # Throw an error if the user's packet is malformed 
        if body == None:
            raise MalformedPacketException("Malformed packet receved from client")

        encoded_message = encode({
            "type": "message",
            "data": {
                "author": client.identity,
                "body": body,
                "color": client.color.name
            }
        })

        for c in server.clients:
            c.connection.send(encoded_message)

    while running:
        time.sleep(5)
        # why hello there


if __name__ == "__main__":
    main()

