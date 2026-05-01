from dataclasses import dataclass
import json
import os
from typing import Optional

from mcstatus.responses import JavaStatusResponse

from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta
from utils.color import termcolor
from utils.fileutils import add_server_dupe

from utils.miscutils import ask_duplicate, is_already_present
from utils.motdutils import get_formatted_motd
from utils.termutils import print_with_icon
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
    status: JavaStatusResponse


class LunarServerMappingsParser(BaseParser):
    CACHE_DIR = "cache/lunarservermappings"
    GIT_DIR = f"{CACHE_DIR}/ServerMappings"

    show_inactive: bool
    amount_to_process: int

    all_servers: list[LunarServer]
    inactive: list[str]

    def __init__(self) -> None:
        super().__init__()
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        os.system(f"cd {self.CACHE_DIR} && git clone https://github.com/LunarClient/ServerMappings")
        os.system(f"cd {self.CACHE_DIR} && cd ServerMappings && git pull")

        self.all_servers = []
        with open(f"{self.GIT_DIR}/inactive.json") as f:
            self.inactive = json.load(f)

    def ask_config(self):
        self.show_inactive = input("Show inactive servers? (y/N): ").lower() == 'y'
        try: 
            self.amount_to_process = int(input("How many servers folders do you want to process at most for this run?: "))
        except:
            print("Bad input, defaulting to all servers.")
            self.amount_to_process = 99999999

    def check_server(self, server: LunarServer):
        server_check = ServerValidator(server.primary_address, False).is_valid_mcstatus()
        # server_check = ServerValidator(server.primary_address, True).is_valid_mcstatus()

        with self.print_lock:
            self.servers_requested += 1
            if server_check:
                self.valid_servers_found += 1
            self.print_status()
        if not server_check:
            return None
        
        server.status = server_check
        
        return server

    def get_parse_everything(self):
        files = os.listdir(f"{self.GIT_DIR}/servers")
        files.sort()

        for i in range(min(self.amount_to_process, len(files))):
            self.pages_parsed = i + 1
            file = files[i]
            if not self.show_inactive and file in self.inactive:
                continue

            self.parse_elements(file, i, len(files))
            self.print_status()

        for future in self.futures:
            server_entry = future.result()
            if server_entry:
                self.all_servers.append(server_entry)
        self.executor.shutdown(wait=True)

        print(f"\nDone, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str, current: int, max: int):
        try: # Required because of ONE server that has a trailing comma after the version list
            with open(f"{self.GIT_DIR}/servers/{data}/metadata.json") as f: 
                json_data: dict = json.load(f)
        except:
            return

        # Including multiple urls is redundant and as per the doc, those are all the possible fields. Try to grab all of them in the given order, otherwise null.
        main_website = json_data.get("website",
                        json_data.get("store", 
                        json_data.get("wiki", 
                        json_data.get("merch", None))))

        if not json_data.get("primaryAddress"):
            return
        if not json_data.get("minecraftVersions"):
            return
        
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
            status=None # type: ignore , bit dirty but meh
        )
        
        future = self.executor.submit(self.check_server, server)
        self.futures.append(future)

    def print_ask(self, server: LunarServer, i: int):
        print(f"============================== {i}/{len(self.all_servers)} ==============================")
        status = server.status
        website = f" - {server.website}" if server.website else ""
        
        lines = [
            f"name: {server.name} (id: {server.id}){website}",
            f"ip: {server.primary_address} ({', '.join(server.addresses)})",
            f"players: {status.players.online}/{status.players.max}",
        ]
        
        if server.description:
            lines.append(f"description: {server.description}")
            
        lines.extend([
            *get_formatted_motd(status),
            "",
        ])
        
        if len(server.versions) == 1 and server.versions[0] == server.primary_version:
            lines.append(f"version: {server.primary_version}")
        else:
            lines.append(f"version: {server.primary_version} ({', '.join(server.versions)})")

        print_with_icon(status.icon, lines, img_width=15, padding=2)
        print("\n")
        ask_duplicate(server.primary_address, False)
    
    def print_ask_all(self):
        for i, server in enumerate(self.all_servers):
            self.print_ask(server, i+1)

def setup() -> ParserMeta:
    return ParserMeta(
        "Lunar Server Mappings",
        "github.com/LunarClient/ServerMappings",
        "1.0",
        termcolor.rgb(255, 255, 255),
        LunarServerMappingsParser,
        run_bulk=False
    )
