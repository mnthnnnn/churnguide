import os
import sys
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, "01_Project", "ChurnGuide_BTech_Project")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app import app

class VercelPathFix:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. Check for original URI headers set by Vercel proxy
        orig = (
            environ.get('HTTP_X_ORIGINAL_URI') or
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('HTTP_X_REWRITE_URL') or
            environ.get('HTTP_X_MATCHED_PATH')
        )
        if orig:
            parsed = urllib.parse.urlparse(orig)
            environ['PATH_INFO'] = parsed.path
            if parsed.query:
                environ['QUERY_STRING'] = parsed.query
        else:
            # 2. Check query string __route__ parameter
            qs = environ.get('QUERY_STRING', '')
            if '__route__' in qs:
                params = urllib.parse.parse_qs(qs)
                if '__route__' in params and params['__route__']:
                    route = params['__route__'][0]
                    cleaned = {k: v for k, v in params.items() if k != '__route__'}
                    environ['QUERY_STRING'] = urllib.parse.urlencode(cleaned, doseq=True)
                    environ['PATH_INFO'] = route if route.startswith('/') else ('/' + route)
            else:
                # 3. Strip /api/index prefixes if still attached
                path = environ.get('PATH_INFO', '')
                for prefix in ['/api/index.py', '/api/index', '/api']:
                    if path.startswith(prefix):
                        new_path = path[len(prefix):]
                        environ['PATH_INFO'] = new_path if new_path.startswith('/') else ('/' + new_path)
                        break

        if not environ.get('PATH_INFO'):
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)
