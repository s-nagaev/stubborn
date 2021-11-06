dev:
	python manage.py runserver 0.0.0.0:8000

reset:
	python manage.py reset_db --noinput && make prepare

uwsgi:
	uwsgi --ini=deploy/uwsgi.ini

uwsgi_dev:
	uwsgi --ini=deploy/uwsgi.ini --py-autoreload=2

prepare:
	python manage.py migrate \
	&& python manage.py collectstatic --no-input

#### Development (Docker) ##############################################################################################

docker_dev:
	docker-compose -f docker-compose.local.yml up --build

#### Staging ###########################################################################################################

staging_run:
	docker-compose -f docker-compose.staging.yml up --build -d

staging_down:
	docker-compose -f docker-compose.staging.yml down
