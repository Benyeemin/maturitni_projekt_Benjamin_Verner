import psycopg2, json, sys
from contextlib import closing
from pathlib import Path
from psycopg2.extras import DictCursor
from nltk.corpus import wordnet

def build_search_sql(text, column):
    cases = [f"case when {column} like '%{word}%' then 1 else 0 end" for word in text]
    return ' + '.join(cases)

def search(text):
    for word in text:
        word = ''.join([i if ord(i) < 128 else '_' for i in word])

    if getattr(sys, 'frozen', False):
        server_info_path = Path(sys._MEIPASS)/'server_connection_info'
    else:
        server_info_path = Path('server_connection_info')

    server_info = json.loads(open(str(server_info_path)).readline())

    command = build_search_sql(text, 'name')
    command = "select key, " + command + ' as words from authors order by words desc limit 1;'
    try:
        conn = psycopg2.connect(host=server_info["host"], user=server_info["user"], password=server_info["password"],
                                database=server_info["database"], sslmode='require', cursor_factory=DictCursor)
    except:
        return None, None
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        try:
            author_key = cursor.fetchone()['key']
        except:
            author_key = '123'

    for word in text:
        if not wordnet.synsets(word):
            text.remove(word)

    command = build_search_sql(text, 'title')
    command = 'select title, main_author, ' + command + " + case when main_author='" + author_key + "' then " + str(max(
        len(text) // 3, 1)) + ' else 0 end as words from works order by words desc limit 1;'
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        book_info = cursor.fetchone()
        book_title = book_info['title']
        author_key = book_info['main_author']

    command = "select name from authors where key='" + author_key + "' limit 1;"
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        try:
            book_author = cursor.fetchone()['name']
        except:
            book_author = 'someone'

    return book_title, book_author