import os
import sys
import json


def get_path(filename):
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        script_dir = sys._MEIPASS
    else:
        # Running as a script
        script_dir = os.path.dirname(os.path.abspath('__main__'))

    return os.path.join(script_dir, filename)


class ScraperConfig:
    def __init__(self, scraper_name,
                 base_url,
                 search_url,
                 data_consent_window,
                 data_consent_switch_to_iframe,
                 data_consent_accept_btn,
                 article_main,
                 article_header,
                 article_date,
                 article_date_format,
                 pages_text):
        self.scraper_name = scraper_name
        self.base_url = base_url
        self.search_url = search_url
        self.data_consent_window = data_consent_window
        self.data_consent_switch_to_iframe = data_consent_switch_to_iframe
        self.data_consent_accept_btn = data_consent_accept_btn
        self.article_main = article_main
        self.article_header = article_header
        self.article_date = article_date
        self.article_date_format = article_date_format
        self.pages_text = pages_text

    @classmethod
    def from_json(cls, filename):
        filepath = get_path(filename)
        with open(filepath, 'r') as file:
            data = json.load(file)
        return cls(**data)
