import os
import sys
import platform


def get_current_directory():
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        if 'macOS' in platform.platform():
            print(platform.platform())
            return os.path.dirname(sys.executable)
        else:
            return os.getcwd()
    else:
        # Running as a script
        return os.getcwd()


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SHORT_DATE_FORMAT = '%Y-%m-%d'
MAX_DATE = '9999-12-31 23:59:59'
MIN_DATE = '0001-01-01 00:00:00'
LAST_MONTHS = 3
WAIT_FOR_ELEMENT_PRESENCE = 30
ROBO_WAIT_TIME = 3
SEVEN_DAYS = 7
SIXTY_DAYS = 60
current_directory = get_current_directory()
report_file_path = current_directory + '/reports'
sources_dir = current_directory + "/sources"
companies_file_path = current_directory + '/sources/companies_list.xlsx'
last_scrape_dates_file_path = current_directory + '/sources/previous_scrape_dates.json'
