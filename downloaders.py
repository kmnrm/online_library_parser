import os
import time
import requests
from pathvalidate import sanitize_filename
from utils import check_response_status

TULULU_URL = 'http://tululu.org'


def download_txt(url, filename, folder):
    response = requests.get(url, allow_redirects=False)
    check_response_status(response, request_in=download_txt.__name__)
    if response.url == TULULU_URL:
        return
    timestamp = int(time.time())
    filename = '_'.join([filename, str(timestamp), '.txt'])
    file_path = os.path.join(folder, sanitize_filename(filename))
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download_image(url, folder):
    response = requests.get(url, allow_redirects=False)
    check_response_status(response, request_in=download_image.__name__)
    if response.url == TULULU_URL:
        return
    filename = url.split('/')[-1].split('.')
    timestamp = int(time.time())
    filename_without_format = '_'.join([filename[0], str(timestamp)])
    filename_format = filename[-1]
    filename = '.'.join([filename_without_format, filename_format])
    file_path = os.path.join(folder, filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path
