import os
import socket
from typing import Literal

import mcstatus

from utils.miscutils import is_already_present
from utils.motdutils import motd_remove_section_signs
from mcstatus.status_response import JavaStatusResponse

from utils.vars import CHECK_FAILED_SERVER_CACHE



def is_ipv4(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False

class FailedServers:
    failed: list[str]
    def __init__(self) -> None:
        if not os.path.isfile("cache/statusfailed.txt"):
            open("cache/statusfailed.txt", "a").close()
            self.failed = []
        else:
            with open("cache/statusfailed.txt") as file:
                self.failed = file.read().strip().split("\n")

    def is_failed(self, ip: str) -> bool:
        return ip in self.failed
    
    def add_failed(self, ip: str):
        self.failed.append(ip)
        with open("cache/statusfailed.txt", "a") as file:
            file.write(f"{ip}\n")


class ServerValidator:
    ip: str
    print_reason: bool
    default_motd_invalid: bool
    def __init__(self, ip: str, print_reason: bool = False, default_motd_invalid: bool = True) -> None:
        self.ip = ip
        self.print_reason = print_reason
        self.default_motd_invalid = default_motd_invalid

    def is_valid_mcstatus(self) -> Literal[False] | JavaStatusResponse:
        if not self.is_valid():
            if self.print_reason: print(f"Server is invalid")
            return False
        
        if CHECK_FAILED_SERVER_CACHE and FAILED_SERVERS.is_failed(self.ip):
            if self.print_reason: print(f"Server is in failed servers cache")
            return False
        
        try:
            status = mcstatus.JavaServer.lookup(self.ip).status(version=773)

            motd = motd_remove_section_signs(status.description)
            motd_valid, motd_valid_reason = MOTD_VALIDATOR.is_motd_valid(self.ip, motd, self.default_motd_invalid)
            if not motd_valid:
                if self.print_reason: print(f"motd invalid: {motd_valid_reason}")
                return False
            return status
        except Exception as e:
            if self.print_reason: print(f"exception happened pinging: {e}")
            FAILED_SERVERS.add_failed(self.ip)
            return False


    def is_valid(self) -> bool:
        if not self._is_server_valid_string(): return False
        if MOTD_VALIDATOR.is_ip_in_motd_cache(self.ip): return False
        return True

    def _get_mcstatus(self, ip: str) -> Literal[False] | JavaStatusResponse:
        try:
            status = mcstatus.JavaServer(ip).status()
            self.motd = motd_remove_section_signs(status.description)
            return status
        except:
            return False

    def _is_server_valid_string(self):
        def dprint(*args): 
            if self.print_reason: print(*args)
        
        if is_already_present(self.ip):
            dprint("already known, skipping")
            return False
        
        if ":" in self.ip:
            ip_alone = self.ip.split(":")[0].lower()
        else:
            ip_alone = self.ip.lower()

        bad_ends = [
            "minehut.gg",
            ".ddns.net",
            "serveminecraft.net", # ddns
            "aternos.me",
            "aternos.host",
            "exaroton.me",
            "eagler.host",
            # Start playit part
            "playit.buzz",
            "playit.cafe",
            "playit.city",
            "playit.fan",
            "playit.game",
            ".at.ply.gg",
            "d6.ply.gg",
            "joinmc.link",
            "playit.love",
            "playit.ooo",
            "minecraft.party",
            "terraria.party",
            "playit.plus",
            "*.at.playit.plus",
            "with.playit.plus",
            "terraria.pro",
            "playit.pub",
            "playit.quest",
            # End playit part
            "pyro.social",
            "pebble.host",
            "minecraft.vodka", # lilypad
            "play.hosting", # lilypad partnered free hosting
            "shockbyte.cc",
            "duckdns.org",
            "mysrv.us", #sparkedhost
            "craft.gg", #omgserv
            "serv.nu", #server.pro
            "serv.gs", #server.pro
            "ferox.host", #feroxhosting.nl
            "srvplay.eu", #unknown
            "jogar.io", #unknown
            "qzz.io", # domain.digitalplat.org, free domain
            "g-portal.game", # g-portal game host
            "serv.cx", # mintservers.com
            "playwm.co", #winternode apparently?
            "ethera.net", # ethera game host
            "bed.ovh", # bedhosting.com.br
            "modded.fun", # bisecthosting
            "gomc.fun", # russian game hosting
            "atbphosting.com",
            "lagfree.me", # TensionHost.com
            "my-smp.net", # foliumhosting,
            "mine.fun", #minestrator
        ]

        for end in bad_ends:
            if ip_alone.endswith(end):
                dprint(f"bad server: ip ends with {end}")
                return False

        if is_ipv4(ip_alone):
            dprint("is ipv4, skipping")
            return False
        
        return True

class MotdValidator:
    invalid_ips_motd: list[str]
    def __init__(self) -> None:
        if not os.path.isfile("cache/motdinvalid.txt"):
            open("cache/motdinvalid.txt", "w").close()
            self.invalid_ips_motd = []
        else:
            with open("cache/motdinvalid.txt") as file:
                self.invalid_ips_motd = file.read().strip().split("\n")
    
    def is_ip_in_motd_cache(self, ip: str):
        return ip in self.invalid_ips_motd
    
    def is_motd_valid(self, ip: str, motd: str, default_motd_invalid: bool) -> tuple[bool, str | None]:
        if self.is_ip_in_motd_cache(ip):
            return False, "Already present in cache."
        valid, reason = self._check_motd_str(motd, default_motd_invalid)
        if not valid:
            self._add_ip_cache(ip)
        return valid, reason

    def _add_ip_cache(self, ip: str):
        self.invalid_ips_motd.append(ip)
        with open("cache/motdinvalid.txt", "a") as file:
            file.write(f"ip\n")
    
    @staticmethod
    def _check_motd_str(motd: str, default_motd_invalid: bool) -> tuple[bool, str | None]:
        if "Invalid hostname. Please refer to our documentation at docs.tcpshield.com" in motd:
            return False, "tcpshield"
        if "Papyrus.vip - Unknown Host" in motd:
            return False, "Papyrus.vip"
        if "NeoProtect > Invalid Hostname!" in motd:
            return False, "NeoProtect invalid hostname"
        if "NeoProtect > Server is deactivated!" in motd:
            return False, "NeoProtect server deactivated"
        if "Hosted by Servcity" in motd:
            return False, "Servcity"
        if "--[ Invalid Server ]--" in motd and "Protection by ⚡ Infinity-Filter.com ⚡" in motd:
            return False, "Infinity-Filter"
        
        if "This server is OFFLINE!" in motd:
            return False, "This server is OFFLINE!"
        
        if "Server is offline." in motd:
            return False, "Server is offline."
        
        if "■ Server Is Paused" in motd:
            return False, "Server Is Paused"
        
        if "powered by powerupstack.com for free" in motd:
            return False, "powerupstack.com"
        

        if default_motd_invalid and motd == "A Minecraft Server":
            return False, "A Minecraft Server"
        if default_motd_invalid and motd == "A Velocity Server":
            return False, "A Velocity Server"
        
        return True, None

MOTD_VALIDATOR = MotdValidator()
FAILED_SERVERS = FailedServers()