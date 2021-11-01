from os import getenv
from settings import debug

def heroku():
    port = getenv('PORT')
    if not port:
        return False
    else:
        return True

debug = debug