from .base_scraper import BaseScraper
from model.news_data import Article
from model.news_data import NewsData
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from util.logger import Log


def scrape_data(driver):
    articles = driver.find_elements(By.CLASS_NAME, 'o-teaser__content')
    articles_list = []
    for article in articles:
        link = article.find_element(By.CLASS_NAME, 'o-teaser__heading').find_element(By.TAG_NAME, 'a')
        try:
            link_url = link.get_attribute('href')
            title = link.text
            date_text = article.find_element(By.CLASS_NAME, 'o-teaser__timestamp-date').get_attribute("datetime")
            date = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date.strftime('%Y-%m-%d')
            articles_list.append(Article(title, link_url, formatted_date))
        except:
            continue
    articles_list.sort(key=lambda x: x.date, reverse=True)
    return articles_list


class FinancialTimesScraper(BaseScraper):
    cookies_accepted = False

    def __init__(self):
        class_name = self.__class__.__name__
        super().__init__("https://ft.com", Log(class_name))

    def search(self, query) -> NewsData:
        super().search(query)

        driver = self.get_driver()
        search_url = f'{self.url}/search?q={query}'
        driver.get(search_url)
        self.accept_cookies(driver)
        articles = scrape_data(driver)
        news_data = NewsData(query, articles)

        return news_data

    def accept_cookies(self, driver):
        if self.cookies_accepted:
            return
        self.cookies_accepted = True
        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="sp_message_iframe_1030615"]'))
        )
        driver.find_element(By.XPATH, '//button[contains(text(),"Accept Cookies")]').click()  # cookies consent
        driver.switch_to.default_content()
