#stuff specific to this install should be used in this file.
DEBUG = False
TEMPLATE_DEBUG = DEBUG

#this should be unique
SECRET_KEY = 'tHiSiSnOtUnIqUew0)_d6az7=^vhffs9sn0zq!g(aopz(x&mzl'

#database info should probably go here too...

GMAIL_USERNAME = "mangrove.nmis"
GMAIL_PASSWORD = ""

# email-sending. used for User registration
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[NMIS] '
EMAIL_USE_TLS = False

# registration
ACCOUNT_ACTIVATION_DAYS = 5

# where to redirect after login
LOGIN_REDIRECT_URL = '/'
