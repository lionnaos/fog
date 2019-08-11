import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

engine = create_engine('sqlite:///db.sqlite3', echo=True)
Base = declarative_base()

class Observation(Base):
    __tablename__ = 'observations'

    id = Column(Integer, primary_key=True)
    wind = Column(String)
    rvr = Column(String)
    vis = Column(String)
    created = Column(DateTime)

    def wind_range(self):
        return self.wind

    def __repr__(self):
       return "<Data {}>".format(self.wind)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()