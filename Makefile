#### Common ############################################################################################################
admin:
	python manage.py create_admin

dummy_admin:  # will create an superuser with login `admin` and passwd `admin`. Doesn't work in production env.
	python manage.py create_dummy_admin

migrate:
	python manage.py migrate

static:
	python manage.py collectstatic --no-input

uwsgi:
	uwsgi --ini=stubborn/settings/uwsgi/uwsgi.ini

run:
	make migrate admin uwsgi

linters:
	flake8 . && mypy .

tests:
	pytest -vv


#### Development #######################################################################################################
dev:
	DJANGO_SETTINGS_MODULE=stubborn.settings.local python manage.py runserver 0.0.0.0:8000

dev_shell:
	DJANGO_SETTINGS_MODULE=stubborn.settings.local python manage.py shell

reset:
	python manage.py reset_db --noinput && make prepare

uwsgi_dev:
	DJANGO_SETTINGS_MODULE=stubborn.settings.local uwsgi --ini=stubborn/settings/uwsgi/uwsgi_dev.ini --py-autoreload=2

upgrade:
	rm -f poetry.lock \
	&& poetry install \
	&& poetry export -f requirements.txt --output requirements.txt \
	&& poetry export --dev -f requirements.txt --output requirements-dev.txt

#### Staging ###########################################################################################################
staging_run:
	docker-compose -f docker-compose.staging.yml up -d

staging_down:
	docker-compose -f docker-compose.staging.yml down

#### Build #############################################################################################################
export_req:
	poetry export -f requirements.txt --output requirements.txt

VERSION ?= dev

build:
	docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 \
		-t pysergio/stubborn:$(VERSION) -f Dockerfile . --push

build_latest:
	docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 \
		-t pysergio/stubborn:$(VERSION) \
		-t pysergio/stubborn:latest --cache-from=pysergio/stubborn:buildcache \
		--cache-to=pysergio/stubborn:buildcache -f Dockerfile . --push
