"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import logging
from django.core.wsgi import get_wsgi_application
from dj_static import Cling

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

web_server_name = print(os.environ.get("SERVER_SOFTWARE", ""))
logger.debug('Web Server : %s' % web_server_name)

"""
if (not web_server_name is None) and ("gunicorn" in web_server_name) :
    application = Cling(get_wsgi_application())
else:
    application = get_wsgi_application()
"""

application = Cling(get_wsgi_application())