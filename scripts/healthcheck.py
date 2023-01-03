import logging

import requests

HOST = '127.0.0.1'
PORT = '8000'
URI = '/srv/alive'

logger = logging.getLogger('healthcheck')


def check():
    try:
        response = requests.get(url=f'http://{HOST}:{PORT}{URI}')
        response.raise_for_status()
    except Exception as e:
        logger.error(f'Health Check FAILED: {e}')
        exit(1)

    logger.info(f'Health Check OK: {response.status_code}')


if __name__ == '__main__':
    check()
