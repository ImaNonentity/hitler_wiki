from logger import logging

import app
from connection import session


class User(app.db.Model):
    __tablename__ = 'users'

    id = app.db.Column(app.db.Integer, primary_key=True)
    ip_address = app.db.Column(app.db.String())

    @classmethod
    def remember_user(cls, ip_address: str) -> "User":
        try:
            user = session.query(User).filter(User.ip_address == ip_address).one_or_none()
            if not user:
                user = User(ip_address=ip_address)
                session.add(user)
                session.commit()
            return user
        except Exception as e:
            logging.critical(e, exc_info=True)

    @property
    def get_info(self) -> str:
        # TODO: use ipinfo to get info of user
        return ""

    def __init__(self, ip_address):
        self.ip_address = ip_address

    def __repr__(self):
        return '<id {}>'.format(self.ip_address)
