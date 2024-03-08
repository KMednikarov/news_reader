from .base_scraper import BaseScraper
from model.news_data import Article
from model.news_data import NewsData
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from util.logger import Log
import time


def scrape_data(driver):
    articles = driver.find_elements(By.XPATH, '//*[@id="resultsListA"]/li/div/div[1]')
    articles_list = []
    for article in articles:
        if article.get_attribute('class') != 'aprev-main':
            continue
        link = article.find_element(By.CLASS_NAME, 'aprev-title').find_element(By.TAG_NAME,'a')
        try:
            link_url = link.get_attribute('href')
            title = link.get_attribute('text')
            date_text = (article.find_element(By.CLASS_NAME,'meta')
                         .find_element(By.TAG_NAME, 'time')
                         .get_attribute('datetime'))
            date = datetime.strptime(date_text, '%d/%m/%Y')
            formatted_date = date.strftime('%Y-%m-%d')
            articles_list.append(Article(title, link_url, formatted_date))
        except Exception as e:
            #print(e)
            continue
    articles_list.sort(key=lambda x: x.date, reverse=True)
    return articles_list


class IlSoleScraper(BaseScraper):
    cookies_accepted = False

    def __init__(self):
        class_name = self.__class__.__name__
        super().__init__("https://ilsole24ore.com", Log(class_name))

    def search(self, query) -> NewsData:
        super().search(query)

        driver = self.get_driver()
        driver.get(self.url)
        self.accept_cookies(driver)
        self.click_search_btn()
        self.search_query(query)
        time.sleep(3)
        driver.switch_to.default_content()

        articles = scrape_data(driver)
        news_data = NewsData(query, articles)

        return news_data

    def click_search_btn(self):
        self.get_driver().find_element(By.XPATH, '//*[@id="header"]/div[2]/div/div/ul[1]/li[2]/a').click()

    def search_query(self, query):
        search_input = self.get_driver().find_element(By.XPATH,'//*[@id="ricercaForm"]/div/input')
        search_input.send_keys(query)
        self.get_driver().find_element(By.XPATH, '//*[@id="ricercaForm"]/div/button').click()

    def accept_cookies(self, driver):
        if self.cookies_accepted:
            return
        self.cookies_accepted = True
        time.sleep(3)
        driver.find_element(By.XPATH, '//button[contains(text(), "Accetto")]').click()  # cookies consent
