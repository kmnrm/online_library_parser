import sys
import requests
from bs4 import BeautifulSoup

TULULU_URL = 'http://tululu.org'


def check_page_arguments(start_page, end_page, collection_last_page):
    if start_page > end_page:
        eprint('Start page may not be greater than end page.')
        sys.exit()
    if end_page > collection_last_page or start_page > collection_last_page:
        eprint(f'Page argument can not be greater than the last page of the collection: {collection_last_page}')
        sys.exit()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def check_response_status(response, request_in):
    if response.status_code != 200:
        eprint(f'{requests.HTTPError.__name__} occurred in {request_in}().')
        sys.exit()


def get_last_page_num(category_url):
    response = requests.get(category_url, allow_redirects=False)
    check_response_status(response, request_in=get_last_page_num.__name__)
    soup = BeautifulSoup(response.text, 'lxml')
    last_page_num = soup.select('.npage')[-1].text
    return int(last_page_num)
