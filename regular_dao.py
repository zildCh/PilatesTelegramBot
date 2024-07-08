import sqlite3

class RegularPostDAO:
    def __init__(self, db_file='database.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS series_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hours INTEGER NOT NULL,
                message TEXT NOT NULL,
                photo_id TEXT
            )
        ''')

    def get_post_for_hours(self, hours):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM series_posts WHERE hours = ?", (hours,))
            row = cursor.fetchone()

            if row:
                columns = [col[0] for col in cursor.description]  # Получаем названия столбцов
                return dict(zip(columns, row))  # Преобразуем кортеж в словарь
            else:
                return None

    def insert_post(self, hours, message, photo_id=None):
        with self.conn:
            self.conn.execute("INSERT INTO series_posts (hours, message, photo_id) VALUES (?, ?, ?)",
                              (hours, message, photo_id))

    def delete_post(self, post_id):
        with self.conn:
            self.conn.execute("DELETE FROM series_posts WHERE id = ?", (post_id,))

    def get_all_posts(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, message FROM series_posts")
            return cursor.fetchall()
