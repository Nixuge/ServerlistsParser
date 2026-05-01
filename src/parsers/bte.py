from dataclasses import dataclass
import json

import httpx

from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.motdutils import get_formatted_motd
from utils.termutils import print_with_icon
from utils.serverchecks import ServerValidator
from mcstatus.responses import JavaStatusResponse

@dataclass
class JavaServer:
    name: str
    desc: str
    where: str
    ip: str
    color: str
    status: JavaStatusResponse


class BteParser(BaseParser):
    all_servers: list
    max_page: int
    def __init__(self) -> None:
        super().__init__()
        self.all_servers = []

    def ask_config(self):
        pass

    def check_server(self, name, desc, where, ip, color):
        serverCheck = ServerValidator(ip, False, False).is_valid_mcstatus()
        with self.print_lock:
            self.servers_requested += 1
            if serverCheck:
                self.valid_servers_found += 1
            self.print_status()
        if serverCheck:
            return JavaServer(name, desc, where, ip, color, serverCheck)
        return None

    def get_parse_everything(self):
        res = httpx.get("https://buildtheearth.net/teams").text
        res = res.split('"data":')[1].split('"_nextI18Next":')[0].strip().removesuffix(",")
        self.parse_elements(json.loads(res))
        
        for future in self.futures:
            server_entry = future.result()
            if server_entry:
                self.all_servers.append(server_entry)
        self.executor.shutdown(wait=True)
        
        print(f"\nDone, got {len(self.all_servers)} new servers.")
    
    def get_page(self, page: int) -> None:
        pass

    def parse_elements(self, data: list):
        if len(data) == 0:
            self.is_empty = True
        
        for elem in data:
            name = elem["name"]
            desc = elem["about"]
            where = elem["slug"]
            ip = elem["ip"]
            color = termcolor.hex(elem["color"])

            future = self.executor.submit(self.check_server, name, desc, where, ip, color)
            self.futures.append(future)

    def print_ask(self, server: JavaServer, i: int):
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
        status = server.status

        lines = [
            f"{server.color}{server.name}, {server.where}{termcolor.RESET}",
            f"ip: {server.ip}, {status.players.online}/{status.players.max} online",
            f"{server.desc[:50]}",
            *get_formatted_motd(status),
            "",
            f"version: {status.version.name}"
        ]

        print_with_icon(status.icon, lines, img_width=15, padding=2)

        print("\n")
        ask_duplicate(server.ip, False)
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "BuildTheEarth", 
        "buildtheearth.net", 
        "1.0", 
        termcolor.rgb(40, 51, 140), 
        BteParser, 
        run_bulk=False
    )
