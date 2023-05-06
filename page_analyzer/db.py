import psycopg2
from psycopg2.extras import NamedTupleCursor
from page_analyzer.check_req import check_request


def get_connection(database_url):
    conn = psycopg2.connect(database_url)
    return conn


def add_url(conn, normalize_name):
    with conn.cursor() as curs:
        curs.execute(
            'INSERT INTO urls (name) \
            VALUES (%s) RETURNING id;',
            (normalize_name,))
        id, = curs.fetchone()
    conn.commit()
    return id


def get_id_by_name(conn, normalize_name):
    with conn.cursor() as curs:
        curs.execute(
            'SELECT id FROM urls \
            WHERE name = (%s);',
            (normalize_name, ))
        id, = curs.fetchone()
    conn.commit()
    return id


def get_url(conn, id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            'SELECT name, id, created_at \
            FROM urls WHERE id = (%s);',
            (id, ))
        result = curs.fetchone()
    conn.commit()
    return [result.name, result.id, result.created_at]


def check_url(conn, url):
    with conn.cursor() as curs:
        curs.execute(
            'SELECT name \
            FROM urls WHERE name = (%s);',
            (url, ))
        names = curs.fetchone()
        conn.commit()
        if names:
            return False
        return True


def get_all_names_and_id(conn):
    urls = []
    with conn.cursor() as curs:
        try:
            curs.execute(
                'SELECT DISTINCT ON (id) urls.id, \
                urls.name, url_checks.created_at, \
                url_checks.h1, url_checks.title, \
                url_checks.status_code, \
                url_checks.description \
                FROM urls \
                JOIN url_checks \
                ON (urls.id = url_checks.url_id)'
            )
            for data in curs:
                urls.append(
                    {"id": data[0],
                     "name": data[1],
                     "created_at": data[2],
                     "h1": data[3],
                     "title": data[4],
                     "status_code": data[5],
                     "description": data[6]
                     }
                )
        except psycopg2.Error:
            return urls
        return urls


def add_url_check(conn, id):
    if check_request(conn, id):
        url_info = check_request(conn, id)
        status_code = url_info['status_code']
        h1 = url_info['h1']
        title = url_info['title']
        description = url_info['description']
        with conn.cursor() as curs:
            try:
                curs.execute(
                    'INSERT INTO url_checks \
                    (url_id, status_code, h1, title, description) \
                    VALUES (%s, %s, %s, %s, %s);',
                    (id, status_code, h1, title, description))
                conn.commit()
                return True
            except psycopg2.Error:
                return False


def get_url_check(conn, url_id):
    urls_checks = []
    with conn.cursor() as curs:
        try:
            curs.execute(
                'SELECT id, status_code, h1, \
                title, created_at, description \
                FROM url_checks \
                WHERE url_id = (%s) \
                ORDER BY id DESC;',
                (url_id, ))
            for data in curs:
                urls_checks.append(
                    {"id": data[0],
                     "status_code": data[1],
                     "h1": data[2],
                     "title": data[3],
                     "created_at": data[4],
                     "description": data[5]
                     }
                )
            conn.commit()
        except psycopg2.Error:
            return None
        return urls_checks


def close(conn):
    return conn.close()
