from page_analyzer import db
import requests
from bs4 import BeautifulSoup


def check_request(curs, id):
    name_url = db.get_urls(curs, id)['name']
    url_info = {}
    try:
        r = requests.get(name_url)
        url_info['status_code'] = r.status_code
        soup = BeautifulSoup(r.text, 'html.parser')
        url_info['title'] = str(soup.find('title').text) \
            if soup.find('title') else ''
        url_info['h1'] = str(soup.find('h1').text) if soup.find('h1') else ''
        url_info['description'] = str(soup.find_all
                                      ('meta',
                                       attrs={'name': 'description'}))[16:-23]

        if 200 <= url_info['status_code'] <= 299:
            return url_info
        else:
            return False
    except requests.ConnectionError or requests.exceptions.RequestException:
        return False
