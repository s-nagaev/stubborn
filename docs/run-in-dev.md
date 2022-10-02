# Running in Developmen (Locally)

## Setting Up

**To set up the development environment:**

1. Install [Poetry](https://python-poetry.org/) dependency manager (please, feel free to use any other way to install it
on your local machine):

```shell
curl -sSL https://install.python-poetry.org | python -
```

2. Check out project code:

```shell
git clone https://github.com/s-nagaev/stubborn.git
```

3. Install requirements using Poetry:

```shell
poetry install
```

4. Create database tables and a superuser account (please, don't forget to install and set up the Postgres first):

```shell
python manage.py migrate
python manage.py createsuperuser
```

## Run

Run development server:

```shell
make dev
```

Or just run everything in docker:

```shell
make docker_dev
```

The site should now be running at <http://localhost:8000>. To access Django administration site, visit <http://localhost:8000/admin/> and log in as a superuser.

## Runing tests

Run tests:

```shell
make tests
```

Or just run them in docker:

```shell
make docker_tests
```
