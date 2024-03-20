import time

from model.scraper_query import ScraperQuery
from model.scraper_config import ScraperConfig
from .base_scraper import BaseScraper
from model.news_data import Article
from model.news_data import NewsData
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from datetime import date
from util.constants import DATE_FORMAT
from util.logger import Log
import re


def scrape_data(driver, last_scrape_date):
    latest_date = datetime.min.strftime(DATE_FORMAT)
    articles = driver.find_elements(By.CLASS_NAME, 'o-teaser__content')
    articles_list = []
    for article in articles:
        link = article.find_element(By.CLASS_NAME, 'o-teaser__heading').find_element(By.TAG_NAME, 'a')
        try:
            date_text = article.find_element(By.CLASS_NAME, 'o-teaser__timestamp-date').get_attribute("datetime")
            date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S%z').strftime(DATE_FORMAT)
            if date <= last_scrape_date:
                continue
            elif date >= latest_date:
                latest_date = date

            link_url = link.get_attribute('href')
            title = link.text

            articles_list.append(Article(title, link_url, date))
        except Exception as e:
            # print('Error: ', e)
            continue

    articles_list.sort(key=lambda x: x.date, reverse=True)
    return articles_list, latest_date


class FinancialTimesScraper(BaseScraper):
    cookies_accepted = False
    config_path = 'config/ft_config.json'

    def __init__(self):
        self.config = ScraperConfig.from_json(self.config_path)
        super().__init__(self.config, Log(self.config.scraper_name))

    def get_pages_count(self):
        driver = self.get_driver()
        pages_text = driver.find_element(By.CLASS_NAME, 'search-pagination__page')
        pages_count = re.search(r'Page \d+ of (\d+)', pages_text.text).group(1)
        return pages_count

    def build_search_url(self, query: ScraperQuery):
        return f'{self.config.base_url}/search?&q={query.keyword}&dateFrom={query.from_date}&contentType=article&page={query.page}'
