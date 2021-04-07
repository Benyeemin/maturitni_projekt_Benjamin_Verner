import isbnlib
from isbntools.app import *

def info_from_image(book_title, book_author, book_number):
    isbn = isbn_from_words(book_title)
    book = isbnlib.meta(isbn)
    if len(book) != 0:
        string = f'''Book No.: {book_number} \n ISBN: {book[
            'ISBN-13']} \n Title: {book['Title']} \n Authors: {'; '.join(book['Authors'])} \n Publisher: {book[
                     'Publisher']} \n Year: {book['Year']} \n Language: {book[
                     'Language']}'''
    else:
        string = f'Database error: BibTex citation for book No. {book_number} not found. Name and author: {book_title}, {book_author}'
    return string

def info_from_barcode(barcode, book_number):
    isbn = str(barcode.data)
    isbn = isbn.replace('b', '')
    isbn = isbn.replace("'", "")
    book = isbnlib.meta(isbn)
    if len(book) != 0:
        string = f'''Book No.: {book_number} \n ISBN: {book[
            'ISBN-13']} \n Title: {book['Title']} \n Authors: {'; '.join(book['Authors'])} \n Publisher: {book[
            'Publisher']} \n Year: {book['Year']} \n Language: {book[
            'Language']}'''
    else:
        string = f'Database error: BibTex citation for book No. {book_number} not found. ISBN: {isbn}'
    return string