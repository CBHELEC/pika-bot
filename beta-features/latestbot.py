from discord.ext import tasks
import asyncio
import discord
from discord.ext import commands
import os
import sqlite3
import random
from datetime import datetime, timedelta
import math
from discord import ButtonStyle, app_commands
from discord.ui import Button, View
import re

from dotenv import load_dotenv
load_dotenv(".env")
TOKEN = os.getenv('BOT_TOKEN')
VOLTIFY_GUILD = os.getenv('VOLTIFY_GUILD')
#ADMIN_USER_ID = os.getenv('ADMIN_USER')
ADMIN_USER_ID = int("820297275448098817")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='v.', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------------------------')
    await bot.tree.sync()
    ensure_columns_exist_players()
    ensure_columns_exist_catches()
    bot.loop.create_task(check_expired_suspensions())
    await bot.change_presence(
        activity=discord.CustomActivity(f"Being Cute <3"))

voltify_prefix = "v."

# User Isn't Player Embed: https://embed.dan.onl/?data=eyJ0aXRsZSI6IllvdSBoYXZlbid0IHN0YXJ0ZWQgZmlzaGluZyEiLCJkZXNjcmlwdGlvbiI6IlVzZSBge3ZvbHRpZnlfcHJlZml4fXN0YXJ0YCB0byBiZWdpbi4iLCJjb2xvciI6IiMwMGIwZjQiLCJmb290ZXIiOnsidGV4dCI6IntjdHguYXV0aG9yLm5hbWV9IiwiaWNvblVybCI6IntjdHguYXV0aG9yLmF2YXRhci51cmx9In0sInRpbWVzdGFtcCI6MTczMjczMjcyNDU4MX0%3D

@bot.command()
async def uwu(ctx):
    await ctx.send("uwu")
    
##############################################################################################################################################################################################

def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    return datetime.fromisoformat(s.decode('utf-8'))

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

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
    total_spent INTEGER DEFAULT 0,
    suspended INTEGER NOT NULL DEFAULT 0,
    suspension_reason TEXT DEFAULT 'No reason provided',
    suspension_end INTEGER
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

# Suspension History
cursor.execute("""
CREATE TABLE IF NOT EXISTS suspension_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    suspension_reason TEXT NOT NULL,
    suspension_start TIMESTAMP NOT NULL,
    suspension_end TIMESTAMP,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def ensure_columns_exist_suspension_history():
    expected_columns = [
        "id", "user_id", "username", "suspension_reason", "suspension_start", "suspension_end", "logged_at"
    ]

    cursor.execute("PRAGMA table_info(suspension_history)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "logged_at" not in columns:
        cursor.execute("""
        DROP TABLE IF EXISTS suspension_history;
        """)
        cursor.execute("""
        CREATE TABLE suspension_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            suspension_reason TEXT NOT NULL,
            suspension_start TIMESTAMP NOT NULL,
            suspension_end TIMESTAMP,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    
    for column in expected_columns:
        if column not in columns:
            if column == "id":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT""")
            if column == "user_id":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN user_id INTEGER NOT NULL""")
            elif column == "username":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN username TEXT NOT NULL""")
            elif column == "suspension_reason":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN suspension_reason TEXT NOT NULL""")
            elif column == "suspension_start":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN suspension_start TIMESTAMP NOT NULL""")
            elif column == "suspension_end":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN suspension_end TIMESTAMP""")
            elif column == "logged_at":
                cursor.execute("""ALTER TABLE suspension_history ADD COLUMN logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP""")

    conn.commit()

def ensure_columns_exist_players():
    expected_columns = [
        "user_id", "coins", "unlocked_locations", "rod_level", 
        "start_date", "total_fish", "total_caught", "total_spent", "suspended", "suspension_reason", "suspension_end"
    ]
    
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
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
            elif column == "suspended":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN suspended INTEGER NOT NULL DEFAULT 0
                """)
            elif column == "suspension_reason":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN suspension_reason TEXT DEFAULT 'No reason provided'
                """)
            elif column == "suspension_end":
                cursor.execute("""
                ALTER TABLE players ADD COLUMN suspension_end INTEGER
                """)
    
    conn.commit()

