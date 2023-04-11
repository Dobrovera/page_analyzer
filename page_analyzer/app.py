import requests
import psycopg2
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
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
                curs.execute('INSERT INTO urls (name) VALUES (%s)',
                             (request.form.get("url"), ))
    return render_template(
        'index.html',
    )


@app.get('/urls')
def get_all_urls():
    return render_template(
        'urls.html'
    )


@app.route('/urls/<id>')
def get_this_url(id):
    return render_template(
        'urls.html'
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


def get_url_id(url):
    CONN = psycopg2.connect(DATABASE_URL)
    CURS = CONN.cursor()
    CURS.execute(f"SELECT id FROM urls WHERE name = '{url}';")
    names = CURS.fetchone()
    return names[0]


def check_url_into_db(url):
    CONN = psycopg2.connect(DATABASE_URL)
    CURS = CONN.cursor()
    CURS.execute(f"SELECT name FROM urls WHERE name = '{url}'")
    names = CURS.fetchone()
    if names:
        return False
    return True
