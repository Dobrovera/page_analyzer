import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, \
    url_for, redirect, flash, get_flashed_messages
from urllib.parse import urlparse
from page_analyzer.db import check_the_link, check_url_into_db, \
    add_to_check_table, get_all_names_and_id, get_info_by_id, \
    get_info_from_check_table, add_to_urls_table, get_id_from_urls

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
    normalize = urlparse(request.form.get("url"))
    normalize_name = f"{normalize.scheme}://{normalize.netloc}"
    if check_the_link(request.form.get("url")) \
            and check_url_into_db(normalize_name):
        add_to_tbl = add_to_urls_table(normalize_name)
        return redirect(url_for('get_url', id=add_to_tbl[0]))
    elif check_the_link(normalize_name):
        get_from_tbl = get_id_from_urls(normalize_name)
        return redirect(url_for('get_url', id=get_from_tbl[0]))
    flash('Некорректный URL', 'danger')
    return render_template(
        'index.html',
        message=get_flashed_messages(with_categories=True)
    ), 422


@app.post('/urls/<id>/checks')
def do_check(id):
    add_to_check_table(id)
    return redirect(url_for('get_url', id=id))


@app.get('/urls')
def get_urls():
    urls = get_all_names_and_id()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.get('/urls/<id>')
def get_url(id):
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
