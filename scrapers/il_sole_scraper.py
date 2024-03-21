import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_scraper import BaseScraper
from model.scraper_config import ScraperConfig
from model.scraper_query import ScraperQuery
import util.constants as cons
from util.logger import Log


class IlSoleScraper(BaseScraper):
    config_path = 'config/ilsole_config.json'

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

        pages_count = driver.find_element(By.XPATH, self.config.pages_text + '/span').text
        return pages_count

    def build_search_url(self, query: ScraperQuery):
        from_dt = datetime.strptime(query.from_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        return f'{self.config.base_url}?cmd=static&chId=30&path=/search/search_engine.jsp&field=Titolo|Testo&orderBy=score+desc&chId=30&disable_user_rqq=false&keyWords={query.keyword}&pageNumber={query.page}&pageSize=&fromDate={from_dt}&toDate=&filter=only_articles'
