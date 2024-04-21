from dao.dao import Dao

d = Dao("database/database.db")
print(d.select("*", "users"))