import requests as rq
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from util.logger import Log


def new_driver_instance():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    return webdriver.Chrome(options=chrome_options)


class BaseScraper:
    driver = None

    def __init__(self, url, logger: Log):
        self._start_time = datetime.now()
        self.url = url
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}  # Add a user agent to mimic a browser
        self.init_driver()

    def get_start_time(self):
        return self._start_time

    def init_driver(self):
        self.driver = new_driver_instance()

    def get_driver(self) -> webdriver.Chrome:
        return self.driver

    def close_driver(self):
        return self.get_driver().quit()

    def fetch_html(self, url):
        try:
            driver = self.get_driver().get(url)

            return driver.page_source
        except rq.exceptions.RequestException as e:
            print(f"Failed to fetch HTML: {e}")
            return None

    def parse_response(self, html):
        if html:
            return BeautifulSoup(html, 'html.parser')
        return None

    def get_logger(self) -> Log:
        return self.logger

    def scrape(self):
        raise NotImplementedError("Subclass must implement this method")

    def search(self, query):
        self.logger.info(" - Searching for {}".format(query))
