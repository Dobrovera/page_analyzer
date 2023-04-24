import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, \
    url_for, redirect, flash, get_flashed_messages
from urllib.parse import urlparse
import page_analyzer.db
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
    conn = page_analyzer.db.get_connection(DATABASE_URL)
    normalize = urlparse(request.form.get("url"))
    normalize_name = f"{normalize.scheme}://{normalize.netloc}"

    if validators.url(request.form.get("url")) \
            and page_analyzer.db.check_url(conn, normalize_name):
        add_to_tbl = page_analyzer.db.add_to_urls(conn, normalize_name)
        if add_to_tbl:
            flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', id=add_to_tbl))

    elif validators.url(normalize_name):
        get_from_tbl = page_analyzer.db.get_id_from_urls(conn, normalize_name)
        if get_from_tbl:
            flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=get_from_tbl))
    flash('Некорректный URL', 'danger')

    conn.close()

    return render_template(
        'index.html',
        message=get_flashed_messages(with_categories=True)
    ), 422


@app.post('/urls/<id>/checks')
def do_check(id):
    conn = page_analyzer.db.get_connection(DATABASE_URL)
    if page_analyzer.db.add_to_url_checks(conn, id):
        flash('Страница успешно проверена', 'success')
    else:
        flash('Произошла ошибка при проверке', 'danger')

    conn.close()

    return redirect(url_for('get_url', id=id))


@app.get('/urls')
def get_urls():
    conn = page_analyzer.db.get_connection(DATABASE_URL)
    urls = page_analyzer.db.get_all_names_and_id(conn)

    conn.close()

    return render_template(
        'urls.html',
        urls=urls
    )


@app.get('/urls/<id>')
def get_url(id):
    conn = page_analyzer.db.get_connection(DATABASE_URL)
    url = page_analyzer.db.get_info_by_id(conn, id)
    message = get_flashed_messages(with_categories=True)
    url_check = page_analyzer.db.get_info_from_url_checks(conn, id)

    conn.close()

    return render_template(
        'urls_id.html',
        name=url['name'],
        id=url['id'],
        created_at=url['created_at'],
        message=message,
        check=url_check,
    )
