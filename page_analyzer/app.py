import os
from dotenv import load_dotenv
from flask import Flask, render_template


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False)
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)


@app.get('/')
def hello_world():
    return render_template(
        'index.html',
    )
