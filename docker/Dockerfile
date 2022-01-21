FROM pysergio/pypoetry:3.9-alpine

LABEL org.label-schema.schema-version = "1.0"
LABEL org.label-schema.name = "Stubborn"
LABEL org.label-schema.vendor = "nagaev.sv@gmail.com"
LABEL org.label-schema.vcs-url = "https://github.com/s-nagaev/stubborn"

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN poetry install

COPY . .
RUN ln -f .env.test /app/stubborn/settings/.env
RUN python manage.py collectstatic --no-input
RUN rm /app/stubborn/settings/.env

RUN addgroup -S django && adduser -S django -G django
USER django

EXPOSE 8000

ENTRYPOINT []
CMD make run
