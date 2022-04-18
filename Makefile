#### Common ############################################################################################################
admin:
	python manage.py create_admin

migrate:
	python manage.py migrate

static:
	python manage.py collectstatic --no-input

uwsgi:
	uwsgi --ini=deploy/uwsgi.ini

run:
	make migrate admin uwsgi

#### Development #######################################################################################################
dev:
	DJANGO_SETTINGS_MODULE=stubborn.settings.local python manage.py runserver 0.0.0.0:8000

dev_shell:
	DJANGO_SETTINGS_MODULE=stubborn.settings.local python manage.py shell

reset:
	python manage.py reset_db --noinput && make prepare

uwsgi_dev:
	uwsgi --ini=deploy/uwsgi.ini --py-autoreload=2

#### Development (Docker) ##############################################################################################
docker_dev:
	docker-compose -f docker-compose.dev.yml up --build

#### Staging ###########################################################################################################
staging_run:
	docker-compose -f docker-compose.staging.yml up -d

staging_down:
	docker-compose -f docker-compose.staging.yml down
