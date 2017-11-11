# Status

[![Build Status](https://travis-ci.org/ckwagaba/flask_api.svg?branch=master)](https://travis-ci.org/ckwagaba/flask_api?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/ckwagaba/flask_api/badge.svg?branch=master)](https://coveralls.io/github/ckwagaba/flask_api?branch=master)

# Bucketlist Flask API

This API helps you build an application that allows users keep track of their dreams and goals.
<br />
Read the documentation <a href="https://ckwagabaflaskapi.docs.apiary.io/">here</a>.
<br /><br />
The API is hosted on heroku: https://ckwagaba-flask-api.herokuapp.com<br />
You can interact with it using <u>Postman</u>

# Installation

<ol>

<li>Firstly, make sure you got the following installed:
<br />brew install... on MacOS
<ul>
<li>Git</li>
<li>PostgreSQL</li>
<li>Virtualenv</li>
</ul>
</li>

<li>Switch into your project directory and create a virtual environment: $ virtualenv venv</li>

<li>
Start the virtual environment: $ . venv/bin/activate
</li>

<li>
Then clone the source code from Github to your development environment by typing the following command at your terminal: <br />
git clone https://github.com/ckwagaba/flask_api.git
</li>

<li>Use branching to your advantage.</li>

<li>
Install dependencies: $ pip install -r requirements.txt
</li>

<li>
Create a database: <br />
$ psql --user postgres <br />
$ postgres=# create database bucketlist;
</li>

<li>
Create the tables: <br />
$ python manage.py db migrate <br />
$ python manage.py db upgrade
</li>

<li>
Export Environment Variables: <br />
$ export APP_SETTINGS='development' <br />
$ export FLASK_DEBUG=1 <br />
export FLASK_APP=run.py
</li>

<li>
Run the application: <br />
$ flask run <br />
The output provides an address to run the app in your browser: http://localhost:5000
</li>

</ol>

# Testing

The API uses the unittest framework for testing and nose for discovery: <br />
$ pip install coveralls
$ nosetests <br />
or <br />
$ nosetests --with-coverage --cover-package=app
