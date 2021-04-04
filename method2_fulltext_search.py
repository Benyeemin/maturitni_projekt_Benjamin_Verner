import psycopg2
from contextlib import closing

def title_search(text):
    conn = #connect to the server
    command = '''SELECT title, main_author from works WHERE to_tsvector(title) @@ to_tsquery('') limit 1;'''
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        info = cursor.fetchall()
    if len(info) > 0:
        book_title = info[0]
        book_key = info[1]

        command = "SELECT auth_key FROM work_auths WHERE work_key='" + str(book_key) + "' limit 1;"
        with closing(conn.cursor()) as cursor:
            cursor.execute(command)
            auth_key = cursor.fetchall()

        command = "SELECT name FROM authors WHERE key='" + str(auth_key) + "' limit 1;"
        with closing(conn.cursor()) as cursor:
            cursor.execute(command)
            book_author = cursor.fetchall()

    return book_title, book_author
