from abc import abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor

from utils.vars import SERVER_REQUEST_WORKERS

class BaseParser:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=SERVER_REQUEST_WORKERS)
        self.futures = []
        self.servers_requested = 0
        self.pages_parsed = 0
        self.valid_servers_found = 0
        self.print_lock = threading.Lock()
    
    def print_status(self, max_page: int | str | None = None):
        max_page_str = self.pages_parsed if max_page == None else f"{self.pages_parsed}/{max_page}"
        print(f"\r{max_page_str} pages parsed, {self.servers_requested}/{len(self.futures)} servers requested, {self.valid_servers_found} new servers...    ", end="", flush=True)

    @abstractmethod
    def ask_config(self):
        raise Exception("Cannot call abstract method")
    
    @abstractmethod
    def get_parse_everything(self):
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def get_page(self, *args) -> str:
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def parse_elements(self, data: str):
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def print_ask(self, *args):
        raise Exception("Cannot call abstract method")

    @abstractmethod
    def print_ask_all(self):
        raise Exception("Cannot call abstract method")
    
    # to be used to eg close selenium sessions
    # automatically called at the end of a module
    def end(self):
        pass