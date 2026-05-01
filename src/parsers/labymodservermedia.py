from dataclasses import dataclass
import json
import os
from typing import Optional

from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta
from utils.color import termcolor

from utils.miscutils import ask_duplicate
from utils.motdutils import get_formatted_motd
from utils.termutils import print_with_icon
from utils.serverchecks import ServerValidator
from mcstatus.responses import JavaStatusResponse

@dataclass
class LabyServer:
    name: str
    raw_name: str
    website: Optional[str]
    color: Optional[str]
    languages: str
    location: str
    ip: str
    status: JavaStatusResponse


class LabymodServerMediaParser(BaseParser):
    CACHE_DIR = "cache/labymodservermedia"
    GIT_DIR = f"{CACHE_DIR}/server-media"

    amount_to_process: int

    all_servers: list[LabyServer]

    def __init__(self) -> None:
        super().__init__()
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        os.system(f"cd {self.CACHE_DIR} && git clone https://github.com/LabyMod/server-media/")
        os.system(f"cd {self.CACHE_DIR} && cd server-media && git pull")

        self.all_servers = []

    def ask_config(self):
        try: 
            self.amount_to_process = int(input("How many servers folders do you want to process at most for this run?: "))
        except:
            print("Bad input, defaulting to all servers.")
            self.amount_to_process = 99999999

    def get_parse_everything(self):
        files = os.listdir(f"{self.GIT_DIR}/minecraft_servers")
        files.sort()

        total = min(self.amount_to_process, len(files))
        for i in range(total):
            self.pages_parsed += 1
            file = files[i]
            future = self.executor.submit(self.check_server, file, total)
            self.futures.append(future)

        for future in self.futures:
            result = future.result()
            if result:
                self.all_servers.append(result)

        self.executor.shutdown(wait=True)
        print(f"\nDone, got {len(self.all_servers)} new servers.")

    def parse_elements(self, data: str):
        pass # Not used

    def check_server(self, file: str, total: int) -> Optional[LabyServer]:
        with open(f"{self.GIT_DIR}/minecraft_servers/{file}/manifest.json") as f: 
            json_data: dict = json.load(f)

        social: Optional[dict] = json_data.get("social")
        main_website = None
        if social:
            main_website = social.get("web",
                            social.get("web_support", 
                            social.get("web_shop", None)))
            
        brand: Optional[dict] = json_data.get("brand")
        color = None
        if brand:
            color = brand.get("primary",
                brand.get("text", 
                brand.get("background", None)))
        if color:
            color = termcolor.hex(color)
        
        raw_name = json_data["server_name"] # Could also be just data, just in case
        name = json_data["nice_name"]
        ip = json_data["direct_ip"]
        
        languages = ", ".join(json_data.get("supported_languages", ("Unknown")))

        locjson: Optional[dict] = json_data.get("location")
        location = ""
        if locjson:
            location += locjson.get("country", "")

            city = locjson.get("city")
            if city:
                if location == "": location = city
                else: location += f", {city}"
            
            code = locjson.get("country_code")
            if code:
                if location == "": location = f"({code})"
                else: location += f" ({code})"

        server_check = ServerValidator(ip, False).is_valid_mcstatus()
        # server_check = ServerValidator(ip, True).is_valid_mcstatus()

        with self.print_lock:
            self.servers_requested += 1
            if server_check:
                self.valid_servers_found += 1
            self.print_status(total)

        if not server_check:
            return None
        
        return LabyServer(
            name = name,
            raw_name = raw_name,
            website = main_website,
            color = color,
            languages = languages,
            location = location,
            ip = ip,
            status = server_check
        )

    def print_ask(self, server: LabyServer, i: int):
        status = server.status
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
                
        color_prefix = server.color if server.color else ""

        lines = [
            f"{color_prefix}name: {server.name} {status.players.online}/{status.players.max} ({server.raw_name}){termcolor.RESET}",
            f"ip: {server.ip}, location: {server.location} ({server.website})",
            *get_formatted_motd(status),
            "",
            f"version: {status.version.name}"
        ]

        print_with_icon(status.icon, lines, img_width=15, padding=2)

        print("\n")
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "LabyMod Server Media",
        "github.com/LabyMod/server-media",
        "1.0",
        termcolor.rgb(48, 132, 209),
        LabymodServerMediaParser,
        run_bulk=False
    )
