from dataclasses import dataclass

import threading
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup, Tag

from selenium.webdriver.common.by import By

from classes.CloudflareParser import CloudflareParser
from classes.CloudflareParser import CFSeleniumOptions
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
    ip: str
    playercount: str
    online: str
    status: JavaStatusResponse


class MinecraftServersOrgParser(CloudflareParser):
    all_servers: list 
    max_page: int
    def __init__(self) -> None:
        super().__init__(
            "https://minecraftservers.org/index/%PAGE%", 
            CFSeleniumOptions((By.XPATH, '//*[@id="wrapper"]/main/section[2]/div[1]/div[1]/div/div'), always_use_selenium=True)
        )
        self.all_servers = []

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.max_page = 30
        else:
            self.max_page = int(page)

    def check_server(self, rank, name, ip, player_count, online):
        serverCheck = ServerValidator(ip, False).is_valid_mcstatus()

        with self.print_lock:
            self.servers_requested += 1
            if serverCheck:
                self.valid_servers_found += 1
            self.print_status(self.max_page)
        if serverCheck:
            return JavaServer(rank, name, ip, player_count, online, serverCheck)
        return None

    def get_parse_everything(self):
        self.is_empty = False
        page = 1
        
        while not self.is_empty and page <= self.max_page:
            self.pages_parsed = page
            self.print_status(self.max_page)
            
            data = self.get_page(page)
            self.parse_elements(data)
            self.print_status(self.max_page)
            page += 1
            
        # Wait for all background checks to finish
        for future in self.futures:
            server_entry = future.result()
            if server_entry:
                self.all_servers.append(server_entry)
                
        self.executor.shutdown(wait=True)
        print(f"\nDone, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        cards: list[Tag] = soup.find_all("div", {"class": "server-listing"}) # pyright: ignore[reportAssignmentType]
        if len(cards) == 0:
            self.is_empty = True

        for card in cards:
            rank = card.find("div", {"class": "col-md-24 rank"})
            if rank.text.strip() != "": # pyright: ignore[reportOptionalMemberAccess]
                rank = rank.text.strip() # pyright: ignore[reportOptionalMemberAccess]
            else:
                rank = "PROMOTED"

            name = card.find("div", {"class": "col-md-48 name"}).text.strip() # pyright: ignore[reportOptionalMemberAccess]
            ip = card.find("div", {"class": "url"}).text.strip() # pyright: ignore[reportOptionalMemberAccess]

            player_count = card.find("div", {"class": "players"}).find("div", {"class": "value"}).text # type: ignore
            online = card.find("div", {"class": "status"}).text.replace("\n", " ").strip().removeprefix("Status").strip() # type: ignore

            future = self.executor.submit(self.check_server, rank, name, ip, player_count, online)
            self.futures.append(future)

    def print_ask(self, server: JavaServer, i: int):
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
        status = server.status

        lines = [
            f"{server.rank}: {server.name} ({server.online})",
            f"ip: {server.ip}, {status.players.online}/{status.players.max} ({server.playercount}) online",
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
        "minecraftservers.org",
        "minecraftservers.org",
        "1.0",
        termcolor.rgb(73, 73, 73),
        MinecraftServersOrgParser
    )
