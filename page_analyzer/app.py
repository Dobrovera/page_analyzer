import requests
import psycopg2
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect
from requests.exceptions import MissingSchema

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False)
A = os.getenv('FLASK_APP')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)


@app.get('/')
def hello_world():
    return render_template('index.html')


@app.post('/urls')
def insert_value():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            if check_the_link(request.form.get("url")) \
                    and check_url_into_db(request.form.get("url")):
                curs.execute(
                    'INSERT INTO urls (name) VALUES (%s) RETURNING id',
                    (request.form.get("url"), ))
                id = curs.fetchone()[0]
                print(id)
                return redirect(url_for('get_id_url', id=id))

    return render_template(
        'index.html',
    )


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
    return render_template(
        'urls_id.html',
        name=url['name'],
        id=url['id'],
        created_at=url['created_at']
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
    print(this_url)
    return this_url


def get_url_id(url):
    conn = psycopg2.connect(DATABASE_URL)
    curs = conn.cursor()
    curs.execute(f"SELECT id FROM urls WHERE name = '{url}';")
    names = curs.fetchone()
    return names[0]


def check_url_into_db(url):
    conn = psycopg2.connect(DATABASE_URL)
    curs = conn.cursor()
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
                    "SELECT DISTINCT ON (id) id, name, created_at "
                    "FROM urls;"
                )
                for data in curs:
                    created_at = data[2]
                    name = data[1]
                    id = data[0]
                    urls.append(
                        {"id": id,
                         "name": name,
                         "created_at": created_at
                         }
                    )
    except psycopg2.Error:
        return urls
    finally:
        conn.close()
    return urls
