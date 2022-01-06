![Build Status](https://github.com/s-nagaev/stubborn/workflows/Quality%20Gate/badge.svg)

<p align="center">
  <img width=150 src="docs/logo.png" alt="logo">
  <br>
Just a (stupidly) simple REST API stub service.
</p>

* * *

## About
**Stubborn** is a free and open-source web application providing a virtual API stub service for testing and 
development purposes.

API stub methods might be handy in mocking the third-party API services. So, the main idea is to provide a minimal 
implementation of an interface that allows the developer or tester to set up an API method that returns hardcoded 
(and partly generated) data tightly coupled to the test suite. Also, it must be easy to share the stub with 
teammates and (or) use it permanently with the staging instance of the main application.

**The building blocks are:**
- Python 3.9+
- Django 3.2+
- Django REST Framework 3+
- PostgreSQL

## The Plan (MVP)
- [ ] add XML response support;
- [ ] add plain text response support;
- [ ] add calculated values support to the response stub;
- [ ] add the `team` entity for sharing stub methods with teammates only;
- [ ] add GraphQL over http support;
- [ ] improve UI/UX.

## Setting Up for Development
**To set up the development environment:**
Install [Poetry](https://python-poetry.org/) dependency manager (please, feel free to use any other way to install it
on your local machine):
```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Check out project code:
```shell
git clone https://github.com/s-nagaev/stubborn.git
```

Install requirements using Poetry:
```shell
poetry install
```

Create database tables and a superuser account (please, don't forget to install and set up the Postgres first):
```shell
python manage.py migrate
python manage.py createsuperuser
```

Run development server:
```shell
python manage.py runserver
```

Or just run everything in docker:
```shell
make docker_dev
```

The site should now be running at http://localhost:8000. To access Django administration site, 
visit `http://localhost:8000/admin/` and log in as a superuser.
