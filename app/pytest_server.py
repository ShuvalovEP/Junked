from server import upload_folde, get_hash, get_short_link, get_urls_file, short_link_validator
from db import db_session, meta
import pytest
import os
import re

# py.test -v pytest_server.py

def test_get_hash():
    hash_ = get_hash(path.join(os.getcwd(), 'upload', 'test_hash', 'UFOrEeYgRJQ.jpg'))
    assert hash_ == 'a263d41244a0b2aa909588f0f5f21f71'


def test_get_short_link():
    short_link = get_short_link()
    assert re.fullmatch(r'[ABCEHKMOPT]+', short_link)


def test_upload_folde():
    upload_path = upload_folde('test')
    assert os.path.isdir(upload_path)



def test_get_urls_file():
    file_ = 'KCCMCHAM'
    query_meta = meta.query.filter(meta.file_short_link == file_)
    query_list = str(query_meta[0]).split()
    assert query_list[3] == file_


def test_short_link_validator():
    assert short_link_validator('ABCEHKMOPT')
