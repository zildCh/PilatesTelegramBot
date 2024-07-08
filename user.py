import json
from datetime import datetime
class User:
    def __init__(self, user_id, username, start_date=None):
        self.user_id = user_id
        self.username = username
        self.start_date = start_date or int(datetime.now().timestamp())

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'start_date': self.start_date
        }

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data['user_id'],
            username=data['username'],
            start_date=data['start_date']
        )