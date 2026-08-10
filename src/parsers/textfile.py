from dataclasses import dataclass
import os
from mcstatus.responses import JavaStatusResponse

from classes.BaseParser import BaseParser

from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.motdutils import get_formatted_motd
from utils.termutils import print_with_icon
from utils.serverchecks import ServerValidator

class TextFileParser(BaseParser):
    max_count: int

    all_servers: list[tuple[str, JavaStatusResponse]]
    def __init__(self, source_path: str = "data/textfile.txt") -> None:
        super().__init__()
        self.source_path = source_path
        self.all_servers: list[tuple[str, JavaStatusResponse]] = []

    def order_servers(self):
        self.all_servers.sort(key=lambda x: x[1].players.online)
        self.all_servers.reverse()

    def ask_config(self):
        inp = input("How many max inputs do you wanna try: ")
        if inp.strip() == "":
            self.max_count = 99999999999999999
        else:
            self.max_count = int(inp)
    
    def check_server(self, server: str):
        server_check = ServerValidator(server).is_valid_mcstatus()
        with self.print_lock:
            self.servers_requested += 1
            if server_check:
                self.valid_servers_found += 1
            self.print_status()
            
        if server_check:
            return (server, server_check)
        return None

    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        if not os.path.isfile(self.source_path):
            open(self.source_path, "a").close()
            print("File textfile.txt didn't exist. Now created. Please put your data in it.")
            return

        with open(self.source_path) as file:
            content = file.readlines()

        for i, elem in enumerate(content):
            elem = elem.strip()
            
            for prefix in (
                ("https://www.", "https://"),
            ):
                if elem.startswith(prefix[0]):
                    elem = prefix[1] + elem.split(prefix[0], 1)[1]

            for domain in (
                "https://namemc.com/server/",
                "https://minechecker.com/status/java/",
                "https://mcsrvstat.us/server/",
                "https://mcstatus.io/status/java/",
                "https://minecraftpinger.com/?server=",
                "https://minecraftserverstatus.com/server?url=",
                "https://api.minetools.eu/ping/",
                "https://minerank.com/pages/server-status-checker?host=",
            ):
                if elem.startswith(domain):
                    elem = elem.split(domain, 1)[1]
            
            # if elem.startswith("https://"):
                # print(f"WARN: Url {elem} starts with https")
            
            if "/" in elem:
                elem = elem.split("/")[0]
            if "?" in elem:
                elem = elem.split("?")[0]
                
            
            content[i] = elem 
        
        content = list(set(content))

        for i, element in enumerate(content):
            self.pages_parsed = i + 1
            self.print_status()
            self.parse_elements(element.split(" ")[0].strip(), i+1, len(content))
            self.print_status()
            if self.pages_parsed >= self.max_count:
                break
            
        for future in self.futures:
            server_entry = future.result()
            if server_entry:
                self.all_servers.append(server_entry)
        self.executor.shutdown(wait=True)
            
        print(f"\nDone, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, server: str, num: int, total: int):
        future = self.executor.submit(self.check_server, server)
        self.futures.append(future)


    def print_ask(self, ip: str, status: JavaStatusResponse, i: int):
        print(f"============================== {i}/{len(self.all_servers)} ==============================")

        lines = [
            f"ip: {ip}",
            f"Player: {status.players.online}/{status.players.max}",
            f"ping: {status.latency}",
            *get_formatted_motd(status),
            "",
            f"version name/protocol: {status.version.name}, {status.version.protocol}"
        ]

        print_with_icon(status.icon, lines, img_width=15, padding=2)

        print("\n")
        ask_duplicate(ip, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers):
            self.print_ask(*server, i)

def setup() -> ParserMeta:
    return ParserMeta(
        "TextFile",
        "~none~",
        "1.0",
        termcolor.rgb(50, 150, 150),
        TextFileParser,
        run_bulk=False
    )
