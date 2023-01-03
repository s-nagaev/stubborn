FROM python:3.9-alpine3.16

LABEL org.label-schema.schema-version = "1.0"
LABEL org.label-schema.name = "Stubborn"
LABEL org.label-schema.vendor = "nagaev.sv@gmail.com"
LABEL org.label-schema.vcs-url = "https://github.com/s-nagaev/stubborn"

RUN apk update \
    && apk upgrade \
    && apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev zlib-dev git bash curl build-base

RUN apk add --no-cache mailcap libpq-dev make

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

RUN apk del .build-deps

COPY . .
RUN ln -f .env.test /app/stubborn/settings/.env
RUN python manage.py collectstatic --no-input
RUN rm /app/stubborn/settings/.env

RUN addgroup -S django && adduser -S django -G django
USER django

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=3s --start-period=30s CMD python scripts/healthcheck.py || exit 1
ENTRYPOINT []
CMD make run
