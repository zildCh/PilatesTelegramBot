from regular_dao import RegularPostDAO

class RegularPostRepository:
    def __init__(self):
        self.dao = RegularPostDAO()

    def get_post_for_hours(self, hours):
        return self.dao.get_post_for_hours(hours)

    def create_table(self):
        self.dao.create_table()

    def insert_post(self, hours, message, photo_id=None):
        self.dao.insert_post(hours, message, photo_id)

    def delete_post(self, post_id):
        self.dao.delete_post(post_id)

    def delete_all_posts(self):
        self.dao.delete_all_posts()

    def get_all_posts(self):
        return self.dao.get_all_posts()