from dataclasses import dataclass
import json
import os
from typing import Optional

from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta
from utils.color import termcolor

from utils.miscutils import ask_duplicate
from utils.serverchecks import ServerValidator
from mcstatus.status_response import JavaStatusResponse

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

        for i in range(min(self.amount_to_process, len(files))):
            file = files[i]

            self.parse_elements(file, i, len(files))

        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str, current: int, max: int):
        # try: 
        with open(f"{self.GIT_DIR}/minecraft_servers/{data}/manifest.json") as f: 
            json_data: dict = json.load(f)
        # except:
            # print("Failed to decode json for server: " + data)
            # return

        print(f"Server: {data} ({current+1}/{max})", end = " - ")

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
        print()
        server_check = ServerValidator(ip, True).is_valid_mcstatus()
        if not server_check:
            return
        
        server = LabyServer(
            name = name,
            raw_name = raw_name,
            website = main_website,
            color = color,
            languages = languages,
            location = location,
            ip = ip,
            status = server_check
        )
        
        self.all_servers.append(server)

    def print_ask(self, server: LabyServer):
        status = server.status
        print("====================")
        if server.color:
            print(server.color, end="")
        print(f"name: {server.name} {status.players.online}/{status.players.max} ({server.raw_name}){termcolor.RESET}")

        print(f"ip: {server.ip}, location: {server.location} ({server.website})")

        print(f"motd: {status.motd.to_ansi()}")
        print(f"version: {status.version.name}")

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta(
        "LabyMod Server Media",
        "github.com/LabyMod/server-media",
        "1.0",
        termcolor.rgb(48, 132, 209),
        LabymodServerMediaParser,
        run_bulk=False
    )
