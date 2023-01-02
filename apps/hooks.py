import logging
from threading import Event
from time import sleep
from typing import Any, Callable, Dict

import requests
from django.conf import settings
from django.db.models import QuerySet

from apps import enums, models
from apps.utils import run_in_separate_thread

logger = logging.getLogger(__name__)


def process_wait(*, timeout, **kwargs):
    logger.debug(f'Run wait hook. timeout={timeout}')
    if settings.DEBUG:
        timeout = 1

    if kwargs.get('threading_mode'):
        Event().wait(timeout)
    else:
        sleep(timeout)


def process_webhook(*, headers, body, uri, method, query_params, **kwargs):
    logger.debug(
        f'Run webhook. headers={headers}, body={body}, destination_url={uri}, '
        f'method={method}, query_params={query_params}'
    )
    try:
        response = requests.request(method=method, url=uri, params=query_params, headers=headers, data=body)
        logger.debug(response)
    except Exception as e:
        logger.debug(f'Hook failed. Error - {e}')


HOOK_FIELDS = [
    'action',
    'timeout',
]
REQUEST_STUB_FIELDS = ['headers', 'body', 'method', 'uri', 'format', 'query_params']

process_action: Dict[str, Callable] = {
    enums.Action.WAIT: process_wait,
    enums.Action.WEBHOOK: process_webhook,
}


def _get_hook_context(hook: models.ResourceHook, extra_context: Dict) -> Dict:
    context: Dict[str, Any] = {}
    for context_field in [*HOOK_FIELDS, *REQUEST_STUB_FIELDS]:
        context.setdefault(context_field, None)

    context.update(
        {
            **extra_context,
            **{k: getattr(hook, k, None) for k in HOOK_FIELDS},
        }
    )

    if hasattr(hook, 'request') and hook.request:
        context.update(**{k: getattr(hook.request, k, None) for k in REQUEST_STUB_FIELDS})

    return context


def process_hook(hooks: QuerySet[models.ResourceHook], **extra_context):
    for hook in hooks:
        _context = _get_hook_context(hook, extra_context)
        action: Callable = process_action[hook.action]
        action(**_context)
    logger.debug('Hooks processed!')


def before_request(resource: models.ResourceStub):
    hooks = resource.hooks.filter(lifecycle=enums.Lifecycle.BEFORE_REQUEST)
    return process_hook(hooks=hooks)


def after_request(resource: models.ResourceStub):
    hooks = resource.hooks.filter(lifecycle=enums.Lifecycle.AFTER_REQUEST)
    return process_hook(hooks=hooks)


@run_in_separate_thread
def after_response(resource_pk: str):
    resource = models.ResourceStub.objects.get(pk=resource_pk)
    hooks = resource.hooks.filter(lifecycle=enums.Lifecycle.AFTER_RESPONSE)
    return process_hook(hooks=hooks, threading_mode=True)
