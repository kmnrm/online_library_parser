from __future__ import print_function
import sys
import os
import json
import argparse
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TULULU_URL = 'http://tululu.org'
IMAGES_FOLDER = os.path.join(ROOT_DIR, 'images')
BOOKS_FOLDER = os.path.join(ROOT_DIR, 'books')
DESCRIPTION = 'This program parses a collection of books of a certain genre from Tululu online library. '\
                  'You can download books in txt format and books covers images. '\
                  'The program generates a json format file with downloaded books data such as: '\
                  'book title, author, book .txt file path, book cover path, genres and comments. '\
                  'The collection on Tululu includes a certain number of pages, which you can choose to be '\
                  'the first (start_page) and the last (end_page) pages to download the books from.'


def dir_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")
    if os.access(path, os.W_OK):
        return path
    else:
        raise Exception(f":{path} is not writeable")


def parse_arguments():

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--start_page', type=int, nargs='?', default=1,
                        help='The first page to parse.'
                             'If start_page is not set as an argument by user, it will be set as page number 1.'
                        )
    parser.add_argument('--end_page', type=int,
                        help='The last page to parse.'
                             'If end_page is not set as an argument by user,'
                             'it will be set as the last page of the collection.'
                        )
    parser.add_argument('--skip_txt', action='store_const', const=True,
                        help='Do not download book .txt files. Download, if not set as an argument by user.'
                        )
    parser.add_argument('--skip_img', action='store_const', const=True,
                        help='Do not download books covers. Download, if not set as an argument by user.'
                        )
    parser.add_argument('--dest_folder', type=dir_path, help='Set books and covers download path.')
    parser.add_argument('--json_path', type=dir_path, help='Set books.json file path')
    return parser.parse_args()


def get_last_page_num(category_url):
    response = requests.get(category_url, allow_redirects=False)
    check_response_status(response)
    soup = BeautifulSoup(response.text, 'lxml')
    last_page_num = soup.select('.npage')[-1].text
    return int(last_page_num)


def check_response_status(response):
    if response.status_code != 200:
        raise requests.HTTPError


def fetch_books_urls(category_url, start_page, end_page):
    books_urls = []
    for page_num in range(start_page, end_page + 1):
        books_list_url = urljoin(category_url, str(page_num))
        response = requests.get(books_list_url, allow_redirects=False)
        check_response_status(response)
        soup = BeautifulSoup(response.text, 'lxml')
        books_from_page_urls = [
            urljoin(
                TULULU_URL,
                tag.find('a')['href']
                )
            for tag in soup.find_all('table', class_='d_book')
        ]
        books_urls += books_from_page_urls
    return books_urls


def get_book(book_page_url):
    response = requests.get(book_page_url, allow_redirects=False)
    check_response_status(response)
    if response.url != TULULU_URL:
        soup = BeautifulSoup(response.text, 'lxml')
        book_href = soup.select('.d_book tr a')[-3]['href']
        if 'txt.php' not in book_href:
            return None
        book_href = urljoin(
            TULULU_URL,
            book_href
        )
        book_name = soup.find('h1').text
        title = book_name.split('\xa0')[0].strip()
        author = book_name.split('\xa0')[2].strip()
        image_src = urljoin(
            TULULU_URL,
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


def download_txt(url, filename, folder=BOOKS_FOLDER):
    response = requests.get(url, allow_redirects=False)
    check_response_status(response)
    if response.url != TULULU_URL:
        filename += '.txt'
        file_path = os.path.join(folder, sanitize_filename(filename))
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path


def download_image(url, folder=IMAGES_FOLDER):
    response = requests.get(url, allow_redirects=False)
    check_response_status(response)
    if response.url != TULULU_URL:
        filename = url.split('/')[-1]
        file_path = os.path.join(folder, filename)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def check_page_arguments(start_page, end_page, collection_last_page):
    if start_page > end_page:
        eprint('Start page may not be greater than end page.')
        sys.exit()
    if end_page > collection_last_page or start_page > collection_last_page:
        eprint(f'Page argument can not be greater than the last page of the collection: {collection_last_page}')
        sys.exit()


def main():
    science_fiction_collection_url = urljoin(TULULU_URL, 'l55/')
    collection_last_page = get_last_page_num(science_fiction_collection_url)
    args = parse_arguments()
    start_page = args.start_page
    end_page = args.end_page
    if end_page is None:
        end_page = collection_last_page
    check_page_arguments(start_page, end_page, collection_last_page)

    if args.dest_folder is not None:
        os.chdir(args.dest_folder)
    if not args.skip_img:
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
    if not args.skip_txt:
        os.makedirs(BOOKS_FOLDER, exist_ok=True)

    books = []
    books_urls = fetch_books_urls(science_fiction_collection_url, start_page, end_page)
    for book_url in books_urls:
        book = get_book(book_url)
        if book is None:
            continue
        book_title = book['title']
        image_url = book['image_src']
        book_download_url = book['book_path']
        if not args.skip_img:
            book['image_src'] = download_image(image_url, folder=IMAGES_FOLDER)
        else:
            del book['image_src']
        if not args.skip_txt:
            book['book_path'] = download_txt(book_download_url, book_title, folder=BOOKS_FOLDER)
        else:
            del book['book_path']
        books.append(book)

    if args.json_path is not None:
        os.chdir(args.json_path)
    with open('books.json', 'w', encoding='utf8') as downloaded_books:
        json.dump(books, downloaded_books, ensure_ascii=False)


if __name__ == "__main__":
    main()
