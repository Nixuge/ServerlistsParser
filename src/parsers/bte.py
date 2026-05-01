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
        self.all_servers = []

    def ask_config(self):
        pass

    def get_parse_everything(self):
        res = httpx.get("https://buildtheearth.net/teams").text
        res = res.split('"data":')[1].split('"_nextI18Next":')[0].strip().removesuffix(",")
        self.parse_elements(json.loads(res))
        
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def get_page(self, page: int) -> None:
        pass

    def parse_elements(self, data: list):
        if len(data) == 0:
            self.is_empty = True
        
        i = 1
        print()
        for elem in data:
            print(f"\rChecking BTE server {i}/{len(data)}", end="")
            name = elem["name"]
            desc = elem["about"]
            where = elem["slug"]
            ip = elem["ip"]
            color = termcolor.hex(elem["color"])

            print(f"\n{name}; {ip}")
            serverCheck = ServerValidator(ip, False, False).is_valid_mcstatus()
            if serverCheck:
                entry = JavaServer(name, desc, where, ip, color, serverCheck)
                self.all_servers.append(entry)
            
            i+=1

        print()

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
