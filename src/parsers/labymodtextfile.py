from dataclasses import dataclass
import os
from typing import Optional
from bs4 import BeautifulSoup
import httpx
from mcstatus.status_response import JavaStatusResponse

from classes.BaseParser import BaseParser

from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate, remove_double_space
from utils.motdutils import motd_remove_section_signs
from utils.serverchecks import ServerValidator

SHOULD_ALWAYS_QUERY_LABYMOD = False

@dataclass
class LabyServer:
    ip: str
    desc: Optional[str]
    version: Optional[str]
    location: Optional[str]
    gamemodes: Optional[str]

    status: JavaStatusResponse

class LabymodTextFileParser(BaseParser):
    SOURCE_PATH = "data/labymodtextfile.txt"

    all_servers: list[LabyServer]
    def __init__(self) -> None:
        self.all_servers = []

    def ask_config(self):
        pass
    
    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        if not os.path.isfile(self.SOURCE_PATH):
            open(self.SOURCE_PATH, "a").close()
            print("File labymodtextfile.txt didn't exist. Now created. Please put your data in it.")
            return

        with open(self.SOURCE_PATH) as file:
            content = file.readlines()

        content = [c.split("/server/")[1].split("?lang=")[0] for c in content]

        content = list(set(content))

        for i, element in enumerate(content):
            self.parse_elements(element.split(" ")[0].strip(), i+1, len(content))
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, server: str, num: int, total: int):
        print(f"Checking server: {server} ({num}/{total})")
        if not SHOULD_ALWAYS_QUERY_LABYMOD and "." in server:
            server_check = ServerValidator(server).is_valid_mcstatus()
            if server_check:
                self.all_servers.append(LabyServer(server, None, None, None, None, server_check))
            return
        
        try:
            data = httpx.get(f"https://laby.net/server/{server}?lang=en", timeout=10.0).text
        except httpx.ReadTimeout as e:
            print("Laby request timed out !")
            return
        
        soup = BeautifulSoup(data, 'html.parser')
        
        ip = soup.find("p", {"class": "text-muted ip btn-copy mt-2"}).text.replace("IP", "").strip() # type: ignore
        
        desc = None
        version = None
        location = None
        gamemodes = None

        data = soup.find_all("div", {"class": "ln-card"})
        for elem in data:
            if len(elem.attrs["class"]) > 1:  # pyright: ignore[reportAttributeAccessIssue]
                continue
            key = elem.find("div", {"class": "ln-card-header"}).attrs["data-trans"] # type: ignore
            content = elem.find("div", {"class": "ln-card-body"}) # type: ignore
            if key == "server.information":
                desc = remove_double_space(motd_remove_section_signs(content.text.replace("\n", "")).strip()) # type: ignore
            elif key == "server.version":
                version = remove_double_space(motd_remove_section_signs(content.text.strip())) # type: ignore
            elif key == "server.game_modes":
                gamemodes = remove_double_space(content.text.replace("\n", "").strip()) # type: ignore
            elif key == "server.location":
                location = remove_double_space(content.text.replace("\n", "").strip()) # type: ignore

        server_check = ServerValidator(server).is_valid_mcstatus()
        if server_check:
            self.all_servers.append(LabyServer(server, desc, version, location, gamemodes, server_check))
        


    def print_ask(self, server: LabyServer):
        status = server.status
        print("====================")
        print(f"ip: {server.ip} ({server.location})")
        print(f"desc: {server.desc}, {server.gamemodes}")
        print(f"motd: {status.motd.to_ansi()}")
        print(f"version: {status.version.name}, {status.version.protocol} ({server.version})")
        print(f"Player: {status.players.online}/{status.players.max}")
        print(f"ping: {status.latency}")

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta(
        "Labymod Text",
        "laby.net/server",
        "1.0",
        termcolor.rgb(48, 132, 209),
        LabymodTextFileParser,
        run_bulk=False
    )
