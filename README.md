[![Quality Gate](https://github.com/s-nagaev/stubborn/actions/workflows/main.yml/badge.svg)](https://github.com/s-nagaev/stubborn/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/s-nagaev/stubborn/branch/main/graph/badge.svg?token=CVVP1BEH9P)](https://codecov.io/gh/s-nagaev/stubborn)
[![Sonar](https://img.shields.io/sonar/quality_gate/s-nagaev_stubborn/main?label=Sonar%20QG&server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/project/overview?id=s-nagaev_stubborn)
[![Issues](https://img.shields.io/github/issues/s-nagaev/stubborn)](https://github.com/s-nagaev/stubborn/issues/new)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/s-nagaev/stubborn/pulls)
<p align="center">
  <img width=150 src="https://github.com/s-nagaev/stubborn/raw/main/docs/logo.png" alt="logo">
  <br>
Just a (stupidly) simple REST API stub service.
</p>

* * *

## About
**Stubborn** is an ultimate tool for testing and debugging your APIs. With Stubborn, you can easily create mock 
responses to simulate different scenarios, proxy requests to other servers, and call webhooks to test your integration. 
Plus, Stubborn comes with full request and response logging, so you can see exactly what's happening behind the scenes. 
Best of all, Stubborn is open-source and self-hosted, so you can use it on your own infrastructure and customize it 
to meet your specific needs.

## Features
- Customizable mocking web resources.
- Customizable response timeout support.
- Full "Service-In-The-Middle" functionality allows proxy requests to third-party resources, fully capturing all 
interactions between the application under test and the third-party service (including the ability to selectively 
mock endpoints).
- Calling the webhook of the integrated application at any moment of its interaction with the Stubborn.
- JSON, XML, and Plain Text response body formats support.
- Exhaustive events log containing requests & response data with GUI.

## Prerequisite
Stubborn is shipped as a [Docker image](https://hub.docker.com/r/pysergio/stubborn). 
To use it, you need a Docker Engine installed on your machine. In addition, Docker Compose is highly recommended.

**Supported platforms:**
- linux/amd64
- linux/arm64
- linux/arm32/v7 *(Yes! You can run it on your Raspberry Pi!)*

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
      UWSGI_THREADS: 3
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
- `UWSGI_THREADS` *(optional)*: number of threads per uWSGI worker (does not connect directly with the Stubborn).

2. Then run the command:
```shell
docker-compose up -d
```
Please, note that the parameter `-d` in the command example will tell Docker Compose to run the apps defined in
`docker-compose.yml` in the background.

The site should now be running at http://0.0.0.0:8000. To access the service admin panel visit 
`http://localhost:8000/admin/` and log in as a superuser.

## Development
**The building blocks are:**
- Python 3.9+
- Django 3.2+
- Django REST Framework 3+
- PostgreSQL

### The Plan (MVP)
- [x] implement JSON response support;
- [x] dockerize the application;
- [x] add basic Quality Gate (CI: linters);
- [x] add README file;
- [x] improve UI to allow CRUD operations under the application-relative models within a specific application;
- [x] add XML response support;
- [x] add plain text response support;
- [x] publish the application images to Docker Hub;
- [x] add request proxy support;
- [x] cover code with tests;
- [x] set up the demo server;
- [x] add template support for the response body;
- [x] add client's webhook call support;
- [x] improve UI/UX.

### The Plan (future versions)
- [ ] add HTML-response support;
- [ ] add the `team` entity for sharing stub methods with teammates only;
- [ ] add the REST API for manipulation with main application entities;

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
make dev
```

Or just run everything in docker:
```shell
make docker_dev
```

The site should now be running at http://localhost:8000. To access Django administration site, 
visit `http://localhost:8000/admin/` and log in as a superuser.

### Running tests
Run tests:
```shell
make tests
```
Or just run them in docker:
```shell
make docker_tests
```