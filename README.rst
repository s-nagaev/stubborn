|Quality Gate| |codecov| |Sonar| |Issues| |PRs Welcome|

.. raw:: html

   <p align="center">
     <img width=150 src="docs/logo.png" alt="logo">
     <br>
   Just a (stupidly) simple REST API stub service.
   </p>

--------------

About
-----

**Stubborn** is a free and open-source web application providing a
virtual API stub service for testing and development purposes.

API stub methods might be handy in mocking the third-party API services.
So, the main idea is to provide a minimal implementation of an interface
that allows the developer or tester to set up an API method that returns
hardcoded (and partly generated) data tightly coupled to the test suite.
Also, it must be easy to share the stub with teammates and (or) use it
permanently with the staging instance of the main application.

**The building blocks are:**

-  Python 3.9+
-  Django 3.2+
-  Django REST Framework 3+
-  PostgreSQL

Features
--------

-  Customizable mocking web resources.
-  JSON, XML, Plain Text response body formats support.
-  Customizable response timeout support.
-  Logging containing exhaustive request & response data.

Prerequisite
------------

Stubborn is shipped as a `Docker
image <https://hub.docker.com/r/pysergio/stubborn>`__. To use it, you
need a Docker Engine installed on your machine. In addition, Docker
Compose is highly recommended.

**Supported platforms:**

-  linux/amd64
-  linux/arm64
-  linux/arm/v7 *(Yes! You can run it on your Raspberry Pi!)*

Quick Start
-----------

Here is a real-world example:

1. Create the file ``docker-compose.yml`` in any directory of your
   choice:

.. code:: yaml

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

In the example above, we have a couple of the environment variables that
are very important for setting up our application:

-  ``DATABASE_URL`` *(required)*: a URL containing database connection
   data.
-  ``SECRET_KEY`` *(required)*: a secret key that provides cryptographic
   signing and should be set to a unique, unpredictable value.
-  ``ADMIN_USERNAME`` *(required for the first run only)*: a username
   for an administrative account.
-  ``ADMIN_PASSWORD`` *(required for the first run only)*: a password
   for an administrative account.
-  ``ADMIN_EMAIL`` *(required for the very first run only)*: an email
   for an administrative account.
-  ``DOMAIN_DISPLAY`` *(optional)*: a protocol and domain where your
   application instance hosted, i.e. ``https://mysite.com``,
   ``http://192.168.1.150:8000``. The default value is
   ``http://127.0.0.1:8000``.

2. Then run the command:

.. code:: shell

   docker-compose up -d

Please, note that the parameter ``-d`` in the command example will tell
Docker Compose to run the apps defined in ``docker-compose.yml`` in the
background.

The site should now be running at
`http://0.0.0.0:8000 <http://0.0.0.0:8000>`__. To access the service
admin panel visit ``http://localhost:8000/admin/`` and log in as a
superuser.

Can I try it right now?
-----------------------

Sure! You may check the DEMO-version of the service here:
`https://mocked.dev <https://mocked.dev>`__

======== ========
Login    Password
======== ========
``demo`` ``demo``
======== ========

..

   Please note, that everything you do will be restored in 1 hour.

Development
-----------

The Plan (MVP)
~~~~~~~~~~~~~~

-  ☒ implement JSON response support;
-  ☒ dockerize the application;
-  ☒ add basic Quality Gate (CI: linters);
-  ☒ add README file;
-  ☒ improve UI to allow CRUD operations under the application-relative
   models within a specific application;
-  ☒ add XML response support;
-  ☒ add plain text response support;
-  ☒ publish the application images to Docker Hub;
-  ☒ add request proxy support;
-  ☒ cover code with tests;
-  ☒ set up the demo server;
-  ☒ add template support for the response body;
-  ☒ add client's webhook call support;
-  ☐ add HTML-response support;
-  ☐ add the ``team`` entity for sharing stub methods with teammates
   only;
-  ☐ add the REST API for manipulation with main application entities;
-  ☐ improve UI/UX.

Setting Up for Development
~~~~~~~~~~~~~~~~~~~~~~~~~~

**To set up the development environment:** Install
`Poetry <https://python-poetry.org/>`__ dependency manager (please, feel
free to use any other way to install it on your local machine):

.. code:: shell

   curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

Check out project code:

.. code:: shell

   git clone https://github.com/s-nagaev/stubborn.git

Install requirements using Poetry:

.. code:: shell

   poetry install

Create database tables and a superuser account (please, don't forget to
install and set up the Postgres first):

.. code:: shell

   python manage.py migrate
   python manage.py createsuperuser

Run development server:

.. code:: shell

   make dev

Or just run everything in docker:

.. code:: shell

   make docker_dev

The site should now be running at
`http://localhost:8000 <http://localhost:8000>`__. To access Django
administration site, visit ``http://localhost:8000/admin/`` and log in
as a superuser.

Running tests
~~~~~~~~~~~~~

Run tests:

.. code:: shell

   make tests

Or just run them in docker:

.. code:: shell

   make docker_tests

.. |Quality Gate| image:: https://github.com/s-nagaev/stubborn/actions/workflows/main.yml/badge.svg
   :target: https://github.com/s-nagaev/stubborn/actions/workflows/main.yml
.. |codecov| image:: https://codecov.io/gh/s-nagaev/stubborn/branch/main/graph/badge.svg?token=CVVP1BEH9P
   :target: https://codecov.io/gh/s-nagaev/stubborn
.. |Sonar| image:: https://img.shields.io/sonar/quality_gate/s-nagaev_stubborn/main?label=Sonar%20QG&server=https%3A%2F%2Fsonarcloud.io
   :target: https://sonarcloud.io/project/overview?id=s-nagaev_stubborn
.. |Issues| image:: https://img.shields.io/github/issues/s-nagaev/stubborn
   :target: https://github.com/s-nagaev/stubborn/issues/new
.. |PRs Welcome| image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg
   :target: https://github.com/s-nagaev/stubborn/pulls
