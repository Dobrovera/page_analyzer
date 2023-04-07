import os
from dotenv import load_dotenv
from flask import Flask
from flask import render_template


app = Flask(__name__)


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False)


@app.route('/')
def hello_world():
    return render_template(
        'index.html',
    )
