from dataclasses import dataclass
import json
import os
from typing import Optional

from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta
from utils.fileutils import add_server_dupe

from utils.miscutils import ask_duplicate, is_already_present
from utils.serverchecks import ServerValidator

@dataclass
class LunarServer:
    id: str
    name: str
    website: Optional[str]
    description: Optional[str] # Unlike what's written in the doc, this can be optional (eg 2b2t)
    addresses: list[str]
    primary_address: str
    versions: list[str]
    primary_version: str
    crossplay: bool
    playercount: Optional[int]
    max_players: Optional[int]
    motd: Optional[str]


class LunarServerMappingsParser(BaseParser):
    CACHE_DIR = "cache/lunarservermappings"
    GIT_DIR = f"{CACHE_DIR}/ServerMappings"

    show_inactive: bool
    amount_to_process: int

    all_servers: list[LunarServer]
    inactive: list[str]

    def __init__(self) -> None:
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        os.system(f"cd {self.CACHE_DIR} && git clone https://github.com/LunarClient/ServerMappings")

        self.all_servers = []
        with open(f"{self.GIT_DIR}/inactive.json") as f:
            self.inactive = json.load(f)

    def ask_config(self):
        self.show_inactive = input("Show inactive servers? (y/N): ").lower() in ('n', '')
        try: 
            self.amount_to_process = int(input("How many servers folders do you want to process at most for this run?: "))
        except:
            print("Bad input, defaulting to all servers.")
            self.amount_to_process = 99999999

    def get_parse_everything(self):
        files = os.listdir(f"{self.GIT_DIR}/servers")
        files.sort()

        for i in range(min(self.amount_to_process, len(files))):
            file = files[i]
            if file in self.inactive:
                continue

            self.parse_elements(file)

        # self.driver.close()
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str):
        with open(f"{self.GIT_DIR}/servers/{data}/metadata.json") as f:
            json_data: dict = json.load(f)

        print("Server: " + data)

        # Including multiple urls is redundant and as per the doc, those are all the possible fields. Try to grab all of them in the given order, otherwise null.
        main_website = json_data.get("website",
                        json_data.get("store", 
                        json_data.get("wiki", 
                        json_data.get("merch", None))))
    
        server = LunarServer(
            id = json_data["id"],
            name = json_data["name"],
            website = main_website,
            description = json_data.get("description"),
            addresses = json_data["addresses"],
            primary_address = json_data["primaryAddress"],
            versions = json_data["minecraftVersions"],
            primary_version = json_data["primaryMinecraftVersion"],
            crossplay = json_data.get("crossplay", False),
            playercount = None,
            max_players = None,
            motd = None
        )
        
        server_check = ServerValidator(server.primary_address, True).is_valid_mcstatus()
        if not server_check:
            return
        
        server.playercount = server_check.players.online
        server.max_players = server_check.players.max
        server.motd = server_check.motd.to_ansi()
        
        self.all_servers.append(server)

    def print_ask(self, server: LunarServer):
        print("====================")
        website = ' - ' + server.website if server.website else ''
        print(f"name: {server.name} {server.playercount}/{server.max_players} (id: {server.id}){website}")
        print(f"ip: {server.primary_address} ({", ".join(server.addresses)})")
        if server.description:
            print(f"description: {server.description}")

        print(f"motd: {server.motd}")
        if len(server.versions) == 1 and server.versions[0] == server.primary_version:
            print(f"version: {server.primary_version}")
        else:
            print(f"version: {server.primary_version} ({", ".join(server.versions)}))")
        
        ask_duplicate(server.primary_address, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("Lunar Server Mappings", "github.com/LunarClient/ServerMappings", "1.0", LunarServerMappingsParser)
