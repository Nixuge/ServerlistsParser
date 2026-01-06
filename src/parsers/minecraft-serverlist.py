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
class McSrvListComJavaEntry:
    num: str
    name: str
    ip: str
    players_on: str
    status: JavaStatusResponse

class MinecraftServerListComParser(CloudflareParser):
    max_page: int
    all_servers: dict[str, McSrvListComJavaEntry] #ip, server to remove duplicates
    def __init__(self) -> None:
        super().__init__("https://minecraft-serverlist.com/servers/%PAGE%/", CFSeleniumOptions((By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[2]/div[2]/div/div[7]")))
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

    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        div = soup.find("div", {"class": "servers"})
        servers: list[Tag] = div.find_all("div", {"class": "col-12"}) # type: ignore
        for server in servers:
            num = server.find("span", {"class": "mb-3 text-xl font-black"})
            if not num:
                num = server.find("span", {"class": "mb-3 text-lg font-bold"})
            num = num.text # pyright: ignore[reportOptionalMemberAccess]

            name = server.find("div", {"class": "text-center lg:text-left text-gray-700 font-bold uppercase text-xl lg:text-[17px] truncate w-full lg:max-w-[13rem] px-6 lg:px-0 mb-1"}).find("span").text # type: ignore
            online = server.find("span", {"class": "text-[13px]"}).text.replace("playing", "").strip() # type: ignore

            # print("========================================")
            # print(server)
            ip = server.find("div", {"class": "copy-ip"})
            if not ip: # "Private server" because that makes sense on a server list?
                continue
            ip = ip.text

            edition = server.find("span", {"class": "rounded px-2 py-1 text-[11px] font-bold mb-0 bg-[#484E5B] text-[#e1e2e5]"})
            if not edition:
                edition = server.find("span", {"class": "rounded px-2 py-1 text-[11px] font-bold mb-0 bg-[#563d09] text-white"})
            edition = edition.text.lower().replace("edition", "").strip() # type: ignore

            if edition != "java":
                continue
            # print(name)
            # print(online)
            # print(ip)
            # print(num)
            # print(edition)
            # input("===============")
            serverCheck = ServerValidator(ip, False).is_valid_mcstatus()
            if not serverCheck:
                continue


            self.all_servers[ip] = McSrvListComJavaEntry(
                num,
                name,
                ip,
                online,
                serverCheck
            )

        
    def print_ask(self, server: McSrvListComJavaEntry, i: int):
        status = server.status
        print(f"=========={i}/{len(self.all_servers)}==========")
        print(f"{server.num}: {server.name}")
        print(f"ip: {server.ip}")
        print(f"players: {status.players.online}/{status.players.max} ({server.players_on})")
        print(f"MOTD: {status.motd.to_ansi()}")

        print(f"version: {status.version.name} ({status.version.protocol})")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers.values()):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "Minecraft-ServerList",
        "minecraft-serverlist.com",
        "1.0",
        termcolor.rgb(118, 184, 61),
        MinecraftServerListComParser
    )
