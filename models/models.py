
from contextlib import contextmanager

from sqlalchemy import Column, TEXT, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

from deploy.config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)


@contextmanager
def session():
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    try:
        yield db_session
    except Exception as e:
        print(e)
    finally:
        db_session.remove()
        connection.close()


class Phrase(Base):
    __tablename__ = 'phrase'
    id = Column(Integer, primary_key=True, autoincrement=True)
    phrase = Column("text", TEXT)
    users_id = Column(Integer, ForeignKey('users_tg.id'), nullable=True)


class Users(Base):
    __tablename__ = 'users_tg'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer)
    first_name = Column(String(50))
    last_name = Column(String(50))
    custom_name = Column(String(120))
    phrase = relationship("Phrase", backref="users", lazy='dynamic', cascade="all, delete, delete-orphan")


Base.metadata.create_all(engine)



