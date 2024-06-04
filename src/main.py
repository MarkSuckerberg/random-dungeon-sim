import json
from classes import RollEntry, RollTable
from src.user import userRoll

def main():
	rollTables = GetTables()
	userRoll(rollTables)

def GetTables() -> dict[str, RollTable]:
	with open('rds.json') as f:
		data: dict[str, dict[str, dict]] = json.load(f)
		data.pop("$schema", None)

	rollTables = {}
	for (name, table) in data.items():
		rollTableData = []
		for (key, value) in table.items():

			linkedTables = []
			for linkedTable in value.get("LinkedRollTables", []):
				if linkedTable not in data:
					print(f"Linked table '{linkedTable}' not found in table '{name}'")
					continue

				linkedTables.append(linkedTable.casefold())

			rollTableData.append(RollEntry(key.casefold(), value.get("Weight", 1), linkedTables, value.get("Description", "")))

		rollTables[name.casefold()] = RollTable(name, rollTableData)

	return rollTables

if __name__ == '__main__':
	main()