def ensure_columns_exist_catches():
    expected_columns = [
        "user_id", "fish_name", "rarity", "fish_id", "ivs", "level"
    ]

    cursor.execute("PRAGMA table_info(catches)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "fish_id" not in columns:
        cursor.execute("""
        DROP TABLE IF EXISTS catches;
        """)
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
    roll = random.uniform(0, 127)

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

def check_suspension():
    async def predicate(ctx):
        cursor.execute("SELECT suspended, suspension_reason FROM players WHERE user_id = ?", (ctx.author.id,))
        player = cursor.fetchone()
        if player and player[0] == 1:
            reason = player[1] if player[1] else "No reason provided"
            raise commands.CheckFailure(reason)
        return True
    return commands.check(predicate)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        reason = str(error) if str(error) else "No reason provided"
        # https://embed.dan.onl/?data=eyJhdXRob3IiOnsibmFtZSI6IlZvbHRpZnkgQWRtaW4gQ29tbWFuZHMgfCBzdXNwZW5kIiwiaWNvblVybCI6Imh0dHBzOi8vaS5pbWd1ci5jb20vMlV6eGVsRi5qcGVnIn0sInRpdGxlIjoiWW91IGFyZSBzdXNwZW5kZWQgZnJvbSBWb2x0aWZ5ISIsImRlc2NyaXB0aW9uIjoiWW91IGhhdmUgYmVlbiBmb3VuZCBndWlsdHkgb2YgYnJlYWtpbmcgdGhlIHJ1bGVzLCBhbmQgaGF2ZSBiZWVuIGJsYWNrbGlzdGVkIGZyb20gdXNpbmcgdGhlIGJvdC5cbioqUmVhc29uKio6IFxue3JlYXNvbn1cbioqQXBwZWFscyoqOlxuSWYgeW91IGJlbGlldmUgeW91IHdlcmUgZmFsc2VseSBzdXNwZW5kZWQgYW5kIHdvdWxkIGxpa2UgdG8gYXBwZWFsIHlvdXIgc3VzcGVuc2lvbiwgcGxlYXNlIG1ha2UgYSB0aWNrZXQgaW4gdGhlIFtvZmZpY2lhbCBzZXJ2ZXJdKGh0dHBzOi8vZGlzY29yZC5nZy84RGJScnFLZkN4KS4iLCJjb2xvciI6IiMwMGIwZjQiLCJmb290ZXIiOnsidGV4dCI6IlZvbHRpZnkgQWRtaW4gVGVhbSIsImljb25VcmwiOiJodHRwczovL2kuaW1ndXIuY29tLzJVenhlbEYuanBlZyJ9LCJ0aW1lc3RhbXAiOjE3MzI3MzI0OTAwNDd9
        embed = discord.Embed(
            title="You are suspended from Voltify!",
            description=(
                f"You have been found guilty of breaking the rules and have been blacklisted from using the bot.\n"
                f"**Reason**: \n{reason}\n"
                f"**Appeals**:\nIf you believe you were falsely suspended and would like to appeal your suspension, "
                f"please make a ticket in the [official server](https://discord.gg/8DbRrqKfCx)."
            ),
            colour=0x5697a9,
            timestamp=datetime.now()
        )
        embed.set_author(name="Voltify Admin Commands | suspend", icon_url="https://i.imgur.com/2UzxelF.jpeg")
        embed.set_footer(text="Voltify Admin Team", icon_url="https://i.imgur.com/2UzxelF.jpeg")
        await ctx.send(embed=embed)

@bot.command()
@check_suspension()
async def start(ctx):
    """Starts your fishing adventure."""
    user_id = ctx.author.id
    start_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        await ctx.send(f"❌ {ctx.author.mention}, you have already started your fishing adventure!")
        return
    
    cursor.execute("""
    INSERT INTO players (user_id, coins, unlocked_locations, rod_level, start_date, total_fish, total_caught, total_spent)
    VALUES (?, 0, 'Pond', 1, ?, 0, 0, 0)
    """, (user_id, start_date))
    conn.commit()

    await ctx.send(f"🌊 {ctx.author.mention}, your fishing adventure has begun! Type `{voltify_prefix}help` for available commands.")

@bot.command()
@check_suspension()
@commands.cooldown(1, 15, commands.BucketType.user)
async def fish(ctx):
    """Catch a random fish."""
    user_id = ctx.author.id

    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        await ctx.send(f"❌ You haven't started your fishing adventure! Use {voltify_prefix}start to begin.")
        return

    rarity = determine_rarity()
    fish = random.choice(fish_tiers[rarity])

    weight = random.randint(0, 25)
    length = random.randint(0, 25)
    aura = random.randint(0, 25)
    radiance = random.randint(0, 25)

    ivs_num = weight + length + aura + radiance
    total_possible_value = 25 * 4
    ivs = (ivs_num / total_possible_value) * 100

    level = random.randint(1, 100)

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

    message = await ctx.send(embed=fishingprogress)

    chance = random.randint(1, 100)
    if chance == 100:
        await asyncio.sleep(5)

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
                    self.disabled = True
                    await interaction.edit_original_response(
                        embed=fishresults,
                        view=None
                    )
                    self.view.stop()
            
            @tasks.loop(seconds=0.1) 
            async def track_clicks(self):
                if self.clicks >= self.max_clicks:
                    self.tracking_task.cancel()
                    await self.message.edit(embed=self.fishresults, view=None)
                    self.view.stop()
                elif self.view.is_finished(): 
                    self.tracking_task.cancel()
                    timeout_embed=discord.Embed(
                        title="🪦 You lost your battle to the shark!",
                        description="You lost your catch, and you cannot fish for another 5 minutes.",
                        colour=0xff0000
                    )
                    await self.message.edit(embed=timeout_embed, view=None)
                else:
                    await asyncio.sleep(0.1)

        class StartSharkView(View):
            def __init__(self, max_clicks):
                super().__init__(timeout=5)
                self.shark_button = SharkButton(max_clicks)
                self.add_item(self.shark_button)

            async def on_timeout(self):
                if self.shark_button.clicks < self.shark_button.max_clicks:
                    await message.edit(
                        embed=discord.Embed(
                            title="🪦 You lost your battle to the shark!",
                            description="You lost your catch, and you cannot fish for another 5 minutes.",
                            colour=0xff0000
                        ),
                        view=None
                    )
                    ctx.command.reset_cooldown(self.ctx)
                    ctx.command._buckets._cooldown = commands.Cooldown(1, 300)

        max_clicks = random.randint(1, 3)

        fishingshark = discord.Embed(
            title="Oh no! A shark is coming!",
            description=f"Click the button {max_clicks} times to kill it!",
            colour=0x5697a9
        )
        fishingshark.set_image(url="https://i.imgur.com/x86d5X2.gif")
        fishingshark.set_footer(text=f"{ctx.author.name}",
                                icon_url=f"{ctx.author.avatar.url}")

        await message.edit(embed=fishingshark, view=StartSharkView(max_clicks))
    else:
        await asyncio.sleep(5)

        fishresults = discord.Embed(
            title=f"You caught a {fish}!",
            description=f"Rarity: {rarity}\nLevel: {level}\nPurity: {round(ivs)}%",
            colour=0x5697a9,
            timestamp=datetime.now()
        )
        fishresults.set_footer(text=f"{ctx.author.name} | Fish ID: {fish_id}",
                               icon_url=f"{ctx.author.avatar.url}")
        fishresults.set_thumbnail(url="https://i.imgur.com/k4arBG7.png")

        await message.edit(embed=fishresults)

@fish.error
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
@check_suspension()
async def bucket(ctx):
    """Display fish collection with pagination."""
    user_id = ctx.author.id

    cursor.execute("SELECT fish_id, fish_name, rarity, ivs, level FROM catches WHERE user_id = ? ORDER BY fish_id ASC", (user_id,))
    fish_collection = cursor.fetchall()

    if not fish_collection:
        await ctx.send(f"🐟 {ctx.author.mention}, your bucket is empty! Try fishing with `{voltify_prefix}fish`.")
        return

    items_per_page = 10
    total_pages = math.ceil(len(fish_collection) / items_per_page)

    def create_embed(page):
        embed = discord.Embed(title=f"🐟 {ctx.author.name}'s Bucket", color=discord.Color.blue())
        start_index = page * items_per_page
        end_index = start_index + items_per_page
        for fish_id, fish_name, rarity, ivs, level in fish_collection[start_index:end_index]:
            embed.add_field(name=f"`{fish_id}` | {fish_name}", value=f"{rarity} | L{level}, {ivs}%", inline=False)
        embed.set_footer(text=f"Page {page + 1}/{total_pages}")
        return embed

    current_page = 0
    message = await ctx.send(embed=create_embed(current_page))

    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "⬅️" and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=create_embed(current_page))
                elif str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                    current_page += 1
                    await message.edit(embed=create_embed(current_page))

                await message.remove_reaction(reaction.emoji, user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

@bot.command()
@check_suspension()
async def sell(ctx, fish_id: int):
    user_id = ctx.author.id
    
    cursor.execute(
        "SELECT fish_name, rarity FROM catches WHERE user_id = ? AND fish_id = ?",
        (user_id, fish_id)
    )
    result = cursor.fetchone()
    
    if result:
        fish_name, rarity = result
        sell_price = {"Common": 2, "Uncommon": 5, "Rare": 10, "Epic": 30, "Legendary": 100, "Mythical": 1000}[rarity]
        
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
@check_suspension()
async def upgrade_rod(ctx):
    """Upgrade fishing rod"""
    user_id = ctx.author.id

    cursor.execute("SELECT rod_level, coins FROM players WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        rod_level, coins = result

        upgrade_costs = {
            1: 50,
            2: 100,
            3: 250,
            4: 500,
            5: 1000
        }
        
        cost = upgrade_costs.get(rod_level, None)
        
        if cost is None:
            await ctx.reply(f"❌ | Woah! Your rod is already at the maximum level.")
            return

        if coins >= cost:
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
@check_suspension()
async def stats(ctx):
    """Displays your fishing stats including start date."""
    user_id = ctx.author.id

    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player:
        await ctx.send(f"❌ You haven't started your fishing adventure! Use `{voltify_prefix}start` to begin.")
        return

    coins = player[1]  
    unlocked_locations = player[2] 
    rod_level = player[3]  
    start_date = player[4] 
    total_fish = player[5] 
    total_caught = player[6]  
    total_spent = player[7] 

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
@check_suspension()
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

        channel = self.get_destination()
        await channel.send(embed=embed)

bot.help_command = CustomHelpCommand()

@bot.hybrid_group(invoke_without_command=True)
async def admin(ctx):
    """Shows admin commands"""
    # Admin Command Embed Template: https://embed.dan.onl/?data=eyJhdXRob3IiOnsibmFtZSI6IlZvbHRpZnkgQWRtaW4gQ29tbWFuZHMgfCB7Y29tbWFuZF9uYW1lfSIsImljb25VcmwiOiJodHRwczovL2kuaW1ndXIuY29tLzJVenhlbEYuanBlZyJ9LCJ0aXRsZSI6IkFkZGVkIHthZGRhbW91bnR9IHNwYXJrcyB0byB7dXNlcm5hbWV9IiwiZGVzY3JpcHRpb24iOiJUaGVpciBmaW5hbCBiYWxhbmNlIGlzIHtmaW5hbGJhbH0gc3BhcmtzLiIsImNvbG9yIjoiIzAwYjBmNCIsImZvb3RlciI6eyJ0ZXh0Ijoie2N0eC5hdXRob3IubmFtZX0iLCJpY29uVXJsIjoie2N0eC5hdXRob3IuYXZhdGFyLnVybH0ifSwidGltZXN0YW1wIjoxNzMyNzMyNDkwMDQ3fQ%3D%3D
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if ctx.invoked_subcommand is None:
        help_text = (
        "Admin Commands:\n"
        "`*admin add <amount> <user>` - Add sparks to a user.\n"
        "`*admin addall <amount>` - Add sparks to a all players.\n"
        "`*admin remove <amount> <user>` - Remove sparks from a user.\n"
        "`*admin removeall <amount>` - Remove sparks from all players.\n"
        "`*admin setall <amount>` - Set all player's sparks to an amount.\n"
        "`*admin clearsparks` - Resets everyone's balances to 0.\n"
        "`*admin clearbal` - Reset all sparks of a specified user.\n"
        "`*admin reset <user>` - Reset all data of a user.\n"
        "`*admin suspend <user> <reason> <duration>` - Suspend a user from the bot.\n"
        "`*admin unsuspend <user> <reason>` - Unsuspend a user from the bot.\n"
        "`*admin upgrade <amount> <user>` - Upgrade the rod of a user.\n"
        "`*admin gearall <gear> <duration>` - Give everyone gear effects for a specified time.\n"
        "`*admin info <user>` - View profile of a user.\n"
        "`*admin addfishadvanced <fish> <weight> <length> <aura> <radiance> <user> <shiny>` - Adds a fish to a user with specified stats.\n"
        "`*admin addfishbasic <fish> <stats> <user> <shiny>` - Adds a fish to a user with random stats from a set total.\n"
        "`*admin delfish <ID> <user>` - Removes a specified fish from a user."
    )
    await ctx.reply(help_text)
    
@admin.command()
@app_commands.describe(
    addamount="The amount of sparks to add",
    user="The user to receive the sparks (optional, default = you)"
)
async def add(ctx, addamount: int, user: discord.Member = None):
    """
    Add sparks to a user.
    """
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if addamount < 0:
        await ctx.reply("Please enter a positive number to add.", ephemeral=True)
        return
    if user is None:
        user = ctx.author
    user_id = user.id
    discorduser = bot.get_user(user_id)
    username = discorduser.name
    command_name = ctx.command.name
    cursor.execute("SELECT coins FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    if not player:
        embed = discord.Embed(title="That user hasn't started fishing!",
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
    await bot.get_channel(1312150369396195338).send(embed=embed)
    
@admin.command()
@app_commands.describe(
    addamount="The amount of sparks to add to all players",
)
async def addall(ctx, addamount: int):
    """
    Add sparks to all players.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    command_name = ctx.command.name
    
    if addamount < 0:
        await ctx.send("Please enter a positive number to add.", ephemeral=True)
        return

    cursor.execute("UPDATE players SET coins = coins + ?", (addamount,))
    conn.commit()

    playeramount = cursor.rowcount
    
    embed = discord.Embed(title=f"Added {addamount} sparks to all players",
                      description=f"Added {addamount} sparks to {playeramount} players.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)
    
@admin.command()
@app_commands.describe(
    remamount="The amount of sparks to remove",
    user="The user to remove the sparks from (optional, default = you)"
)
async def remove(ctx, remamount: int, user: discord.Member = None):
    """
    Remove sparks from a user.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if remamount < 0:
        await ctx.send("Please enter a positive number to remove.", ephemeral=True)
        return
    if user is None:
        user = ctx.author
    user_id = user.id
    discorduser = bot.get_user(user_id)
    username = discorduser.name
    command_name = ctx.command.name
    cursor.execute("SELECT coins FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    if not player:
        embed = discord.Embed(title="That user hasn't started fishing!",
                      description=f"Use `{voltify_prefix}start` to begin.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    coins = player[0]
    cursor.execute("UPDATE players SET coins = coins - ? WHERE user_id = ?", (remamount, user_id))
    conn.commit()
    finalbal = coins - remamount
    embed = discord.Embed(title=f"Removed {remamount} sparks from {username}",
                      description=f"Their final balance is {finalbal} sparks.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)

@admin.command()
@app_commands.describe(
    remamount="The amount of sparks to remove from all players",
)
async def removeall(ctx, remamount: int):
    """
    Remove sparks from all players.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    command_name = ctx.command.name
    
    if remamount < 0:
        await ctx.send("Please enter a positive number to remove.", ephemeral=True)
        return

    cursor.execute("UPDATE players SET coins = coins - ?", (remamount,))
    conn.commit()

    playeramount = cursor.rowcount
    
    embed = discord.Embed(title=f"Removed {remamount} sparks from all players",
                      description=f"Removed {remamount} sparks from {playeramount} players.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)

@admin.command()
@app_commands.describe(
    confirmation="Whether to proceed with the action",
)
async def clearsparks(ctx, confirmation: bool = None):
    """
    Resets everyone's balances to 0.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if confirmation is None:
        await ctx.reply("Please provide a confirmation value (True/False) to proceed with the action.")
        return

    command_name = ctx.command.name
    
    if confirmation:

        cursor.execute("UPDATE players SET coins = 0", ())
        conn.commit()

        playeramount = cursor.rowcount
    
        embed = discord.Embed(title=f"Set all players balances to 0",
                      description=f"Set balances to 0 for {playeramount} players.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        await bot.get_channel(1312150369396195338).send(embed=embed)
    
    else:
        await ctx.reply("Aborted. Please set the confirmation value to True then try again.")
        
@admin.command()
@app_commands.describe(
    setamount="The amount of sparks the user will have",
    user="The user to set the sparks for (optional, default = you)"
)
async def setsparks(ctx, setamount: int, user: discord.Member = None):
    """
    Set sparks for a user.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if setamount < 0:
        await ctx.send("Please enter a positive number to set.", ephemeral=True)
        return
    if user is None:
        user = ctx.author
    user_id = user.id
    discorduser = bot.get_user(user_id)
    username = discorduser.name
    command_name = ctx.command.name
    cursor.execute("SELECT coins FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    if not player:
        embed = discord.Embed(title="That user hasn't started fishing!",
                      description=f"Use `{voltify_prefix}start` to begin.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    coins = player[0]
    cursor.execute("UPDATE players SET coins = ? WHERE user_id = ?", (setamount, user_id))
    conn.commit()
    finalbal = setamount
    embed = discord.Embed(title=f"Set {setamount} sparks for {username}",
                      description=f"Their final balance is {finalbal} sparks.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)

@admin.command()
@app_commands.describe(
    setamount="The amount of sparks to set for all players",
)
async def setall(ctx, setamount: int):
    """
    Set sparks for all players.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    command_name = ctx.command.name
    
    if setamount < 0:
        await ctx.send("Please enter a positive number to set.", ephemeral=True)
        return

    cursor.execute("UPDATE players SET coins = ?", (setamount,))
    conn.commit()

    playeramount = cursor.rowcount
    
    embed = discord.Embed(title=f"Set {setamount} sparks for all players",
                      description=f"Set {setamount} sparks for {playeramount} players.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)

@admin.command()
@app_commands.describe(
    user="The user to reset the data of",
)
async def reset(ctx, user: discord.Member = None):
    """Resets a user's fishing data."""
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if user is None:
        user = ctx.author

    command_name = ctx.command.name

    user_id = user.id
    discorduser = bot.get_user(user_id)
    username = discorduser.name
    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    
    if not player:
        embed = discord.Embed(title="That user hasn't started fishing!",
                      description=f"Use `{voltify_prefix}start` to begin.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return

    cursor.execute("DELETE FROM catches WHERE user_id = ?", (user_id,))
    cursor.execute(""" 
    UPDATE players 
    SET coins = 0, total_fish = 0, total_caught = 0, total_spent = 0 
    WHERE user_id = ? 
    """, (user_id,))

    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'catches';")
    
    conn.commit()

    embed = discord.Embed(title=f"Reset {username}'s fishing data",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)
    
@admin.command()
@app_commands.describe(
    user="The user to clear (optional, default = you)"
)
async def clearbal(ctx, user: discord.Member = None):
    """
    Clear sparks for a user.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    if user is None:
        user = ctx.author
    user_id = user.id
    discorduser = bot.get_user(user_id)
    username = discorduser.name
    command_name = ctx.command.name
    cursor.execute("SELECT coins FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()
    if not player:
        embed = discord.Embed(title="That user hasn't started fishing!",
                      description=f"Use `{voltify_prefix}start` to begin.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    cursor.execute("UPDATE players SET coins = 0 WHERE user_id = ?", (user_id))
    conn.commit()
    embed = discord.Embed(title=f"Cleared balance for {username}",
                      description=f"Reset {username}'s balance to 0 sparks.",
                      colour=0x5697a9,
                      timestamp=datetime.now())

    embed.set_author(name=f"Voltify Admin Commands | {command_name}",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

    embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)

@admin.command()
@app_commands.describe(
    user="The user to suspend",
    reason="The reason for the suspension",
    duration="The suspension duration (eg. 10m, 1h, 2d. Optional -> Blank = Permanent)"
)
async def suspend(ctx, user: discord.Member, reason: str, duration: str = None):
    """
    Suspend a user from the bot.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    user_id = user.id
    username = user.name
    command_name = ctx.command.name

    cursor.execute("SELECT suspended, suspension_end, suspension_reason FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

    if player and player[0] == 1:
        if player[1]:
            embed = discord.Embed(
                title="Error: User Already Suspended",
                description=f"{username} is already suspended until <t:{int(player[1])}:F>.\n"
                            f"**Reason:** {player[2]}",
                colour=0x5697a9,
                timestamp=datetime.now()
            )
        else:
            embed = discord.Embed(
                title="Error: User Already Suspended",
                description=f"{username} is permanently suspended.\n"
                            f"**Reason:** {player[2]}",
                colour=0x5697a9,
                timestamp=datetime.now()
            )
    
        embed.set_footer(text=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")
        embed.set_author(
            name=f"Voltify Admin Commands | {command_name}",
            icon_url="https://i.imgur.com/2UzxelF.jpeg"
        )
        await ctx.reply(embed=embed)
        await bot.get_channel(1311750805358903318).send(embed=embed)
        return

    if duration:
        duration_seconds = parse_duration(duration)
        if duration_seconds is None:
            await ctx.reply("Invalid duration format. Use something like '10m', '1h', or '2d'.")
            return
        suspension_end = datetime.now() + timedelta(seconds=duration_seconds)
    else:
        suspension_end = None

    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player:
        embed = discord.Embed(
            title="You haven't started fishing!",
            description=f"Use `{voltify_prefix}start` to begin.",
            colour=0x5697a9,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return

    if suspension_end:
        discord_timestamp = f"{duration} (until <t:{int(suspension_end.timestamp())}:F>)"
    else:
        discord_timestamp = "Permanent"

    if suspension_end:
        cursor.execute("""
            UPDATE players 
            SET suspended = 1, suspension_reason = ?, suspension_end = ?
            WHERE user_id = ?
        """, (reason, int(suspension_end.timestamp()), user_id))
    else:
        cursor.execute("""
            UPDATE players 
            SET suspended = 1, suspension_reason = ?, suspension_end = NULL
            WHERE user_id = ?
        """, (reason, user_id))

    cursor.execute("""
        INSERT INTO suspension_history (user_id, username, suspension_reason, suspension_start, suspension_end)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, reason, datetime.now(), int(suspension_end.timestamp()) if suspension_end else None))

    conn.commit()

    embed = discord.Embed(
        title=f"Suspended {username} from Voltify",
        description=(
            f"**Reason:** {reason}\n"
            f"**Duration:** {discord_timestamp}"
        ),
        colour=0x5697a9,
        timestamp=datetime.now()
    )
    embed.set_author(
        name=f"Voltify Admin Commands | {command_name}",
        icon_url="https://i.imgur.com/2UzxelF.jpeg"
    )
    embed.set_footer(text=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")

    try:
        await ctx.reply(embed=embed)
        await user.send(embed=embed)
        await bot.get_channel(1312150369396195338).send(embed=embed)
    except discord.DiscordException:
        await bot.get_channel(1311750805358903318).send(f"Suspend | Failed to send a DM to user `{user_id}`. They may have DMs disabled or are not reachable.")

def parse_duration(duration: str):
    """
    Parse a duration string (e.g., '10m', '1h', '2d') into seconds.
    """
    match = re.match(r"(\d+)([smhd])", duration)
    if not match:
        return None

    time_value, unit = match.groups()
    time_value = int(time_value)

    if unit == "s":  # seconds
        return time_value
    elif unit == "m":  # minutes
        return time_value * 60
    elif unit == "h":  # hours
        return time_value * 3600
    elif unit == "d":  # days
        return time_value * 86400
    return None

async def check_expired_suspensions():
    """
    Periodically checks for expired suspensions and removes them.
    This function should run in the background to unsuspend users automatically.
    """
    while True:
        current_time = datetime.now()

        cursor.execute("""
            SELECT user_id, suspension_end, suspension_reason FROM players 
            WHERE suspended = 1 AND suspension_end IS NOT NULL
        """)
        players = cursor.fetchall()

        for player in players:
            user_id, suspension_end, suspension_reason = player

            if datetime.fromtimestamp(suspension_end) <= current_time:
                cursor.execute("""
                    UPDATE players 
                    SET suspended = 0, suspension_reason = NULL, suspension_end = NULL 
                    WHERE user_id = ?
                """, (user_id,))
                conn.commit()

                cursor.execute("""
                    INSERT INTO suspension_history (
                        user_id, username, suspension_reason, suspension_start, suspension_end
                    )
                    SELECT user_id, ?, suspension_reason, suspension_end - ?, suspension_end
                    FROM players
                    WHERE user_id = ?
                """, (None))

                try:
                    user = await bot.fetch_user(user_id)
                    if user:
                        embed = discord.Embed(
                            title="You have been unsuspended from Voltify",
                            description="Your suspension has expired and you have been unsuspended. You may continue using the bot.",
                            colour=0x5697a9,
                            timestamp=datetime.now()
                        )
                        embed.set_author(name="Voltify Admin Commands | Unsuspend",
                                         icon_url="https://i.imgur.com/2UzxelF.jpeg")
                        await user.send(embed=embed)

                        username = user.name
                        embed = discord.Embed(
                            title=f"{username} has been unsuspended from Voltify",
                            description=f"{username}'s suspension has expired and they have been unsuspended. They may continue using the bot.",
                            colour=0x5697a9,
                            timestamp=datetime.now()
                        )
                        embed.set_author(name="Voltify Admin Commands | Unsuspend",
                                         icon_url="https://i.imgur.com/2UzxelF.jpeg")
                        await bot.get_channel(1312150369396195338).send(embed=embed)
                except discord.DiscordException:
                    await bot.get_channel(1311750805358903318).send(
                        f"Unsuspend | Failed to send a DM to user `{user_id}`. They may have DMs disabled or are not reachable."
                    )

        await asyncio.sleep(5)

@admin.command()
@app_commands.describe(
    user="The user to unsuspend",
    reason="The reason for the unsuspension"
)
async def unsuspend(ctx, user: discord.Member, reason: str):
    """
    Unsuspend a user from the bot.
    """
    
    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return
    
    user_id = user.id
    username = user.name

    cursor.execute("SELECT suspended FROM players WHERE user_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player or player[0] == 0:
        embed = discord.Embed(title=f"{username} isn't suspended!",
                      colour=0x5697a9,
                      timestamp=datetime.now())

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return

    cursor.execute("""
        UPDATE players 
        SET suspended = 0, suspension_reason = NULL, suspension_end = NULL
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()

    current_time = datetime.now()

    cursor.execute("""
        INSERT INTO suspension_history (
            user_id, username, suspension_reason, suspension_start, suspension_end
        )
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, f"Unsuspended: {reason}", current_time, current_time))
    conn.commit()
    
    embed = discord.Embed(
        title=f"Unsuspended {username} from Voltify",
        description=(
            f"**Reason:** {reason}"
        ),
        colour=0x5697a9,
        timestamp=datetime.now()
    )
    embed.set_author(
        name=f"Voltify Admin Commands | unsuspend",
        icon_url="https://i.imgur.com/2UzxelF.jpeg"
    )
    embed.set_footer(text=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")

    await ctx.reply(embed=embed)
    await bot.get_channel(1312150369396195338).send(embed=embed)
    try:
        await user.send(embed=embed)
    except discord.DiscordException:
        await bot.get_channel(1311750805358903318).send(f"Unsuspend | Failed to send a DM to user `{user_id}`. They may have DMs disabled or are not reachable.")

@unsuspend.error
async def unsuspend_error(ctx, error):
    if isinstance(error, sqlite3.IntegrityError):
        await ctx.send("An error occurred while processing the database operation: Integrity constraint failed. Please check the database constraints.")
        print(f"Database IntegrityError: {error}")
    elif isinstance(error, discord.app_commands.CommandInvokeError):
        await ctx.send("An unexpected error occurred while executing the command. Please contact support.")
        print(f"CommandInvokeError: {error}")
    else:
        await ctx.send(f"An error occurred: {error}")
        print(f"Unexpected error: {error}")

@admin.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def adminfish(ctx):
    """Catch a random fish."""
    user_id = ctx.author.id

    if ctx.author.id != ADMIN_USER_ID:
        embed = discord.Embed(title="You do not have permission to use this command!",
                      colour=0x00b0f4,
                      timestamp=datetime.now())

        embed.set_author(name="Voltify Admin Commands | No Permissions",
                 icon_url="https://i.imgur.com/2UzxelF.jpeg")

        embed.set_footer(text=f"{ctx.author.name}",
                 icon_url=f"{ctx.author.avatar.url}")
        await ctx.reply(embed=embed)
        return

    cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        await ctx.send(f"❌ You haven't started your fishing adventure! Use {voltify_prefix}start to begin.")
        return

    rarity = determine_rarity()
    fish = random.choice(fish_tiers[rarity])

    weight = random.randint(0, 25)
    length = random.randint(0, 25)
    aura = random.randint(0, 25)
    radiance = random.randint(0, 25)

    ivs_num = weight + length + aura + radiance
    total_possible_value = 25 * 4
    ivs = (ivs_num / total_possible_value) * 100 

    level = random.randint(1, 100)

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

    message = await ctx.send(embed=fishingprogress)

    chance = random.randint(1, 1)
    if chance == 1:
        await asyncio.sleep(5) 

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
                    self.disabled = True
                    await interaction.edit_original_response(
                        embed=fishresults,
                        view=None
                    )
                    self.view.stop()  
            
            @tasks.loop(seconds=0.1) 
            async def track_clicks(self):
                if self.clicks >= self.max_clicks:
                    self.tracking_task.cancel() 
                    await self.message.edit(embed=self.fishresults, view=None)
                    self.view.stop()
                elif self.view.is_finished(): 
                    self.tracking_task.cancel()
                    timeout_embed=discord.Embed(
                        title="🪦 You lost your battle to the shark!",
                        description="You lost your catch, and you cannot fish for another 5 minutes.",
                        colour=0xff0000
                    )
                    await self.message.edit(embed=timeout_embed, view=None)
                else:
                    await asyncio.sleep(0.1) 
                    
        class StartSharkView(View):
            def __init__(self, ctx, max_clicks):
                super().__init__(timeout=5)  
                self.shark_button = SharkButton(max_clicks)
                self.add_item(self.shark_button)
                self.ctx = ctx

            async def on_timeout(self):
                if self.shark_button.clicks < self.shark_button.max_clicks:
                    await message.edit(
                        embed=discord.Embed(
                            title="🪦 You lost your battle to the shark!",
                            description="You lost your catch, and you cannot fish for another 5 minutes.",
                            colour=0xff0000
                        ),
                        view=None
                    )
                    ctx.command.reset_cooldown(self.ctx)
                    ctx.command._buckets._cooldown = commands.Cooldown(1, 300)
                    
        max_clicks = random.randint(1, 3)
        await ctx.send("uwu") # ✅ IT IS GETTING TO HERE
        fishingshark = discord.Embed(
            title="Oh no! A shark is coming!",
            description=f"Click the button {max_clicks} times to kill it!",
            colour=0x5697a9
        )
        fishingshark.set_image(url="https://i.imgur.com/x86d5X2.gif")
        fishingshark.set_footer(text=f"{ctx.author.name}",
                                icon_url=f"{ctx.author.avatar.url}")
        await ctx.send("uwu2")
        await message.edit(embed=fishingshark, view=StartSharkView(max_clicks))
    else:
        await asyncio.sleep(5)

        fishresults = discord.Embed(
            title=f"You caught a {fish}!",
            description=f"Rarity: {rarity}\nLevel: {level}\nPurity: {round(ivs)}%",
            colour=0x5697a9,
            timestamp=datetime.now()
        )
        fishresults.set_footer(text=f"{ctx.author.name} | Fish ID: {fish_id}",
                               icon_url=f"{ctx.author.avatar.url}")
        fishresults.set_thumbnail(url="https://i.imgur.com/k4arBG7.png")

        await message.edit(embed=fishresults)

@adminfish.error
async def adminfish_error(ctx, error):
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

bot.run(TOKEN)