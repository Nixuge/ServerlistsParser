from bs4 import BeautifulSoup, Tag

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser

from selenium.webdriver.common.by import By

from classes.ParserMeta import ParserMeta
from utils.miscutils import ask_duplicate
from utils.motdutils import motd_remove_section_signs
from utils.serverchecks import ServerValidator

from mcstatus.status_response import JavaStatusResponse

@dataclass
class McSrvListEntry:
    title: str
    country: str
    desc: str
    ip: str
    playersOn: str
    playersMax: str
    votesMonth: int
    votesAll: int
    status: JavaStatusResponse

class MinecraftServerListParser(CloudflareParser):
    MAX_PAGE = 30
    ALL_PRINTS = False
    all_servers: dict[str, McSrvListEntry] #ip, server to remove duplicates
    def __init__(self) -> None:
        super().__init__("https://minecraft-server-list.com/page/%PAGE%/", CFSeleniumOptions((By.CLASS_NAME, "serverdatadiv1")))
        self.all_servers = {}

    def get_parse_everything(self):
        self.is_empty = False
        for page in range(1, self.MAX_PAGE+1):
            print(f"\rGrabbing page {page}... (new servers: {len(self.all_servers)})", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            page += 1
        print()

        print(f"Done, got {len(self.all_servers)} new servers.")

    # type: ignore
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        div = soup.find("div", {"class": "serverdatadiv1"})
        tbody = div.find("tbody") # type: ignore
        servers: list[Tag] = tbody.find_all("tr") # type: ignore
        for server in servers:
            title = server.find("h2", {"class": "column-heading"}).text # type: ignore
            country = str(server.find("img", {"class": "flag"})["title"]) # type: ignore
            desc = server.find("div", {"class": "serverListing"}).text.replace("\n...", "") # type: ignore
            if desc[-3:] == "...": desc = desc[:-3]

            rightPart = server.find("td", {"class": "n3"})
            ip = str(rightPart.find("input", {"class": "copylinkinput"})["value"]) # type: ignore

            playersOn, playersMax = (x.strip() for x in rightPart.find("span", {"style": "color:blue"}).text.strip().replace("Players Online:", "").split("/")) # type: ignore

            votesMonth, votesAll = rightPart.find_all("span")[-1].text.split("\n") # type: ignore
            votesMonth = int(votesMonth.strip().split(" ")[-1])
            votesAll = int(votesAll.strip().split(" ")[-1])

            serverCheck = ServerValidator(ip, self.ALL_PRINTS).is_valid_mcstatus()
            if not serverCheck:
                continue

            self.all_servers[ip] = McSrvListEntry(
                title, country, desc,
                ip, playersOn, playersMax, 
                votesMonth, votesAll,
                serverCheck
            )
            # print(len(self.all_servers))

        
    def print_ask(self, server: McSrvListEntry):
        status = server.status
        print("====================")
        print(f"name: {server.title}")
        print(f"ip: {server.ip} ({server.country.upper()})")
        print(f"players: {status.players.online}/{status.players.max} (excepted {server.playersOn}/{server.playersMax})")
        print(f"Votes: {server.votesMonth} this month, {server.votesAll} overrall")
        print(f"MOTD: {motd_remove_section_signs(status.description)}")

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers.values():
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("MinecraftServerList", "minecraft-server-list.com", "1.0", MinecraftServerListParser)
