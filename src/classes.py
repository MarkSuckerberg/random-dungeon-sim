import random


class RollEntry:
	Name: str = ""
	Title: str = ""
	Weight: int = 1
	LinkedRollTables: list[str] = []
	Description: str = ""

	def __init__(self, name: str, weight: int, linkedRollTables: list[str], description: str):
		self.Name = name.casefold()
		self.Title = name
		self.Weight = weight
		self.LinkedRollTables = linkedRollTables
		self.Description = description

class RollTable:
	Name: str = ""
	Title: str = ""
	Entries: list[RollEntry] = []
	TotalWeight: int = 0

	def __init__(self, name: str, entries: list[RollEntry]):
		self.Name = name.casefold()
		self.Title = name
		self.Entries = entries
		self.TotalWeight = sum([entry.Weight for entry in entries])

	def roll(self):
		roll = random.randint(1, self.TotalWeight)
		for entry in self.Entries:
			roll -= entry.Weight
			if roll <= 0:
				return entry

		return None
