import os

from classes.ParserMeta import ParserMeta

from utils.color import termcolor
from parsers.textfile import TextFileParser


class StatusFailedRetryer(TextFileParser):
    def __init__(self):
        super().__init__(source_path="data/statusfailed.txt")
        with open("data/statusfailed.txt", "w"):
            pass
        
    def get_parse_everything(self):
        if not os.path.isdir("data/"):
            os.makedirs("data/")
        
        os.rename("cache/statusfailed.txt", "data/statusfailed.txt")
                
        super().get_parse_everything()
    
def setup() -> ParserMeta:
    return ParserMeta(
        "Status Failed Retryer",
        "~None~",
        "1.0",
        termcolor.rgb(240, 69, 77),
        StatusFailedRetryer,
        run_bulk=False
    )
