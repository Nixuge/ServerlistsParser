from dataclasses import dataclass

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
    rank: str
    name: str
    website: str
    country: str
    gamemode: str
    ip: str
    desc: str
    status: JavaStatusResponse


class MineRankParser(BaseParser):
    all_servers: list
    max_page: int
    bedrock: bool
    def __init__(self) -> None:
        self.all_servers = []

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.max_page = 30
        else:
            self.max_page = int(page)
        
        self.bedrock = input("Process bedrock servers? TODO (y/N): ").strip().lower() in ("y", "o")


    def get_parse_everything(self):
        self.is_empty = False
        page = 1
        while not self.is_empty and page <= self.max_page:
            print(f"\rGrabbing page {page}...", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            print(f" {len(self.all_servers)} elements", end="")
            page += 1
        print()

        # self.driver.close()
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def get_page(self, page: int) -> list:
        res = httpx.post(
            "https://sb.minerank.com/rest/v1/rpc/get_ranked_servers",
            data={"page":page},
            headers={
                "apikey": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1MDMyMDMwMCwiZXhwIjo0OTA1OTkzOTAwLCJyb2xlIjoiYW5vbiJ9.PCIx-lpLGfnTam9XUm25PsEM8_1y3KasLjWbYUT1Iw4"
            }
        )
        return res.json()

    def parse_elements(self, data: list):
        if len(data) == 0:
            self.is_empty = True
        
        for elem in data:
            rank = elem["rank"]
            name = elem["general_name"]
            website = elem["link_website"]
            country = elem["detail_country"].upper()
            gamemode = elem["detail_main_gamemode"]
            
            ip = elem["connection_host"]
            port = elem["connection_port"]
            if port and port != 25565:
                ip += str(port)
            
            desc = elem["general_description_short"]
            # print("ip: '" + ip + "'")
            serverCheck = ServerValidator(ip, False).is_valid_mcstatus()
            if serverCheck:
                # print("cc")
                entry = JavaServer(rank, name, website, country, gamemode, ip, desc, serverCheck)
                self.all_servers.append(entry)

        pass

    def print_ask(self, server: JavaServer, i: int):
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
        status = server.status
        
        lines = [
            f"{server.rank}: {server.name}, {server.country} ( {server.website} )",
            f"ip: {server.ip}, {status.players.online}/{status.players.max} online",
            f"{server.gamemode} server, {server.desc}",
            * get_formatted_motd(status),
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
        "minerank",
        "minerank.com",
        "0.1",
        termcolor.rgb(124, 206, 0),
        MineRankParser
    )
# TODO: Add Bedrock support