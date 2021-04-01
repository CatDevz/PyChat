from enum import Enum
import json
import random

FORMAT = 'utf-8' # String encoding method to use


class MalformedPacketException(Exception):
    pass


class TermColors(Enum):
    # This enum class defines colors for the terminal
    RED    = "\033[31m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    BLUE   = "\033[34m"
    PURPLE = "\033[35m"
    AQUA   = "\033[36m"
    GRAY   = "\033[37m"
    WHITE  = "\033[38m"

    @staticmethod
    def randomColor():
        # Method to get a random color from the selection
        return random.choices([color for color in TermColors])[0]

    @staticmethod
    def resetColor():
        return "\033[0m"


def encode(jsonObject):
    # This helper function will encode a json string into a binary
    # package with a header to determine its length
    msg = str(json.dumps(jsonObject)).encode(FORMAT)
    msg_length = int(len(msg)).to_bytes(4, byteorder="big", signed=False)
    return msg_length + msg
    

def decode(connection):
    # This helper function will decode a json string from a connection
    msg_length = int.from_bytes(connection.recv(4), byteorder="big", signed=False)
    msg = json.loads(connection.recv(msg_length).decode(FORMAT))
    return msg
