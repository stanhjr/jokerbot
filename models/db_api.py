from functools import wraps

from sqlalchemy.sql.expression import func
from sqlalchemy import or_

from models.models import session, Phrase, Users


def with_session(function):
    @wraps(function)
    def context_session(*args, **kwargs):
        with session() as s:
            kwargs['s'] = s
            return function(*args, **kwargs)

    return context_session


class DataApi:
    def __init__(self):
        self.session = session

    def set_phrase(self, text, user_id):

        with self.session() as s:
            phrase = Phrase()
            phrase.phrase = text
            phrase.users_id = user_id
            s.add(phrase)
            s.commit()
            return True

    def get_random_phrase(self):
        with self.session() as s:

            phrase = s.query(Phrase).order_by(func.random()).first()
            if phrase.users.custom_name:
                return f'"{phrase.phrase}" © ({phrase.users.custom_name})'

            return f'"{phrase.phrase}" © ({phrase.users.last_name} {phrase.users.first_name})'

    def set_user(self, telegram_id, first_name, last_name):
        with self.session() as s:
            user = s.query(Users).filter(or_(Users.telegram_id == telegram_id, Users.last_name == last_name)).first()
            if user:
                return user.id

            user = Users()
            user.first_name = first_name
            user.last_name = last_name
            user.telegram_id = telegram_id
            s.add(user)
            s.commit()
            return user.id

    def set_custom_phrase(self, data):
        with self.session() as s:
            user = s.query(Users).filter(Users.custom_name == data.get("name")).first()
            if user:
                phrase = Phrase()
                phrase.phrase = data.get("phrase")
                phrase.users_id = user.id
                s.add(phrase)
                s.commit()
            else:
                user = Users()
                user.custom_name = data.get("name")
                s.add(user)
                user = s.query(Users).filter(Users.custom_name == data.get("name")).first()
                phrase = Phrase()
                phrase.phrase = data.get("phrase")
                phrase.users_id = user.id
                s.add(phrase)
                s.commit()
                return True

    def get_all_user_telegram_id(self):
        with self.session() as s:
            result = s.query(Users.telegram_id).all()
            result_list = []
            for tuple in result:
                result_list.append(tuple[0])
            return result_list


data_api = DataApi()


