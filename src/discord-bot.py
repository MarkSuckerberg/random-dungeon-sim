import discord
from discord import app_commands
from discord.ext import commands
from json import dumps

from dotenv import load_dotenv, dotenv_values

from user import GetRollList
from main import GetTables

key = dotenv_values().get('TOKEN')

if key is None:
	raise ValueError('No token found in .env')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

rollTables = GetTables()

@bot.event
async def on_ready():
	await bot.tree.sync()
	print('ready')

async def table_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	return [app_commands.Choice(name=table.title(), value=table) for table in rollTables.keys() if (current.casefold() in table)][:25]

@bot.tree.command(name='roll', description='Roll on a table')
@app_commands.describe(table='The name of the table to roll on', public='Whether to show the result to everyone', silent='Whether to not show even the roll numbers')
@app_commands.autocomplete(table=table_autocomplete)
async def roll(interaction: discord.Interaction, table: str = "Rooms", public: bool = False, silent: bool = False):
	await interaction.response.send_message(f'Rolling on table {table}...', ephemeral=(not public))

	table = table.casefold()

	for tableName in rollTables:
		if tableName.startswith(table):
			table = tableName
			break

	if table not in rollTables:
		await interaction.edit_original_response(content=f"Table '{table}' not found")
		return

	embed = discord.Embed(title=f"'{table.title()}' Roll Results", color=discord.Color.blue())
	rollValues = GetRollList(rollTables, table)

	rollList = rollValues[0]

	for (key, value) in rollList.items():
		embed.add_field(name=key, value=value, inline=False)

	await interaction.edit_original_response(embed=embed, content=None)

	if not public and not silent:
		await interaction.followup.send(f'{interaction.user.name} rolled {str.join(", ", [str(roll) for roll in rollValues[1]])}')

@bot.tree.command(name='reload', description='Reload the tables')
async def reload(interaction: discord.Interaction):
	global rollTables
	rollTables = GetTables()
	await interaction.response.send_message('Tables reloaded', ephemeral=True)

@bot.tree.command(name='tables', description='List all tables')
async def tables(interaction: discord.Interaction, public: bool = False):
	embed = discord.Embed(title='Tables', color=discord.Color.blue())

	embed.description = '\n'.join([f'- **{table.Title}**: {len(table.Entries)} entries, max roll {table.TotalWeight}' for (name, table) in rollTables.items()])

	await interaction.response.send_message(embed=embed, ephemeral=(not public))

async def entry_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
	table = interaction.data['options'][0]['value']

	table = table.casefold()

	for tableName in rollTables:
		if tableName.startswith(table):
			table = tableName
			break

	if table not in rollTables:
		return []

	return [app_commands.Choice(name=entry.Title, value=entry.Name) for entry in rollTables[table].Entries if current.casefold() in entry.Name][:25]

@bot.tree.command(name='find', description='Find details on a specific roll entry on a table')
@app_commands.describe(table='The name of the table to search in', entry='The name of the entry to search for')
@app_commands.autocomplete(table=table_autocomplete, entry=entry_autocomplete)
async def find(interaction: discord.Interaction, table: str, entry: str, public: bool = False):
	table = table.casefold()
	entry = entry.casefold()

	await interaction.response.send_message(f'Finding entry {entry} in table {table}...', ephemeral=(not public))

	for tableName in rollTables:
		if tableName.startswith(table):
			table = tableName
			break

	if table not in rollTables:
		await interaction.edit_original_response(content=f"Table '{table}' not found")
		return

	for rollEntry in rollTables[table].Entries:
		if rollEntry.Name.startswith(entry):
			embed = discord.Embed(title=f"'{rollEntry.Title}' Entry Details", color=discord.Color.blue())
			embed.add_field(name='Table', value=table.title())
			embed.add_field(name='Weight', value=rollEntry.Weight)
			embed.add_field(name='Linked Roll Tables', value=', '.join(rollEntry.LinkedRollTables) if len(rollEntry.LinkedRollTables) > 0 else 'None')
			embed.add_field(name='Description', value=rollEntry.Description if len(rollEntry.Description) > 0 else 'None', inline=False)
			embed.add_field(name='JSON', value=f'```json\n{dumps(rollEntry.__dict__, indent=4)}```', inline=False)
			await interaction.edit_original_response(embed=embed, content=None)
			return

	await interaction.edit_original_response(content=f"Entry '{entry}' not found in table '{table}'")

bot.run(key)
