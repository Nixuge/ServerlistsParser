import os

import httpx

from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from parsers.textfile import TextFileParser


class WebarchiveLists(TextFileParser):
    LINKS = (
        "namemc.com/server/*",
        "minechecker.com/status/java/*",
        "mcstatus.io/status/java/*",
        "mcsrvstat.us/server/*",
        "minecraftserverstatus.com/server?url=*",
        "minecraftpinger.com/?server=*",
        "api.minetools.eu/ping/*",
        "minerank.com/pages/server-status-checker?host=*",
        
    )
    
    def __init__(self):
        super().__init__(source_path="data/webarchive_links.txt")
        with open("data/webarchive_links.txt", "w"):
            pass
        
    def ask_config(self):
        super().ask_config()
        answer = input("Do you want to retry queries to the webarchive? If yes, enter the number of retries or nothing for 3. Otherwise 'no': ")
        try:
            if answer.strip() == "3":
                self.auto_retry = 3
            else:
                self.auto_retry = int(answer)
        except:
            self.auto_retry = 0
        
        for i, link in enumerate(self.LINKS):
            print(f"{i+1}: {link}")
        
        
        ans2 = input("Answer the indexes of the links you want included separated by a space or nothing for all links: ")
        if ans2.strip() == "":
            self.used_links = self.LINKS
            print("Using all links.")
        else:
            self.used_links = [self.LINKS[int(x)-1] for x in ans2.strip().split(" ")]
    
    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        
        for link in self.used_links:
            i = 0
            res: httpx.Response | None = None
            while res == None and i <= self.auto_retry:
                try:
                    print(f"Grabbing webarchive results for '{link}'...", end=" ", flush=True)
                    res = httpx.get(f"https://web.archive.org/cdx/search/cdx?url={link}&output=txt&fl=original&collapse=urlkey", timeout=30)
                except Exception as e:
                    print(f"Failed ({e}), retrying")
            
            if not res:
                print(f"Failed for link {link} !")
                continue
            
            print(f"Got {res.text.count("\n")} entries")
            with open("data/webarchive_links.txt", "a") as f:
                f.write(res.text)
                
        super().get_parse_everything()
    
def setup() -> ParserMeta:
    return ParserMeta(
        "WebArchive",
        "web.archive.org",
        "1.0",
        termcolor.rgb(240, 69, 77),
        WebarchiveLists,
        run_bulk=False
    )
