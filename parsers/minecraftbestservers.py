import ast
from dataclasses import dataclass
import json
import re

from bs4 import BeautifulSoup, Tag

from selenium.webdriver.common.by import By

from classes.CloudflareParser import CloudflareParser
from classes.CloudflareParser import CFSeleniumOptions
from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from utils.miscutils import ask_duplicate
from utils.serverchecks import ServerValidator
from mcstatus.status_response import JavaStatusResponse

import mcstatus

@dataclass
class JavaServer:
    ip: str
    name: str
    playercount: str
    themes: list[str]
    status: JavaStatusResponse


class MinecraftBestServersParser(CloudflareParser):
    all_servers: list 
    max_page: int
    bedrock: bool
    java: bool
    def __init__(self) -> None:
        super().__init__(
            "https://minecraftbestservers.com/pg.%PAGE%", 
            CFSeleniumOptions((By.XPATH, '//*[@id="content-container"]/a[1]/div[2]'))
        )
        self.all_servers = []

    def ask_config(self):
        page = input("Enter the max page to go for (nothing for 30): ")
        if page.strip() == "":
            self.max_page = 30
        else:
            self.max_page = int(page)

        self.java = input("Should we add Java servers? (Y/n)").strip().lower() in ["", "y", "o"]
        self.bedrock = input("Should we add Bedrock servers? (y/N)").strip().lower() in ["y", "o"]

    def get_parse_everything(self):
        self.is_empty = False
        page = 1
        while not self.is_empty and page <= self.max_page:
            print(f"\rGrabbing page {page}...", end="")
            data = self.get_page(page)
            self.parse_elements(data)
            print(f" {len(self.all_servers)} elements", end="")
            page += 1
        print()

        # self.driver.close()
        print(f"Done, got {len(self.all_servers)} new servers.")
    
    def parse_elements(self, data: str):
        soup = BeautifulSoup(data, 'html.parser')
        cards: list[Tag] = soup.find_all("a", {"class": "bg-white mb-4 block md:grid lg:grid-cols-[1fr_260px]"}) # pyright: ignore[reportAssignmentType]
        if len(cards) == 0:
            self.is_empty = True

        # print()
        for card in cards:
            # print(card)

        #     header = card.find("div", {"class": "mb-3 flex w-full items-center lg:mb-0 lg:w-auto"})
        #     name = header.find("h3", {"class": "mr-2 font-bold text-brand-900 lg:mr-3"}).text # type: ignore

            java_ip = card.find("input", {"class": "cursor-pointer text-green-700 bg-transparent font-bold text-inter text-center focus:outline-hidden"}).attrs.get("value") # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]
            if not java_ip:
                continue
            else:
                java_ip = str(java_ip)
            
            themes = card.find_all("div", {"class": "rounded-md px-2 text-sm font-bold m-1"})
            themes = [theme.text for theme in themes]

            server_name_number = card.find("div", {"class": "text-xl font-bold text-gray-900 flex items-center justify-center lg:justify-start ml-1"}).text # pyright: ignore[reportOptionalMemberAccess]
            server_name_number = server_name_number.strip().replace("\n", ": ")

            online = card.find("div", {"class": "flex items-center justify-center lg:justify-start"})
            if online:
                online = online.text.strip().replace(" players online", "")
            else:
                online = online = card.find("div", {"class": "flex items-center justify-center lg:justify-start text-red-500"}).text # pyright: ignore[reportOptionalMemberAccess]

            full_bedrock_java_ip: str = card.find("button", {"class": "bg-[#31a936] shadow-sm border-b-4 border-black/10 rounded-md text-white font-bold py-4 px-6 mb-2 transition-transform hover:scale-105 hidden md:flex"}).attrs.get("@click.prevent") # type: ignore
            full_bedrock_java_ip = full_bedrock_java_ip.replace("$store.page.openServer('", "")
            java_ip_inner = full_bedrock_java_ip.split("'")[0]
            full_bedrock_java_ip = ", ".join(full_bedrock_java_ip.split(", ")[1:])
            full_bedrock_java_ip = full_bedrock_java_ip.removesuffix(")")
            
            fixed_string = re.sub(r" (\w+): ", r' "\1": ', full_bedrock_java_ip)
            
            try:
                data = ast.literal_eval(fixed_string)
            except Exception as e:
                print("FAILED TO JSON LOADS: " + str(e))
                print(fixed_string)
                print(full_bedrock_java_ip)

            # TODO: Add Bedrock support
            serverCheck = ServerValidator(java_ip, False).is_valid_mcstatus()
            if serverCheck:
                entry = JavaServer(java_ip, server_name_number, online, themes, serverCheck)
                self.all_servers.append(entry)

        pass

    def print_ask(self, server: JavaServer):
        print("====================")
        print(f"{server.name}")
        print(f"ip: {server.ip}, {server.status.players.online}/{server.status.players.max} ({server.playercount}) online")
        print(f"themes: {', '.join(server.themes)}")

        print(f"motd: {server.status.motd.to_ansi()}")
        print(f"version: {server.status.version.name}")
        
        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("minecraftbestservers", "minecraftbestservers.com", "0.1", termcolor.rgb(227, 152, 82), MinecraftBestServersParser)
