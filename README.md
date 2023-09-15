[![Actions Status](https://github.com/Dobrovera/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Dobrovera/python-project-83/actions) [![linter](https://github.com/Dobrovera/python-project-83/actions/workflows/linter.yml/badge.svg)](https://github.com/Dobrovera/python-project-83/actions/workflows/linter.yml) <a href="https://codeclimate.com/github/Dobrovera/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/2062294c2fbac526d5ab/maintainability" /></a>

#### [link](https://python-project-83-production-33cc.up.railway.app/) to the domain

### Web Page Analyzer 

Application to analyze web pages. Prints and stores data on requested url: 
 + h1
 + status_code
 + title
 + description
 +  date of the last check
 
To run locally:
> #### git clone https://github.com/Dobrovera/page_analyzer
> 
> #### cd python-project-83
> 
> #### make install
> 
> #### touch .env


You need to add variables to .env file


+ FLASK_APP=page_analyzer 
+ FLASK_RUN_PORT=8000 
+ DATABASE_URL={provider}://{user}:{password}@{host}:{port}/{db} 
+ SECRET_KEY="some-txt"

SQL queries for creating tables in local database are in database.sql file
