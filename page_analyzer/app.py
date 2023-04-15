import requests
import psycopg2
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request, \
    url_for, redirect, flash, get_flashed_messages
from requests.exceptions import MissingSchema

load_dotenv()
A = os.getenv('FLASK_APP')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.get('/')
def get_root():
    return render_template('index.html')


@app.post('/urls')
def insert_value():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            if check_the_link(request.form.get("url")) \
                    and check_url_into_db(request.form.get("url")):
                curs.execute(
                    'INSERT INTO urls (name) VALUES (%s) RETURNING id;',
                    (request.form.get("url"), ))
                id = curs.fetchone()[0]
                flash('Ссылка успешно добавлена', 'success')
                return redirect(url_for('get_id_url', id=id))
            elif check_the_link(request.form.get("url")):
                url = request.form.get("url")
                curs.execute(f"SELECT id FROM urls WHERE name = '{url}';")
                id = curs.fetchone()[0]
                flash('Страница уже существует', 'warning')
                return redirect(url_for('get_id_url', id=id))
    flash('Некорректный URL', 'error ')
    return render_template(
        'index.html',
        message=get_flashed_messages(with_categories=True)
    )


@app.post('/urls/<id>/checks')
def do_check(id):
    add_to_check_table(id)
    return redirect(url_for('get_id_url', id=id))


@app.get('/urls')
def get_all_urls():
    urls = get_all_names_and_id()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.get('/urls/<id>')
def get_id_url(id):
    url = get_info_by_id(id)
    message = get_flashed_messages(with_categories=True)
    url_check = get_info_from_check_table(id)
    return render_template(
        'urls_id.html',
        name=url['name'],
        id=url['id'],
        created_at=url['created_at'],
        message=message,
        check=url_check,
    )


def check_the_link(link):
    valids = 0
    if len(link) < 255:
        try:
            requests.get(link, timeout=5)
            valids = 1
        except MissingSchema:
            pass

    if valids == 1:
        return True


def get_info_by_id(id):
    this_url = {}
    conn = psycopg2.connect(DATABASE_URL)
    curs = conn.cursor()
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


def add_to_check_table(id):
    name_url = get_info_by_id(id)['name']
    r = requests.get(name_url)
    status_code = r.status_code
    soup = BeautifulSoup(r.text, 'html.parser')
    title = str(soup.find_all('title'))[8:-9]
    h1 = str(soup.find_all('h1'))[5:-7]
    description = str(soup.find_all('meta',
                                    attrs={'name': 'description'}))[16:-24]
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute(""
                             "INSERT INTO url_checks "
                             "(url_id, status_code, h1, title, description) "
                             "VALUES (%s, %s, %s, %s, %s);",
                             (id, status_code, h1, title, description)
                             )
        flash('Страница успешно проверена', 'success')
    except psycopg2.Error:
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
