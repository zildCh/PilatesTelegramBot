import sqlite3
from user import User
from datetime import datetime, timedelta

class UserDAO:
    #def __init__(self, db_file="/app/data/database.db"):
    def __init__(self, db_file="database1337.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    start_date INTEGER NOT NULL,
                    workout_choice TEXT  
                )
            ''')

    def update_workout_choice(self, user_id, workout_choice):
        with self.conn:
            self.conn.execute('''
                UPDATE users
                SET workout_choice = ?
                WHERE user_id = ?
            ''', (workout_choice, user_id))

    def get_workout_choice(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT workout_choice FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def add_user(self, user):
        with self.conn:
            self.conn.execute('''
                INSERT INTO users (user_id, username, start_date, workout_choice)
                VALUES (?, ?, ?, ?)
            ''', (user.user_id, user.username, user.start_date, user.workout_choice))

    def user_exists(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 1 FROM users WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchone() is not None

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, username, start_date, workout_choice FROM users
        ''')
        rows = cursor.fetchall()
        return [User(user_id=row[0], username=row[1], start_date=row[2], workout_choice=row[3]) for row in rows]

    def get_users_by_less_join_date(self, days_ago):
        date_limit = datetime.now() - timedelta(days=days_ago)
        print(date_limit)
        print(date_limit.timestamp())
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE start_date >= ?", (date_limit.timestamp(),))
            return [row[0] for row in cursor.fetchall()]

    def get_users_by_more_join_date(self, days_ago):
        date_limit = datetime.now() - timedelta(days=days_ago)
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE start_date < ?", (date_limit.timestamp(),))
            return [row[0] for row in cursor.fetchall()]

    def get_all_users2(self):
        cursor = self.conn.cursor()
        cursor.execute('''
               SELECT user_id, username, start_date FROM users
           ''')
        return [row[0] for row in cursor.fetchall()]

    def delete_user(self, user_id):
        with self.conn:
            self.conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
