from .base_scraper import BaseScraper
from model.news_data import Article
from model.news_data import NewsData
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from util.constants import DATE_FORMAT
from util.logger import Log


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

    def __init__(self, last_scraped_dates):
        class_name = self.__class__.__name__
        super().__init__("https://ft.com", Log(class_name))
        self.last_scraped_dates = last_scraped_dates

    def search(self, query) -> NewsData:
        super().search(query)

        driver = self.get_driver()
        search_url = f'{self.url}/search?q={query}'
        driver.get(search_url)
        self.accept_cookies(driver)

        [articles, earliest_date] = scrape_data(driver, self.last_scraped_dates.get(query, datetime.min.strftime(DATE_FORMAT)))
        self.last_scraped_dates[query] = earliest_date

        return NewsData(query, articles)

    def accept_cookies(self, driver):
        if self.cookies_accepted:
            return
        self.cookies_accepted = True
        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="sp_message_iframe_1030615"]'))
        )
        driver.find_element(By.XPATH, '//button[contains(text(),"Accept Cookies")]').click()  # cookies consent
        driver.switch_to.default_content()
