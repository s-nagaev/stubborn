FROM pysergio/pypoetry:3.9-alpine

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

RUN poetry install

COPY . .
RUN ln -f .env.test /app/stubborn/settings/.env
RUN python manage.py collectstatic --no-input

RUN addgroup -S django && adduser -S django -G django
