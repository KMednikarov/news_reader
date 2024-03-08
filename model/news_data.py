class NewsData:
    def __init__(self, source, company, articles):
        self.source = source
        self.company = company
        self.articles = articles


class Article:
    def __init__(self, title, link, date):
        self.title = title
        self.link = link
        self.date = date
