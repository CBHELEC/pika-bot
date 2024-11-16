import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
import string
from datetime import datetime, timedelta
import os
import asyncio

from dotenv import load_dotenv
load_dotenv(".env")
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.all()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=';', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------------------------')
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.CustomActivity(f"Testing new event??"))
    asyncio.create_task(remove_expired_roles())
    print("Bot is ready!")
    
##################################################################################### Role Codes ###############################################################################################

conn = sqlite3.connect('codes.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS codes (
    role INTEGER,
    time TEXT,
    key TEXT PRIMARY KEY,
    ID INTEGER,
    uses INTEGER,
    created_at TEXT,
    remaining_uses INTEGER
)
''')
conn.commit()

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def get_next_id():
    cursor.execute('SELECT MAX(ID) FROM codes')
    result = cursor.fetchone()[0]
    return (result + 1) if result else 1

@bot.tree.command(name="create_code", description="Create a code redeemable for a role.")
@app_commands.describe(
    role="Role to assign when code is redeemed",
    duration="How long role lasts when redeemed (e.g., '1d', '2h'). Leave empty for no expiration",
    uses="Number of times code can be redeemed"
)
async def create_code(interaction: discord.Interaction, role: discord.Role, duration: str = None, uses: int = 1, ephemeral: bool = True):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You do not have permission to manage roles.", ephemeral=True)
        return

    code = generate_code()
    code_id = get_next_id()
    expiry_time = None

    # Handle expiration time if specified
    if duration:
        unit = duration[-1]
        amount = int(duration[:-1])
        if unit == 's':  # seconds
            expiry_time = datetime.now() + timedelta(seconds=amount)
        elif unit == 'd':  # days
            expiry_time = datetime.now() + timedelta(days=amount)
        elif unit == 'h':  # hours
            expiry_time = datetime.now() + timedelta(hours=amount)
        elif unit == 'm':  # minutes
            expiry_time = datetime.now() + timedelta(minutes=amount)

    formatted_expiry = "Never"
    if expiry_time:
        formatted_expiry = f"`{expiry_time.strftime('%d-%m-%Y %H:%M:%S')}`"

    # Insert the code into the database, with the expiration time and max uses
    cursor.execute('INSERT INTO codes (role, time, key, ID, uses, created_at, remaining_uses) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (role.id, expiry_time.isoformat() if expiry_time else None, code, code_id, uses, datetime.now().isoformat(), uses))
    conn.commit()

    channel = bot.get_channel(1305600603241582642)
    if channel:
        embed = discord.Embed(title="New Code Created", color=discord.Color.blue())
        embed.add_field(name="ID", value=f"`{code_id}`", inline=True)
        embed.add_field(name="Code", value=f"```{code}```", inline=True)
        embed.add_field(name="Role", value=f"`{role.name}`", inline=True)
        embed.add_field(name="Expires", value=f"{formatted_expiry}", inline=True)
        embed.add_field(name="Max Uses", value=f"`{uses}`", inline=True)
        await channel.send(embed=embed)

        codeembed = discord.Embed(title="Code Created Successfully", color=discord.Color.red())
        codeembed.description = (
            f"The code for <@&{role.id}> has been successfully created.\n"
            "Please click below to reveal it.\n"
            f"||# {code}||"
        )
        codeembed.set_footer(text=f"{interaction.user.display_name} | ID: {code_id}", icon_url=interaction.user.avatar.url)
        print(f"[DEBUG | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] | Code Created! Code: {code}, Uses: {uses}, Expires: {formatted_expiry}")
        await interaction.response.send_message(embed=codeembed, ephemeral=ephemeral)


@bot.event
async def on_code_redeemed(code: str, user: discord.User):
    # Fetch the code from the database to check its status
    cursor.execute('SELECT * FROM codes WHERE key = ?', (code,))
    result = cursor.fetchone()
    if not result:
        await user.send("This code is invalid.")
        return
    
    role_id = result[0]
    expiry_time = result[1]
    remaining_uses = result[6]

    # Check if the code is expired, but allow redemption if uses are left
    if expiry_time:
        expiry_time = datetime.fromisoformat(expiry_time)
        if datetime.now() > expiry_time and remaining_uses <= 0:
            await user.send("This code has expired and cannot be redeemed.")
            return

    if remaining_uses > 0:
        # Assign the role to the user
        role = discord.utils.get(user.guild.roles, id=role_id)
        if role:
            await user.add_roles(role)
            cursor.execute('UPDATE codes SET remaining_uses = remaining_uses - 1 WHERE key = ?', (code,))
            conn.commit()
            await user.send(f"You have redeemed the code and received the role {role.name}.")
        else:
            await user.send("Role not found.")
    else:
        await user.send("This code has already been used the maximum number of times.")

redconn = sqlite3.connect('redemptions.db')
redcursor = redconn.cursor()
redcursor.execute('''
CREATE TABLE IF NOT EXISTS redemptions (
    user_id INTEGER,
    code_key TEXT,
    redeemed_at TEXT,
    PRIMARY KEY (user_id, code_key)
)
''')
redconn.commit()

@bot.tree.command(name="redeem", description="Redeem a code to receive a role.")
async def redeem(interaction: discord.Interaction, code: str):
    # Fetch the code details
    cursor.execute("SELECT role, uses, time, remaining_uses FROM codes WHERE key = ?", (code,))
    result = cursor.fetchone()

    if not result:
        await interaction.response.send_message("Invalid code. Please contact a mod for help.", ephemeral=True)
        return

    role_id, max_uses, global_expiration, remaining_uses = result
    role = interaction.guild.get_role(role_id)
    if not role:
        await interaction.response.send_message("This role no longer exists or I cannot access it. Please contact a mod for help.", ephemeral=True)
        return

    # Check if the user has already redeemed the code
    cursor.execute("SELECT * FROM redemptions WHERE user_id = ? AND code_key = ?", (interaction.user.id, code))
    if redcursor.fetchone():
        await interaction.response.send_message("You have already redeemed this code.", ephemeral=True)
        return

    # Check if the code is out of uses
    if remaining_uses <= 0:
        await interaction.response.send_message("This code has no remaining uses. Please contact a mod for help.", ephemeral=True)
        return

    # Check if the code has globally expired
    if global_expiration:
        try:
            expiration_time = datetime.fromisoformat(global_expiration)
            if datetime.now() > expiration_time:
                await interaction.response.send_message("This code has expired. Please contact a mod for help.", ephemeral=True)
                return
        except ValueError:
            print("Invalid global expiration time format.")

    # Grant the role and log the redemption
    try:
        await interaction.user.add_roles(role)

        # Add redemption to the database
        redcursor.execute("INSERT INTO redemptions (user_id, code_key, redeemed_at) VALUES (?, ?, ?)",
                       (interaction.user.id, code, datetime.now().isoformat()))
        # Reduce the remaining uses
        cursor.execute("UPDATE codes SET remaining_uses = remaining_uses - 1 WHERE key = ?", (code,))
        conn.commit()

        # Schedule role expiration
        redcursor.execute("SELECT time FROM codes WHERE key = ?", (code,))
        duration_str = cursor.fetchone()[0]

        if duration_str:  # Only schedule removal if time is specified
            expiry_time = datetime.now()
            unit = duration_str[-1]
            amount = int(duration_str[:-1])
            if unit == 's':
                expiry_time += timedelta(seconds=amount)
            elif unit == 'm':
                expiry_time += timedelta(minutes=amount)
            elif unit == 'h':
                expiry_time += timedelta(hours=amount)
            elif unit == 'd':
                expiry_time += timedelta(days=amount)

            # Schedule the role removal
            bot.loop.call_later(
                (expiry_time - datetime.now()).total_seconds(),
                lambda: bot.loop.create_task(remove_role(interaction.user, role))
            )

        # Inform the user
        await interaction.response.send_message(
            f"You have redeemed the code and received the '{role.name}' role! Remaining uses: {remaining_uses - 1}.",
            ephemeral=True
        )
        print(
            f"[DEBUG | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Code Redeemed! Code: {code}, User: {interaction.user.name}, Role: {role.name}, Uses Left: {remaining_uses - 1}"
        )

    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to assign this role. Please contact a mod for help.", ephemeral=True)


async def remove_role(member, role):
    try:
        await member.remove_roles(role)
        print(f"[DEBUG | {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Role '{role.name}' removed from {member}.")
    except discord.DiscordException as e:
        print(f"[ERROR] Failed to remove role: {e}")

@bot.tree.command(name="delete_code", description="Delete a code by its ID.")
@app_commands.describe(code_id="The ID of the code to delete.")
async def delete_code(interaction: discord.Interaction, code_id: int):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You do not have permission to manage roles.", ephemeral=True)
        return
    cursor.execute('SELECT key FROM codes WHERE ID = ?', (code_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute('DELETE FROM codes WHERE ID = ?', (code_id,))
        conn.commit()
        await interaction.response.send_message(f"Code with ID `{code_id}` has been deleted.", ephemeral=True)
    else:
        await interaction.response.send_message("No code found with that ID.", ephemeral=True)
        
@bot.tree.command(name="list_codes", description="List all the created codes with their details.")
async def list_codes(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You do not have permission to manage roles.", ephemeral=True)
        return
    cursor.execute("SELECT ID, key, role, time, uses, created_at FROM codes")
    rows = cursor.fetchall()

    if not rows:
        await interaction.response.send_message("No codes have been created yet.", ephemeral=True)
        return

    embed = discord.Embed(title="List of All Created Codes", color=discord.Color.blue())

    # Iterate through the rows and add them to the embed
    for row in rows:
        code_id, code, role_id, expiry_time_str, uses_left, created_at_str = row

        role = interaction.guild.get_role(role_id)
        role_name = role.name if role else "Unknown Role"
        expiry_time = None
        if expiry_time_str:
            try:
                expiry_time = datetime.fromisoformat(expiry_time_str)
            except ValueError:
                pass  # Ignore invalid date format

        # Format expiry and created time
        expiry_str = f"Expires at {expiry_time.strftime('%d-%m-%Y %H:%M:%S')}" if expiry_time else "No expiration"
        created_at = datetime.fromisoformat(created_at_str).strftime('%d-%m-%Y %H:%M:%S')

        # Add the code details to the embed
        embed.add_field(
            name=f"Code {code_id} - {code}",
            value=(
                f"Role: {role_name}\n"
                f"Expires: {expiry_str}\n"
                f"Uses Left: {uses_left}\n"
                f"Created At: {created_at}\n"
            ),
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

###################################################################################### Temp Roles ###############################################################################################

trconn = sqlite3.connect('temproles.db')
trcursor = trconn.cursor()

# Create the table to store temporary roles data
trcursor.execute('''
CREATE TABLE IF NOT EXISTS temp_roles (
    role_id INTEGER,
    user_id INTEGER,
    expiry_time TEXT,
    created_at TEXT,
    PRIMARY KEY (role_id, user_id)
)
''')
trconn.commit()

@bot.tree.command(name="temprole_add", description="Add a temporary role to a user.")
async def temprole_add(interaction: discord.Interaction, role: discord.Role, user: discord.User, duration: str):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You do not have permission to manage roles.", ephemeral=True)
        return
    
    await user.add_roles(role)
    
    expiration_time = None

    if duration:
        unit = duration[-1] 
        amount = int(duration[:-1]) 
        if unit == 's':  # seconds
            expiration_time = datetime.now() + timedelta(seconds=amount)
        elif unit == 'd':  # days
            expiration_time = datetime.now() + timedelta(days=amount)
        elif unit == 'h':  # hours
            expiration_time = datetime.now() + timedelta(hours=amount)
        elif unit == 'm':  # minutes
            expiration_time = datetime.now() + timedelta(minutes=amount)
    
    formatted_expiry = "Never"
    if expiration_time:
        formatted_expiry = f"`{expiration_time.strftime('%d-%m-%Y %H:%M:%S')}`"
   
    if expiration_time:
        expiration_time_str = expiration_time.strftime('%d-%m-%Y %H:%M:%S')
        trcursor.execute('''
            INSERT OR REPLACE INTO temp_roles (role_id, user_id, expiry_time, created_at)
            VALUES (?, ?, ?, ?)
        ''', (role.id, user.id, expiration_time_str, datetime.now().strftime('%d-%m-%Y %H:%M:%S')))
        trconn.commit()
    
    trembed=discord.Embed(title="Temporary Role Assigned", color=discord.Color.green())
    trembed.description=(
        f"Role: <@&{role.id}>\n Added To: {user.mention}\n Expires: {formatted_expiry}"
    )
    await interaction.response.send_message(embed=trembed)

@bot.tree.command(name="temprole_list", description="List all temporary roles, users, and expiration times.")
@commands.has_permissions(moderate_members=True)
async def temprole_list(interaction: discord.Interaction):
    trcursor.execute('''SELECT role_id, user_id, expiry_time FROM temp_roles''')
    rows = trcursor.fetchall()

    if not rows:
        await interaction.response.send_message("There are no temporary roles currently assigned.", ephemeral=True)
        return

    embed = discord.Embed(title="Temporary Roles List", color=discord.Color.green())

    for row in rows:
        role_id, user_id, expiry_time_str = row
        role = interaction.guild.get_role(role_id)
        user = interaction.guild.get_member(user_id)

        if role and user:
            try:
                expiry_time = datetime.strptime(expiry_time_str, '%d-%m-%Y %H:%M:%S')
                expiry_time_str = expiry_time.strftime('%d-%m-%Y %H:%M:%S')
            except ValueError:
                expiry_time_str = "Never"

            embed.add_field(
                name=f"Role: {role.name}",
                value=f"User: {user.name}\nExpires: {expiry_time_str}",
                inline=False
            )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="temprole_remove", description="Remove a temporary role from a user.")
async def temprole_remove(interaction: discord.Interaction, role: discord.Role, user: discord.User):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You do not have permission to manage roles.", ephemeral=True)
        return

    await user.remove_roles(role)

    trcursor.execute('''
        DELETE FROM temp_roles WHERE role_id = ? AND user_id = ?
    ''', (role.id, user.id))
    trconn.commit()

    await interaction.response.send_message(f"Temporary role {role.name} removed from {user.name}.")

async def remove_expired_roles():
    while True:
        current_time = datetime.now()
        trcursor.execute('''
            SELECT role_id, user_id, expiry_time FROM temp_roles
        ''')
        rows = trcursor.fetchall()

        for role_id, user_id, expiry_time_str in rows:
            expiry_time = datetime.strptime(expiry_time_str, '%d-%m-%Y %H:%M:%S')

            if expiry_time <= current_time:
                role = discord.utils.get(bot.get_guild(1237815910887194624).roles, id=role_id)
                user = discord.utils.get(bot.get_guild(1237815910887194624).members, id=user_id)

                if role and user:
                    await user.remove_roles(role)
                    trcursor.execute('''
                        DELETE FROM temp_roles WHERE role_id = ? AND user_id = ?
                    ''', (role_id, user_id))
                    trconn.commit()

        # Wait for a minute before checking again
        await asyncio.sleep(5)

#################################################################################################################################################################################################

bot.run(TOKEN)