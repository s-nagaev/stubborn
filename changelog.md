# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.0] - 2023-11-25

### Added

- Ability to turn applications on/off.

### Changed

- Code slightly refactored.
- Dependencies updated.

## [1.5.0] - 2023-09-30

### Added

- The "duplicate" functionality for applications.

## [1.4.3] - 2023-09-13

### Added

- Optional Stubborn request ID header injection: now it's possible to automatically inject headers `Stubborn-Log-Id`
and `Stubborn-Log-Url` to the Stubborn response. `Stubborn-Log-Id` containing the corresponding log ID in the Stubborn 
database and `Stubborn-Log-Url` containing full URL to the corresponding log record.
corresponding request log.
- Advanced filters for Request Logs data including multiselect filter for the related Application Resource.

### Changed

- Dependencies updated.
- Base docker image changed to the `python:3.10-alpine3.18`. 

## [1.4.2] - 2023-07-01

### Changed

- Base docker image changed to the `python:3.10-alpine3.16`.

## [1.4.1] - 2023-06-18

### Changed

- Dependencies actualized.

## [1.4.0] - 2023-04-27

### Added

- The "duplicate" functionality for resources, responses and webhooks.

### Changed

- Dependencies updated.

## [1.3.0] - 2023-03-11

### Added

- The ability to create identical resources and switch between them.
- Tests covering "Stub It!" functionality.
- Redirect to the application page after related objects deleted.

### Fixed

- A bug when creating a resource stub from the request log could cause an exception if the request didn't contain the Content-Type header.

## [1.2.0] - 2023-03-05

### Added

- docker-compose examples updated and moved to the separate directory.

### Changed

- Default environment set to "production".
- Project files structure slightly updated.
- `README.md` file updated: outdated info (from the MVP milestopne) removed.
- Typos in the `changelog.md` file fixed.

### Fixed

- Fixed bug when the clicking "Stub it!" button on the request log page could cause an exception.

## [1.1.1] - 2023-02-23

### Changed

- Updated project dependencies to package versions that do not contain known vulnerabilities.

## [1.1.0] - 2023-02-01

### Fixed

- Fixed bug when the stub response with an empty body could cause an exception.

## [1.0.2] - 2023-01-14

### Changed

- Dockerfile updated, docker image size reduced.
- README file slightly updated.

## [1.0.1] - 2023-01-05

### Changed

- Default sorting fixed for Request Logs and Application change lists.
- Response HTML code displaying fixed in the Request Log detail page.
- Log format slightly updated.

## [1.0.0] - 2023-01-03

### Changed

- Now using UUID as and ID and PK for every entity.
- Request Logs UI improved: added search functionality and data filters.
- Hooks UI improved: removed the ability to configure hooks using mutually exclusive options.
- Code refactored.
- Improved logging of incoming API requests and service responses.
- Dependencies updated.
- Dockerfile updated: removed poetry from the docker image build steps.

### Fixed

- Fixed a 500 error occurred while proxying data containing request body in latin-1 encoding.

## [0.5.0] - 2022-08-17

### Added

- Global proxy functionality.
- Ability to stub the specific resource from proxy logging.
- Client's webhook call support.
- Jinja template support for the response body.
- Syntax highlighting for the Response and Hooks TextEdit fields.
- Healthcheck API endpoint (`/srv/alive`).
- List of reserved application slugs.

### Changed

- Syntax highlighting theme for Log view.
- Dependencies updated.
- Whitenoise removed (serving static via uwsgi).

## [0.4.1] - 2022-05-15

### Changed

- Fixed display of Cyrillic characters in logs.
- Response body strip disabled.

## [0.4.0] - 2022-05-02

### Changed

- Bug preventing the creation of a new application record fixed.

## [0.3.3] - 2022-04-25

### Added

- Tests covering the main functionality.
- Codecov for GitHub Actions.
- Dockerfile for local test run.
- DEMO-mode for application run.
- Test covering the response timeout.

### Changed

- Dependencies updated.
- Readme updated: tests run described, codecov badge added, DEMO service info added.
- Breadcrumbs bug fixed.
- Json handling bug fixed.
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

[Unreleased]: https://github.com/s-nagaev/stubborn/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/s-nagaev/stubborn/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/s-nagaev/stubborn/compare/v1.4.3...v1.5.0
[1.4.3]: https://github.com/s-nagaev/stubborn/compare/v1.4.2...v1.4.3
[1.4.2]: https://github.com/s-nagaev/stubborn/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/s-nagaev/stubborn/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/s-nagaev/stubborn/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/s-nagaev/stubborn/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/s-nagaev/stubborn/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/s-nagaev/stubborn/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/s-nagaev/stubborn/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/s-nagaev/stubborn/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/s-nagaev/stubborn/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/s-nagaev/stubborn/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/s-nagaev/stubborn/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/s-nagaev/stubborn/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/s-nagaev/stubborn/compare/v0.3.3...v0.4.0
[0.3.3]: https://github.com/s-nagaev/stubborn/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/s-nagaev/stubborn/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/s-nagaev/stubborn/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/s-nagaev/stubborn/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/s-nagaev/stubborn/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/s-nagaev/stubborn/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/s-nagaev/stubborn/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/s-nagaev/stubborn/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/s-nagaev/stubborn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/s-nagaev/stubborn/tree/v0.1.0
