from dataclasses import dataclass
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.CloudflareParser import CloudflareParser
from classes.ParserMeta import ParserMeta

from utils.miscutils import ask_duplicate, is_already_present

@dataclass
class Server:
    ip: str
    playercount: int
    motd: str

class NameMCParser(CloudflareParser):
    END_PAGE = 30
    PRINT_DOWN_SERVERS = True

    all_servers: dict[str, Server] # dict to avoid multiple same ips
    servers_down: set
    new_servers: int
    def __init__(self) -> None:
        super().__init__(f"https://namemc.com/minecraft-servers?page=%PAGE%")
        self.all_servers = {}
        self.servers_down = set()
        self.new_servers = 0

    def get_parse_everything(self):
        for i in range(1, self.END_PAGE+1):
            print(f"\rGrabbing page {i}... (new servers: {self.new_servers})", end="")
            data = self.get_page(i)
            self.parse_elements(data)

        if self.PRINT_DOWN_SERVERS:
            print(f"Servers down: {self.servers_down}")
        print(f"Done, got {len(self.all_servers)} new servers.")


    def get_page_selenium(self, page: int) -> str:
        if not self.selenium: raise Exception()
        self.clear_selenium_data()
        good = False
        while not good:
            try:
                self.selenium.get(self.page_url.replace("%PAGE%", str(page)))
                good = True
            except: time.sleep(1)

        # tryexcept temp test, to see if it works once i get cloudflare flagged again
        try:
            WebDriverWait(self.selenium, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mb-2"))
            )
        except:
            self.get_page_selenium(page)

        data = self.selenium.page_source
        return data
    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        count = 0

        cards = soup.find_all("a", {"class": "card-link"})
        for card in cards:
            ip = card["href"].replace("/server/", "")

            if is_already_present(ip):
                continue

            playercount_elem = card.find("span", {"class": "float-end ms-3"})
            if not playercount_elem:
                self.servers_down.add(ip)
                continue
            
            playercount = playercount_elem.text.replace(" / ", "/")

            motd_elem = card.find("div", {"class": "col mc-reset p-1"}).find_all("span")
            if len(motd_elem) < 3:
                motd = "None"
            else:
                motd = motd_elem[2].text.replace("\n", "----").strip()

            self.all_servers[ip] = Server(ip, playercount, motd)
            count += 1
        
        self.new_servers += count
    
    def print_ask(self, server: Server):
        print("====================")
        print(f"ip: {server.ip}, {server.playercount}")
        print("motd: " + server.motd)

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers.values():
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("NameMC", "namemc.net", "1.0", NameMCParser)