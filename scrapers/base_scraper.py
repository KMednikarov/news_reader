import time
from datetime import datetime

from model.news_data import Article, NewsData
from model.scraper_query import ScraperQuery
from model.scraper_config import ScraperConfig
from util.logger import Log
import util.constants as cons

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def new_driver_instance():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('log-level=3')

    # chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    return webdriver.Chrome(options=chrome_options)


class BaseScraper:
    driver = None
    cookies_accepted = False
    data_consent_wait_time = 30
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}  # Add a user agent to mimic a browser

    def __init__(self, config: ScraperConfig, logger: Log):
        self.config = config
        self.logger = logger
        self.init_driver()

    def __init__(self, url, logger: Log):
        self._start_time = datetime.now()
        self.url = url
        self.logger = logger
        self.init_driver()

    def init_driver(self):
        self.driver = new_driver_instance()

    def get_driver(self) -> webdriver.Chrome:
        return self.driver

    def close_driver(self):
        return self.get_driver().quit()

    def get_logger(self) -> Log:
        return self.logger

    def scrape(self, query: ScraperQuery):
        self.logger.info(" - Searching for {}".format(query.keyword))
        self.load_webpage(query)
        self.personal_data_consent(self.config.data_consent_window
                                   , self.config.data_consent_accept_btn
                                   , self.config.data_consent_switch_to_iframe)
        pages_count = self.get_pages_count()
        articles = self.loop_pages_for_articles(pages_count, query)
        articles = sorted(articles,
                          key=lambda x: x.date, reverse=True)
        return NewsData(self.config.scraper_name, query.keyword, articles)

    def get_pages_count(self):
        raise NotImplementedError("Subclass must implement this method")

    def get_articles(self, query):
        articles_list = []
        driver = self.get_driver()
        articles = driver.find_elements(By.XPATH, self.config.article_main)
        for article in articles:
            header = article.find_element(By.XPATH, self.config.article_header).find_element(By.TAG_NAME, 'a')
            title = header.text
            link_url = header.get_attribute('href')
            date_text = article.find_element(By.XPATH, self.config.article_date).get_attribute("datetime")
            article_date = (datetime
                            .strptime(date_text, self.config.article_date_format)
                            .strftime(cons.DATE_FORMAT))

            if isinstance(query.last_scraped_date, str):
                last_date = (datetime
                             .strptime(query.last_scraped_date, cons.DATE_FORMAT)
                             .strftime(cons.DATE_FORMAT))
            else:
                last_date = query.last_scraped_date.strftime(cons.DATE_FORMAT)
            if article_date <= last_date:
                continue

            articles_list.append(Article(title, link_url, article_date))

        return articles_list

    def search(self, query):
        self.logger.info(" - Searching for {}".format(query))

    def load_webpage(self, query):
        search_url = self.build_search_url(query)
        self.get_driver().get(search_url)

    def personal_data_consent(self, consent_window_xpath, accept_btn_xpath, switch_to_iframe):
        if self.cookies_accepted:
            return
        self.cookies_accepted = True
        driver = self.get_driver()
        if switch_to_iframe:
            WebDriverWait(driver, self.data_consent_wait_time).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, consent_window_xpath))
            )
        else:
            WebDriverWait(driver, self.data_consent_wait_time).until(
                EC.presence_of_element_located((By.XPATH, consent_window_xpath))
            )
        time.sleep(3)
        driver.find_element(By.XPATH, accept_btn_xpath).click()  # cookies consent
        driver.switch_to.default_content()

    def build_search_url(self, query: ScraperQuery):
        raise NotImplementedError("Subclass must implement this method")

    def loop_pages_for_articles(self, pages_count, query: ScraperQuery):
        articles = []
        driver = self.get_driver()
        for page in range(1, int(pages_count)+1):
            query.page = page
            search_url = self.build_search_url(query)
            driver.get(search_url)
            articles.extend(self.get_articles(query))

        return articles

    def get_name(self):
        return self.config.scraper_name