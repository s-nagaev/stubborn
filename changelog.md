# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
