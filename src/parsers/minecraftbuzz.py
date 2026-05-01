from bs4 import BeautifulSoup, Tag

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser

from selenium.webdriver.common.by import By

from classes.ParserMeta import ParserMeta
from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.motdutils import get_formatted_motd
from utils.termutils import print_with_icon
from utils.serverchecks import ServerValidator

from mcstatus.responses import JavaStatusResponse

@dataclass
class McBeeBasicEntry:
    name: str
    ip: str
    status: JavaStatusResponse

class MinecraftBuzzParser(CloudflareParser):
    ALL_PRINTS = False

    max_page: int
    all_servers: dict[str, McBeeBasicEntry]
    def __init__(self) -> None:
        super().__init__("https://minecraft.buzz/java/%PAGE%/", CFSeleniumOptions((By.XPATH, "/html/body/div[1]/div/div/table/tbody/tr")))
        self.all_servers = {}

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.max_page = 30
        else:
            self.max_page = int(page)

    def check_server(self, name, ip):
        serverCheck = ServerValidator(ip, False).is_valid_mcstatus()
        with self.print_lock:
            self.servers_requested += 1
            if serverCheck:
                self.valid_servers_found += 1
            self.print_status(self.max_page)
        
        if serverCheck:
            return McBeeBasicEntry(name, ip, serverCheck)
        return None

    def get_parse_everything(self):
        self.is_empty = False
        for page in range(1, self.max_page+1):
            self.pages_parsed = page
            self.print_status(self.max_page)
            data = self.get_page(page)
            self.parse_elements(data)
            self.print_status(self.max_page)
        
        for future in self.futures:
            server_entry = future.result()
            if server_entry:
                self.all_servers[server_entry.ip] = server_entry
        self.executor.shutdown(wait=True)

        print(f"\nDone, got {len(self.all_servers)} new servers.")

    # type: ignore
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        l1: list[Tag] = soup.find_all("tr", {"class": "row server-row server-listing py-3 py-lg-2 border-bottom border-lg-none"}) # type: ignore
        l2: list[Tag] = soup.find_all("tr", {"class": "row server-row server-listing py-3 py-lg-2 border-bottom border-lg-none non-sponsor"}) # type: ignore
        l = l1 + l2
        for elem in l:
            ip = elem.find("data", {"class": "ip-block"}).text # type: ignore
            name = elem.find("h3", {"class": "fs-6 w-100"}).text # type: ignore
            future = self.executor.submit(self.check_server, name, ip)
            self.futures.append(future)
        
    def print_ask(self, server: McBeeBasicEntry, i: int):
        status = server.status
        print(f"============================== {i}/{len(self.all_servers)} ==============================")

        lines = [
            f"name: {server.name}",
            f"ip: {server.ip}",
            f"players: {status.players.online}/{status.players.max}",
            *get_formatted_motd(status),
            "",
            f"version: {status.version.name} ({status.version.protocol})"
        ]

        print_with_icon(status.icon, lines, img_width=15, padding=2)

        print("\n")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers.values()):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "Minecraft.buzz",
        "minecraft.buzz",
        "0.1",
        termcolor.rgb(229, 177, 79),
        MinecraftBuzzParser
    )

# Really only getting the basic properties (IP & Name) for now, nothing else 