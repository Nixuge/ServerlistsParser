from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from selenium.webdriver.common.by import By

from classes.CloudflareParser import CloudflareParser
from classes.CloudflareParser import CFSeleniumOptions
from classes.ParserMeta import ParserMeta
from utils.fileutils import add_server_dupe

from utils.miscutils import ask_duplicate, is_already_present
from utils.serverchecks import ServerValidator

# Note:
# Unfortunately, due to some (probably on purpose) shitty webpage from curse,
# we have to use Selenium if we want to have something halfway decent, since the thing
# seems to be loaded using js from a quick glance.
@dataclass
class Server:
    ip: str
    name: str
    playercount: str

class CurseForgeParser(CloudflareParser):
    all_servers: list 
    def __init__(self) -> None:
        super().__init__(
            "https://www.curseforge.com/servers/minecraft?page=%PAGE%", 
            CFSeleniumOptions((By.XPATH, '/html/body/div[1]/div/main/div[2]/div/div[1]/div[1]/div/div'), always_use_selenium=True)
        )
        self.all_servers = []

    def get_parse_everything(self):
        self.is_empty = False
        page = 1
        while not self.is_empty:
            print(f"\rGrabbing page {page}...", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            page += 1
        print()

        # self.driver.close()
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        cards: list[Tag] = soup.find_all("div", {"class": "-mx-5 block bg-brand-100 p-5 xs:-mx-10 lg:mx-0 lg:flex lg:flex-wrap lg:items-center lg:justify-between"})
        if len(cards) == 0:
            self.is_empty = True
        for card in cards:
            header = card.find("div", {"class": "mb-3 flex w-full items-center lg:mb-0 lg:w-auto"})
            name = header.find("h3", {"class": "mr-2 font-bold text-brand-900 lg:mr-3"}).text # type: ignore
            ip = header.find("p", {"class": "text-brand-700 lg:hidden"}).text # type: ignore

            playercount = card.find("p", {"class": "text-approved"})
            if not playercount:
                playercount = card.find("p", {"class": "text-error"})

            playercount = playercount.text.replace(" Playing", "").replace(",", " ") # type: ignore
            
            serverCheck = ServerValidator(ip, True).is_valid_mcstatus()
            if not serverCheck:
                continue
            
            if playercount == "Offline":
                add_server_dupe("duplicates.txt", ip, "down")
                print(f"Skipped {ip} (down)")
            
            
            self.all_servers.append(Server(ip, name, playercount))

    def print_ask(self, server: Server):
        print("====================")
        print(f"name: {server.name}")
        print(f"ip: {server.ip}, {server.playercount}")

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("CurseForge", "curseforge.com/servers", "1.0", CurseForgeParser)
