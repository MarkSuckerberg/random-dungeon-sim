import discord
from discord import app_commands
from discord.ext import commands
from json import dumps

from dotenv import load_dotenv
from os import getenv

from user import GetRollList
from main import GetTables

from tinydb import TinyDB, Query

load_dotenv()
key = getenv("TOKEN")

if key is None:
    raise ValueError("No token found in .env")

db = TinyDB("data/db.json")
userRollsTable = db.table("users")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

rollTables = GetTables()


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot ready")


async def table_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=table.title(), value=table)
        for table in rollTables.keys()
        if (current.casefold() in table)
    ][:25]


async def user_rolls_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    roll = Query()
    data = userRollsTable.search(
        (roll.user_id == interaction.user.id) & (current in roll.table.casefold())
    )

    if not data:
        return []

    return [
        app_commands.Choice(
            name=f"{data[i]['table'].title()} - {str.join(', ', [str(roll) for roll in data[i]['rolls']])} - ({i + 1} roll(s) ago)",
            value=str(i + 1),
        )
        for i in range(len(data))
    ]


@bot.tree.command(name="roll", description="Roll on a table")
@app_commands.describe(
    table="The name of the table to roll on",
    public="Whether to show the result to everyone",
    silent="Whether to not show even the roll numbers",
)
@app_commands.autocomplete(table=table_autocomplete)
async def roll(
    interaction: discord.Interaction,
    table: str = "Rooms",
    public: bool = False,
    silent: bool = False,
):
    await do_roll(interaction, table, public, silent)


async def do_roll(
    interaction: discord.Interaction, table: str, public: bool, silent: bool
):
    await interaction.response.send_message(
        f"Rolling on table {table}...", ephemeral=(not public)
    )

    table = table.casefold()

    for tableName in rollTables:
        if tableName.startswith(table):
            table = tableName
            break

    if table not in rollTables:
        await interaction.edit_original_response(content=f"Table '{table}' not found")
        return

    embed = discord.Embed(
        title=f"'{table.title()}' Roll Results", color=discord.Color.blue()
    )
    rollValues = GetRollList(rollTables, table)

    rollList = rollValues[0]

    for key, value in rollList.items():
        embed.add_field(name=key, value=value, inline=False)

    await interaction.edit_original_response(embed=embed, content=None)

    if not public and not silent:
        name = interaction.user.name
        if isinstance(interaction.user, discord.Member) and interaction.user.nick:
            name = interaction.user.nick

        await interaction.followup.send(
            f'{name} rolled {str.join(", ", [str(roll) for roll in rollValues[1]])}'
        )

    location = interaction.channel.id if interaction.channel else interaction.user.id

    userSaveData = {
        "user_id": interaction.user.id,
        "channel_id": location,
        "table": table,
        "rolls": rollValues[1],
        "rollDetails": rollList,
    }

    userRollsTable.insert(userSaveData)


@bot.tree.command(name="show", description="Show the last roll")
@app_commands.describe(
    roll_number="The number of the roll to show",
    public="Whether to show the result to everyone",
)
@app_commands.autocomplete(roll_number=user_rolls_autocomplete)
async def show(
    interaction: discord.Interaction, roll_number: int = 1, public: bool = False
):

    data = userRollsTable.search(Query().user_id == interaction.user.id)
    data.reverse()

    if not data:
        await interaction.response.send_message(
            "No previous roll to get", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"'{data[roll_number - 1]['table'].title()}' Last Roll",
        color=discord.Color.blue(),
    )

    for key, value in data[roll_number - 1]["rollDetails"].items():
        embed.add_field(name=key, value=value, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=(not public))


@bot.tree.command(name="reroll", description="Reroll the last roll")
@app_commands.describe(
    public="Whether to show the result to everyone",
    silent="Whether to not show even the roll numbers",
)
async def reroll(
    interaction: discord.Interaction, public: bool = False, silent: bool = False
):
    data = userRollsTable.search(Query().user_id == interaction.user.id)

    if not data:
        await interaction.response.send_message(
            "No previous roll to reroll", ephemeral=True
        )
        return

    await do_roll(interaction, data[0]["table"], public, silent)


@bot.tree.command(name="reload", description="Reload the tables")
async def reload(interaction: discord.Interaction):
    global rollTables
    rollTables = GetTables()
    await interaction.response.send_message("Tables reloaded", ephemeral=True)


@bot.tree.command(name="tables", description="List all tables")
async def tables(interaction: discord.Interaction, public: bool = False):
    embed = discord.Embed(title="Tables", color=discord.Color.blue())

    embed.description = "\n".join(
        [
            f"- **{table.Title}**: {len(table.Entries)} entries, max roll {table.TotalWeight}"
            for (name, table) in rollTables.items()
        ]
    )

    await interaction.response.send_message(embed=embed, ephemeral=(not public))


async def entry_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    if not interaction.data:
        return []

    options = interaction.data.get("options")
    if not isinstance(options, list):
        return []

    table = options[0].get("value")

    table = table.casefold()

    for tableName in rollTables:
        if tableName.startswith(table):
            table = tableName
            break

    if table not in rollTables:
        return []

    return [
        app_commands.Choice(name=entry.Title, value=entry.Name)
        for entry in rollTables[table].Entries
        if current.casefold() in entry.Name
    ][:25]


@bot.tree.command(
    name="find", description="Find details on a specific roll entry on a table"
)
@app_commands.describe(
    table="The name of the table to search in",
    entry="The name of the entry to search for",
)
@app_commands.autocomplete(table=table_autocomplete, entry=entry_autocomplete)
async def find(
    interaction: discord.Interaction, table: str, entry: str, public: bool = False
):
    table = table.casefold()
    entry = entry.casefold()

    await interaction.response.send_message(
        f"Finding entry {entry} in table {table}...", ephemeral=(not public)
    )

    for tableName in rollTables:
        if tableName.startswith(table):
            table = tableName
            break

    if table not in rollTables:
        await interaction.edit_original_response(content=f"Table '{table}' not found")
        return

    for rollEntry in rollTables[table].Entries:
        if rollEntry.Name.startswith(entry):
            embed = discord.Embed(
                title=f"'{rollEntry.Title}' Entry Details", color=discord.Color.blue()
            )
            embed.add_field(name="Table", value=table.title())
            embed.add_field(name="Weight", value=rollEntry.Weight)
            embed.add_field(
                name="Linked Roll Tables",
                value=(
                    ", ".join(rollEntry.LinkedRollTables)
                    if len(rollEntry.LinkedRollTables) > 0
                    else "None"
                ),
            )
            embed.add_field(
                name="Description",
                value=(
                    rollEntry.Description if len(rollEntry.Description) > 0 else "None"
                ),
                inline=False,
            )
            embed.add_field(
                name="JSON",
                value=f"```json\n{dumps(rollEntry.__dict__, indent=4)}```",
                inline=False,
            )
            await interaction.edit_original_response(embed=embed, content=None)
            return

    await interaction.edit_original_response(
        content=f"Entry '{entry}' not found in table '{table}'"
    )


bot.run(key)
