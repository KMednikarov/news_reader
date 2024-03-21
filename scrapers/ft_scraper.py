import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_scraper import BaseScraper
from model.scraper_config import ScraperConfig
from model.scraper_query import ScraperQuery
from util.logger import Log
import util.constants as cons


class FinancialTimesScraper(BaseScraper):
    config_path = 'config/ft_config.json'

    def __init__(self):
        self.config = ScraperConfig.from_json(self.config_path)
        super().__init__(self.config, Log(self.config.scraper_name))

    def get_pages_count(self):
        driver = self.get_driver()
        time.sleep(cons.ROBO_WAIT_TIME)
        try:
            WebDriverWait(driver, cons.ROBO_WAIT_TIME).until(
                EC.visibility_of_element_located((By.XPATH, self.config.pages_text))
            )
        except Exception as e:
            return 1
        pages_text = driver.find_element(By.XPATH, self.config.pages_text)
        pages_count = re.search(r'Page \d+ of (\d+)', pages_text.text).group(1)
        return pages_count

    def build_search_url(self, query: ScraperQuery):
        return f'{self.config.base_url}/search?&q={query.keyword}&dateFrom={query.from_date}&contentType=article&page={query.page}'
