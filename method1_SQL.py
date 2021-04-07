import psycopg2, json, sys, logging
from contextlib import closing
from pathlib import Path
from psycopg2.extras import DictCursor

def build_search_sql(text, column, table):
    cases = [f"case when {column} ilike '%{word}%' then 1 else 0 end" for word in text]
    union = [f"select * from {table} where {column} ilike '%{word}%'" for word in text]
    return [' + '.join(cases), ' union all '.join(union)]

def search(text):
    max_title_len = 10

    text = set(text)
    filtered_text = []
    for word in text:
        max_title_len += len(word) + 1
        if len(word) > 2 and word.lower() not in ['the', 'and', 'has']:
            word = ''.join([i if ord(i) < 128 else '_' for i in word])
            word = word.replace('.', '')
            filtered_text.append(word)
    text = filtered_text

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
        logging.root.info(f'Running SQL query: {command}')
        cursor.execute(command)
        try:
            author_key = cursor.fetchone()['key']
        except:
            author_key = '123'
        logging.root.info('OK.')

    cases, union = build_search_sql(text, 'title', 'works')
    command = f'''select title, main_author, {cases} + case when main_author='{author_key}' then {str(max(
        len(text) // 3, 1))} else 0 end as words from ({union}) as books  where char_length(title) < {max_title_len} order by words desc limit 1;'''

    with closing(conn.cursor()) as cursor:
        logging.root.info(f'Running SQL query: {command}')
        cursor.execute(command)
        book_info = cursor.fetchone()
        if not book_info:
            return None, None
        book_title = book_info['title']
        author_key = book_info['main_author']
        logging.root.info('OK.')

    command = "select name from authors where key='" + author_key + "' limit 1;"
    with closing(conn.cursor()) as cursor:
        logging.root.info(f'Running SQL query: {command}')
        cursor.execute(command)
        try:
            book_author = cursor.fetchone()['name']
        except:
            book_author = 'someone'
        logging.root.info('OK.')
    return book_title, book_author