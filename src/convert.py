import json
from main import GetTables

tables = GetTables()
table_values = [table for table in tables.values()]
json.dump(
    table_values, open("rds-out.json", "w"), default=lambda o: o.__dict__, indent=4
)
