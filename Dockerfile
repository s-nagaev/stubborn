FROM python:3.10-alpine3.16 AS builder

RUN apk update \
    && apk upgrade \
    && apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev zlib-dev git bash curl build-base

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

FROM python:3.10-alpine3.16

LABEL org.label-schema.schema-version = "1.0"
LABEL org.label-schema.name = "Stubborn"
LABEL org.label-schema.vendor = "nagaev.sv@gmail.com"
LABEL org.label-schema.vcs-url = "https://github.com/s-nagaev/stubborn"
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk add --no-cache mailcap libpq-dev make

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
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
