__author__ = 'akalend'

import  os
from datetime import datetime

class UploaderValueError(BaseException):
    pass


class Uploader():

    _settings = None
    _filename = None
    _fullname = None
    _cnn = None
    _data = None
    _tags = None
    _maker = None
    _model = None
    _datetime = None
    _size = None

    def __init__(self, settings):
        self._settings = settings
        self._cnn = settings['cnn']


    @property
    def id(self):
        return self._filename


    def check_mime(self, file):
        if file is None: return False

        if len(file.mimetype) >= 4 and file.mimetype[0:4] == 'imag':
            return True

        return False


    def check_extension(self, filename):

        ext_list = self._settings['ALLOWED_EXTENSIONS']
        r1 = '.' in filename
        filename_sm = filename.lower()
        r2 = filename_sm.rsplit('.', 1)[1] in ext_list
        return r1 and r2

    def sha1(self, file):
        data = file.read(1024)
        file.seek(0)

        from hashlib import sha1

        digest = sha1(data)
        self._filename = digest.hexdigest()

        cur = self._cnn.cursor()
        sql = "SELECT sha1 FROM photos WHERE sha1=%s"

        cur.execute(sql, (self._filename))
        res = cur.fetchall()

        ret = True
        if len(res):
            self._data = res.pop()
            ret = False

        cur.close()
        return ret


    # package magis is crash
    def check_file_type(self):
        import magic

        res = magic.from_file(self._fullname)
        return 'image' in res.decode('ascii')

    def setFile(self, filename):
        self._filename = filename
        self._fullname = os.path.join(self._settings['UPLOAD_FOLDER'], self._filename)

    def moveFile(self, file):
        if file is None:
            return

        self._fullname = os.path.join(self._settings['UPLOAD_FOLDER'], self._filename)
        file.save(self._fullname)

    def delete(self):
        try:
            os.remove(self._fullname)
        except TypeError: return
        finally: return

    def get_exif(self):
        import exifread
        f = open(self._fullname, 'rb')
        if f is None:
            return False

        self._tags = exifread.process_file(f)

        date_time = self._tags.get( 'EXIF DateTimeOriginal', None)

        if ( date_time is None):
            date_time = self._tags.get( 'DateTime', None)
            if date_time is None:
                date_time = self._tags.get( 'Image DateTime', None)

        if date_time is not None:
            self._datetime = str(date_time)

        self._model = self._tags.get( 'Image Model', None)
        self._maker = self._tags.get( 'Image Make', None)

        f.close()
        return True

    def check_date(self, days):
        if self._datetime is None: return False

        photo_date = datetime.strptime(self._datetime, "%Y:%m:%d %H:%M:%S")
        res = (datetime.today() - photo_date).days < days

        return res

    def get_size(self):
        stat = os.stat(self._fullname)
        self._size = stat.st_size


    def savedb(self):
        """
        +-------------+-------------+------+-----+-------------------+-------+
        | Field       | Type        | Null | Key | Default           | Extra |
        +-------------+-------------+------+-----+-------------------+-------+
        | sha1        | varchar(40) | NO   | PRI | NULL              |       |
        | name        | varchar(45) | YES  |     | NULL              |       |
        | cam         | varchar(45) | YES  |     | NULL              |       |
        | maker       | varchar(45) | YES  |     | NULL              |       |
        | size        | int(11)     | YES  |     | NULL              |       |
        | data_create | date        | YES  |     | NULL              |       |
        | ts          | timestamp   | NO   |     | CURRENT_TIMESTAMP |       |
        +-------------+-------------+------+-----+-------------------+-------+
        """

        sql = "INSERT INTO photos (sha1,cam,maker,size,data_create) VALUES(%s,%s,%s,%s,%s)"
        cur = self._cnn.cursor()

        photo_date = datetime.strptime(self._datetime, "%Y:%m:%d %H:%M:%S")
        date_create = photo_date.strftime('%Y-%m-%d %H:%M')


        cur.execute(sql, (self.id, self._model.values, self._maker.values, self._size, date_create ))
        self._cnn.commit()


    def update_name(self, id, name):

        sql = "UPDATE photos SET name=%s WHERE sha1=%s"
        cur = self._cnn.cursor()

        cur.execute(sql, (name, id))
        self._cnn.commit()

    def delte_from_db(self, sha1):
        cur = self._cnn.cursor()
        sql = "DELETE FROM photos WHERE sha1=%s"
        cur.execute(sql,sha1)
        self._cnn.commit()

    def get_list(self):

        cur = self._cnn.cursor()
        sql = "SELECT * FROM photos"
        cur.execute(sql)

        row = cur.fetchone()
        res = []
        while row is not None:
            row['ts'] = row['ts'].strftime("%d.%m.%Y")
            row['data_create'] = row['data_create'].strftime("%d.%m.%Y")
            # if row['name'] is None: row['name'] = ''
            res.append(row)
            row = cur.fetchone()


        return res