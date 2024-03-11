from util.constants import DATE_FORMAT
from .base_scraper import BaseScraper
from model.news_data import Article
from model.news_data import NewsData
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from util.logger import Log
import time


def scrape_data(driver, last_scrape_date):
    latest_date = datetime.min.strftime(DATE_FORMAT)

    # wait_to_show_result(driver)
    time.sleep(5)

    articles = driver.find_elements(By.XPATH, './/div[@class="aprev-main"]')
    articles_list = []
    for article in articles:
        try:
            link = article.find_element(By.CLASS_NAME, 'aprev-title').find_element(By.TAG_NAME, 'a')
            link_url = link.get_attribute('href')
            title = link.get_attribute('text')
            date_text = article.find_element(By.XPATH, './/time[@class="meta-part time"]').get_attribute('datetime')
            date = datetime.strptime(date_text, '%d/%m/%Y').strftime(DATE_FORMAT)
            if date <= last_scrape_date:
                continue
            elif date >= latest_date:
                latest_date = date

            articles_list.append(Article(title, link_url, date))

        except Exception as e:
            #print(e)
            continue
    articles_list.sort(key=lambda x: x.date, reverse=True)
    return articles_list, latest_date


def wait_to_show_result(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, './/div[@class="aprev aprev--fbtm  aprev--mid aprev--ilist"]'))
    )


class IlSoleScraper(BaseScraper):
    cookies_accepted = False

    def __init__(self, last_scraped_dates):
        self.class_name = self.__class__.__name__
        super().__init__("https://www.ricerca24.ilsole24ore.com/", Log(self.class_name))
        self.last_scraped_dates = last_scraped_dates

    def search(self, query) -> NewsData:
        super().search(query)

        driver = self.get_driver()
        driver.get(f'{self.url}?cmd=static&chId=30&path=/search/search_engine.jsp&field=Titolo|Testo&orderBy=score'
                   f'+desc&chId=30&disable_user_rqq=false&keyWords={query}&pageNumber=&pageSize=&fromDate=&'
                   f'toDate=&filter=all')
        self.accept_cookies(driver)

        [articles, earliest_date] = scrape_data(driver,
                                                self.last_scraped_dates.get(query, datetime.min.strftime(DATE_FORMAT)))
        self.last_scraped_dates[query] = earliest_date

        return NewsData(self.class_name, query, articles)

    def accept_cookies(self, driver):
        if self.cookies_accepted:
            return
        self.cookies_accepted = True

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, './/button[contains(text(), "Accetto")]'))
        )
        driver.find_element(By.XPATH, './/button[contains(text(), "Accetto")]').click()
        time.sleep(10)
