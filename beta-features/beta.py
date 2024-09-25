import discord
from discord.ext import commands
from discord.utils import get
from discord import app_commands
import os
import json

# Load boost data from the JSON file
def load_boost_data():
    try:
        with open("boost_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save boost data to the JSON file
def save_boost_data(data):
    with open("boost_data.json", "w") as f:
        json.dump(data, f, indent=4)

# Load boost data at the start
user_boost_data = load_boost_data()

# Load environment variables
from dotenv import load_dotenv
load_dotenv(".env")
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send(f"I synced for you senpai 😫")

# Function to check how many times the user boosted
def get_boost_count(member):
    if member.premium_since:
        return len([role for role in member.roles if role.is_premium_subscriber()])
    return 0

# Slash Command: /boosterrole claim
@bot.tree.command(name="boosterrole_claim", description="Claim a default Booster Role if you have boosted.")
async def boosterrole_claim(interaction: discord.Interaction):
    member = interaction.user
    boost_count = user_boost_data.get(str(member.id), {}).get("boost_count", 0)

    if boost_count == 0:
        await interaction.response.send_message("You haven't boosted this server yet!", ephemeral=True)
    else:
        guild = interaction.guild
        if str(member.id) not in user_boost_data or not user_boost_data[str(member.id)].get("roles"):
            # Create the default Booster Role
            custom_role = await guild.create_role(name="Booster Role")
            await member.add_roles(custom_role)

            # Track user data for future edits
            user_boost_data[str(member.id)]["roles"] = [custom_role.id]
            save_boost_data(user_boost_data)

            await interaction.response.send_message(f"{member.mention}, your default Booster Role has been created and added to you!", ephemeral=True)
        else:
            await interaction.response.send_message("You have already claimed your custom role(s).", ephemeral=True)

# Slash Command: /boosterrole edit
@bot.tree.command(name="boosterrole_edit", description="Edit your custom role's name or colour.")
@app_commands.describe(
    new_name="Enter a new name for your role",
    new_colour="Enter a hex code for the new colour of your role"
)
async def boosterrole_edit(interaction: discord.Interaction, new_name: str = None, new_colour: str = None):
    member = interaction.user
    boost_info = user_boost_data.get(str(member.id))

    if boost_info is None or not boost_info.get("roles"):
        await interaction.response.send_message("You don't have a custom role to edit.", ephemeral=True)
        return

    role_id = boost_info["roles"][-1]
    custom_role = get(interaction.guild.roles, id=role_id)

    if custom_role:
        # Track changes made
        changes = []

        # Update role name if provided
        if new_name:
            await custom_role.edit(name=new_name)
            changes.append(f"Name updated to **{new_name}**")

        # Update role colour if provided
        if new_colour:
            try:
                color = discord.Color(int(new_colour.lstrip("#"), 16))
                await custom_role.edit(colour=color)
                changes.append(f"Colour updated to **{new_colour}**")
            except ValueError:
                await interaction.response.send_message("Invalid hex color code. Please provide a valid one.", ephemeral=True)
                return

        if changes:
            await interaction.response.send_message(f"{member.mention}, your role **{custom_role.mention}** has been updated: {', '.join(changes)}", ephemeral=True)
        else:
            await interaction.response.send_message("No changes were made.", ephemeral=True)
    else:
        await interaction.response.send_message("Role not found.", ephemeral=True)

# Load boost data from the JSON file
def load_boost_data():
    try:
        with open("boost_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create an empty file if it doesn't exist
        save_boost_data({})
        return {}

# Save boost data to the JSON file
def save_boost_data(data):
    with open("boost_data.json", "w") as f:
        json.dump(data, f, indent=4)

# Event listener to track boosts
@bot.event
async def on_member_update(before, after):
    # Check if the user started or stopped boosting
    if before.premium_since != after.premium_since:
        member = after
        boost_count = get_boost_count(member)

        # Initialize user data if not present
        if str(member.id) not in user_boost_data:
            user_boost_data[str(member.id)] = {
                "boost_count": 0,
                "roles": []
            }
        
        # Update the boost count
        user_boost_data[str(member.id)]["boost_count"] = boost_count
        save_boost_data(user_boost_data)

        # Notify in a specific channel if a user starts boosting
        boost_channel = bot.get_channel(1245096650704294050)  # Replace with the correct boost channel ID
        if boost_count > 0:
            await boost_channel.send(f"{member.mention} has boosted the server! Total boosts: {boost_count}")
        else:
            await boost_channel.send(f"{member.mention} has stopped boosting the server.")

# ON BOT START
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------')
    await bot.change_presence(
        activity=discord.CustomActivity("I don't get paid enough"))
    print("Bot is ready!")

# Start the bot
bot.run(TOKEN)
