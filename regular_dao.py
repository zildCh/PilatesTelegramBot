import sqlite3

class RegularPostDAO:
    def __init__(self, db_file="database1337.db"):
    #def __init__(self, db_file="/app/data/database.db"):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                   CREATE TABLE IF NOT EXISTS series_posts (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       hours INTEGER NOT NULL,
                       message TEXT NOT NULL,
                       photo_id TEXT,
                       video_id TEXT,  -- Поле для видео
                       workout_choice TEXT  -- Новое поле для типа тренировки
                   )
               ''')

    def get_post_for_hours(self, hours, workout_choice=None):
        with self.conn:
            cursor = self.conn.cursor()

            if workout_choice:
                cursor.execute("SELECT * FROM series_posts WHERE hours = ? AND workout_choice = ?",
                               (hours, workout_choice))
            else:
                cursor.execute("SELECT * FROM series_posts WHERE hours = ?", (hours,))

            rows = cursor.fetchall()

            if rows:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            else:
                return []

    def insert_post(self, hours, message, photo_id=None, video_id=None, workout_choice=None):
        with self.conn:
            self.conn.execute('''
                INSERT INTO series_posts (hours, message, photo_id, video_id, workout_choice)
                VALUES (?, ?, ?, ?, ?)
            ''', (hours, message, photo_id, video_id, workout_choice))

    def delete_post(self, post_id):
        with self.conn:
            self.conn.execute("DELETE FROM series_posts WHERE id = ?", (post_id,))

    def get_all_posts(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, message, workout_choice FROM series_posts")
            return cursor.fetchall()

    def delete_all_posts(self):
        with self.conn:
            self.conn.execute("DELETE FROM series_posts")
