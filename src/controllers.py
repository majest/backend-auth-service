"""
Backend Experiment Service used for A/B tests
"""
from flask.ext.restful import Resource
from flask_oauthlib.provider import OAuth2Provider, OAuth2RequestValidator
from src.wsgi import app, api, statsd
from src.oauth2 import load_client, load_token, save_token, get_user

oauth = OAuth2Provider(app)
oauth._validator = OAuth2RequestValidator(load_client, load_token, None, get_user, save_token)


@app.route('/ping', methods=['GET'])
def ping():
    return 'PONG.'

class OAuthTokenAPI(Resource):
    @oauth.token_handler
    def post(self):
        return None


api.add_resource(OAuthTokenAPI, '/oauth/token', endpoint='oauth_token')

if __name__ == '__main__':
    app.run(debug=True)



