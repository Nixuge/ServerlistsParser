from abc import abstractmethod

import cloudscraper
from selenium.webdriver import Firefox

from classes.BaseParser import BaseParser
from utils.vars import SELENIUM_FIREFOX_OPTIONS

class CloudflareParser(BaseParser):
    scraper: cloudscraper.CloudScraper
    selenium: Firefox | None
    page_url: str
    def __init__(self, page_url: str, always_use_selenium: bool = False) -> None:
        self.scraper = cloudscraper.create_scraper()
        self.selenium = Firefox(options=SELENIUM_FIREFOX_OPTIONS) if always_use_selenium else None
        self.page_url = page_url

    def clear_selenium_data(self):
        if self.selenium == None: return
        self.selenium.delete_all_cookies()

    def get_page(self, page: int) -> str:
        if self.selenium != None:
            return self.get_page_selenium(page)
        data = self.scraper.get(self.page_url.replace("%PAGE%", str(page))).text

        # check for cloudflare
        if "Just a moment..." in data and "Enable JavaScript and cookies to continue" in data:
            print(f"  [Cloudflare flagged as of page {page}]", end="")
            self.selenium = Firefox(options=SELENIUM_FIREFOX_OPTIONS)
            return self.get_page_selenium(page)
        
        return data
    
    def end(self):
        if self.selenium:
            self.selenium.close()
            print("closed selenium session")

    @abstractmethod
    def get_page_selenium(self, *args) -> str:
        raise Exception("Cannot call abstract method")