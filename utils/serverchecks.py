import os
import socket
from typing import Literal

import mcstatus

from utils.miscutils import is_already_present
from utils.motdutils import motd_remove_section_signs
from mcstatus.status_response import JavaStatusResponse

def is_ipv4(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False

class ServerValidator:
    ip: str
    print_reason: bool
    def __init__(self, ip: str, print_reason: bool = False) -> None:
        self.ip = ip
        self.print_reason = print_reason

    def is_valid_mcstatus(self) -> Literal[False] | JavaStatusResponse:
        if not self.is_valid():
            return False
        
        try:
            status = mcstatus.JavaServer(self.ip).status()
            motd = motd_remove_section_signs(status.description)
            motd_valid, motd_valid_reason = MOTD_VALIDATOR.is_motd_valid(self.ip, motd)
            if not motd_valid:
                if self.print_reason: print(f"motd invalid: {motd_valid_reason}")
                return False
            return status
        except:
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
        
        ip = self.ip

        if is_already_present(ip):
            dprint("already known, skipping")
            return False
        if ip.endswith("minehut.gg"):
            dprint("ip from hosting provider, skipping")
            return False
        if ip.endswith(".ddns.net"):
            dprint("ddns server, skipping")
            return False
        if is_ipv4(ip):
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
    
    def is_motd_valid(self, ip: str, motd: str) -> tuple[bool, str | None]:
        if self.is_ip_in_motd_cache(ip):
            return False, "Already present in cache."
        valid, reason = self._check_motd_str(motd)
        if not valid:
            self._add_ip_cache(ip)
        return valid, reason

    def _add_ip_cache(self, ip: str):
        self.invalid_ips_motd.append(ip)
        with open("cache/motdinvalid.txt", "a") as file:
            file.write(f"ip\n")
    
    @staticmethod
    def _check_motd_str(motd: str) -> tuple[bool, str | None]:
        if "Invalid hostname. Please refer to our documentation at docs.tcpshield.com" in motd:
            return False, "tcpshield"
        if "Papyrus.vip - Unknown Host" in motd:
            return False, "Papyrus.vip"
        if "NeoProtect > Invalid Hostname!" in motd:
            return False, "NeoProtect"
        if "Hosted by Servcity" in motd:
            return False, "Servcity"
        if "--[ Invalid Server ]--" in motd and "Protection by ⚡ Infinity-Filter.com ⚡" in motd:
            return False, "Infinity-Filter"
        
        return True, None

MOTD_VALIDATOR = MotdValidator()