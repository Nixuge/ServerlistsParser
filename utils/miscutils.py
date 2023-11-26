import pyperclip
from utils.fileutils import add_server, add_server_dupe

from utils.vars import BEDROCK_LIST, JAVA_LIST


def only_keep_main_domain(ip: str):
    split = ip.split(".")
    lenSplit = len(split)
    if lenSplit == 2:
        return split[0]
    return split[-2]

def ask_duplicate(ip: str, bedrock: bool):
    pyperclip.copy(only_keep_main_domain(ip))
    duplicated = input("is the server a duplicate? ") in ["yes", "y", "oui", "o"]
    if duplicated:
        if bedrock:
            name = "duplicates_bedrock.txt"
        else:
            name = "duplicates.txt"
        add_server_dupe(name, ip)
    else:
        if bedrock:
            name = "ips_bedrock.txt"
        else:
            name = "ips.txt"
        add_server(name, ip)


def remove_subdomain(ip: str):
    split = ip.split(".")[1:]
    if len(split) == 1:
        return ip
    return '.'.join(split)


def is_already_present(ip: str, bedrock: bool = False):
    if bedrock:
        used_list = BEDROCK_LIST
    else:
        used_list = JAVA_LIST
    
    ip = ip.lower()

    if ip in used_list:
        return True

    ip_noprefix = remove_subdomain(ip)
    if ip_noprefix in used_list:
        return True

    for server in used_list:
        server_noprefix = remove_subdomain(server)
        if server_noprefix == ip or server_noprefix == ip_noprefix:
            return True

    return False