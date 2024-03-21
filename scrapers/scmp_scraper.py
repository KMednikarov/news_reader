import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_scraper import BaseScraper
from model.news_data import Article
from model.scraper_config import ScraperConfig
from model.scraper_query import ScraperQuery
import util.constants as cons
from util.constants import DATE_FORMAT
from util.logger import Log


def scrape_data(driver, query: ScraperQuery):
    try:
        wait_loader(driver)
        curr_date = datetime.strptime(datetime.strftime(datetime.now(), cons.DATE_FORMAT), DATE_FORMAT)
        if isinstance(query.last_scraped_date, str):
            last_date = datetime.strptime(query.last_scraped_date, cons.DATE_FORMAT)
        else:
            last_date = query.last_scraped_date.strftime(cons.DATE_FORMAT)
            last_date = datetime.strptime(last_date, cons.DATE_FORMAT)

        if (curr_date - last_date).days > 7:
            filter_for_days = 60
        else:
            filter_for_days = 7
        filter_results_by_last_days(driver,filter_for_days)
        wait_loader(driver)
        time.sleep(cons.ROBO_WAIT_TIME)

        scroll(driver)

        articles = driver.find_elements(By.XPATH,
                                        '//div[@data-qa="ArticleSearchResultList-List"]//div['
                                        '@data-qa="ContentItemSearch-Container"]')
    except Exception as e:
        # print('Error: ', e)
        return []

    articles_list = []
    for article in articles:
        try:
            date_text = article.find_element(By.XPATH, './/time[@data-qa="ContentActionBar'
                                                       '-handleRenderDisplayDateTime-time"]').get_attribute("datetime")
            article_date = datetime.fromisoformat(date_text[:-1]).strftime(DATE_FORMAT)

            if article_date <= last_date.strftime(DATE_FORMAT):
                continue

            link = article.find_element(By.TAG_NAME, 'a')
            link_url = link.get_attribute('href')
            title = link.find_element(By.XPATH, './/span[@data-qa="ContentHeadline-Headline"]').text.strip()

            articles_list.append(Article(title, link_url, article_date))
        except Exception as e:
            # print('Error: ', e)
            continue

    articles_list.sort(key=lambda x: x.date, reverse=True)

    return articles_list


def filter_results_by_last_days(driver, days):
    show_article_last_days = '{} Days'.format(days)
    driver.find_element(By.XPATH,
                        '//span[@data-qa="DropdownMenu-Display" and contains(text(),"Date Range")]').click()

    WebDriverWait(driver, cons.WAIT_FOR_ELEMENT_PRESENCE).until(
        EC.presence_of_element_located((By.XPATH, '//li[@role="menuitem" and contains(text(), "{}")]'.format(show_article_last_days)))
    )
    driver.find_element(By.XPATH, '//li[@role="menuitem" and contains(text(), "{}")]'.format(show_article_last_days)).click()


def wait_loader(driver):
    WebDriverWait(driver, cons.WAIT_FOR_ELEMENT_PRESENCE).until(EC.any_of(
        EC.presence_of_element_located((By.XPATH, ".//div[@data-qa='SearchResultList-HeaderContainer']")),
        EC.presence_of_element_located((By.XPATH, ".//div[@data-qa='SearchResultList-NoResultsContainer']"))
    ))


def scroll(driver):
    prev_height = -1
    max_scrolls = 100
    scroll_count = 0

    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(cons.ROBO_WAIT_TIME)  # give some time for new results to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height
        scroll_count += 1
    time.sleep(cons.ROBO_WAIT_TIME)


class SouthChinaMorningPostScraper(BaseScraper):
    config_path = 'config/scmp_config.json'

    def __init__(self):
        self.config = ScraperConfig.from_json(self.config_path)
        super().__init__(self.config, Log(self.config.scraper_name))

    def loop_pages_for_articles(self, pages_count, query: ScraperQuery):
        driver = self.get_driver()
        search_url = self.build_search_url(query)
        driver.get(search_url)
        self.personal_data_consent(self.config.data_consent_window,
                                   self.config.data_consent_accept_btn,
                                   self.config.data_consent_switch_to_iframe)

        articles = scrape_data(driver, query)

        return articles

    def build_search_url(self, query: ScraperQuery):
        return f'{self.config.base_url}/search/{query.keyword}'

    def get_pages_count(self):
        return 1

