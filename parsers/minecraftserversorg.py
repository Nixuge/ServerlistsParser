from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from selenium.webdriver.common.by import By

from classes.CloudflareParser import CloudflareParser
from classes.CloudflareParser import CFSeleniumOptions
from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.serverchecks import ServerValidator
from mcstatus.status_response import JavaStatusResponse

@dataclass
class JavaServer:
    rank: str
    name: str
    ip: str
    playercount: str
    online: str
    status: JavaStatusResponse


class MinecraftServersOrgParser(CloudflareParser):
    all_servers: list 
    max_page: int
    def __init__(self) -> None:
        super().__init__(
            "https://minecraftservers.org/index/%PAGE%", 
            CFSeleniumOptions((By.XPATH, '//*[@id="wrapper"]/main/section[2]/div[1]/div[1]/div/div'), always_use_selenium=True)
        )
        self.all_servers = []

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.max_page = 30
        else:
            self.max_page = int(page)


    def get_parse_everything(self):
        self.is_empty = False
        page = 1
        while not self.is_empty and page <= self.max_page:
            print(f"\rGrabbing page {page}...", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            print(f" {len(self.all_servers)} elements", end="")
            page += 1
        print()

        # self.driver.close()
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        cards: list[Tag] = soup.find_all("div", {"class": "server-listing"}) # pyright: ignore[reportAssignmentType]
        if len(cards) == 0:
            self.is_empty = True

        for card in cards:
            # print(card)

        #     header = card.find("div", {"class": "mb-3 flex w-full items-center lg:mb-0 lg:w-auto"})
        #     name = header.find("h3", {"class": "mr-2 font-bold text-brand-900 lg:mr-3"}).text # type: ignore

            rank = card.find("div", {"class": "col-md-24 rank"})
            if rank.text.strip() != "": # pyright: ignore[reportOptionalMemberAccess]
                rank = rank.text.strip() # pyright: ignore[reportOptionalMemberAccess]
            else:
                rank = "PROMOTED"

            name = card.find("div", {"class": "col-md-48 name"}).text.strip() # pyright: ignore[reportOptionalMemberAccess]
            ip = card.find("div", {"class": "url"}).text.strip() # pyright: ignore[reportOptionalMemberAccess]

            player_count = card.find("div", {"class": "players"}).find("div", {"class": "value"}).text # type: ignore
            online = card.find("div", {"class": "status"}).text.replace("\n", " ").strip().removeprefix("Status").strip() # type: ignore
            
                
            # print(name)
            # print(ip)
            # print(rank)
            # print(player_count)
            # print(online)
            # print("=========")

            serverCheck = ServerValidator(ip, False).is_valid_mcstatus()
            if serverCheck:
                entry = JavaServer(rank, name, ip, player_count, online, serverCheck)
                self.all_servers.append(entry)

        pass

    def print_ask(self, server: JavaServer):
        print("====================")
        print(f"{server.rank}: {server.name} ({server.online})")
        print(f"ip: {server.ip}, {server.status.players.online}/{server.status.players.max} ({server.playercount}) online")

        print(f"motd: {server.status.motd.to_ansi()}")
        print(f"version: {server.status.version.name}")
        
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("minecraftservers.org", "minecraftservers.org", "1.0", termcolor.rgb(73, 73, 73), MinecraftServersOrgParser)
