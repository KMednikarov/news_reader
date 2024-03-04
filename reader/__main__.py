from reader.scrapers.base_scraper import BaseScraper
from reader.scrapers.ft_scraper import FinancialTimesScraper
import time
import pandas as pd
import logging
from datetime import datetime

companies_list_file = "sources/companies_list.xlsx"
report_file = 'reports/report.xlsx'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('my_logger')

scrapers = [FinancialTimesScraper()]


def main():
    companies = load_companies(companies_list_file)
    news_list = get_articles(companies, scrapers)
    save_results(news_list)


def load_companies(file_path):
    df = pd.read_excel(file_path)
    first_column_values = df.iloc[:, 0].tolist()
    return first_column_values


def get_articles(queries, article_sources: [BaseScraper]):
    articles_list = []
    for source in article_sources:
        class_name = source.__class__.__name__
        starting_time = source.get_start_time()
        logger.info("[{}] Scraping {}".format(starting_time, class_name))

        for query in queries:
            logger.info("[{}] - Searching for {}".format(datetime.now(), query))
            articles_list.append(source.search(query))
            #time.sleep(2)

        source.close_driver()

    return articles_list


def save_results(news_list):
    data = []
    for news in news_list:
        for article in news.articles:
            news_data = {'Company': news.company, 'Title': article.title, 'Link': article.link, 'Date': article.date}
            data.append(news_data)

    df = pd.DataFrame(data)
    df.to_excel(report_file, index=False)


if __name__ == "__main__":
    main()
