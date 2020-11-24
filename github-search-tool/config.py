class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "breqwatr-secret-precious"


class TestingConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
