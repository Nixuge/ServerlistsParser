from dataclasses import dataclass
from classes.BaseParser import BaseParser

from bs4 import BeautifulSoup, Tag

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.ParserMeta import ParserMeta
from utils.fileutils import add_server_dupe

from utils.miscutils import ask_duplicate, is_already_present
from utils.vars import SELENIUM_FIREFOX_OPTIONS


@dataclass
class Server:
    ip: str
    name: str
    playercount: str

class CurseForgeParser(BaseParser):
    all_servers: list 
    driver: webdriver.Firefox
    def __init__(self) -> None:
        self.all_servers = []
        self.driver = webdriver.Firefox(options=SELENIUM_FIREFOX_OPTIONS)

    def get_parse_everything(self):
        self.is_empty = False
        page = 1
        while not self.is_empty:
            print(f"\rGrabbing page {page}...", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            page += 1
        print()

        self.driver.close()
        print(f"Done, got {len(self.all_servers)} new servers.")


    def get_page(self, page: int) -> str:
        self.driver.get(f"https://www.curseforge.com/servers/minecraft?page={page}")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div[2]/div/div[1]/div[1]/div/div'))
        )
        data = self.driver.page_source
        return data
    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        cards: list[Tag] = soup.find_all("div", {"class": "-mx-5 block bg-brand-100 p-5 xs:-mx-10 lg:mx-0 lg:flex lg:flex-wrap lg:items-center lg:justify-between"})
        if len(cards) == 0:
            self.is_empty = True
        for card in cards:
            header = card.find("div", {"class": "mb-3 flex w-full items-center lg:mb-0 lg:w-auto"})
            name = header.find("h3", {"class": "mr-2 font-bold text-brand-900 lg:mr-3"}).text
            ip = header.find("p", {"class": "text-brand-700 lg:hidden"}).text

            playercount = card.find("p", {"class": "text-approved"})
            if not playercount:
                playercount = card.find("p", {"class": "text-error"})

            playercount = playercount.text.replace(" Playing", "").replace(",", " ")
            
            self.all_servers.append(Server(ip, name, playercount))

    def print_ask(self, server: Server):
        if is_already_present(server.ip, False):
            return
        
        if server.playercount == "Offline":
            add_server_dupe("duplicates.txt", server.ip, "down")
            print(f"Skipped {server.ip} (down)")
            return

        print("====================")
        print(f"name: {server.name}")
        print(f"ip: {server.ip}, {server.playercount}")

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("CurseForge", "curseforge.com/servers", "1.0", CurseForgeParser)
