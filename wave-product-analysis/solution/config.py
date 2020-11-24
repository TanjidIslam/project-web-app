class Config(object):
    '''
    Config Environment for the application
    This will keep some data safe
    '''
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'waverandomkeyasdklasdjsa'


class WaveAppsConfig(Config):
    URL = 'https://api.waveapps.com/'
    BUSINESS_ID = '89746d57-c25f-4cec-9c63-34d7780b044b'
    ACCESS_TOKEN = '6W9hcvwRvyyZgPu9Odq7ko8DSY8Nfm'
