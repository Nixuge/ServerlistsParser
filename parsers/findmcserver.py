import json
from selenium.webdriver.common.by import By

from classes.CloudflareParser import CFSeleniumOptions, CloudflareParser
from classes.ParserMeta import ParserMeta
from utils.miscutils import ask_duplicate, is_already_present


class FindMcServerParser(CloudflareParser):
    PRINT_HIDDEN_IPS = True

    all_servers: list
    hidden_ips: set
    def __init__(self) -> None:
        super().__init__(
            "https://findmcserver.com/api/servers?pageNumber=%PAGE%&pageSize=15&sortBy=name_asc",
            CFSeleniumOptions((By.CSS_SELECTOR, "pre"))
        )
        self.all_servers = []
        self.hidden_ips = set()

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
        self.all_servers += data
    
    def print_ask(self, name, ip, port, online_p, max_p, desc, bedrock):
        if not port:
            port = "19132" if bedrock else "25565"
        
        if ip == "IP Address Hidden":
            self.hidden_ips.add(name)
            return

        str_port = f":{port}".replace(":19132", "") if bedrock else f":{port}".replace(":25565", "")
        ip_port = f"{ip}{str_port}"
        if is_already_present(ip_port, bedrock):
            return
        
        v_str = "BEDROCK" if bedrock else "JAVA"

        print("====================")
        print(f"Name: {name} | {v_str}")
        print(f"ip: {ip_port}, {online_p}/{max_p}")
        print(f"desc: {desc}")
        print("====================")
        ask_duplicate(f"{ip_port}", bedrock)
    
    def print_ask_all(self):
        for elem in self.all_servers:
            max_p = elem["currentMaxPlayers"]
            online_p = elem["currentOnlinePlayers"]
            name = elem["name"]
            desc = elem["shortDescription"]
            
            bedrock_ip = elem["bedrockAddress"]
            bedrock_port = elem["bedrockPort"]
            java_ip = elem["javaAddress"]
            java_port = elem["javaPort"]
            
            if bedrock_ip:
                self.print_ask(name, bedrock_ip, bedrock_port, online_p, max_p, desc, True)
            if java_ip:
                self.print_ask(name, java_ip, java_port, online_p, max_p, desc, False)
        
        if self.PRINT_HIDDEN_IPS:
            print(f"Hidden IP addresses: {self.hidden_ips}")

def setup() -> ParserMeta:
    return ParserMeta("Official Mojang Serverlist", "findmcserver.com", "1.0", FindMcServerParser)