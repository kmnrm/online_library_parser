# Book collection parser
This program parses a collection of books of a 
certain genre from [Tululu online library](http://tululu.org/).
The default genre set is [Science Fiction](http://tululu.org/l55/)
with code `\l55\`. 


### Getting started
User can download books in `txt` 
format and books covers images. 
The program also generates a `json` format file with downloaded 
books data such as:
- book title
- author
- book `.txt` file path
- book cover image path
- genres
- comments

The collection on Tululu includes a 
certain number of pages, which you can choose to be 
the first (`start_page`) and the last (`end_page`) 
pages to download the books from.

The program is launched from the command line
with __optional arguments__:
- `start_page` — The first page to parse. 
If start_page is not set as an
argument by user, it will be set as page number 1.
- `end_page` — The last page to parse. 
If end_page is not set as an
argument by user, it will be set as the last page of
the collection.
- `skip_txt` — Do not download book `.txt` files. 
The program will download `book.txt` files to `books/` directory,
 if the argument 
is not set by user.
- `skip_img` — Do not download book covers images. 
The program will download images files to `images/` directory, 
if the argument 
is not set by user.
- `dest_folder` — This argument lets user set the path for
downloaded files.
- `json_path` — This argument lets user set the path for 
generated `books.json` file only.


### How to use
Install Python3 to use this program.
1. Download project scripts.
2. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
    ```commandline
    pip install -r requirements.txt
    ```
3. In the command line enter:
    ```commandline
    python parse_tululu_category.py optional_arguments
    ```
   
##### Examples
Download the books `.txt` files and covers images from page 5 to page 10 of the collection to 
and create `books.json` in `C:\Folder` directory:
```commandline
python parse_tululu_category.py --start_page 5 --end_page 10 --dest_folder C:\Folder 
```

Download the books covers images from page 1 to page 10 to `C:\Folder` directory, 
and create `books.json` file in `C:\jsons` directory:
```commandline
python parse_tululu_category.py --end_page 10 --skip_txt --dest_folder C:\Folder --json_path C:\jsons 
```

Create `books.json` file with books data from all the collection pages:
```commandline
python parse_tululu_category.py --skip_img --skip_txt
```
