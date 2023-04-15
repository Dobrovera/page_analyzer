#### Hexlet tests and linter status:
[![Actions Status](https://github.com/Dobrovera/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Dobrovera/python-project-83/actions) [![linter](https://github.com/Dobrovera/python-project-83/actions/workflows/linter.yml/badge.svg)](https://github.com/Dobrovera/python-project-83/actions/workflows/linter.yml) <a href="https://codeclimate.com/github/Dobrovera/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/2062294c2fbac526d5ab/maintainability" /></a>

#### [Ссылка](https://python-project-83-production-33cc.up.railway.app/) на домен

### Анализатор страниц

Приложение для анализа сраниц в интернете. Выводит и хранит данные по запрошеным url:
 + h1
 + status_code
 + title
 + description
 + Дату последней проверки

В файле database.url можно найти SQL-запросы для создания локальной БД

Для локального запуска:
> git clone https://github.com/Dobrovera/python-project-83
> 
> cd python-project-83
> 
> make install

> touch .env


Необходимо самостоятельно добавить в .env файл переменные окрyжения 

+ FLASK_APP=page_analyzer 
+ FLASK_RUN_PORT=8000 
+ DATABASE_URL={provider}://{user}:{password}@{host}:{port}/{db} 
+ SECRET_KEY="some-txt"