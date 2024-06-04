from re import A
import sys
import socket
from argparse import Namespace, ArgumentParser, RawTextHelpFormatter
from pfmongo import __main__
from pfmongo.pfmongo import options_initialize
from pfmongo.commands import smash
import pudb
from typing import Any


TERMINATION_SEQUENCE = b"\r\n\r\n"


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
        "--response",
        type=str,
        default="string",
        help="response type: either a 'string' or 'dict'",
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
    options: Namespace = Namespace()
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
        if len(args[0]):
            if isinstance(args[0][0], list):
                options = parser.parse_args(args[0][0])
            elif isinstance(args[0][0], dict):
                options = parser.parse_args(parser_JSONinterpret(args[0][0]))
        else:
            options = parser.parse_args(sys.argv[1:])
    return options


def parser_JSONinterpret(d_JSONargs) -> list:
    """
    Interpret a JSON dictionary in lieu of CLI.

    For each <key>:<value> in the d_JSONargs, append to
    list two strings ["--<key>", "<value>"] and then
    argparse.
    """
    l_args = []
    for k, v in d_JSONargs.items():
        if isinstance(v, bool):
            if v:
                l_args.append("--%s" % k)
            continue
        l_args.append("--%s" % k)
        l_args.append("%s" % v)
    return l_args


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
            response: bytes = b""
            while True:
                chunk: bytes = self.clientSocket.recv(1024)
                if not chunk:
                    break
                response += chunk
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
        response: str | bytes
        ret: str = ""
        mdbOptions: Namespace = options_initialize()
        response = smash.smash_execute(
            smash.command_parse(smash.command_get(mdbOptions, noninteractive=incoming))
        )
        if isinstance(response, str):
            ret = response
        if isinstance(response, bytes):
            ret = response.decode()
        print(f"{ret}")
        return ret

    def response_await(self) -> str:
        incoming: str = ""
        resp: str = ""
        self.connection, self.clientAddress = self.serverSocket.accept()
        try:
            print(f"Connection from {self.clientAddress}")
            data: bytes = b""
            data = self.connection.recv(32768)
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


def response_toConsole(resp: dict[str, str]) -> str:
    return resp["response"]


def main(*args: list[Any]) -> str | dict[str, str]:
    options: Namespace = parser_interpret(parser_setup(), args)

    dresp: dict[str, str]
    if options.server:
        server_handle(options)

    dresp = client_handle(options)
    if "string" in options.response:
        return response_toConsole(dresp)
    return dresp


if __name__ == "__main__":
    main()
