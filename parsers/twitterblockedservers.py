from dataclasses import dataclass
import os
import re
from classes.BaseParser import BaseParser

from classes.ParserMeta import ParserMeta

from utils.miscutils import ask_duplicate, is_already_present

# Good old REALLY DIRTY scraper, been a while since i wrote one like that w splits & regexes mixed.

@dataclass
class BlockedServerEntry:
    hash: str
    ip: str

class BlockedServerParser(BaseParser):
    all_servers: list[BlockedServerEntry]
    def __init__(self) -> None:
        self.all_servers = []

    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        if not os.path.isfile("data/blockedserverstwitter.har"):
            open("data/blockedservers.html", "a").close()
            print("File blockedserverstwitter.har didn't exist. Now created. Please put your data in it.")
            print("To get the data, open the devtools, go to the network tab, search for")
            print("'from:BlockedServers has been unblocked' on twitter, filter requests by 'SearchTimeline', then")
            print("right click>save all as HAR")
            return
        self.parse_elements()
    
    def parse_elements(self):
        with open("data/blockedserverstwitter.har") as file:
            content = file.read()

        elems = content.split("has been unblocked by Mojang!")
        for elem in elems[:-1]:
            text = re.findall('"(.{40}) \((.*?)\)', elem)[0]
            correct_url = text[1]
            if "https://t.co" in text[1]:
                # Handle servers w a name that's clickable
                correct_url = re.findall('\{\\\\\"display_url\\\\\":\\\\\"([a-zA-Z0-9-\.]*?)\\\\\",\\\\\"expanded_url\\\\\":\\\\\"[a-zA-Z0-9\.\:/-]*?\\\\\",\\\\\"url\\\\\":\\\\\"' + text[1] + '\\\\\"', elem)[0]

            self.all_servers.append(BlockedServerEntry(text[0], correct_url))
    
    def print_ask(self, server: BlockedServerEntry):
        if server.ip == "Hostname not yet known" or is_already_present(server.ip) or not '.' in server.ip:
            return
        if server.ip.endswith(".ddns.net"):
            print("ddns server, skipping")
            return

        print("====================")
        print(f"ip: {server.ip}")
        print("hash: " + server.hash)

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("BlockedServers", "twitter.com/BlockedServers", "0.1", BlockedServerParser)

