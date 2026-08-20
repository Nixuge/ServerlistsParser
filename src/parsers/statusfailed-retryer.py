import os

from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from parsers.textfile import TextFileParser
from utils.serverchecks import ServerValidator


class StatusFailedRetryer(TextFileParser):
    def __init__(self):
        super().__init__(source_path="data/statusfailed.txt")
        
    
    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        
        with open("cache/statusfailed.txt") as file:
            res = [x.split(" ")[0] for x in file.read().strip().split("\n")]

        with open("data/statusfailed.txt", "w") as file:
            for line in res:
                file.write(line)
                
        super().get_parse_everything()
    
    
    def check_server(self, server: str):
        server_check = ServerValidator(server).is_valid_mcstatus(failed_threshold=999999999)
        with self.print_lock:
            self.servers_requested += 1
            if server_check:
                self.valid_servers_found += 1
            self.print_status()
            
        if server_check:
            return (server, server_check)
        return None

    
def setup() -> ParserMeta:
    return ParserMeta(
        "Status Failed Retryer",
        "~None~",
        "1.0",
        termcolor.rgb(240, 69, 77),
        StatusFailedRetryer,
        run_bulk=False
    )
