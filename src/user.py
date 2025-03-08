from classes import RollTable


def userRoll(rollTables: dict[str, RollTable]):
    """
    Allows the user to roll on a table of their choice.
    """
    while True:
        try:
            selectedTable = input(
                "\nEnter the name of the table you want to roll on: "
            ).casefold()
        except KeyboardInterrupt:
            break

        if selectedTable == "" or selectedTable == "exit" or selectedTable == "quit":
            break

        if selectedTable not in rollTables:
            for table in rollTables:
                if table.startswith(selectedTable):
                    selectedTable = table
                    break

        if selectedTable not in rollTables:
            print(f"Table '{selectedTable}' not found.")
            continue

        values, _ = GetRollList(rollTables, selectedTable)

        for key, value in values.items():
            print(f"\033[1;4m{key}\033[0m\n{value}")


def GetRollList(
    rollTables: dict[str, RollTable], selectedTable: str, _depth=0
) -> tuple[dict[str, str], list[int]]:
    """
    Rolls on the given table and returns the result.
    """
    if _depth > 5:
        raise RecursionError()

    retval = f"\nRolling on table '{selectedTable.title()}'...\n"

    result = rollTables[selectedTable].roll()
    entry = result[0]

    retval += f"Rolled {result[1]}: {entry.Title}\n"

    if len(entry.Description) > 0:
        retval += f"Description: {entry.Description}\n"

    retList = {entry.Title: retval}

    rollNumbers = [result[1]]

    for linkedTable in entry.LinkedRollTables:
        rollValue = GetRollList(rollTables, linkedTable, _depth + 1)

        retList.update(rollValue[0])
        rollNumbers.extend(rollValue[1])

    return (retList, rollNumbers)
