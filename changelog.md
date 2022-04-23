# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Tests covering the main functionality.
- Codecov for GitHub Actions.
- Dockerfile for local test run.

### Changed
- Dependencies updated.
- Readme updated: tests run described, codecov badge added.
- Minor fixes.

## [0.3.2] - 2022-04-10
### Added
- Request proxy functionality implemented.

### Changed
- Fixed a bug connected with Request Log delete permission.

## [0.3.1] - 2022-03-25
### Changed
- Admin site URL fixed.

## [0.3.0] - 2022-01-22
### Changed
- Request Log displaying fixed: displaying some log records containing the request body could raise 500 errors.
- Routing issue fixed: some POST requests could be redirected in the wrong way.

## [0.2.1] - 2022-01-21
### Added
- Environment variable `DOMAIN_DISPLAY` added: now the full resource URL can be displayed correct on the admin site 
in any environment. 

## [0.2.0] - 2022-01-21
### Added
- XML response format support.
- Plain Text response format support.
- Dockerfile for production build.
- `create_admin` manage command for creation a superuser with login, email and password according to provided 
environment variables.
- Settings module for production.
- Quick start description in README file.

### Changed
- Request Log entity updated: now, it stores full requested and response data.
- Project dependencies updated.
- Lots of minor UI fixes.
- Updated `docker-compose`-file for staging environment.

## [0.1.3] - 2022-01-06
### Changed
- README updated: added project description and plan for the MVP milestone.

## [0.1.2] - 2022-01-06
### Added
- GitHub actions with the Flake8 and Mypy checks.

### Changed
- RequestLog entity modified: relationship with the ResponseStub entity provided.
- Project dependencies updated.

## [0.1.1] - 2021-11-06
### Added
- Config for the staging environment.
- Uwsgi config.
- Dockerfile for application.
- Docker-compose files for local and staging environments.
- Makefile with basic commands.
- Django manage command `createadmin` (easy to make admin user for local and staging environments). 

### Changed
- Django updated to 3.2.9.
- Flake8 and flake8-isort updated to the latest versions.
- Flake8 errors fixed.


## [0.1.0] - 2021-11-05
### Added
- CRUD functionality for Application, Resource, and Response entities from the admin site.
- RO functionality for RequestLog entity from the admin site.
- API-stub functionality based on Application settings.
- Applications settings for the local and test environments.
- Custom template and style for the Application record to provide a convenient way to manage related records.
- Custom django admin style.
- Application logos for the admin site and Readme file.
- Flake8 and Mypy setups.
- This changelog file.
- Initial Readme file. 
