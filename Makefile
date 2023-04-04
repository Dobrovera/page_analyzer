dev:
	poetry run flask --app page_analyzer:app run

build:
	poetry build

package-install:
	python3 -m pip install --force dist/*.whl

lint:
	poetry run flake8 page_analyzer

PORT ?= 8000
start:
	pip install --upgrade pip
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

install:
	poetry install
