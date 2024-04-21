from dao.dao import d
d.create_table("admin", "story_name TEXT, uuid TEXT, message_type TEXT, message TEXT")
d.insert("admin", "story_name, uuid, message_type, message", ("бла23бда", "13232323", "HumanMessage", "ytn"))
# d.delete("admin", "story_name != 'gfg'")
print(d.select("*", "admin"))
