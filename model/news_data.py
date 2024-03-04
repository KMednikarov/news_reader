class NewsData:
    def __init__(self, company, articles):
        self.company = company
        self.articles = articles


class Article:
    def __init__(self, title, link, date):
        self.title = title
        self.link = link
        self.date = date
