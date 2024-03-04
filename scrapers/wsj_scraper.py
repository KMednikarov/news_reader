import time
from .base_scraper import BaseScraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import random

class WSJScraper(BaseScraper):
    proxy_list = ['143.255.176.161:4153', '212.79.107.116:5678', '189.125.22.10:5678', '167.71.171.26:44550', '201.121.249.246:8080']
    def __init__(self):
        super().__init__("https://wsj.com")

    def scrape_data(self):
        html = self.fetch_html()
        soup = self.parse_response(html)

        # Add specific scraping logic for Wall Street Journal
        # For example, extract article titles
        titles = soup.find_all('a', href=True)
        for title in titles:
            print(title.get('href'))


    def search(self, query):
        search_url = f'{self.url}/search'
        print(search_url)
        driver = self.get_driver()

        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 

            driver.get(search_url)
            time.sleep(4)
            WebDriverWait(driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="sp_message_iframe_910380"]'))
            )
            time.sleep(2.5)
            driver.find_element(By.XPATH, '//button[contains(text(), "YES, I AGREE")]').click() #cookies consent
            driver.switch_to.default_content()
            time.sleep(2)
            driver.execute_script('window.scrollTo(0, 125)') 

            time.sleep(3.5)
            search_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/div[1]/div[1]/div/form/div/input')))
            search_input.click()
            time.sleep(1.5)
            search_input.send_keys(query)
            time.sleep(3)
            search_btn = driver.find_element(By.XPATH, '//*[@id="main"]/div[1]/div[1]/div[1]/form/button')
            time.sleep(2)
            search_btn.click() 
            soup = self.parse_response(driver.page_source)

            # Extract and print search results
            results = soup.find_all('a', href=True)
            for result in results:
                print(result.get('href'))
        finally:
            print('end')

    
    def get_driver(self) -> webdriver.Chrome:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        chrome_options.add_experimental_option("useAutomationExtension", False) 
        #chrome_options.add_argument("--proxy-server=%s" % self.proxy_list[random.randint(0,4)]) 

        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  
        return webdriver.Chrome(options=chrome_options)