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

## Features
- Customizable mocking web resources.
- JSON, XML, Plain Text response body formats support.
- Customizable response timeout support.
- Logging containing exhaustive request & response data.

## Prerequisite
Stubborn is shipped as a [Docker image](https://hub.docker.com/r/pysergio/stubborn). 
To use it, you need a Docker Engine installed on your machine. In addition, Docker Compose is highly recommended.

**Supported platforms:**
- linux/amd64
- linux/arm64
- linux/arm/v7 *(Yes! You can run it on your Raspberry Pi!)*

## Quick Start
Here is a real-world example: 
1. Create the file `docker-compose.yml` in any directory of your choice:

```yaml
version: '3'

services:
  postgres:
    restart: unless-stopped
    image: postgres:12-alpine
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: stubborn_db
      POSTGRES_USER: stubborn_user
      POSTGRES_PASSWORD: pg_secret_password

  stubborn:
    restart: unless-stopped
    image: pysergio/stubborn:latest
    environment:
      DATABASE_URL: postgres://stubborn_user:pg_secret_password@postgres:5432/stubborn_db
      SECRET_KEY: 'stubborn-secure!$k%6kqx641a)-a6d7j8*n(!154#t+^5f)#^z5mjvlrf#u!'
      ADMIN_USERNAME: admin
      ADMIN_PASSWORD: very_secret_password
      ADMIN_EMAIL: admin@example.com
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    links:
      - postgres

volumes:
  pg_data:
```

In the example above, we have a couple of the environment variables that are very important for setting up our 
application:
- `DATABASE_URL` *(required)*: a URL containing database connection data. 
- `SECRET_KEY` *(required)*: a secret key that provides cryptographic signing and should be set to a unique, 
unpredictable value.
- `ADMIN_USERNAME` *(required for the first run only)*: a username for an administrative account.
- `ADMIN_PASSWORD` *(required for the first run only)*: a password for an administrative account.
- `ADMIN_EMAIL` *(required for the very first run only)*: an email for an administrative account.
- `DOMAIN_DISPLAY` *(optional)*: a protocol and domain where your application instance hosted, i.e. 
`https://mysite.com`, `http://192.168.1.150:8000`. The default value is `http://127.0.0.1:8000`.

2. Then run the command:
```shell
docker-compose up -d
```
Please, note that the parameter `-d` in the command example will tell Docker Compose to run the apps defined in
`docker-compose.yml` in the background.

The site should now be running at http://0.0.0.0:8000. To access the service admin panel visit 
`http://localhost:8000/admin/` and log in as a superuser.

## Development

### The Plan (MVP)
- [x] implement JSON response support;
- [x] dockerize the application;
- [x] add basic Quality Gate (CI: linters);
- [x] add README file;
- [x] improve UI to allow CRUD operations under the application-relative models within a specific application;
- [x] add XML response support;
- [x] add plain text response support;
- [x] publish the application images to Docker Hub;
- [ ] cover code with tests;
- [ ] add template support for the response body;
- [ ] add client's webhook call support;
- [ ] add GraphQL over http support;
- [ ] add the REST API for manipulation with main application entities;  
- [ ] add the `team` entity for sharing stub methods with teammates only;
- [ ] improve UI/UX.

### Setting Up for Development
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
