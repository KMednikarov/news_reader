from .base_scraper import BaseScraper
from model.news_data import Article
from model.news_data import NewsData
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from util.constants import DATE_FORMAT
from util.logger import Log

import time


def scrape_data(driver, last_scrape_date):
    latest_date = datetime.min.strftime(DATE_FORMAT)
    try:
        wait_loader(driver)

        filter_results_by_last_days(driver,7)
        wait_loader(driver)
        time.sleep(3)

        scroll(driver)

        articles = driver.find_elements(By.XPATH,
                                        '//div[@data-qa="ArticleSearchResultList-List"]//div['
                                        '@data-qa="ContentItemSearch-Container"]')
    except Exception as e:
        # print('Error: ', e)
        return [], last_scrape_date

    articles_list = []
    for article in articles:
        try:
            date_text = article.find_element(By.XPATH, './/time[@data-qa="ContentActionBar-handleRenderDisplayDateTime'
                                                       '-time"]').get_attribute("datetime")
            date = datetime.fromisoformat(date_text[:-1]).strftime(DATE_FORMAT)
            if date <= last_scrape_date:
                continue
            elif date >= latest_date:
                latest_date = date

            link = article.find_element(By.TAG_NAME, 'a')
            link_url = link.get_attribute('href')
            title = link.find_element(By.XPATH, './/span[@data-qa="ContentHeadline-Headline"]').text.strip()

            articles_list.append(Article(title, link_url, date))
        except Exception as e:
            # print('Error: ', e)
            continue

    articles_list.sort(key=lambda x: x.date, reverse=True)

    return articles_list, latest_date


def filter_results_by_last_days(driver, days):
    show_article_last_days = '{} Days'.format(days)
    driver.find_element(By.XPATH,
                        '//span[@data-qa="DropdownMenu-Display" and contains(text(),"Date Range")]').click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//li[@role="menuitem" and contains(text(), "{}")]'.format(show_article_last_days)))
    )
    driver.find_element(By.XPATH, '//li[@role="menuitem" and contains(text(), "{}")]'.format(show_article_last_days)).click()


def wait_loader(driver):
    WebDriverWait(driver, 20).until(EC.any_of(
        EC.presence_of_element_located((By.XPATH, ".//div[@data-qa='SearchResultList-HeaderContainer']")),
        EC.presence_of_element_located((By.XPATH, ".//div[@data-qa='SearchResultList-NoResultsContainer']"))
    ))


def scroll(driver):
    prev_height = -1
    max_scrolls = 50
    scroll_count = 0

    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # give some time for new results to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height
        scroll_count += 1
    time.sleep(2)


class SouthChinaMorningPostScraper(BaseScraper):
    data_consent_accepted = False

    def __init__(self, last_scraped_dates):
        self.class_name = self.__class__.__name__
        super().__init__("https://www.scmp.com", Log(self.class_name))
        self.last_scraped_dates = last_scraped_dates

    def search(self, query) -> NewsData:
        super().search(query)

        driver = self.get_driver()
        search_url = f'{self.url}/search/{query}'
        driver.get(search_url)
        self.personal_data_consent(driver)

        [articles, latest_date] = scrape_data(driver, self.last_scraped_dates.get(query, datetime.min.strftime(DATE_FORMAT)))
        self.last_scraped_dates[query] = latest_date

        return NewsData(self.class_name, query, articles)

    def personal_data_consent(self, driver):
        if self.data_consent_accepted:
            return
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="fc-dialog-container"]'))
        )
        driver.find_element(By.XPATH, '//p[contains(text(),"Consent")]').click()  # cookies consent
        driver.switch_to.default_content()
        self.data_consent_accepted = True
