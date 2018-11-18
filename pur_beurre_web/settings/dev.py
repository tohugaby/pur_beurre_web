import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

import pur_beurre_web
from . import *


def before_send(event, hint):
    """
    fake method to experiment sentry custom before_send function.
    """
    print(hint) if hint else None
    return event


def before_breadcrumb(crumb, hint):
    """
    fake method to experiment sentry custom before_breadcrumb function.
    """
    print(hint) if hint else None
    return crumb


sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    before_send=before_send,
    before_breadcrumb=before_breadcrumb,
    send_default_pii=True,
    release=pur_beurre_web.__version__
)
