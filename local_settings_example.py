
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

#this should be unique
SECRET_KEY = 'tHiSiSnOtUnIqUew0)_d6az7=^vhffs9sn0zq!g(aopz(x&mzl'

#database info should probably go here too...

GMAIL_USERNAME = "mangrove.nmis"
GMAIL_PASSWORD = ""  # "platformnameYEARprojectacronym"

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

# where massive pictures are stored
PICTURES_FOLDER = '%s/pictures/' % CURRENT_DIR

# URL you client access your pictures
PICTURES_URL = 'http://nmis.openmangrove.org/medias/pictures/'

# sized of pictures for convertion script
PICTURES_FORMATS = ['140x140']
