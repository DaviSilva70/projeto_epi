from django.conf import settings


def project_settings(request):
    return {
        "ALLOW_SELF_REGISTRATION": settings.ALLOW_SELF_REGISTRATION,
    }
