"""
WSGI config for glamour_store project.
"""

import os
import sys
import traceback
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')

try:
    _django_app = get_wsgi_application()

    def application(environ, start_response):
        try:
            return _django_app(environ, start_response)
        except Exception as e:
            err_msg = f"SERVER EXCEPTION: {e}\n\n{traceback.format_exc()}"
            print(err_msg, file=sys.stderr)
            status = '500 Internal Server Error'
            response_headers = [('Content-Type', 'text/plain')]
            start_response(status, response_headers)
            return [err_msg.encode('utf-8')]

    app = application
except Exception as init_err:
    init_msg = f"WSGI INIT EXCEPTION: {init_err}\n\n{traceback.format_exc()}"
    print(init_msg, file=sys.stderr)
    def application(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return [init_msg.encode('utf-8')]
    app = application
