import os
import sys
import urllib.parse

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import app

class VercelPathFix:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get('QUERY_STRING', '')
        if '__route__' in qs:
            params = urllib.parse.parse_qs(qs)
            if '__route__' in params and params['__route__']:
                route = params['__route__'][0]
                cleaned = {k: v for k, v in params.items() if k != '__route__'}
                environ['QUERY_STRING'] = urllib.parse.urlencode(cleaned, doseq=True)
                environ['PATH_INFO'] = route if route.startswith('/') else ('/' + route)
        else:
            path = environ.get('PATH_INFO', '')
            for prefix in ['/api/index.py', '/api/index', '/api']:
                if path.startswith(prefix):
                    new_path = path[len(prefix):]
                    environ['PATH_INFO'] = new_path if new_path.startswith('/') else ('/' + new_path)
                    break

        if not environ.get('PATH_INFO') or environ.get('PATH_INFO') in ['/api/index', '/api/index.py', '/api']:
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)
