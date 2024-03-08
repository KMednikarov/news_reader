from scrapers.base_scraper import BaseScraper
from scrapers.ft_scraper import FinancialTimesScraper
from scrapers.il_sole_scraper import IlSoleScraper
from scrapers.scmp_scraper import SouthChinaMorningPostScraper
import pandas as pd

companies_list_file = "sources/companies_list.xlsx"
report_file = 'reports/report.xlsx'


scrapers = [IlSoleScraper()]


def main():
    #companies = load_companies(companies_list_file)
    companies = ['apple']
    news_list = get_articles(companies, scrapers)
    save_results(news_list)


def load_companies(file_path):
    df = pd.read_excel(file_path)
    first_column_values = df.iloc[:, 0].tolist()
    return first_column_values


def get_articles(queries, article_sources: [BaseScraper]):
    articles_list = []
    for source in article_sources:
        source.get_logger().info('Started scraping')
        for query in queries:
            articles_list.append(source.search(query))
            #time.sleep(2)

        source.close_driver()
        source.get_logger().info('Scraping completed')

    return articles_list


def save_results(news_list):
    data = []
    for news in news_list:
        for article in news.articles:
            news_data = {'Company': news.company, 'Title': article.title, 'Link': article.link, 'Date': article.date}
            data.append(news_data)

    df = pd.DataFrame(data)
    df.to_excel(report_file, index=False)


main()
