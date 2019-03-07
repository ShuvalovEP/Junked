from flask import Flask, render_template, request, redirect, send_from_directory
from db import db_session, meta
from datetime import datetime
from os import path
import hashlib
import uuid
import os
import re


app = Flask(__name__)


def get_date(mask_date):
    """ Returns the current date to the input accepts a date mask """
    return datetime.now().strftime(mask_date)


def get_hash(file_):
    """ Returns the hash of a file """
    with open(file_, 'rb') as f:
        m_hash = hashlib.md5()
        while True:
            data = f.read(8192)  # Reads the file in blocks of 8192 bytes
            if not data:
                break
            m_hash.update(data)
        return m_hash.hexdigest()


def get_short_link():
    """ Returns a short link to the file """
    short_link = ''
    alpha = {'1': 'A',
             '2': 'B',
             '3': 'C',
             '4': 'E',
             '5': 'H',
             '6': 'K',
             '7': 'M',
             '8': 'O',
             '9': 'P',
             '0': 'T'}
    for row in str(hash(str(uuid.uuid1())) % 100000000):
        short_link = (alpha.get(row)) + short_link
    return short_link


def upload_folde(file_id):
    """ Creates a directory structure returns the full path to the file """
    folder = path.join(os.getcwd(), 'upload', get_date('%Y/%m/%d'), file_id)
    if path.isdir(folder) == False:
        os.makedirs(folder, mode=0o777, exist_ok=False)
    return folder


def upload(files_request):
    """ The main function of processing the input file """
    file_name = files_request.filename
    file_id = int(meta.query.count()) + 1  # Takes the last ID and adds 1

    file_ = path.join(upload_folde(str(file_id)), file_name)
    files_request.save(file_)

    short_link = get_short_link()

    db_session.add(meta(None,
                        path.splitext(file_name)[0],
                        path.splitext(file_name)[1],
                        short_link,
                        get_date('%Y-%m-%d %H:%M:%S'),
                        path.getsize(file_),
                        get_hash(file_),
                        upload_folde(str(file_id))))
    db_session.commit()
    db_session.close()
    return short_link


def get_file(short_link):
    query_meta = meta.query.filter(meta.file_short_link == short_link)
    query_list = str(query_meta[0]).split()
    return query_list[8], query_list[1] + query_list[2]


def get_urls_file(short_link):
    url = [url.file_short_link for url in meta.query.filter(meta.file_short_link == f'{short_link}')]
    if url != []:
        return url[0]
    else:
        return False


def short_link_validator(short_link):
    """ Checks short link for the correctness of the incoming """
    if re.fullmatch(r'[ABCEHKMOPT]+', short_link):
        return get_urls_file(short_link)
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files_request = request.files['file']
        upload(files_request)
        return render_template("index.html")
    elif request.method == 'GET':
        return render_template("index.html")


@app.route('/<short_link>')
def redirect_link(short_link):
    urls_path = short_link_validator(short_link)
    if urls_path:
        directory = get_file(short_link)[0]
        filename = get_file(short_link)[1]
        return send_from_directory(directory, filename)
    else:
        return render_template('index.html', code=404)


if __name__ == "__main__":
    app.run(debug=True)
