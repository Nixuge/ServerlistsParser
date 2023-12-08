import tldextract
def remove_port(ip: str) -> str:
    if not ":" in ip:
        return ip
    return ip.split(":")[0]

def remove_subdomain(ip: str) -> str:
    subdomain = tldextract.extract(ip).subdomain

    ip_nosub = ip.replace(subdomain, "", 1)
    if ip_nosub[0] == '.':
        ip_nosub = ip_nosub[1:]
    
    return ip_nosub

print(remove_subdomain(remove_port("play.hattmc.net")))