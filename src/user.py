from classes import RollEntry, RollTable
from sys import stdin

def userRoll(rollTables: dict[str, RollTable]) -> str:
	"""
	Allows the user to roll on a table of their choice.
	"""
	while True:
		selectedTable = input("\nEnter the name of the table you want to roll on: ").casefold()

		if selectedTable not in rollTables:
			for table in rollTables:
				if table.startswith(selectedTable):
					selectedTable = table
					break

		if selectedTable not in rollTables:
			print(f"Table '{selectedTable}' not found.")
			continue


		print(DoRoll(rollTables, selectedTable))

def DoRoll(rollTables: dict[str, RollTable], selectedTable: str, _depth = 0) -> str:
	"""
	Rolls on the given table and returns the result.
	"""
	if _depth > 5:
		return "Infinite loop detected. Stopping."

	indent = "> " * _depth

	retval = f"\n{indent}Rolling on table '{selectedTable.title()}'...\n\n"

	entry = rollTables[selectedTable].roll()

	retval += f"{indent}Rolled: {entry.Title}\n\n"

	if len(entry.Description) > 0:
		retval += f"{indent}Description: {entry.Description}\n\n"

	for linkedTable in entry.LinkedRollTables:
		retval += DoRoll(rollTables, linkedTable, _depth + 1)

	return retval
