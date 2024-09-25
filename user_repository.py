from user_dao import UserDAO
from datetime import datetime

class UserRepository:
    def __init__(self, google_sheets):
        self.dao = UserDAO()
        self.google_sheets = google_sheets
        self.last_message_statuses = {}


    def add_user(self, user):
        if not self.dao.user_exists(user.user_id):
            self.dao.add_user(user)
            user_data = user.to_dict()
            last_message_status_emoji = '✅'
            user_data['start_date'] = self.convert_timestamp_to_date(user_data['start_date'])
            self.google_sheets.append_row([user_data['user_id'], user_data['username'], user_data['start_date'], last_message_status_emoji, user_data['workout_choice']])
            return True
        return False

    def update_user_status_to_false(self, user_id):
        users_data = self.get_all_users()
        for i, user in enumerate(users_data, start=2):  # Assuming the first row is the header
            if user.user_id == user_id:
                last_message_status_emoji = '❌'
                self.google_sheets.update_cell(i, 4, last_message_status_emoji)  # Assuming status is in the 4th column
                break

    def update_workout_choice(self, user_id, workout_choice):
        self.dao.update_workout_choice(user_id, workout_choice)

    def get_workout_choice(self, user_id):
        return self.dao.get_workout_choice(user_id)


    def save_all_users_to_google_sheets(self):
        all_users = self.get_all_users()
        for user in all_users:
            user_data = user.to_dict()
            last_message_status_emoji = '✅'
            user_data['start_date'] = self.convert_timestamp_to_date(user_data['start_date'])
            self.google_sheets.append_row([user_data['user_id'], user_data['username'], user_data['start_date'], last_message_status_emoji, user_data['workout_choice']])

    def user_exists(self, user_id):
        return self.dao.user_exists(user_id)

    def get_all_users(self):
        return self.dao.get_all_users()

    def get_less_then_users(self, days):
        return self.dao.get_users_by_less_join_date(days)

    def get_more_then_users(self, days):
        return self.dao.get_users_by_more_join_date(days)

    def delete_user(self, user_id):
        self.dao.delete_user(user_id)

    def get_all_users2(self):
        return self.dao.get_all_users2()

    @staticmethod
    def convert_timestamp_to_date(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')