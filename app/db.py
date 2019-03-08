from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import path
import os


environ_ = path.join(os.getcwd(), 'environment', 'engine_db.env')
with open(environ_, 'r', encoding='UTF-8') as f:
    os.environ['db_engine'] = f.read()


engine = create_engine(f'postgresql://{os.environ.get("db_engine")}')
db_session = scoped_session(sessionmaker(bind=engine))


Base = declarative_base()
Base.query = db_session.query_property()


class meta(Base):
    __tablename__ = 'meta'
    file_id = Column(Integer, primary_key=True)
    file_name = Column(String(512))
    file_exte = Column(String(64))
    file_short_link = Column(String(120))
    file_date = Column(String(120))
    file_size = Column(String(128))
    file_hash = Column(String(512))
    file_path = Column(String(512))

    def __init__(self, file_id=None,
                 file_name=None,
                 file_exte=None,
                 file_short_link=None,
                 file_date=None,
                 file_size=None,
                 file_hash=None,
                 file_path=None):
        self.file_id = file_id
        self.file_name = file_name
        self.file_exte = file_exte
        self.file_short_link = file_short_link
        self.file_date = file_date
        self.file_size = file_size
        self.file_hash = file_hash
        self.file_path = file_path

    def __repr__(self):
        return f'''{self.file_id} 
                   {self.file_name} 
                   {self.file_exte} 
                   {self.file_short_link} 
                   {self.file_date} 
                   {self.file_size} 
                   {self.file_hash} 
                   {self.file_path}'''


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
