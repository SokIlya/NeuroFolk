import sqlite3


class Dao:
    def __init__(self, path="database/database.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self, name, columns):
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {name} ({columns});''')
        self.conn.commit()

    def insert(self, table, columns, values):
        self.cursor.execute(f'''INSERT INTO {table} ({columns}) VALUES ({", ".join(["?" for _ in range(len(values))])})''', values)
        self.conn.commit()

    def select(self, select, table, where=None):
        if where is None:
            res = self.cursor.execute(f'''SELECT {select} FROM {table}''').fetchall()
        else:
            res = self.cursor.execute(f'''SELECT {select} FROM {table} WHERE {where}''').fetchall()
        self.conn.commit()
        return res

    def delete(self, table, where):
        self.cursor.execute(f"DELETE FROM {table} WHERE {where}")
        self.conn.commit()

    def __del__(self):
        self.conn.close()


d = Dao("database/database.db")
d.create_table("users", "username TEXT, password TEXT")
