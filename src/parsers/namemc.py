from dataclasses import dataclass

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser
from classes.ParserMeta import ParserMeta

from utils import serverchecks
from utils.color import termcolor
from utils.miscutils import ask_duplicate, is_already_present
from utils.motdutils import get_formatted_motd
from utils.serverchecks import ServerValidator
from mcstatus.responses import JavaStatusResponse

from utils.termutils import print_with_icon

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
            data = self.get_page(i)
            self.pages_parsed += 1
            self.print_status(self.end_page)
            self.parse_elements(data)

        for future in self.futures:
            result = future.result()
            if result:
                self.all_servers[result.ip] = result
        
        self.executor.shutdown(wait=True)

        if self.PRINT_DOWN_SERVERS:
            print(f"\nServers down: {self.servers_down}")
        print(f"\nDone, got {len(self.all_servers)} new servers.")

    def check_server(self, ip: str, playercount: str, motd: str):
        serverCheck = ServerValidator(ip, self.PRINT_DOWN_SERVERS).is_valid_mcstatus()

        with self.print_lock:
            self.servers_requested += 1
            if serverCheck:
                self.valid_servers_found += 1
            self.print_status(self.end_page)
        
        if not serverCheck:
            return None
        
        return Server(ip, playercount, motd, serverCheck)
    
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

            future = self.executor.submit(self.check_server, ip, playercount, motd)
            self.futures.append(future)
    
    # def print_ask(self, server: Server, i: int):
    #     print(f"=========={i}/{len(self.all_servers)}==========")
    #     print(f"ip: {server.ip}, {server.status.players.online}/{server.status.players.max} ({server.playercount})")
    #     print("namemc motd: " + server.motd)
    #     print("motd: " + server.status.motd.to_ansi())

    #     print(f"version: {server.status.version.name}")
    #     ask_duplicate(server.ip, False)

    def print_ask(self, server: Server, i: int):
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
        
        lines = [
            f"ip: {server.ip}, {server.status.players.online}/{server.status.players.max} ({server.playercount})",
            "",
            f"namemc motd: {server.motd}",
            "",
            *get_formatted_motd(server.status),
            "",
            f"version: {server.status.version.name}"
        ]

        print_with_icon(server.status.icon, lines, img_width=15, padding=2)
        
        print("\n")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers.values()):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "NameMC",
        "namemc.net",
        "1.0",
        termcolor.rgb(238, 240, 242),
        NameMCParser
    )