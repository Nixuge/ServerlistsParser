from bs4 import BeautifulSoup, Tag

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser

from selenium.webdriver.common.by import By

from classes.ParserMeta import ParserMeta
from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.termutils import print_with_icon
from utils.motdutils import get_formatted_motd, motd_remove_section_signs
from utils.serverchecks import ServerValidator

from mcstatus.responses import JavaStatusResponse

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
    ALL_PRINTS = False

    max_page: int
    all_servers: dict[str, McSrvListEntry] #ip, server to remove duplicates
    def __init__(self) -> None:
        super().__init__("https://minecraft-server-list.com/page/%PAGE%/", CFSeleniumOptions((By.CLASS_NAME, "serverdatadiv1")))
        self.all_servers = {}

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.max_page = 30
        else:
            self.max_page = int(page)

    def check_server(self, title, country, desc, ip, playersOn, playersMax, votesMonth, votesAll):
        serverCheck = ServerValidator(ip, self.ALL_PRINTS).is_valid_mcstatus()
        with self.print_lock:
            self.servers_requested += 1
            if serverCheck:
                self.valid_servers_found += 1
            self.print_status(self.max_page)

        if not serverCheck:
            return None

        return McSrvListEntry(
            title, country, desc,
            ip, playersOn, playersMax, 
            votesMonth, votesAll,
            serverCheck
        )

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
        print()

        print(f"\nDone, got {len(self.all_servers)} new servers.")

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

            future = self.executor.submit(self.check_server, title, country, desc, ip, playersOn, playersMax, votesMonth, votesAll)
            self.futures.append(future)

        
    def print_ask(self, server: McSrvListEntry, i: int):
        status = server.status
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
        
        lines = [
            f"name: {server.title}",
            f"ip: {server.ip} ({server.country.upper()})",
            f"players: {status.players.online}/{status.players.max} ({server.playersOn}/{server.playersMax})",
            f"Votes: {server.votesMonth} this month, {server.votesAll} overrall",
            *get_formatted_motd(status),
            "",
            f"version: {status.version.name}"
        ]

        print_with_icon(status.icon, lines, img_width=15, padding=2)

        print("\n")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers.values()):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "Minecraft-Server-List",
        "minecraft-server-list.com",
        "1.0",
        termcolor.rgb(244, 155, 47),
        MinecraftServerListParser
    )
