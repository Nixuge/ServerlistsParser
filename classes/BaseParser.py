from abc import abstractmethod


class BaseParser:
    def __init__(self) -> None:
        pass
    
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