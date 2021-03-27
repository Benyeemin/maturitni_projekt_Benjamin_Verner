import psycopg2, json
from contextlib import closing

def search(text):
    for word in text:
        word = ''.join([i if ord(i) < 128 else '_' for i in word])
    
    server_info = json.loads(open('server_connection_info').readline())

    command = "select key, "
    first = True
    for word in text:
        if first:
            command = command + "case when name like '%" + word + "%' then 1 else 0 end"
            first = False
        else:
            command = command + " + case when name like '%" + word + "%' then 1 else 0 end"
    command = command + ' as words from authors order by words desc limit 1;'
    conn = psycopg2.connect(host=server_info["host"], user=server_info["user"], password=server_info["password"], database=server_info["database"])
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        author_key = cursor.fetchall()['key']

    command = 'select title, main_author, '
    for word in text:
        command = command + "case when title like '%" + word + "%' then 1 else 0 end + "
    command = command + "case when main_author='" + author_key + "' then " + str(len(text)//3) + ' else 0 end as words from works order by words desc limit 1;'
    conn = psycopg2.connect(host=server_info["host"], user=server_info["user"], password=server_info["password"], database=server_info["database"])
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        book_info = cursor.fetchall()
        book_title = book_info['title']
        author_key = book_info['main_author']

    command = "'select name from authors where key='" + author_key + "' limit 1;"
    conn = psycopg2.connect(host=server_info["host"], user=server_info["user"], password=server_info["password"], database=server_info["database"])
    with closing(conn.cursor()) as cursor:
        cursor.execute(command)
        book_author = cursor.fetchall()

    return book_title, book_author
