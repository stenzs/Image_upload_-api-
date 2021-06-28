from flask import Flask, request, jsonify
import os
import sqlite3
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'image'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
os.makedirs('image',exist_ok=True)

class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
    def patch_exist(self, patch):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `images` WHERE `route` = ?', (patch,)).fetchall()
            return bool(len(result))
    def add_patch(self, patch):
        with self.connection:
            return self.cursor.execute('INSERT INTO `images` (`route`) VALUES(?)', (patch,))
    def close(self):
        self.connection.close()
base = SQLighter('base.db')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        print('asfasf')
        return resp
    files = request.files.getlist('files[]')
    errors = {}
    success = False
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path, dirs, files = next(os.walk("./image"))
            file_count = str(len(files) + 1)
            new_name = 'image(' + file_count + ').' + filename.rsplit('.', 1)[1].lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            patch = os.path.dirname(os.path.abspath(__file__)) + '\\image' + '\\' + new_name
            if (not base.patch_exist(patch)):
                base.add_patch(patch)

            success = True
        else:
            errors[file.filename] = 'File type is not allowed'
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)