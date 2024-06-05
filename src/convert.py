import json
from main import GetTables

tables = GetTables()
tables = [table for table in tables.values()]
json.dump(tables, open("rds-out.json", 'w' ), default=lambda o: o.__dict__, indent=4)

