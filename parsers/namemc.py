from dataclasses import dataclass
from classes.BaseParser import BaseParser

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.ParserMeta import ParserMeta

from utils.miscutils import ask_duplicate, is_already_present
from utils.vars import SELENIUM_FIREFOX_OPTIONS

import cloudscraper

@dataclass
class Server:
    ip: str
    playercount: int
    motd: str

class NameMCParser(BaseParser):
    END_PAGE = 30
    PRINT_DOWN_SERVERS = True

    all_servers: dict[str, Server] # dict to avoid multiple same ips
    servers_down: set
    new_servers: int
    scraper: cloudscraper.CloudScraper
    def __init__(self) -> None:
        self.all_servers = {}
        self.servers_down = set()
        self.new_servers = 0
        self.scraper = cloudscraper.create_scraper()

    def get_parse_everything(self):
        for i in range(1, self.END_PAGE+1):
            print(f"\rGrabbing page {i}... (new servers: {self.new_servers})", end="")
            data = self.get_page(i)
            self.parse_elements(data)
        print()
        if self.PRINT_DOWN_SERVERS:
            print(f"Servers down: {self.servers_down}")
        print(f"Done, got {len(self.all_servers)} new servers.")


    def get_page(self, page: int) -> str:
        return self.scraper.get(f"https://namemc.com/minecraft-servers?page={page}").text
        # driver = webdriver.Firefox(options=SELENIUM_FIREFOX_OPTIONS)
        # driver.get(f"https://namemc.com/minecraft-servers?page={page}")
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "mb-2"))
        # )
        # data = driver.page_source
        # driver.close()
        # return data
    
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