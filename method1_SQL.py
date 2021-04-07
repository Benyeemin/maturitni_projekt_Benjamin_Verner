import psycopg2, json, sys
from contextlib import closing
from pathlib import Path
from psycopg2.extras import DictCursor

def build_search_sql(text, column, table):
    cases = [f"case when {column} ilike '%{word}%' then 1 else 0 end" for word in text]
    union = [f"select * from {table} where {column} ilike '%{word}%'" for word in text]
    return [' + '.join(cases), ' union all '.join(union)]

def search(text):
    max_title_len = 10
    for word in text:
        max_title_len += len(word) + 1
        if len(word) > 2 and word not in ['the']:
            word = ''.join([i if ord(i) < 128 else '_' for i in word])
        else:
            text.remove(word)
    text = set(text)

    if getattr(sys, 'frozen', False):
        server_info_path = Path(sys._MEIPASS)/'server_connection_info'
    else:
        server_info_path = Path('server_connection_info')

    server_info = json.loads(open(str(server_info_path)).readline())

    cases, union = build_search_sql(text, 'name', 'authors')
    command = f'select key, {cases} as words from ({union}) as books order by words desc limit 1;'
    conn = psycopg2.connect(host=server_info["host"], user=server_info["user"], password=server_info["password"],
                                database=server_info["database"], sslmode='require', cursor_factory=DictCursor)
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        try:
            author_key = cursor.fetchone()['key']
        except:
            author_key = '123'

    cases, union = build_search_sql(text, 'title', 'authors')
    command = f'''select title, main_author, {cases} + case when main_author='{author_key}' then {str(max(
        len(text) // 3, 1))} else 0 end as words from ({union}) as books  where char_length(title) < {max_title_len} order by words desc limit 1;'''

    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        book_info = cursor.fetchone()
        if not book_info:
            return None, None
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