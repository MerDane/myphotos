__author__ = 'akalend'

from flask import Flask,Response,request,abort,redirect, url_for
import json, os

import pymysql
from uploader import Uploader

app = Flask(__name__)
app.config.from_object('settings')
app.debug = app.config['DEBUG']

app.config['cnn'] = pymysql.connect(host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        passwd= app.config['DB_PASS'],
        db=app.config['DB_NAME'],
	charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)


@app.route('/api/index')
def get_user_list():

    response = Response()
    response.headers['Content-Type'] ='text/json'

    uploader = Uploader( app.config )
    data = uploader.get_list()

    response.data = json.dumps(data)

    return response

@app.route('/api/photoname', methods=['POST'])
def update_name():

    response = Response()
    response.headers['Content-Type'] ='text/json'

    id = request.form.get('id', None)
    name = request.form.get('name', None)

    if (id is None or name is None or name == '' ):
        response.data = '{"status":"DataError"}'
        return response

    uploader = Uploader( app.config )
    uploader.update_name(id, name)

    return '{"status":"OK"}'

@app.route('/api/delphoto',  methods=['POST'])
def upload_delete():

    sha1 = request.form["sha1"]

    uploader = Uploader(app.config)
    uploader.delte_from_db(sha1)
    uploader.setFile(sha1)
    uploader.delete()

    return 'Ok'


@app.route('/api/upload',  methods=['POST'])
def upload_data():

    file = request.files.get('myfile', None);

    uploader = Uploader( app.config )

    response = Response()
    response.headers['Content-Type'] ='text/json'

    res = uploader.check_mime(file)

    if not res:
        response.data = '{"status":"BadType"}'
        return response

    res = uploader.check_extension(file.filename);

    if not uploader.sha1(file):
        response.data = '{"status":"Exist"}'
        return response

    uploader.moveFile(file)

   # if not uploader.check_file_type():
   #     uploader.delete()
   #     response.data ='{"status":"BadType"}'
   #     return response

    if not uploader.get_exif():
        uploader.delete()
        response.data = '{"status":"BadExif"}'
        return response

    if not uploader.check_date(app.config['EXPIRE_DAYS']):
        uploader.delete()
        response.data = '{"status":"VeryOld"}'
        return response

    uploader.get_size()

    uploader.savedb()

    response.data = '{"status":"OK", "id": "'+ uploader.id +'" }'
    return response


if __name__ == '__main__':
        app.run(port=app.config['APP_PORT'])
