from discord.ext import tasks
import asyncio
import discord
from discord.ext import commands
import os
import sqlite3
import random
from datetime import datetime
import math
from discord import ButtonStyle, app_commands
from discord.ui import Button, View

from dotenv import load_dotenv
load_dotenv(".env")
TOKEN = os.getenv('BOT_TOKEN')
VOLTIFY_GUILD = os.getenv('VOLTIFY_GUILD')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='v.', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------------------------')
    await bot.tree.sync()
    # yes, i know this is bad. do I care? no.
    ensure_columns_exist_players()
    ensure_columns_exist_catches()
    await bot.change_presence(
        activity=discord.CustomActivity(f"Being Cute <3"))

voltify_prefix = "v."

# User Isn't Player Embed: https://embed.dan.onl/?data=eyJ0aXRsZSI6IllvdSBoYXZlbid0IHN0YXJ0ZWQgZmlzaGluZyEiLCJkZXNjcmlwdGlvbiI6IlVzZSBge3ZvbHRpZnlfcHJlZml4fXN0YXJ0YCB0byBiZWdpbi4iLCJjb2xvciI6IiMwMGIwZjQiLCJmb290ZXIiOnsidGV4dCI6IntjdHguYXV0aG9yLm5hbWV9IiwiaWNvblVybCI6IntjdHguYXV0aG9yLmF2YXRhci51cmx9In0sInRpbWVzdGFtcCI6MTczMjczMjcyNDU4MX0%3D

@bot.command()
async def uwu(ctx):
    await ctx.send("uwu")
    
##############################################################################################################################################################################################

conn = sqlite3.connect("fishing.db")
cursor = conn.cursor()

# Players
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    unlocked_locations TEXT DEFAULT 'Pond',
    rod_level INTEGER DEFAULT 1,
    start_date TEXT NOT NULL,
    total_fish INTEGER DEFAULT 0,
    total_caught INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0
)
""")

# Fish Catches
cursor.execute("""
CREATE TABLE IF NOT EXISTS catches (
    user_id INTEGER,
    fish_name TEXT,
    rarity TEXT,
    fish_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ivs INTEGER,
    level INTEGER,
    UNIQUE(user_id, fish_id)
)
""")

conn.commit()

def ensure_columns_exist_players():
    # List of expected columns in the players table
    expected_columns = [
        "user_id", "coins", "unlocked_locations", "rod_level", 
        "start_date", "total_fish", "total_caught", "total_spent"
    ]
    
    # Get the current columns in the players table
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Loop through the expected columns and add any missing ones
    for column in expected_columns:
        if column not in columns:
            if column == "total_fish":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN total_fish INTEGER DEFAULT 0
                """)
            elif column == "total_caught":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN total_caught INTEGER DEFAULT 0
                """)
            elif column == "total_spent":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN total_spent INTEGER DEFAULT 0
                """)
            elif column == "coins":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN coins INTEGER DEFAULT 0
                """)
            elif column == "unlocked_locations":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN unlocked_locations TEXT DEFAULT 'Pond'
                """)
            elif column == "rod_level":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN rod_level INTEGER DEFAULT 1
                """)
            elif column == "start_date":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN start_date TEXT DEFAULT CURRENT_TIMESTAMP
                """)
    
    # Commit the changes
    conn.commit()

