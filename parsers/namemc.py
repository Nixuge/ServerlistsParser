from dataclasses import dataclass

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser
from classes.ParserMeta import ParserMeta

from utils import serverchecks
from utils.color import termcolor
from utils.miscutils import ask_duplicate, is_already_present
from utils.serverchecks import ServerValidator
from mcstatus.status_response import JavaStatusResponse

@dataclass
class Server:
    ip: str
    playercount: int
    motd: str
    status: JavaStatusResponse

class NameMCParser(CloudflareParser):
    PRINT_DOWN_SERVERS = True

    end_page: int
    all_servers: dict[str, Server] # dict to avoid multiple same ips
    servers_down: set
    new_servers: int
    def __init__(self) -> None:
        super().__init__(
            f"https://namemc.com/minecraft-servers?page=%PAGE%", 
            CFSeleniumOptions((By.CLASS_NAME, "mb-2"), clear_every_request=True)
        )
        self.all_servers = {}
        self.servers_down = set()
        self.new_servers = 0

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.end_page = 30
        else:
            page = int(page)
            if page > 30:
                print("Max page is 30, falling back to that.")
                self.end_page = 30
            else:
                self.end_page = page
            

    def get_parse_everything(self):
        for i in range(1, self.end_page+1):
            print(f"\rGrabbing page {i}... (new servers: {self.new_servers})", end="")
            data = self.get_page(i)
            self.parse_elements(data)

        if self.PRINT_DOWN_SERVERS:
            print(f"Servers down: {self.servers_down}")
        print(f"Done, got {len(self.all_servers)} new servers.")

    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        count = 0

        cards = soup.find_all("a", {"class": "card-link"})
        for card in cards:
            ip = card["href"].replace("/server/", "") # type: ignore

            if is_already_present(ip):
                continue

            playercount_elem = card.find("span", {"class": "float-end ms-3"}) # type: ignore
            if not playercount_elem:
                self.servers_down.add(ip)
                continue
            
            playercount = playercount_elem.text.replace(" / ", "/") # pyright: ignore[reportAttributeAccessIssue]

            motd_elem = card.find("div", {"class": "col mc-reset p-1"}).find_all("span") # type: ignore
            if len(motd_elem) < 3:
                motd = "None"
            else:
                motd = motd_elem[2].text.replace("\n", "----").strip()

            serverCheck = ServerValidator(ip, self.PRINT_DOWN_SERVERS).is_valid_mcstatus()
            if not serverCheck:
                continue
            
            self.all_servers[ip] = Server(ip, playercount, motd, serverCheck)
            count += 1
        
        self.new_servers += count
    
    def print_ask(self, server: Server):
        print("====================")
        print(f"ip: {server.ip}, {server.status.players.online}/{server.status.players.max} ({server.playercount})")
        print("namemc motd: " + server.motd)
        print("motd: " + server.status.motd.to_ansi())

        print(f"version: {server.status.version.name}")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers.values():
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("NameMC", "namemc.net", "1.0", termcolor.rgb(238, 240, 242), NameMCParser)