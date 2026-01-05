from dataclasses import dataclass
import json

import httpx

from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.serverchecks import ServerValidator
from mcstatus.status_response import JavaStatusResponse

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

    def print_ask(self, server: JavaServer):
        print("====================")
        print(f"{server.color}{server.name}, {server.where}{termcolor.RESET}")
        print(f"ip: {server.ip}, {server.status.players.online}/{server.status.players.max} online")
        print(f"{server.desc[:50]}")

        print(f"motd: {server.status.motd.to_ansi()}")
        print(f"version: {server.status.version.name}")
        
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta(
        "BuildTheEarth", 
        "buildtheearth.net", 
        "1.0", 
        termcolor.rgb(40, 51, 140), 
        BteParser, 
        run_bulk=False
    )