def ensure_columns_exist_catches():
    expected_columns = [
        "user_id", "fish_name", "rarity", "fish_id", "ivs", "level"
    ]

    cursor.execute("PRAGMA table_info(catches)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # If 'fish_id' doesn't exist, recreate the table with the correct structure
    if "fish_id" not in columns:
        cursor.execute("""
        DROP TABLE IF EXISTS catches;
        """)
        # Recreate the table with fish_id as PRIMARY KEY AUTOINCREMENT
        cursor.execute("""
        CREATE TABLE catches (
            user_id INTEGER,
            fish_name TEXT,
            rarity TEXT,
            fish_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ivs INTEGER,
            level INTEGER,
            UNIQUE(user_id, fish_id)
        );
        """)
    
    # If other columns are missing, add them (non-primary key columns can be added)
    for column in expected_columns:
        if column not in columns:
            if column == "user_id":
                cursor.execute("""ALTER TABLE catches ADD COLUMN user_id INTEGER""")
            elif column == "fish_name":
                cursor.execute("""ALTER TABLE catches ADD COLUMN fish_name TEXT""")
            elif column == "rarity":
                cursor.execute("""ALTER TABLE catches ADD COLUMN rarity TEXT""")
            elif column == "ivs":
                cursor.execute("""ALTER TABLE catches ADD COLUMN ivs INTEGER""")
            elif column == "level":
                cursor.execute("""ALTER TABLE catches ADD COLUMN level INTEGER""")
            elif column == "fish_id":
                cursor.execute("""ALTER TABLE catches ADD COLUMN fish_id INTEGER PRIMARY KEY AUTOINCREMENT""")

    conn.commit()

fish_tiers = {
    "Common": ["Aetherfin", "Shadowscale", "Embergill"],
    "Uncommon": ["Duskhawk", "Stormsnap", "Ironjaw"],
    "Rare": ["Zephyric", "Bloodspine", "Crystalfin"],
    "Epic": ["Frostfang", "Vortexblade", "Noxscale"],
    "Legendary": ["Eclipsera", "Thundermane", "Dreadfin"],
    "Mythical": ["Nexusfang", "Goldvein", "Leviathan"]
}

def determine_rarity():
    roll = random.uniform(0, 127)  # Generate a random number between 0 and 127

    if roll < 60.381:  # ~47.56% chance for Common
        return "Common"
    elif roll < 60.381 + 40.254:  # ~31.69% chance for Uncommon
        return "Uncommon"
    elif roll < 60.381 + 40.254 + 20.127:  # ~15.85% chance for Rare
        return "Rare"
    elif roll < 60.381 + 40.254 + 20.127 + 5.032:  # ~3.96% chance for Epic
        return "Epic"
    elif roll < 60.381 + 40.254 + 20.127 + 5.032 + 1.006:  # ~0.79% chance for Legendary
        return "Legendary"
    else:  # ~0.1% chance for Mythical
        return "Mythical"

# Gear effects
gear_effects = {
    1: 1.0,  # Basic Rod
    2: 1.5,  # Advanced Rod
    3: 2.0   # Master Rod
}

# Commands
@bot.command()
async def start(ctx):
    """Starts your fishing adventure."""
    user_id = ctx.author.id
    username = ctx.author.name
    start_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Current date and time

    # Check if the player already exists
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        await ctx.send(f"❌ {ctx.author.mention}, you have already started your fishing adventure!")
        return
    
    # Insert new player data
    cursor.execute("""
    INSERT INTO players (user_id, coins, unlocked_locations, rod_level, start_date, total_fish, total_caught, total_spent)
    VALUES (?, 0, 'Pond', 1, ?, 0, 0, 0)
    """, (user_id, start_date))
    conn.commit()

    await ctx.send(f"🌊 {ctx.author.mention}, your fishing adventure has begun! Type `{voltify_prefix}help` for available commands.")

@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def testfish(ctx):
    """Catch a random fish."""
    user_id = ctx.author.id

    # Ensure player has started
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        await ctx.send(f"❌ You haven't started your fishing adventure! Use {voltify_prefix}start to begin.")
        return

    # Determine rarity and fish
    rarity = determine_rarity()
    fish = random.choice(fish_tiers[rarity])

    # Generate fish stats
    weight = random.randint(0, 25)
    length = random.randint(0, 25)
    aura = random.randint(0, 25)
    radiance = random.randint(0, 25)

    ivs_num = weight + length + aura + radiance
    total_possible_value = 25 * 4
    ivs = (ivs_num / total_possible_value) * 100  # Calculate the IVs as a percentage

    # Generate random level for the fish
    level = random.randint(1, 100)

    # Insert fish into the database
    cursor.execute("""
        INSERT INTO catches (user_id, fish_name, rarity, ivs, level) 
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, fish, rarity, round(ivs), level))
    conn.commit()

    fish_id = cursor.lastrowid

    fishingprogress = discord.Embed(title="You cast your rod...",
                                    colour=0x5697a9,
                                    timestamp=datetime.now())
    fishingprogress.set_image(url="https://i.imgur.com/NAvT1Dz.gif")
    fishingprogress.set_footer(text=f"{ctx.author.name}",
                               icon_url=f"{ctx.author.avatar.url}")

    # Send the fishing progress message
    message = await ctx.send(embed=fishingprogress)

    # Random chance to encounter a shark
    chance = random.randint(1, 1)
    if chance == 1:
        # Start the shark encounter
        await asyncio.sleep(1)  # Brief fishing animation

        class SharkButton(Button):
            def __init__(self, max_clicks):
                super().__init__(label="Fight the Shark!", style=ButtonStyle.danger, emoji='🦈')
                self.clicks = 0
                self.max_clicks = max_clicks
                self.tracking_task = self.track_clicks.start()

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("This isn't your shark to fight!", ephemeral=True)
                    return
                await interaction.response.defer()
                self.clicks += 1
                if self.clicks >= self.max_clicks:
                    fishresults = discord.Embed(
                    title=f"You caught a {fish}!",
                    description=f"Rarity: {rarity}\nLevel: {level}\nPurity: {round(ivs)}%",
                    colour=0x5697a9,
                    timestamp=datetime.now()
                    )
                    fishresults.set_footer(text=f"{ctx.author.name} | Fish ID: {fish_id}",
                               icon_url=f"{ctx.author.avatar.url}")
                    fishresults.set_thumbnail(url="https://i.imgur.com/k4arBG7.png")
                    self.fishresults = fishresults
                    self.message = interaction.message
                    # Successfully defeated the shark
                    self.disabled = True
                    await interaction.response.edit_message(
                        embed=fishresults,
                        view=None
                    )
                    self.view.stop()  # End the interaction
            
            @tasks.loop(seconds=0.1)  # Adjust the interval as needed
            async def track_clicks(self):
                if self.clicks >= self.max_clicks:
                    self.tracking_task.cancel()  # Stop the task
                    # Handle successful shark defeat
                    await self.message.edit(embed=self.fishresults, view=None)
                    self.view.stop()
                elif self.view.is_finished():  # Check if the view has timed out
                    self.tracking_task.cancel()
                    # Handle timeout logic
                    timeout_embed=discord.Embed(
                        title="🪦 You lost your battle to the shark!",
                        description="You lost your catch, and you cannot fish for another 5 minutes.",
                        colour=0xff0000
                    )
                    await self.message.edit(embed=timeout_embed, view=None)
                    # Apply cooldown penalty
                else:
                    await asyncio.sleep(0.1)  # Yield control to avoid blocking

        class StartSharkView(View):
            def __init__(self, max_clicks):
                super().__init__(timeout=5)  # Shark encounter lasts 5 seconds
                self.shark_button = SharkButton(max_clicks)
                self.add_item(self.shark_button)

            async def on_timeout(self):
                # If the user doesn't click enough times within 5 seconds
                if self.shark_button.clicks < self.shark_button.max_clicks:
                    await message.edit(
                        embed=discord.Embed(
                            title="🪦 You lost your battle to the shark!",
                            description="You lost your catch, and you cannot fish for another 5 minutes.",
                            colour=0xff0000
                        ),
                        view=None
                    )
                    # Apply a 5-minute cooldown manually
                    ctx.command.reset_cooldown(self.ctx)
                    ctx.command._buckets._cooldown = commands.Cooldown(1, 300)
                    
        # Random number of clicks needed to defeat the shark
        max_clicks = random.randint(1, 3)
        
        # Shark encounter embed
        fishingshark = discord.Embed(
            title="Oh no! A shark is coming!",
            description=f"Click the button {max_clicks} times to kill it!",
            colour=0x5697a9
        )
        fishingshark.set_image(url="https://i.imgur.com/x86d5X2.gif")
        fishingshark.set_footer(text=f"{ctx.author.name}",
                                icon_url=f"{ctx.author.avatar.url}")

        # Send the shark encounter message
        await message.edit(embed=fishingshark, view=StartSharkView(max_clicks))
    else:
        # Wait 5 seconds before editing the message with the final result
        await asyncio.sleep(5)

        # Create the fish caught message with fish ID
        fishresults = discord.Embed(
            title=f"You caught a {fish}!",
            description=f"Rarity: {rarity}\nLevel: {level}\nPurity: {round(ivs)}%",
            colour=0x5697a9,
            timestamp=datetime.now()
        )
        fishresults.set_footer(text=f"{ctx.author.name} | Fish ID: {fish_id}",
                               icon_url=f"{ctx.author.avatar.url}")
        fishresults.set_thumbnail(url="https://i.imgur.com/k4arBG7.png")

        # Edit the message with the final result (caught fish details)
        await message.edit(embed=fishresults)

@testfish.error
async def fish_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining_time = int(error.retry_after)
        embed = discord.Embed(
            title="⏳| Cooldown!",
            description=f"You need to wait {remaining_time}s before fishing again!",
            colour=0x5697a9
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(remaining_time)
        await message.delete()

@bot.hybrid_command(aliases=["bag", "inv", "inventory"])
async def bucket(ctx):
    """Display fish collection with pagination."""
    user_id = ctx.author.id

    # Query to get the fish collection for the user, sorted by fish_id in ascending order
    cursor.execute("SELECT fish_id, fish_name, rarity, ivs, level FROM catches WHERE user_id = ? ORDER BY fish_id ASC", (user_id,))
    fish_collection = cursor.fetchall()

    if not fish_collection:
        await ctx.send(f"🐟 {ctx.author.mention}, your bucket is empty! Try fishing with `{voltify_prefix}fish`.")
        return

    # Constants
    items_per_page = 10
    total_pages = math.ceil(len(fish_collection) / items_per_page)

    # Function to create an embed for a specific page
    def create_embed(page):
        embed = discord.Embed(title=f"🐟 {ctx.author.name}'s Bucket", color=discord.Color.blue())
        start_index = page * items_per_page
        end_index = start_index + items_per_page
        for fish_id, fish_name, rarity, ivs, level in fish_collection[start_index:end_index]:
            embed.add_field(name=f"`{fish_id}` | {fish_name}", value=f"{rarity} | L{level}, {ivs}%", inline=False)
        embed.set_footer(text=f"Page {page + 1}/{total_pages}")
        return embed

    # Start with the first page
    current_page = 0
    message = await ctx.send(embed=create_embed(current_page))

    # Add reactions for pagination
    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        # Check function for reaction events
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        # Handle reactions
        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=create_embed(current_page))
                elif str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                    current_page += 1
                    await message.edit(embed=create_embed(current_page))

                # Remove the user's reaction to keep the message clean
                await message.remove_reaction(reaction.emoji, user)
            except asyncio.TimeoutError:
                # Remove reactions after timeout
                await message.clear_reactions()
                break

@bot.command()
async def sell(ctx, fish_id: int):
    user_id = ctx.author.id
    
    # Check if the fish exists and belongs to the user
    cursor.execute(
        "SELECT fish_name, rarity FROM catches WHERE user_id = ? AND fish_id = ?",
        (user_id, fish_id)
    )
    result = cursor.fetchone()
    
    if result:
        fish_name, rarity = result
        sell_price = {"Common": 2, "Uncommon": 5, "Rare": 10, "Epic": 30, "Legendary": 100, "Mythical": 1000}[rarity]
        
        # Update user's coins and remove the fish
        cursor.execute("UPDATE players SET coins = coins + ? WHERE user_id = ?", (sell_price, user_id))
        cursor.execute("DELETE FROM catches WHERE user_id = ? AND fish_id = ?", (user_id, fish_id))
        conn.commit()
        
        sellembed = discord.Embed(title=f"You sold your {fish_name}!",
                      description=f"Your {fish_name} (ID:{fish_id}) was successfully sold for {sell_price} sparks!",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        sellembed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        
        await ctx.send(embed=sellembed)
    else:
        await ctx.send(f"❌ | {ctx.author.mention}, no fish with ID {fish_id} found.")

@bot.hybrid_command(aliases=["upgrade"])
async def upgrade_rod(ctx):
    """Upgrade fishing rod"""
    user_id = ctx.author.id

    # Get player's current rod level and coins
    cursor.execute("SELECT rod_level, coins FROM players WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        rod_level, coins = result

        # Define the upgrade costs based on levels
        upgrade_costs = {
            1: 50,
            2: 100,
            3: 250,
            4: 500,
            5: 1000
        }
        
        # Get the upgrade cost for the current level
        cost = upgrade_costs.get(rod_level, None)  # None if the level exceeds the defined costs
        
        if cost is None:
            await ctx.reply(f"❌ | Woah! Your rod is already at the maximum level.")
            return

        if coins >= cost:
            # Deduct coins and upgrade rod
            cursor.execute("UPDATE players SET rod_level = rod_level + 1, coins = coins - ? WHERE user_id = ?", (cost, user_id))
            conn.commit()
            rod_level += 1
            upgradeembed = discord.Embed(title="You upgraded your rod!",
                      description=f"You paid {cost} sparks and \nupgraded your rod to Level\n{rod_level}!",
                      colour=0x5697a9,
                      timestamp=datetime.now())
            upgradeembed.set_thumbnail(url="https://i.imgur.com/rgPJiCK.gif")
            upgradeembed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
            await ctx.reply(embed=upgradeembed)
        else:
            await ctx.reply(f"❌ | You need {cost} sparks to upgrade your rod.")
    else:
        await ctx.reply(f"❌ | You haven't started fishing! Use `{voltify_prefix}start` to begin.")

@bot.hybrid_command()
async def stats(ctx):
    """Displays your fishing stats including start date."""
    user_id = ctx.author.id

    # Ensure the player exists in the database
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player:
        await ctx.send(f"❌ You haven't started your fishing adventure! Use `{voltify_prefix}start` to begin.")
        return

    # Extract player data
    coins = player[1]  # Coins are stored as the 2nd column
    unlocked_locations = player[2]  # Locations are the 3rd column
    rod_level = player[3]  # Rod level is the 4th column
    start_date = player[4]  # Start date is the 5th column
    total_fish = player[5]  # Total fish caught (6th column)
    total_caught = player[6]  # Total times fished (7th column)
    total_spent = player[7]  # Total money spent (8th column)

    # Create the stats message
    stats_message = (
        f"📊 **{ctx.author.mention}'s Fishing Stats:**\n"
        f"💰 **Coins**: {coins}\n"
        f"🌍 **Unlocked Locations**: {unlocked_locations}\n"
        f"🎣 **Rod Level**: {rod_level}\n"
        f"🐟 **Total Fish Caught**: {total_fish}\n"
        f"🔨 **Total Fishing Attempts**: {total_caught}\n"
        f"💸 **Total Spent**: {total_spent} coins\n"
        f"📅 **Started On**: {start_date}\n"
    )

    await ctx.send(stats_message)

@bot.hybrid_command(aliases=["lb"])
async def leaderboard(ctx):
    """Display coin leaderboard"""
    cursor.execute("SELECT user_id, coins FROM players ORDER BY coins DESC LIMIT 10")
    leaderboard = cursor.fetchall()

    if leaderboard:
        leaderboard_text = "\n".join(
            [f"{i+1}. <@{user_id}> - 💰 {coins} coins" for i, (user_id, coins) in enumerate(leaderboard)]
        )
        await ctx.send(f"🏆 **Fishing Leaderboard** 🏆\n{leaderboard_text}")
    else:
        await ctx.send(f"❌ No players on the leaderboard yet. Start fishing with `{voltify_prefix}fish`!")

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        """Display the main help menu."""
        embed = discord.Embed(
            title="Voltify Commands",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )
        
        for cog, commands in mapping.items():
            # Filter commands that the user can run and have descriptions
            command_list = [
                f"`{self.context.clean_prefix}{cmd.name}` - {cmd.short_doc or 'No description available.'}"
                for cmd in commands if await self.filter_commands([cmd])
            ]
            if command_list:
                embed.add_field(
                    name=cog.qualified_name if cog else "No Category",
                    value="\n".join(command_list),
                    inline=False
                )
        
        # Send the embed
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        """Display help for a specific command."""
        embed = discord.Embed(
            title=f"Help: {self.context.clean_prefix}{command.name}",
            description=command.short_doc or "No description available.",
            color=discord.Color.green()
        )
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        if command.usage:
            embed.add_field(name="Usage", value=f"`{self.context.clean_prefix}{command.name} {command.usage}`", inline=False)

        # Send the embed
        channel = self.get_destination()
        await channel.send(embed=embed)

# Replace the bot's help command with the custom one
bot.help_command = CustomHelpCommand()

@bot.hybrid_command()
async def reset(ctx, user: discord.Member = None):
    """Resets a user's fishing data. If no user is mentioned, it resets the calling user."""
    
    # If no user is provided, use the author (the person who called the command)
    if user is None:
        user = ctx.author  # Defaults to the author if no mention

    user_id = user.id

    # Ensure the player exists in the database
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    
    if not player:
        await ctx.send(f"❌ {user.mention} hasn't started their fishing adventure! Use `{voltify_prefix}start` to begin.")
        return

    # Reset the user's fish bag, balance, and stats
    cursor.execute("DELETE FROM catches WHERE user_id = ?", (user_id,))  # Clear fish bag
    cursor.execute(""" 
    UPDATE players 
    SET coins = 0, total_fish = 0, total_caught = 0, total_spent = 0 
    WHERE user_id = ? 
    """, (user_id,))

    # Reset the auto-increment sequence for the catches table (for this user)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'catches';")
    
    # Commit the changes to the database
    conn.commit()

    await ctx.send(f"🔄 {user.mention}'s fishing data has been reset!")
    
@bot.hybrid_group(invoke_without_command=True)
# this is where i get the error. im assuming i did smth wrong here?
async def admin(ctx):
    """Shows admin commands"""
    # Admin Command Embed Template: https://embed.dan.onl/?data=eyJhdXRob3IiOnsibmFtZSI6IlZvbHRpZnkgQWRtaW4gQ29tbWFuZHMgfCB7Y29tbWFuZF9uYW1lfSIsImljb25VcmwiOiJodHRwczovL2kuaW1ndXIuY29tLzJVenhlbEYuanBlZyJ9LCJ0aXRsZSI6IkFkZGVkIHthZGRhbW91bnR9IHNwYXJrcyB0byB7dXNlcm5hbWV9IiwiZGVzY3JpcHRpb24iOiJUaGVpciBmaW5hbCBiYWxhbmNlIGlzIHtmaW5hbGJhbH0gc3BhcmtzLiIsImNvbG9yIjoiIzAwYjBmNCIsImZvb3RlciI6eyJ0ZXh0Ijoie2N0eC5hdXRob3IubmFtZX0iLCJpY29uVXJsIjoie2N0eC5hdXRob3IuYXZhdGFyLnVybH0ifSwidGltZXN0YW1wIjoxNzMyNzMyNDkwMDQ3fQ%3D%3D
    if ctx.invoked_subcommand is None:
        help_text = (
        "Admin Commands:\n"
        "`*admin add <amount> <user>` - Add sparks to a user.\n"
        "`*admin addall <amount>` - Add sparks to a all players.\n"
        "`*admin remove <amount> <user>` - Remove sparks from a user.\n"
        "`*admin removeall <amount>` - Remove sparks from all players.\n"
        "`*admin clearsparks` - Reset all player's sparks.\n"
        "`*admin reset <user>` - Reset all data of a user.\n"
        "`*admin suspend <user> <reason> <duration>` - Suspend a user from the bot.\n"
        "`*admin unsuspend <user> <reason>` - Unsuspend a user from the bot.\n"
        "`*admin upgrade <amount> <user>` - Upgrade the rod of a user.\n"
        "`*admin gearall <gear> <duration>` - Give everyone gear effects for a specified time.\n"
        "`*admin info <user>` - View profile of a user.\n"
        "`*admin addfishadvanced <fish> <weight> <length> <aura> <radiance> <user> <shiny>` - Adds a fish to a user with specified stats.\n"
        "`*admin addfishbasic <fish> <stats> <user> <shiny>` - Adds a fish to a user with random stats from a set total."
        "`*admin delfish <ID> <user>` - Removes a specified fish from a user."
    )
    await ctx.reply(help_text)
    
@admin.hybrid_command()
@app_commands.describe(
    addamount="The amount of sparks to add",
    user="The user to receive the sparks (optional, default = you)"
)
async def add(ctx, addamount: int, user: discord.Member = None):
    if user is None:
        user = ctx.author
    user_id = user.id
    discorduser = bot.get_user(user_id)
    username = discorduser.name
    command_name = ctx.command.name
    cursor.execute("SELECT coins FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    if not player:
        embed = discord.Embed(title="You haven't started fishing!",
                      description=f"Use `{voltify_prefix}start` to begin.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    coins = player[0]
    cursor.execute("UPDATE players SET coins = coins + ? WHERE user_id = ?", (addamount, user_id))
    conn.commit()
    finalbal = coins + addamount
    embed = discord.Embed(title=f"Added {addamount} sparks to {username}",
                      description=f"Their final balance is {finalbal} sparks.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)

bot.run(TOKEN)
