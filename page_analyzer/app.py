import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, \
    url_for, redirect, flash, get_flashed_messages
from urllib.parse import urlparse
from page_analyzer import db
import validators


load_dotenv()
A = os.getenv('FLASK_APP')
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.get('/')
def get_index():
    return render_template('index.html')


@app.post('/urls')
def insert_value():
    conn = db.get_connection(DATABASE_URL)
    normalize = urlparse(request.form.get('url'))
    normalize_name = f"{normalize.scheme}://{normalize.netloc}"

    if validators.url(request.form.get('url')) \
            and db.check_url(conn, normalize_name):
        added_page_id = db.add_url(conn, normalize_name)
        if added_page_id:
            flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', id=added_page_id))

    elif validators.url(normalize_name):
        get_from_tbl = db.get_id_by_name(conn, normalize_name)
        if get_from_tbl:
            flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=get_from_tbl))
    flash('Некорректный URL', 'danger')

    db.close(conn)

    return render_template(
        'index.html',
        message=get_flashed_messages(with_categories=True)
    ), 422


@app.post('/urls/<id>/checks')
def do_check(id):
    conn = db.get_connection(DATABASE_URL)
    if db.add_url_check(conn, id):
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка при проверке', 'danger')

    db.close(conn)

    return redirect(url_for('get_url', id=id))


@app.get('/urls')
def get_urls():
    conn = db.get_connection(DATABASE_URL)
    urls = db.get_all_names_and_id(conn)

    db.close(conn)

    return render_template(
        'urls.html',
        urls=urls
    )


@app.get('/urls/<id>')
def get_url(id):
    conn = db.get_connection(DATABASE_URL)
    url = db.get_url(conn, id)
    message = get_flashed_messages(with_categories=True)
    url_check = db.get_url_check(conn, id)

    db.close(conn)

    return render_template(
        'urls_id.html',
        name=url[0],
        id=url[1],
        created_at=url[2],
        message=message,
        check=url_check,
    )
