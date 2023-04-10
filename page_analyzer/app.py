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
# conn = psycopg2.connect(DATABASE_URL)
app = Flask(__name__)


@app.get('/')
def hello_world():
    return render_template('index.html')


@app.post('/')
def insert_value():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            if check_the_link(request.form.get("url")):
                curs.execute('INSERT INTO urls (name) VALUES (%s)',
                             (request.form.get("url"), ))

    return render_template('index.html')


def check_the_link(link):
    valids = 0
    if 0 < len(link) < 255:
        try:
            requests.get(link, timeout=5)
            valids = 1
        except MissingSchema:
            pass

    if valids == 1:
        print("OK")
        return True
