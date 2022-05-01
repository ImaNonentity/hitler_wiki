import traceback
from logger import logging
from functools import wraps
from typing import TypeVar

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError, StatementError, InterfaceError, InvalidRequestError, IntegrityError
from sqlalchemy.orm.exc import DetachedInstanceError, NoResultFound
from sqlalchemy.orm import Session, sessionmaker
try:
    from config_local import DATABASE
except:
    from config import DATABASE
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.sql.sqltypes import String, DateTime, NullType


Base = declarative_base()
DATABASE_URL = f"postgresql:///{DATABASE}"


engine = create_engine(DATABASE_URL, encoding="utf8", echo=False)

Base.metadata.create_all(engine)
session_maker = sessionmaker(bind=engine, autoflush=False)
session: Session = session_maker()

import os
basedir = os.path.abspath(os.path.dirname(__file__))


def reconnect():
    global engine, session, session_maker
    session.rollback()
    session.close()
    session = session_maker()
    session.expunge_all()
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(e, exc_info=True)
    return session


class StringLiteral(String):
    """Teach SA how to literalize various things."""
    def literal_processor(self, dialect):
        super_processor = super(StringLiteral, self).literal_processor(dialect)

        def process(value):
            if isinstance(value, int):
                return str(value)
            if not isinstance(value, str):
                value = str(value)
            result = super_processor(value)
            if isinstance(result, bytes):
                result = result.decode(dialect.encoding)
            return result
        return process


class LiteralDialect(DefaultDialect):
    colspecs = {
        # prevent various encoding explosions
        String: StringLiteral,
        # teach SA about how to literalize a datetime
        DateTime: StringLiteral,
        # don't format py2 long integers to NULL
        NullType: StringLiteral,
    }


def literalquery(statement):
    """NOTE: This is entirely insecure. DO NOT execute the resulting strings."""
    import sqlalchemy.orm
    if isinstance(statement, sqlalchemy.orm.Query):
        statement = statement.statement
    return statement.compile(
        dialect=LiteralDialect(),
        compile_kwargs={'literal_binds': True},
    ).string


FuncT = TypeVar("FuncT")


def catch_exception(error_value=None):

    def decorator(function: FuncT) -> FuncT:
        @wraps(function)
        def wrapper(*args, **kwargs):
            global session
            for i in range(5):
                try:
                    session.commit()
                    result = function(*args, **kwargs)
                except OperationalError as e:
                    logging.critical("".join(traceback.extract_stack().format()[:-1]))
                    logging.critical(e)
                    session.rollback()
                    session = reconnect()
                except StatementError as e:
                    logging.critical("".join(traceback.extract_stack().format()[:-1]))
                    logging.critical(e)
                    session.rollback()
                    session = reconnect()
                except InterfaceError as e:
                    logging.critical("".join(traceback.extract_stack().format()[:-1]))
                    logging.critical(e)
                    session.rollback()
                    session = reconnect()
                except DetachedInstanceError as e:
                    logging.critical("".join(traceback.extract_stack().format()[:-1]))
                    logging.critical(e)
                    session.rollback()
                    session.expunge_all()
                except NoResultFound:
                    result = error_value
                    break
                except InvalidRequestError as e:
                    logging.critical("".join(traceback.extract_stack().format()[:-1]))
                    logging.critical(e)
                    session.rollback()
                except IntegrityError as e:
                    session.rollback()
                    return error_value
                except Exception as e:
                    result = error_value
                    if not isinstance(e, NoResultFound):
                        logging.info(type(e))
                        logging.critical(e, stack_info=traceback.extract_stack())
                    break
                else:
                    break
            else:
                session.rollback()
                result = error_value
            return result
        return wrapper
    return decorator
