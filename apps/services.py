from rest_framework.request import Request

from apps.models import Application, RequestLog, ResourceStub, ResponseStub


def request_log_create(application: Application,
                       resource_stub: ResourceStub,
                       response_stub: ResponseStub,
                       request: Request) -> RequestLog:

    log_record = RequestLog.objects.create(
        application=application,
        resource=resource_stub,
        response=response_stub,
        params=request.query_params,
        request_body=request.body,
        request_headers=dict(request.headers),
        response_body=response_stub.body,
        response_headers=response_stub.headers,
        ipaddress=request.META.get('REMOTE_ADDR'),
        x_real_ip=request.headers.get('X-REAL-IP')
    )
    return log_record
