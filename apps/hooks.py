import logging
from time import sleep
from typing import cast

import requests
from django.conf import settings
from django.db.models import QuerySet

from apps import enums, models

logger = logging.getLogger(__name__)


def process_wait(*, timeout, **kwargs):
    logger.debug(f"Run wait hook. timeout={timeout}")
    if settings.DEBUG:
        timeout = 1
    sleep(timeout)


def process_webhook(*, headers, body, uri, method, **kwargs):
    logger.debug(f"Run webhook. headers={headers}, body={body}, destination_url={uri}, method={method}")
    try:
        requests.request(
            method=method,
            url=uri,
            # params=query_params,
            headers=headers,
            data=body
        )
    except Exception as e:
        logger.debug(f"Hook failed. Error - {e}")
        ...


HOOK_FIELDS = ["action", "timeout", ]
REQUEST_STUB_FIELDS = ["headers", "body", "method", "uri", "format"]

process_action = {
    enums.Action.WAIT: process_wait,
    enums.Action.WEBHOOK: process_webhook,
}


def process_hook(hooks: QuerySet, **context):
    for hook in hooks:
        cast(hook, models.ResourceHook)
        _context = {
            **context,
            **{k: v for k, v in hook.__dict__.items() if k in HOOK_FIELDS}
        }
        if hasattr(hook, "request") and hook.request:
            _context.update(**{k: v for k, v in hook.request.__dict__.items() if k in REQUEST_STUB_FIELDS})

        process_action[hook.action](**_context)


def before_request(resource: models.ResourceStub):
    hooks = resource.resourcehook_set.filter(lifecycle=enums.Lifecycle.BEFORE_REQUEST)
    return process_hook(hooks=hooks)


def after_request(resource: models.ResourceStub):
    hooks = resource.resourcehook_set.filter(lifecycle=enums.Lifecycle.AFTER_REQUEST)
    return process_hook(hooks=hooks)


def after_response(resource: models.ResourceStub):
    # ToDo run after_response
    hooks = resource.resourcehook_set.filter(lifecycle=enums.Lifecycle.AFTER_RESPONSE)
    return process_hook(hooks=hooks)