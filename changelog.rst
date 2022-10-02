Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`__, and this project
adheres to `Semantic
Versioning <https://semver.org/spec/v2.0.0.html>`__.

`Unreleased <https://github.com/s-nagaev/stubborn/compare/v0.5.0...HEAD>`__
---------------------------------------------------------------------------

`0.5.0 <https://github.com/s-nagaev/stubborn/compare/v0.4.1...v0.5.0>`__ - 2022-08-17
-------------------------------------------------------------------------------------

Added
~~~~~

-  Global proxy functionality.
-  Ability to stub the specific resource from proxy logging.
-  Client’s webhook call support.
-  Jinja template support for the response body.
-  Syntax highlighting for the Response and Hooks TextEdit fields.
-  Healthcheck API endpoint (``/srv/alive``).
-  List of reserved application slugs.

Changed
~~~~~~~

-  Syntax highlighting theme for Log view.
-  Dependencies updated.
-  Whitenoise removed (serving static via uwsgi).

.. _section-1:

`0.4.1 <https://github.com/s-nagaev/stubborn/compare/v0.4.0...v0.4.1>`__ - 2022-05-15
-------------------------------------------------------------------------------------

.. _changed-1:

Changed
~~~~~~~

-  Fixed display of Cyrillic characters in logs.
-  Response body strip disabled.

.. _section-2:

`0.4.0 <https://github.com/s-nagaev/stubborn/compare/v0.3.3...v0.4.0>`__ - 2022-05-02
-------------------------------------------------------------------------------------

.. _changed-2:

Changed
~~~~~~~

-  Bug preventing the creation of a new application record fixed.

.. _section-3:

`0.3.3 <https://github.com/s-nagaev/stubborn/compare/v0.3.2...v0.3.3>`__ - 2022-04-25
-------------------------------------------------------------------------------------

.. _added-1:

Added
~~~~~

-  Tests covering the main functionality.
-  Codecov for GitHub Actions.
-  Dockerfile for local test run.
-  DEMO-mode for application run.
-  Test covering the response timeout.

.. _changed-3:

Changed
~~~~~~~

-  Dependencies updated.
-  Readme updated: tests run described, codecov badge added, DEMO
   service info added.
-  Breadcrumbs bug fixed.
-  Json handling bug fixed.
-  Minor fixes.

.. _section-4:

`0.3.2 <https://github.com/s-nagaev/stubborn/compare/v0.3.1...v0.3.2>`__ - 2022-04-10
-------------------------------------------------------------------------------------

.. _added-2:

Added
~~~~~

-  Request proxy functionality implemented.

.. _changed-4:

Changed
~~~~~~~

-  Fixed a bug connected with Request Log delete permission.

.. _section-5:

`0.3.1 <https://github.com/s-nagaev/stubborn/compare/v0.3.0...v0.3.1>`__ - 2022-03-25
-------------------------------------------------------------------------------------

.. _changed-5:

Changed
~~~~~~~

-  Admin site URL fixed.

.. _section-6:

`0.3.0 <https://github.com/s-nagaev/stubborn/compare/v0.2.1...v0.3.0>`__ - 2022-01-22
-------------------------------------------------------------------------------------

.. _changed-6:

Changed
~~~~~~~

-  Request Log displaying fixed: displaying some log records containing
   the request body could raise 500 errors.
-  Routing issue fixed: some POST requests could be redirected in the
   wrong way.

.. _section-7:

`0.2.1 <https://github.com/s-nagaev/stubborn/compare/v0.2.0...v0.2.1>`__ - 2022-01-21
-------------------------------------------------------------------------------------

.. _added-3:

Added
~~~~~

-  Environment variable ``DOMAIN_DISPLAY`` added: now the full resource
   URL can be displayed correct on the admin site in any environment.

.. _section-8:

`0.2.0 <https://github.com/s-nagaev/stubborn/compare/v0.1.3...v0.2.0>`__ - 2022-01-21
-------------------------------------------------------------------------------------

.. _added-4:

Added
~~~~~

-  XML response format support.
-  Plain Text response format support.
-  Dockerfile for production build.
-  ``create_admin`` manage command for creation a superuser with login,
   email and password according to provided environment variables.
-  Settings module for production.
-  Quick start description in README file.

.. _changed-7:

Changed
~~~~~~~

-  Request Log entity updated: now, it stores full requested and
   response data.
-  Project dependencies updated.
-  Lots of minor UI fixes.
-  Updated ``docker-compose``-file for staging environment.

.. _section-9:

`0.1.3 <https://github.com/s-nagaev/stubborn/compare/v0.1.2...v0.1.3>`__ - 2022-01-06
-------------------------------------------------------------------------------------

.. _changed-8:

Changed
~~~~~~~

-  README updated: added project description and plan for the MVP
   milestone.

.. _section-10:

`0.1.2 <https://github.com/s-nagaev/stubborn/compare/v0.1.1...v0.1.2>`__ - 2022-01-06
-------------------------------------------------------------------------------------

.. _added-5:

Added
~~~~~

-  GitHub actions with the Flake8 and Mypy checks.

.. _changed-9:

Changed
~~~~~~~

-  RequestLog entity modified: relationship with the ResponseStub entity
   provided.
-  Project dependencies updated.

.. _section-11:

`0.1.1 <https://github.com/s-nagaev/stubborn/compare/v0.1.0...v0.1.1>`__ - 2021-11-06
-------------------------------------------------------------------------------------

.. _added-6:

Added
~~~~~

-  Config for the staging environment.
-  Uwsgi config.
-  Dockerfile for application.
-  Docker-compose files for local and staging environments.
-  Makefile with basic commands.
-  Django manage command ``createadmin`` (easy to make admin user for
   local and staging environments).

.. _changed-10:

Changed
~~~~~~~

-  Django updated to 3.2.9.
-  Flake8 and flake8-isort updated to the latest versions.
-  Flake8 errors fixed.

.. _section-12:

`0.1.0 <https://github.com/s-nagaev/stubborn/tree/v0.1.0>`__ - 2021-11-05
-------------------------------------------------------------------------

.. _added-7:

Added
~~~~~

-  CRUD functionality for Application, Resource, and Response entities
   from the admin site.
-  RO functionality for RequestLog entity from the admin site.
-  API-stub functionality based on Application settings.
-  Applications settings for the local and test environments.
-  Custom template and style for the Application record to provide a
   convenient way to manage related records.
-  Custom django admin style.
-  Application logos for the admin site and Readme file.
-  Flake8 and Mypy setups.
-  This changelog file.
-  Initial Readme file.
