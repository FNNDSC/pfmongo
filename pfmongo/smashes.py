from re import A
import sys
import socket
from argparse import Namespace, ArgumentParser, RawTextHelpFormatter
from pfmongo import __main__
import pfmongo
from pfmongo.pfmongo import options_initialize
from pfmongo.commands import smash
import pudb
from typing import Any
import asyncio
import aiohttp
from pfmisc import Colors as C
from copy import deepcopy
from pathlib import Path
from pydantic import BaseModel
import asyncio
from urllib.parse import quote
import re

LG = C.LIGHT_GREEN
YL = C.YELLOW
NC = C.NO_COLOUR

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
        "--url",
        type=str,
        default="http://localhost:8025/api/v1/",
        help="address of a pfmdb server",
    )

    parser.add_argument(
        "--msg", type=str, default="", help="message to transmit in client mode"
    )

    parser.add_argument(
        "--repl",
        default=False,
        action="store_true",
        help="If specified, run the client in REPL mode",
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


def nixToWin_path(cmd: str) -> str:
    """
    Any cmd from the client that contains a windows style '\\'
    has this replaced with '/'
    """
    return re.sub(r"/(?!/)", r"\\", cmd)


def path_to_dbCol(path: Path) -> tuple:
    db: str = ""
    collection: str = ""
    match len(path.parts):
        case _ if len(path.parts) == 2:
            (root, db) = path.parts
        case _ if len(path.parts) > 2:
            (root, db, collection) = path.parts[:3]
    return (db, collection)


class FastAPIparams(BaseModel):
    database: str
    collection: str
    handler: str = "smash"


class FastAPIheader(BaseModel):
    headers: str = "accept: application/json"


class FastAPIpayload(BaseModel):
    url: str
    params: FastAPIparams
    headers: FastAPIheader
    data: str = ""

    def msg_parse(self, msg: str) -> tuple[str, str, str]:
        args: list[str] = msg.split()
        path_index: int
        database: str = ""
        collection: str = ""

        if msg.startswith("cd"):
            msg = nixToWin_path(msg)
            return quote(msg), database, collection

        # Find the index of the last argument that starts with '/'
        for i in range(len(args) - 1, -1, -1):
            if args[i].startswith("/"):
                path_index = i
                break
        else:
            # No path found, return the original command
            return quote(msg), database, collection
        last_arg = args.pop(path_index)
        (database, collection) = path_to_dbCol(Path(last_arg))
        path_prefix, file_name = last_arg.rsplit("/", 1)
        args.append(file_name)
        msg = " ".join(args)
        return quote(msg), database, collection

    def __init__(self, url: str, msg: str, **data):
        cmd: str
        database: str
        collection: str
        cmdurl: str
        cmd, database, collection = self.msg_parse(msg)
        cmdurl = f"{url}/{cmd}"
        super().__init__(
            url=cmdurl,
            params=FastAPIparams(database=database, collection=collection),
            headers=FastAPIheader(),
        )


class FastAPIresponse(BaseModel):
    status: int
    response: Any


class FastAPIclient:
    def __init__(self, url: str):
        self.url = f"{url}pfmongo/cli"

    async def message_sendAndReceive(self, msg: str) -> FastAPIresponse:
        pudb.set_trace()
        fastAPIpayload: FastAPIpayload = FastAPIpayload(self.url, msg)
        status: int
        payload: Any

        session: aiohttp.ClientSession = aiohttp.ClientSession()
        try:
            async with session.post(
                fastAPIpayload.url,
                params=fastAPIpayload.params.model_dump(),
                headers=fastAPIpayload.headers.model_dump(),
                data=fastAPIpayload.data,
            ) as response:
                status = response.status
                if response.headers.get("Content-Type", "").startswith(
                    "application/json"
                ):
                    payload = await response.json()
                else:
                    payload = await response.text()

        finally:
            await session.close()

        return FastAPIresponse(status=status, response=payload)


class IPCclient:
    def __init__(self, host: str, port: str):
        self.clientSocket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.clientSocket.connect((host, int(port)))

    async def message_sendAndReceive(self, msg: str) -> dict[str, str]:
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

    async def response_process(self, incoming: str) -> str:
        response: str | bytes
        ret: str = ""
        mdbOptions: Namespace = options_initialize()
        response = await smash.smash_execute_async(
            smash.command_parse(
                await smash.command_get(mdbOptions, noninteractive=incoming)
            ),
            smash.pipe_handler,
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
                resp = asyncio.run(self.response_process(incoming))
                self.connection.sendall(resp.encode())
        finally:
            self.connection.close()

        return resp

    def start(self) -> None:
        while True:
            incoming: str = self.response_await()


def server_handle(options: Namespace) -> None:
    server: IPCserver = IPCserver(options.host, options.port)
    server.start()


def options_msg(options: Namespace, msg: str) -> Namespace:
    localOptions: Namespace = deepcopy(options)
    localOptions.msg = msg
    return localOptions


async def client_handle(options: Namespace) -> dict[str, str]:
    client: IPCclient | FastAPIclient
    if options.url:
        client = FastAPIclient(options.url)
    else:
        client = IPCclient(options.host, options.port)
    pudb.set_trace()
    return await client.message_sendAndReceive(options.msg)


def response_toConsole(resp: dict[str, str]) -> str:
    return resp["response"]


def prompt_prefix(options: Namespace) -> str:
    if options.host:
        return f"{YL}[{options.host}:{options.port}]{NC}"
    else:
        return f"{YL}[options:url]{NC}"


async def client_repl(options: Namespace) -> None:
    pfOptions: Namespace = options_initialize()
    pudb.set_trace()
    while True:
        remoteLS: dict[str, str] = await client_handle(options_msg(options, "ls --raw"))
        print(f"{prompt_prefix(options)}")
        command: str = await smash.command_get(pfOptions, files=remoteLS["response"])
        if "exit" in command.lower():
            break
        dresp: dict[str, str] = await client_handle(options_msg(options, command))
        resp: str = response_toConsole(dresp)
        if "No response received" not in resp:
            print(resp)


def main(*args: list[Any]) -> str | dict[str, str]:
    options: Namespace = parser_interpret(parser_setup(), args)

    dresp: dict[str, str]
    if options.server:
        server_handle(options)

    if options.repl:
        asyncio.run(client_repl(options))
        return "0"

    dresp = asyncio.run(client_handle(options))
    if "string" in options.response:
        return response_toConsole(dresp)
    return dresp


if __name__ == "__main__":
    main()
