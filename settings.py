__author__ = 'akalend'

APP_PORT = 8080

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = 'test'
DB_NAME = 'test'
DB_PASS = 'test'

DEBUG= True

EXPIRE_DAYS = 365

UPLOAD_FOLDER = '/home/akalend/projects/myphotos/static/uploaded'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif', 'tiff'])
MAX_CONTENT_LENGTH = 10 * 1024 * 1024