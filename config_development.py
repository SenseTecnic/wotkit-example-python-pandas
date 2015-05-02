class Config(object):
    CONSUMER_KEY = 'your-consumer-application'
    CONSUMER_SECRET = 'your-consumer-secret'

class ProductionConfig(Config):
    DEBUG = False;

class DevelopmentConfig(Config):
    DEBUG = True
