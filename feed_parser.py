import feedparser

def fetch_rss_data(url):
    feed = feedparser.parse(url)
    print("Feed Title:", feed.feed.title)
    print(len(feed.entries))
#    for entry in feed.entries:
#        print("Entry Title:", entry.title)
#        print("Entry Link:", entry.link)
#        print("Entry Published Date:", entry.published)
#        print("Entry Summary:", entry.summary)
#        print("\n")
# List of RSS feed URLs
rss_feed_urls = [
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.ft.com/world?format=rss",
]
# Fetch data from multiple RSS feeds
for url in rss_feed_urls:
    fetch_rss_data(url)

