import pyperclip
import tldextract
from utils.fileutils import add_server, add_server_dupe

from utils.vars import BEDROCK_LIST, JAVA_LIST

def only_keep_main_domain(ip: str):
    split = ip.split(".")
    lenSplit = len(split)
    if lenSplit == 2:
        return split[0]
    if lenSplit == 1:
        return split[0]
    
    if lenSplit >= 3:
        if split[-2] == "co" and split[-1] in ("uk", "il", "za", "nz"):
            return split[-3]
        if split[-2] == "com" and split[-1] in ("br", "tr", "ar", "au"):
            return split[-3]
        if split[-2] == "net" and split[-1] in ("br", "ar"):
            return split[-3]
        if split[-2] == "in" and split[-1] in ("ua"):
            return split[-3]

    return split[-2]

def ask_duplicate(ip: str, bedrock: bool):
    pyperclip.copy(only_keep_main_domain(ip))
    duplicated_answer = input("is the server a duplicate? ")
    if duplicated_answer in ["r", "s"]: #remove/skip
        print("skipped.")
        return
    duplicated = duplicated_answer in ["yes", "y", "oui", "o"]
    if duplicated:
        if bedrock:
            name = "duplicates_bedrock.txt"
        else:
            name = "duplicates.txt"
        
        reason = input("Enter the server info: ")
        add_server_dupe(name, ip, reason)
    else:
        if bedrock:
            name = "ips_bedrock.txt"
        else:
            name = "ips.txt"
        add_server(name, ip)

def remove_port(ip: str) -> str:
    if not ":" in ip:
        return ip
    return ip.split(":")[0]

def remove_subdomain(ip: str) -> str:
    subdomain = tldextract.extract(ip).subdomain

    ip_nosub = ip.replace(subdomain, "", 1).strip()
    if ip_nosub[0] == '.':
        ip_nosub = ip_nosub[1:]
    
    return ip_nosub

def is_already_present(ip: str, bedrock: bool = False):
    if bedrock:
        used_list = BEDROCK_LIST
    else:
        used_list = JAVA_LIST
    
    ip = ip.lower()

    if ip in used_list:
        return True

    ip_noprefix = remove_subdomain(remove_port(ip))
    if ip_noprefix in used_list:
        return True

    for server in used_list:
        server_noprefix = remove_subdomain(remove_port(server.lower()))
        if server_noprefix == ip or server_noprefix == ip_noprefix:
            return True

    return False