from dataclasses import dataclass
import os
from mcstatus.status_response import JavaStatusResponse

from classes.BaseParser import BaseParser

from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.serverchecks import ServerValidator

class TextFileParser(BaseParser):
    SOURCE_PATH = "data/textfile.txt"

    all_servers: list[tuple[str, JavaStatusResponse]]
    def __init__(self) -> None:
        self.all_servers = []

    def ask_config(self):
        pass
    
    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        if not os.path.isfile(self.SOURCE_PATH):
            open(self.SOURCE_PATH, "a").close()
            print("File textfile.txt didn't exist. Now created. Please put your data in it.")
            return

        with open(self.SOURCE_PATH) as file:
            content = file.readlines()

        content = list(set(content))

        for i, element in enumerate(content):
            self.parse_elements(element.split(" ")[0].strip(), i+1, len(content))
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, server: str, num: int, total: int):
        print(f"Checking server: {server} ({num}/{total})")
        server_check = ServerValidator(server).is_valid_mcstatus()
        if server_check:
            print("Done !")
            self.all_servers.append((server, server_check))


    def print_ask(self, ip: str, status: JavaStatusResponse):
        print("====================")
        print(f"ip: {ip}")
        print(f"motd: {status.motd.to_ansi()}")
        print(f"version name/protocol: {status.version.name}, {status.version.protocol}")
        print(f"Player: {status.players.online}/{status.players.max}")
        print(f"ping: {status.latency}")

        ask_duplicate(ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(*server)

def setup() -> ParserMeta:
    return ParserMeta("TextFile", "~none~", "1.0", termcolor.rgb(50, 150, 150), TextFileParser)
