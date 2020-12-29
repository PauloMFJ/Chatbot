import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    THREADED = True
    PORT = int(os.environ.get('PORT', 5000))
    # This shouldn't be visible
    SECRET_KEY = '\xe3\xa3\xecK>\x82\xc1\xdfH=\xd0S\xb3\x9eX\x97\xfd\xeb\xefO\xdf\xda\x10\x96'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True