from src import models, redis_connection
import json, logging
import datetime
r = redis_connection.pipeline()


def load_client(client_id):
    try:
        client = models.Client.get_by_client_id(client_id)
    except models.Client.DoesNotExist:
        return None

    return client


def load_token(access_token=None, refresh_token=None):
    # get tokens from redis

    r.get(access_token)
    tokens = r.execute()

    # check if we have the data belonging to the token

    if len(tokens) != 1:
        logging.error("Could not find token: %s", access_token)
        return None

    # load the token

    token_data = json.loads(tokens[0])
    token = models.Token(**token_data)
    return token


def save_token(newToken, request, *args, **kwargs):
    access_token = newToken['access_token']

    # check if we have a client for this client id
    # we need scopes
    try:
        client = models.Client.get_by_client_id(request.body["client_id"])
    except models.Client.DoesNotExist:
        logging.error("No such client: %s", request.body["client_id"])
        return None

    token = models.Token()
    token.client = request.body["client_id"]
    token.user = request.body["username"]
    token.token_type = 'Bearer'
    token.access_token = access_token
    token.refresh_token = newToken['refresh_token']
    token._scopes = client.scopes

    # deal with expiry date later, default set for 2020

    # serialise the data
    token_data = json.dumps(token.to_dict())

    # save data in redis
    r.set(access_token, token_data)
    r.execute()


def get_user(username, password, *args, **kwargs):
    try:
        user = models.User.get_by_email(username)
    except models.User.DoesNotExist:
        return None

    if user.verify_password(password):
        return user
    return None