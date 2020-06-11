import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from utils import check_response_status

TULULU_URL = 'http://tululu.org'


def fetch_books_urls(category_url, start_page, end_page):
    books_urls = []
    for page_num in range(start_page, end_page + 1):
        books_list_url = urljoin(category_url, str(page_num))
        response = requests.get(books_list_url, allow_redirects=False)
        check_response_status(response, request_in=fetch_books_urls.__name__)
        soup = BeautifulSoup(response.text, 'lxml')
        books_from_page_urls = [
            urljoin(
                category_url,
                tag.find('a')['href']
                )
            for tag in soup.find_all('table', class_='d_book')
        ]
        books_urls += books_from_page_urls
    return books_urls


def get_book(category_url, book_page_url):
    response = requests.get(book_page_url)
    if response.url == TULULU_URL or response.status_code != 200:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    book_href = soup.select('.d_book tr a')[-3]['href']
    if 'txt.php' not in book_href:
        return None
    book_href = urljoin(
        category_url,
        book_href
    )
    book_name = soup.find('h1').text
    title = book_name.split('\xa0')[0].strip()
    author = book_name.split('\xa0')[2].strip()
    image_src = urljoin(
        category_url,
        soup.select_one('.bookimage img')['src']
    )
    genres = [
        genres_tag.text
        for genres_tag in soup.select('span.d_book a')
    ]
    comments = [
        comments_tag.select_one('.black').text
        for comments_tag in soup.select('.texts')
    ]
    book = {
        'title': title,
        'author': author,
        'comments': comments,
        'genres': genres,
        'image_src': image_src,
        'book_path': book_href,
    }
    return book
