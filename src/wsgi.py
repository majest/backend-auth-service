from flask import Flask, make_response
from flask.ext.restful import Api
from flask_restful_swagger import swagger
from flask.ext.cors import CORS
from flask.ext.statsd import StatsD

from src import settings, utils
from src.models import db

__version__ = '0.0.1'

app = Flask(__name__,
            template_folder=settings.STATIC_ASSETS_PATH,
            static_folder=settings.STATIC_ASSETS_PATH,
            static_path='/static')

app.debug = settings.DEBUG
app.config['OAUTH2_PROVIDER_TOKEN_EXPIRES_IN'] = settings.OAUTH2_PROVIDER_TOKEN_EXPIRES_IN
app.config['STATSD_HOST'] = settings.STATSD_HOST
CORS(app, headers=['Content-Type', 'Authorization'])

statsd = StatsD(app)
api = swagger.docs(Api(app), apiVersion='0.1')


# configure our database
settings.DATABASE_CONFIG.update({'threadlocals': True})
app.config['DATABASE'] = settings.DATABASE_CONFIG
db.init_app(app)


@api.representation('application/json')
def json_representation(data, code, headers=None):
    resp = utils.json_dumps(data)
    signature = utils.sign(resp)

    response = make_response(resp, code)
    response.headers.extend(headers or {})
    response.headers.add('signature', signature)
    response.headers.set("Content-Type", "application/json")
    return response


from src import controllers