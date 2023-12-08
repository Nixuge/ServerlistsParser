from abc import abstractmethod

import cloudscraper
from selenium.webdriver import Firefox

from classes.BaseParser import BaseParser
from utils.vars import SELENIUM_FIREFOX_OPTIONS

class CloudflareParser(BaseParser):
    scraper: cloudscraper.CloudScraper
    selenium: Firefox | None
    page_url: str
    def __init__(self, page_url: str) -> None:
        self.scraper = cloudscraper.create_scraper()
        self.selenium = None
        self.page_url = page_url

    def get_page(self, page: int) -> str:
        if self.selenium != None:
            return self.get_page_selenium(page)
        data = self.scraper.get(self.page_url.replace("%PAGE%", str(page))).text

        # check for cloudflare
        if "Just a moment..." in data and "Enable JavaScript and cookies to continue" in data:
            self.selenium = Firefox(options=SELENIUM_FIREFOX_OPTIONS)
            return self.get_page_selenium(page)
        
        return data

    @abstractmethod
    def get_page_selenium(self, *args) -> str:
        raise Exception("Cannot call abstract method")