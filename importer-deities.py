# Formats a human-redable roll table into a JSON file.

import json

def main():
	"""
		Input format:

		1. Entry 1
		2-6. Entry 2
		7-10. Entry 3
		11. Entry 4

		Output format:

		{
			"Entry 1": {
				"Weight": 1
			},
			"Entry 2": {
				"Weight": 5
			},
			"Entry 3": {
				"Weight": 4
			},
			"Entry 4": {
				"Weight": 1
			}
		}
	"""

	with open('rds.txt') as f:
		lines = f.readlines()

	data = {}
	for line in lines:
		line = line.strip()
		description = ""
		if len(line) == 0:
			continue

		if not line[0].isdigit():
			continue

		weight = 1
		if '-' in line[:4]:
			weight = int(line.split('.')[0].split('-')[1]) - int(line.split('-')[0]) + 1
			line = line.split('.')[1].strip()
		else:
			line = line.split('.')[1].strip()

		blessing, curse, sideEffect = "", "", ""

		if ' (' in line:
			blessing = line.split(" (")[1].split(")")[0].strip()
		if ' [' in line:
			curse = line.split(" [")[1].split("]")[0].strip()
		if ' {' in line:
			sideEffect = line.split(" {")[1].split("}")[0].strip()

		if blessing:
			description = f"\nBlessing: {blessing}"
		if curse:
			description += f"\nCurse: {curse}"
		if sideEffect:
			description += f"\nSide Effect: {sideEffect}"

		line = line.split(" (")[0].split(" [")[0].split(" {")[0].split(" -")[0].strip()

		data[line] = {
			"Weight": weight
		}

		if description:
			data[line]["Description"] = description

	with open('rds-out.json', 'w') as f:
		json.dump(data, f, indent=4)

if __name__ == '__main__':
	main()
