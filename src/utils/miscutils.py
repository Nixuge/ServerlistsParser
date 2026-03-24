import pyperclip
import tldextract
from utils.fileutils import add_line, add_server, add_server_dupe

from utils.vars import BEDROCK_LIST, JAVA_LIST

def only_keep_main_domain(ip: str):
    split = ip.split(":")[0].split(".")
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

def remove_leading_mc_play(ip: str):
    ip = ip.removeprefix("play").removesuffix("play")
    ip = ip.removeprefix("mc").removesuffix("mc")
    return ip

def remove_port_if(ip: str, query: str):
    if "ip" in query:
        ip = ip.split(":")[0]
    return ip

def ask_duplicate(ip: str, bedrock: bool):
    pyperclip.copy(remove_leading_mc_play(only_keep_main_domain(ip)))
    duplicated_answer = input("is the server a duplicate? ").lower()

    if duplicated_answer in ["r", "s"]: #remove/skip
        print("skipped.")
        return
    
    if duplicated_answer in ["i"]:
        if bedrock:
            add_line(f"cache/ignored_bedrock.txt", ip)
        else:
            add_line(f"cache/ignored.txt", ip)
        print("added to the ignored list.")
        return
    
    duplicated = duplicated_answer in ["yes", "y", "oui", "o", "yip", "oip"]
    if duplicated:
        if bedrock:
            name = "duplicates_bedrock.txt"
        else:
            name = "duplicates.txt"
        
        reason = input("Enter the server info: ")
        add_server_dupe(name, remove_port_if(ip, duplicated_answer), reason)
    else:
        if bedrock:
            name = "ips_bedrock.txt"
        else:
            name = "ips.txt"
        add_server(name, remove_port_if(ip, duplicated_answer))

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

def remove_double_space(data: str):
    out = data
    while "  " in out:
        out = out.replace("  ", " ")
    return out