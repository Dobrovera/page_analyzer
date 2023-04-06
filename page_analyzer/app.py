import os
from dotenv import load_dotenv
from flask import Flask


app = Flask(__name__)


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False)


@app.route('/')
def hello_world():
    return 'Hello 3 project!'
