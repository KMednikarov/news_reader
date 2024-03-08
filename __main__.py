from scrapers.base_scraper import BaseScraper
from scrapers.ft_scraper import FinancialTimesScraper
from scrapers.il_sole_scraper import IlSoleScraper
from scrapers.scmp_scraper import SouthChinaMorningPostScraper
import pandas as pd
import json

last_scrape_dates_file = "sources/previous_scrape_dates.json"
companies_list_file = "sources/companies_list.xlsx"
report_file = 'reports/report.xlsx'

scrapers = [FinancialTimesScraper, SouthChinaMorningPostScraper]


def main():
    last_scrape_dates = get_previous_dates(last_scrape_dates_file)
    companies = load_companies(companies_list_file)
    news_list = get_articles(companies, scrapers, last_scrape_dates)
    save_results(news_list)


def get_previous_dates(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file does not exist, create it and return an empty dictionary
        with open(file_path, 'w') as file:
            json.dump({}, file)
        return {}


def save_previous_dates(file_path, data):
    out_file = open(file_path, "w")
    json.dump(data, out_file, indent=4)
    out_file.close()


def load_companies(file_path):
    df = pd.read_excel(file_path)
    first_column_values = df.iloc[:, 0].tolist()
    return first_column_values


def get_articles(queries, article_sources: [BaseScraper], last_scrape_dates):
    articles_list = []
    for source in article_sources:
        if source.__name__ not in last_scrape_dates:
            last_scrape_dates[source.__name__] = {}
        source = source(last_scrape_dates[source.__name__])

        source.get_logger().info('Started scraping')
        for query in queries:
            articles_list.append(source.search(query))

        source.close_driver()
        source.get_logger().info('Scraping completed')

    save_previous_dates(last_scrape_dates_file, last_scrape_dates)

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
