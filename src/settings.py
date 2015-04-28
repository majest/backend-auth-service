import json
import os
import urlparse


def parse_db_url(url):
    url_parts = urlparse.urlparse(url)
    connection = {'threadlocals': True}

    if url_parts.hostname and not url_parts.path:
        connection['name'] = url_parts.hostname
    else:
        connection['name'] = url_parts.path[1:]
        connection['host'] = url_parts.hostname
        connection['port'] = url_parts.port
        connection['user'] = url_parts.username
        connection['password'] = url_parts.password

    return connection


def fix_assets_path(path):
    fullpath = os.path.join(os.path.dirname(__file__), path)
    return fullpath


def array_from_string(str):
    array = str.split(',')
    if "" in array:
        array.remove("")

    return array


def parse_boolean(str):
    return json.loads(str.lower())


APP_ENV = os.environ.get('APP_ENV', 'DEV')
NAME = os.environ.get('APP_NAME', 'experiment-service')
DEBUG = os.environ.get('APP_DEBUG', True)

REDIS_URL = os.environ.get('APP_REDIS_URL', "redis://localhost:6379/0")

STATSD_HOST = os.environ.get('APP_STATSD_HOST', "127.0.0.1")
STATSD_PORT = int(os.environ.get('APP_STATSD_PORT', "8125"))
STATSD_PREFIX = os.environ.get('APP_STATSD_PREFIX', "app")

# Connection settings for the app's own database (where we store the queries, results, etc)
DATABASE_CONFIG = parse_db_url(os.environ.get("APP_DATABASE_URL", "postgresql://postgres"))

STATIC_ASSETS_PATH = fix_assets_path(os.environ.get("APP_STATIC_ASSETS_PATH", "../rd_ui/app/"))
LOG_LEVEL = os.environ.get("APP_LOG_LEVEL", "INFO")

STATSD_HOST = os.environ.get("STATSD_HOST", "localhost")
SECURITY_SIGN_KEY = os.environ.get("SECURITY_SIGN_KEY", "pE3y/V3eivQQ+AqO628+fD3KtqTd9Z4b")
OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = int(os.environ.get("OAUTH2_PROVIDER_TOKEN_EXPIRES_IN", 3600))