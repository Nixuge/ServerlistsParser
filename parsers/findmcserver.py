from dataclasses import dataclass
import json
from selenium.webdriver.common.by import By

from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser
from classes.ParserMeta import ParserMeta
from utils.color import termcolor
from utils.miscutils import ask_duplicate, is_already_present
from utils.serverchecks import ServerValidator

@dataclass
class Server:
    name: str
    playercount: int
    max_players: int
    desc: str
    ip: str
    port: str
    is_bedrock: bool
    ip_port: str = ""

class FindMcServerParser(CloudflareParser):
    PRINT_HIDDEN_IPS = False

    all_servers: list[Server]
    hidden_ips: set
    def __init__(self) -> None:
        super().__init__(
            "https://findmcserver.com/api/servers?pageNumber=%PAGE%&pageSize=15&sortBy=name_asc",
            CFSeleniumOptions((By.CSS_SELECTOR, "pre"))
        )
        self.all_servers = []
        self.hidden_ips = set()

    def ask_config(self):
        pass
        
    def get_parse_everything(self):
        self.isEmpty = False
        page = 0
        while not self.isEmpty:
            data = self.get_page(page)
            page += 1
            self.parse_elements(data)
            print(f"\rParsed page {page}...", end="")
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str):
        servers_raw = []
        if "<html>" in data:
            raise Exception("not yet implemented, see below on source")
            # previous selenium implementation, to redo w beautifulsoup or similar if this actually triggers CF & switches to selenium (which i havent been able to reproduce)
            # driver = webdriver.Firefox(options=SELENIUM_FIREFOX_OPTIONS)
            # driver.get(f"https://findmcserver.com/api/servers?pageNumber={page}&pageSize=15&sortBy=name_asc")
            # data = json.loads(driver.find_element(By.CSS_SELECTOR, "pre").text)["data"]
            # driver.close()
        data = json.loads(data)["data"]
        if len(data) == 0:
            self.isEmpty = True
        servers_raw += data
        
        # Parse raw json to Server objects
        servers_parsed: list[Server] = []
        for server in servers_raw:
            same_params = (
                server["name"], 
                int(server["currentOnlinePlayers"]),
                int(server["currentMaxPlayers"]),
                server["shortDescription"],
            )
            if server["bedrockAddress"]:
                servers_parsed.append(Server(*same_params, server["bedrockAddress"], server["bedrockPort"], True))
            if server["javaAddress"]:
                servers_parsed.append(Server(*same_params, server["javaAddress"], server["javaPort"], False))
        
        # Filter out bad servers
        for server in servers_parsed:
            # Set port
            if not server.port: server.port = "19132" if server.is_bedrock else "25565"
            # Set ip_port
            to_replace = ":19132" if server.is_bedrock else ":25565"
            server.ip_port = f"{server.ip}:{server.port}".replace(to_replace, "")
            
            # Hidden IP check
            if server.ip == "IP Address Hidden":
                self.hidden_ips.add(server.name)
                continue
            
            # If bedrock, only run already_present check
            if server.is_bedrock:
                if is_already_present(server.ip_port, True):
                    continue
            # Otherwise run whole ServerValidator on Java servers
            else:
                serverCheck = ServerValidator(server.ip_port, self.PRINT_HIDDEN_IPS).is_valid_mcstatus()
                if not serverCheck:
                    continue
            
            self.all_servers.append(server)
        
            
    def print_ask(self, server: Server):
        v_str = "BEDROCK" if server.is_bedrock else "JAVA"

        print("====================")
        print(f"Name: {server.name} | {v_str}")
        print(f"ip: {server.ip_port}, {server.playercount}/{server.max_players}")
        print(f"desc: {server.desc}")
        print("====================")
        ask_duplicate(f"{server.ip_port}", server.is_bedrock)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)
        
        # Can be removed here, since it's now grabbed in parse_elements
        if self.PRINT_HIDDEN_IPS:
            print(f"Hidden IP addresses: {self.hidden_ips}")

def setup() -> ParserMeta:
    return ParserMeta("Official Mojang Serverlist", "findmcserver.com", "1.0", termcolor.rgb(82, 165, 53), FindMcServerParser)