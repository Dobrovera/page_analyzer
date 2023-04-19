import requests
import psycopg2
import os
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, flash

load_dotenv()
A = os.getenv('FLASK_APP')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def add_to_urls_table(normalize_name):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(
                'INSERT INTO urls (name) VALUES (%s) RETURNING id;',
                (normalize_name,))
            id = curs.fetchone()[0]
            flash('Страница успешно добавлена', 'success')
            return [id, flash]


def get_id_from_urls(normalize_name):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(f""
                         f"SELECT id "
                         f"FROM urls "
                         f"WHERE name = '{normalize_name}';")
            id = curs.fetchone()[0]
            flash('Страница уже существует', 'info')
            return [id, flash]


def check_the_link(link):
    if validators.url(link):
        return True


def get_info_by_id(id):
    this_url = {}
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(f"SELECT name FROM urls WHERE id = {id};")
            this_url['name'] = curs.fetchone()[0]
            curs.execute(f"SELECT id FROM urls WHERE id = {id};")
            this_url['id'] = curs.fetchone()[0]
            curs.execute(f"SELECT created_at FROM urls WHERE id = {id};")
            this_url['created_at'] = curs.fetchone()[0]
    return this_url


def get_url_id(url):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(f"SELECT id FROM urls WHERE name = '{url}';")
            names = curs.fetchone()
            return names[0]


def check_url_into_db(url):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute(f"SELECT name FROM urls WHERE name = '{url}'")
            names = curs.fetchone()
        if names:
            return False
        return True


def get_all_names_and_id():
    urls = []
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute(
                    "SELECT DISTINCT ON (id) urls.id, urls.name, "
                    "url_checks.created_at, url_checks.h1, "
                    "url_checks.title, url_checks.status_code, "
                    "url_checks.description "
                    "FROM urls "
                    "JOIN url_checks ON (urls.id = url_checks.url_id)"
                )
                for data in curs:
                    description = data[6]
                    status_code = data[5]
                    title = data[4]
                    h1 = data[3]
                    created_at = data[2]
                    name = data[1]
                    id = data[0]
                    urls.append(
                        {"id": id,
                         "name": name,
                         "created_at": created_at,
                         "h1": h1,
                         "title": title,
                         "status_code": status_code,
                         "description": description
                         }
                    )
    except psycopg2.Error:
        return urls
    return urls


def check_request(id):
    name_url = get_info_by_id(id)['name']
    url_info = {}
    try:
        r = requests.get(name_url)
        url_info['status_code'] = r.status_code
        soup = BeautifulSoup(r.text, 'html.parser')
        url_info['title'] = str(soup.find_all('title'))[8:-9]
        url_info['h1'] = str(soup.find_all('h1'))[5:-6]
        url_info['description'] = str(soup.find_all
                                      ('meta',
                                       attrs={'name': 'description'}))[16:-23]
        return url_info
    except requests.ConnectionError or requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        pass


def add_to_check_table(id):
    if check_request(id):
        url_info = check_request(id)
        status_code = url_info['status_code']
        h1 = url_info['h1']
        title = url_info['title']
        description = url_info['description']
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as curs:
                    curs.execute(""
                                 "INSERT INTO url_checks "
                                 "(url_id, status_code, h1, "
                                 "title, description) "
                                 "VALUES (%s, %s, %s, %s, %s);",
                                 (id, status_code, h1, title, description)
                                 )
            flash('Страница успешно проверена', 'success')
        except psycopg2.Error:
            print(status_code)
            flash('Произошла ошибка при проверке', 'danger')


def get_info_from_check_table(url_id):
    urls_check = []
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute(f"SELECT id, status_code, h1, title, "
                             f"created_at, description "
                             f"FROM url_checks WHERE url_id = {url_id} "
                             f"ORDER BY id DESC;")
                for data in curs:
                    description = data[5]
                    created_at = data[4]
                    title = data[3]
                    h1 = data[2]
                    status_code = data[1]
                    id = data[0]
                    urls_check.append(
                        {"id": id,
                         "created_at": created_at,
                         "h1": h1,
                         "title": title,
                         "status_code": status_code,
                         "description": description
                         }
                    )
    except psycopg2.Error:
        return urls_check
    return urls_check
