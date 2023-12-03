from dataclasses import dataclass
import os
import re
import socket

import mcstatus.status_response
from classes.BaseParser import BaseParser

from classes.ParserMeta import ParserMeta

from utils.miscutils import ask_duplicate, is_already_present
from utils.motdutils import motd_remove_section_signs

# Good old REALLY DIRTY scraper, been a while since i wrote one like that w splits & regexes mixed.

def is_ipv4(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False
    

@dataclass
class BlockedServerEntry:
    hash: str
    ip: str
    status: mcstatus.status_response.JavaStatusResponse

class BlockedServerParser(BaseParser):
    all_servers: list[BlockedServerEntry]
    down_servers: list[str]
    def __init__(self) -> None:
        self.all_servers = []
        self.down_servers = []

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
        if not os.path.isfile("data/DOWN.txt"):
            open("data/DOWN.txt", "a").close()
        else:
            try: self.down_servers = open("data/DOWN.txt").read().strip().split("\n")
            except Exception as e: print(e)
        self.parse_elements()
    
    def parse_elements(self):
        with open("data/blockedserverstwitter.har") as file:
            content = file.read()

        elems = content.split("has been unblocked by Mojang!")
        lenelems = len(elems[:-1])
        for index, elem in enumerate(elems[:-1]):
            text = re.findall('"(.{40}) \((.*?)\)', elem)[0]
            correct_url = text[1]
            if "https://t.co" in text[1]:
                # Handle servers w a name that's clickable
                correct_url = re.findall('\{\\\\\"display_url\\\\\":\\\\\"([a-zA-Z0-9-\.]*?)\\\\\",\\\\\"expanded_url\\\\\":\\\\\"[a-zA-Z0-9\.\:/-]*?\\\\\",\\\\\"url\\\\\":\\\\\"' + text[1] + '\\\\\"', elem)[0]

            print(f"Processing {index}/{lenelems}")
            server = BlockedServerEntry(text[0], correct_url, None)
            good_server = self.check_element_mcstatus(server)
            if good_server:
                self.all_servers.append(good_server)
    
    def check_element_mcstatus(self, server: BlockedServerEntry):
        if not '.' in server.ip:
            print("invalid ip, skipping")
            return
        if server.ip == "Hostname not yet known":
            print("no hostname known, skipping")
            return
        if is_already_present(server.ip):
            print("already known, skipping")
            return
        if server.ip.endswith("minehut.gg"):
            print("ip from hosting provider, skipping")
            return
        if server.ip.endswith(".ddns.net") or "hopto.org" in server.ip:
            print("ddns server, skipping")
            return
        if is_ipv4(server.ip):
            print("is ipv4, skipping")
            return
        
        if server.ip in self.down_servers:
            print(f"server down: {server.ip}")
            return
        
        working_ip = False

        if server.ip.startswith("*."):
            print("Server starts with a *")
            stripped_ip = server.ip[2:]
            server_status = None
            for prefix in ["", "mc.", "play."]:
                ip_full = prefix + stripped_ip
                print(f"Trying {ip_full}")
                server_status = self.req_stats(ip_full)
                if server_status: 
                    working_ip = ip_full
                    break
        else:
            print(f"Trying {server.ip}")
            server_status = self.req_stats(server.ip)
            if server_status: working_ip = server.ip

        if not server_status:
            self.add_down_server(server.ip)
            print("NO SERVER STATUS")
            return False
        
        return BlockedServerEntry(server.hash, working_ip, server_status)
        

    def add_down_server(self, ip: str):
        self.down_servers.append(ip)
        with open("data/DOWN.txt", "a") as file:
            file.write(f"{ip}\n")

    def req_stats(self, ip: str):
        try:
            return mcstatus.JavaServer(ip).status()
        except:
            return

    def print_ask(self, server: BlockedServerEntry):
        server_status = server.status
        if "§cInvalid hostname. §7Please refer to our documentation at docs.tcpshield.com" in server_status.description:
            print("invalid tcpshield hostname.")
            return
        if "Papyrus.vip§r§b §r§8- §r§cUnknown Host" in server_status.description:
            print("invalid papyrus hostname.")
            return
        print("====================")
        print(f"ip: {server.ip}")
        print(f"motd: {motd_remove_section_signs(server_status.description)}")
        print(f"version name/protocol: {server_status.version.name}, {server_status.version.protocol}")
        print(f"Player: {server_status.players.online}/{server_status.players.max}")
        print(f"ping: {server_status.latency}")
        print("hash: " + server.hash)

        ask_duplicate(server.ip, False)
    
    def print_ask_all(self):
        for server in self.all_servers:
            self.print_ask(server)

def setup() -> ParserMeta:
    return ParserMeta("BlockedServers", "twitter.com/BlockedServers", "0.1", BlockedServerParser)

# Honestly not worth using rn.
# maybe (MAYBE) when i've implemented mcstatus & a "down server list" in here directly
# 1 / 0