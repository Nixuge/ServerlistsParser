from bs4 import BeautifulSoup, Tag

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser

from selenium.webdriver.common.by import By

from classes.ParserMeta import ParserMeta
from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.serverchecks import ServerValidator

from mcstatus.status_response import JavaStatusResponse

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

    def get_parse_everything(self):
        self.is_empty = False
        for page in range(1, self.max_page+1):
            print(f"\rGrabbing page {page}... (new servers: {len(self.all_servers)})", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            page += 1
        print()

        print(f"Done, got {len(self.all_servers)} new servers.")

    # type: ignore
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        l1: list[Tag] = soup.find_all("tr", {"class": "row server-row server-listing py-3 py-lg-2 border-bottom border-lg-none"}) # type: ignore
        l2: list[Tag] = soup.find_all("tr", {"class": "row server-row server-listing py-3 py-lg-2 border-bottom border-lg-none non-sponsor"}) # type: ignore
        l = l1 + l2
        print(f": {len(l)}", end="")
        for elem in l:
            ip = elem.find("data", {"class": "ip-block"}).text # type: ignore
            name = elem.find("h3", {"class": "fs-6 w-100"}).text # type: ignore
            # print(f"'{ip}'")
            serverCheck = ServerValidator(ip, False).is_valid_mcstatus()
            if serverCheck:
                entry = McBeeBasicEntry(name, ip, serverCheck)
                self.all_servers[ip] = entry
        
    def print_ask(self, server: McBeeBasicEntry):
        status = server.status
        print("====================")
        print(f"name: {server.name}")
        print(f"ip: {server.ip}")
        print(f"players: {status.players.online}/{status.players.max}")
        print(f"MOTD: {status.motd.to_ansi()}")

        print(f"version: {status.version.name} ({status.version.protocol})")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers.values():
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta(
        "Minecraft.buzz",
        "minecraft.buzz",
        "0.1",
        termcolor.rgb(229, 177, 79),
        MinecraftBuzzParser
    )

# Really only getting the basic properties (IP & Name) for now, nothing else 