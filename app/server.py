from flask import Flask, render_template, request, redirect, send_from_directory, session
from werkzeug.contrib.fixers import ProxyFix
from db import db_session, meta
from datetime import datetime
from os import path
import hashlib
import uuid
import os
import re


secret_key = path.join(os.getcwd(), 'environment', 'secret_key.env')
with open(secret_key, 'r', encoding='UTF-8') as f:
    os.environ['SECRET_KEY'] = f.read()


app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = f'{os.environ.get("SECRET_KEY")}'


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
    """ Checks short link for a valid """
    if re.fullmatch(r'[ABCEHKMOPT]+', short_link):
        return get_urls_file(short_link)
    else:
        return False


def get_token():
    """Sets a token to prevent double posts."""
    return str(uuid.uuid1())


def generate_form_token():
    """ Sets a token to prevent double posts """
    if '_form_token' not in session:
        form_token = get_token()
        session['_form_token'] = form_token
    return session['_form_token']


@app.before_request
def check_form_token():
    """ Checks for a valid form token in POST requests """
    if request.method == 'POST':
        token = session.pop('_form_token', None)
        if not token or token != request.form.get('_form_token'):
            return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    link = ''
    if request.method == 'POST':
        files_request = request.files['file']
        link = upload(files_request)
        return render_template('link.html', link=link)
    elif request.method == 'GET':
        form_token = get_token()
        app.jinja_env.globals['form_token'] = generate_form_token
        return render_template('index.html')


@app.route('/<short_link>')
def redirect_link(short_link):
    urls_path = short_link_validator(short_link)
    if urls_path:
        directory = get_file(short_link)[0]
        filename = get_file(short_link)[1]
        return send_from_directory(directory, filename)
    else:
        return render_template('index.html', code=404)


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
