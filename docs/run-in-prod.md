# Running in Production

Stubborn is shipped as a [Docker image](https://hub.docker.com/r/pysergio/stubborn). To use it, you need a [Docker Engine](https://docs.docker.com/engine/installation/) installed on your machine. In addition, [Docker Compose](https://docs.docker.com/compose/install/) is highly recommended. Please, refer to their documentation about download and installation options.

## Simple real-world example

1. Create the file `docker-compose.yml` in any directory of your choice:

```yaml
version: '3'

services:
  postgres:
    restart: unless-stopped
    image: postgres:12-alpine
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: stubborn_db
      POSTGRES_USER: stubborn_user
      POSTGRES_PASSWORD: pg_secret_password

  stubborn:
    restart: unless-stopped
    image: pysergio/stubborn:latest
    environment:
      DATABASE_URL: postgres://stubborn_user:pg_secret_password@postgres:5432/stubborn_db
      SECRET_KEY: 'stubborn-secure!$k%6kqx641a)-a6d7j8*n(!154#t+^5f)#^z5mjvlrf#u!'
      ADMIN_USERNAME: admin
      ADMIN_PASSWORD: very_secret_password
      ADMIN_EMAIL: admin@example.com
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    links:
      - postgres

volumes:
  pg_data:
```

2. Then run the command:

```shell
docker-compose up -d
```

Please, note that the parameter `-d` in the command example will tell Docker Compose to run the apps defined in
`docker-compose.yml` in the background.

The site should now be running at <http://0.0.0.0:8000>. To access the service admin panel visit <http://localhost:8000/admin/> and log in as a superuser.

## Running service via HTTPS using reverse-proxy

### Using [HTTPS-PORTAL](https://github.com/SteveLTN/https-portal)

```yaml
version: '3'

services:
  https-portal:
    image: steveltn/https-portal:1
    ports:
      - '80:80'
      - '443:443'
    restart: always
    environment:
      STAGE: production
      DOMAINS: 'my-lovely-domain-name.com -> http://stubborn:8000'
    volumes:
      - https-portal-data:/var/lib/https-portal
  
  postgres:
    restart: unless-stopped
    image: postgres:12-alpine
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: stubborn_db
      POSTGRES_USER: stubborn_user
      POSTGRES_PASSWORD: pg_secret_password

  stubborn:
    restart: unless-stopped
    image: pysergio/stubborn:latest
    environment:
      DATABASE_URL: postgres://stubborn_user:pg_secret_password@postgres:5432/stubborn_db
      SECRET_KEY: 'stubborn-insecure!$k%6kqx641a)-a6d7j8*n(!154#t+^5f)#^z5mjvlrf#u!'
      ADMIN_USERNAME: admin
      ADMIN_PASSWORD: very_secret_password
      ADMIN_EMAIL: admin@example.com
    depends_on:
      - postgres
    links:
      - postgres

volumes:
  pg_data:
  https-portal-data:
```

### Using [Caddy](https://github.com/caddyserver/caddy)

```yaml
version: '3'

services:
  postgres:
    restart: unless-stopped
    image: postgres:12-alpine
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: stubborn_db
      POSTGRES_USER: stubborn_user
      POSTGRES_PASSWORD: pg_secret_password

  stubborn:
    restart: unless-stopped
    image: pysergio/stubborn:latest
    environment:
      DATABASE_URL: postgres://stubborn_user:pg_secret_password@postgres:5432/stubborn_db
      SECRET_KEY: 'stubborn-insecure!$k%6kqx641a)-a6d7j8*n(!154#t+^5f)#^z5mjvlrf#u!'
      ADMIN_USERNAME: admin
      ADMIN_PASSWORD: very_secret_password
      ADMIN_EMAIL: admin@example.com
    depends_on:
      - postgres
    links:
      - postgres
  
  caddy:
    image: caddy:latest
    restart: unless-stopped
    command: caddy reverse-proxy --from https://my-lovely-domain-name.com:443 --to http://stubborn:8000
    ports:
      - 80:80
      - 443:443
    volumes:
      - caddy:/data
    depends_on:
      - stubborn

volumes:
  pg_data:
  caddy:
```

## Envirionment Variables

In the examples above, we have a couple of the environment variables that are very important for setting up our application:

- `DATABASE_URL` *(required)*: a URL containing database connection data.
It should looks like:
`postgres://<postgres user name>:<postgres user password>@<postgres domain name or IP address>:<postgres port>/<database name>`
- `SECRET_KEY` *(required)*: a secret key that provides cryptographic signing and should be set to a unique, unpredictable value.
- `ADMIN_USERNAME` *(required for the first run only)*: a username for an administrative account.
- `ADMIN_PASSWORD` *(required for the first run only)*: a password for an administrative account.
- `ADMIN_EMAIL` *(required for the very first run only)*: an email for an administrative account.
- `DOMAIN_DISPLAY` *(optional)*: a protocol and domain where your application instance hosted, i.e. `https://mysite.com`, `http://192.168.1.150:8000`. The default value is `http://127.0.0.1:8000`.
