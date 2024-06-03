from re import A
import sys
import socket
from argparse import Namespace, ArgumentParser, RawTextHelpFormatter
from pfmongo import __main__
from pfmongo.commands import smash


def parser_setup(str_desc: str = "") -> ArgumentParser:
    description: str = ""
    if len(str_desc):
        description = str_desc
    parser = ArgumentParser(
        description=description, formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        "--host",
        type=str,
        default="",
        help="host name or IP of server",
    )

    parser.add_argument(
        "--port",
        type=str,
        default="",
        help="port on which remote server is listening",
    )

    parser.add_argument(
        "--server",
        default=False,
        action="store_true",
        help="If specified, run in server mode",
    )

    parser.add_argument(
        "--msg", type=str, default="", help="message to transmit in client mode"
    )

    return parser


def parser_interpret(parser: ArgumentParser, *args, **kwargs) -> Namespace:
    """
    Interpret the list space of *args, or sys.argv[1:] if
    *args is empty
    """
    options: Namespace
    asModule: bool = False
    for k, v in kwargs.items():
        if k == "asModule":
            asModule = v
    if asModule:
        # Here, this code is used a module to another app
        # and we don't want to "interpret" the host app's
        # CLI.
        options, unknown = parser.parse_known_args()
        return options
    if len(args):
        options = parser.parse_args(*args[1:])
    else:
        options = parser.parse_args(sys.argv[1:])
    return options


class IPCclient:
    def __init__(self, host: str, port: str):
        self.clientSocket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.clientSocket.connect((host, int(port)))

    def message_sendAndReceive(self, msg: str) -> dict[str, str]:
        resp: dict[str, str] = {"response": ""}
        result: str = ""
        try:
            self.clientSocket.sendall(msg.encode())
            response: bytes = self.clientSocket.recv(1024)
            if response:
                result = response.decode()
            else:
                result = "No response received"
            resp["response"] = result
        finally:
            self.clientSocket.close()

        return resp


class IPCserver:
    def __init__(self, host: str, port: str):
        self.serverSocket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.serverSocket.bind((host, int(port)))
        self.serverSocket.listen(1)
        self.connection: socket.socket
        self.clientAddress: tuple[str, str]
        print(f"smashes server setup and listening on '{host}:{port}'")

    def response_process(self, incoming: str) -> str:
        response: str = "This is the response"
        return response

    def response_await(self) -> str:
        incoming: str = ""
        resp: str = ""
        self.connection, self.clientAddress = self.serverSocket.accept()
        try:
            print(f"Connection from {self.clientAddress}")
            data: bytes = self.connection.recv(1024)
            if data:
                incoming = data.decode()
                print(f"Received: {incoming}")
                self.connection.sendall(self.response_process(incoming).encode())
        finally:
            self.connection.close()

        return resp

    def start(self) -> None:
        while True:
            incoming: str = self.response_await()


def server_handle(options: Namespace) -> None:
    server: IPCserver = IPCserver(options.host, options.port)
    server.start()


def client_handle(options: Namespace) -> dict[str, str]:
    client: IPCclient = IPCclient(options.host, options.port)
    return client.message_sendAndReceive(options.msg)


def main(*args: list[str]) -> dict[str, str]:
    resp: dict[str, str]
    options: Namespace = parser_interpret(parser_setup(), args)
    if options.server:
        server_handle(options)

    resp = client_handle(options)
    return resp


if __name__ == "__main__":
    main()
