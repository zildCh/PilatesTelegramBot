from user_dao import UserDAO

class UserRepository:
    def __init__(self):
        self.dao = UserDAO()

    def add_user(self, user):
        if not self.dao.user_exists(user.user_id):
            self.dao.add_user(user)
            return True
        return False

    def user_exists(self, user_id):
        return self.dao.user_exists(user_id)

    def get_all_users(self):
        return self.dao.get_all_users()

    def get_recent_users(self):
        return self.dao.get_users_by_less_join_date(7)

    def get_users_2_weeks_ago(self):
        return self.dao.get_users_by_less_join_date(21)

    def get_users_3_weeks_ago(self):
        return self.dao.get_users_by_less_join_date(28)

    def get_users_4_weeks_ago(self):
        return self.dao.get_users_by_more_join_date(28)

    def delete_user(self, user_id):
        self.dao.delete_user(user_id)

    def get_all_users2(self):
        return self.dao.get_all_users2()
