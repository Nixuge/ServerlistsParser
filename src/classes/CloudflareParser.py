from abc import abstractmethod
from dataclasses import dataclass
import time
from webbrowser import Chrome

import cloudscraper

from selenium import webdriver
from selenium.webdriver import Firefox, Safari, Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from classes.BaseParser import BaseParser
from utils.vars import SELENIUM_FIREFOX_OPTIONS

def make_webdriver() -> webdriver.Chrome:
    option = webdriver.ChromeOptions()
    # SOMEHOW(?) this hides the webdriver shit
    # https://www.browserscan.net/bot-detection
    option.add_argument('--disable-blink-features=AutomationControlled')
    # option.add_argument('--headless=new')
    option.add_argument

    driver = webdriver.Chrome(options=option)
    driver.set_page_load_timeout(5)
    return driver

@dataclass
class CFSeleniumOptions:
    element_to_find: tuple[str, str] | None # by, element
    clear_every_request: bool = False
    always_use_selenium: bool = False

class CloudflareParser(BaseParser):
    scraper: cloudscraper.CloudScraper
    selenium: webdriver.Chrome | None
    selenium_opts: CFSeleniumOptions
    page_url: str
    def __init__(self, page_url: str, selenium_opts: CFSeleniumOptions) -> None:
        super().__init__()
        self.scraper = cloudscraper.create_scraper()
        self.selenium_opts = selenium_opts
        self.selenium = make_webdriver() if selenium_opts.always_use_selenium else None
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
            self.selenium = make_webdriver()
            return self.get_page_selenium(page)
        
        return data
    
    def get_page_selenium(self, page: int) -> str:
        if not self.selenium_opts.element_to_find:
            raise Exception("No 'element_to_find'. This method is meant to either be called when this is set or to be replaced if the implementation needs custom logic")
        if not self.selenium: 
            raise Exception("Shouldn't happen.")
        
        if self.selenium_opts.clear_every_request:
            self.clear_selenium_data()
        
        get_successful = False
        while not get_successful:
            try:
                self.selenium.get(self.page_url.replace("%PAGE%", str(page)))
                get_successful = True
            except: 
                time.sleep(1) # retry

        try:
            WebDriverWait(self.selenium, 5).until(
                EC.presence_of_element_located(self.selenium_opts.element_to_find)
            )
        except:
            # see if that's good to have
            time.sleep(1)
            self.get_page_selenium(page)

        return self.selenium.page_source

    def end(self):
        if self.selenium:
            self.selenium.close()
