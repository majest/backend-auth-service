from flask.ext.restful import fields

import logging
import os
import threading
import datetime
import peewee
import time
from passlib.apps import custom_app_context as pwd_context
from src import settings
from flask_restful_swagger import swagger


class Database(object):
    def __init__(self):
        self.database_config = dict(settings.DATABASE_CONFIG)
        self.database_name = self.database_config.pop('name')
        self.database = peewee.PostgresqlDatabase(self.database_name, **self.database_config)
        self.app = None
        self.pid = os.getpid()

    def init_app(self, app):
        self.app = app
        self.register_handlers()

    def connect_db(self):
        self._check_pid()
        self.database.connect()

    def close_db(self, exc):
        self._check_pid()
        if not self.database.is_closed():
            self.database.close()

    def _check_pid(self):
        current_pid = os.getpid()
        if self.pid != current_pid:
            logging.info("New pid detected (%d!=%d); resetting database lock.", self.pid, current_pid)
            self.pid = os.getpid()
            self.database._conn_lock = threading.Lock()

    def register_handlers(self):
        self.app.before_request(self.connect_db)
        self.app.teardown_request(self.close_db)


db = Database()


class BaseModel(peewee.Model):
    class Meta:
        database = db.database

    @classmethod
    def get_by_id(cls, model_id):
        return cls.get(cls.id == model_id)

    @classmethod
    def all(cls):
        return cls.select().order_by(cls.id.desc())



class User(BaseModel):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField(max_length=320)
    email = peewee.CharField(max_length=320, index=True, unique=True)
    password = peewee.CharField(max_length=128)
    hash = peewee.CharField(max_length=128)
    level = peewee.IntegerField(default=0)
    xp = peewee.IntegerField(default=0)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    required = {
        'name': {'type': 'string'},
        'email': {'type': 'string', 'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'},
        'password': {'type': 'string'},
        'hash': {'type': 'string'},
        'level': {'type': 'integer'},
        'xp': {'type': 'integer'}
    }

    # id = 1
    # name = 'Eve Smith'
    # email = 'eve@everadventure.com'
    # password = 'abc123'

    class Meta:
        db_table = 'users'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'hash': self.hash,
            'level': self.level,
            'xp': self.xp
        }

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._allowed_tables = None

    @classmethod
    def get_by_email(cls, email):
        return cls.get(cls.email == email)


    def __unicode__(self):
        return '%r, %r' % (self.name, self.email)

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)


    def verify_password(self, password):
        return self.password and pwd_context.verify(password, self.password)



class Client(BaseModel):
    id = peewee.PrimaryKeyField()
    client_id = peewee.CharField(max_length=100)
    client_secret = peewee.CharField(max_length=100)  # 'mysupersecret'
    type = peewee.CharField(max_length=100)  # 'mysupersecret'
    uris = peewee.TextField()  # 'http://127.0.0.1:5000'
    scopes = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    @property
    def client_type(self):
        return self.type

    @property
    def redirect_uris(self):
        if self.uris:
            return self.uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.uris[0]

    @property
    def default_scopes(self):
        if self.scopes:
            return self.scopes.split()
        return []

    @classmethod
    def get_by_client_id(cls, client_id):
        return cls.get(cls.client_id == client_id)

    class Meta:
        db_table = 'clients'

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_secret': self.client_secret,  # should we include that?
            'redirect_uris': self.redirect_uris,
            'default_scopes': self.default_scopes,
            'client_type': self.client_type,
            'scopes': self.scopes
        }


class Token():
    client = None
    user = None
    token_type = 'Bearer'
    access_token = None
    refresh_token = None
    expires = datetime.datetime(2020, 1, 1)
    _scopes = None

    def __init__(self, **dictionary):
        for k, v in dictionary.items():
            # convert the timestamp format back to datetime required by the interface
            if k == "expires":
                v = datetime.datetime.fromtimestamp(v)
            setattr(self, k, v)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    def to_dict(self):
        return {
            'client': self.client,
            'user': self.user,
            'token_type': self.token_type,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires': time.mktime(self.expires.timetuple()),
            'scopes': self._scopes
        }


all_models = (Client)


def create_db(create_tables, drop_tables):
    db.connect_db()

    for model in all_models:
        if drop_tables and model.table_exists():
            # TODO: submit PR to peewee to allow passing cascade option to drop_table.
            db.database.execute_sql('DROP TABLE %s CASCADE' % model._meta.db_table)

        if create_tables and not model.table_exists():
            model.create_table()

    db.close_db(None)


def init_db():
    db.connect_db()
    db.close_db(None)

