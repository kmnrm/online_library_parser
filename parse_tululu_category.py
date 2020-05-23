from __future__ import print_function
import os
import json
import logging
import argparse
from urllib.parse import urljoin
from utils import get_last_page_num, check_page_arguments
from tululu_books import fetch_books_urls, get_book
from downloaders import download_txt, download_image

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    )

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
            logging.warning(f'The book with URL {book_url} can not be downloaded.')
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
        logging.info(f'The book "{book_title}" with URL {book_url} has been downloaded.')


    if args.json_path is not None:
        os.chdir(args.json_path)
    with open('books.json', 'w', encoding='utf8') as downloaded_books:
        json.dump(books, downloaded_books, ensure_ascii=False)
    json_dir = os.path.dirname(os.path.abspath(__file__))
    logging.info(f'The JSON-file has been created and added to {json_dir} directory.')


if __name__ == "__main__":
    main()
