import util.constants as cons


class ScraperQuery:
    def __init__(self, keyword, from_date='', to_date='', page=1, last_scraped_date=cons.MIN_DATE):
        self.keyword = keyword
        self.from_date = from_date
        self.to_date = to_date
        self.page = page
        self.last_scraped_date = last_scraped_date
