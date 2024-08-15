import asyncio
import dataclasses
import datetime
from datetime import datetime,timedelta,timezone
import os
import random
import re
import time
from dataclasses import dataclass
from random import choice
from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import operator
from googletrans import Translator

# DOTENV
from dotenv import load_dotenv
load_dotenv(".env")
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='+', intents=intents)


# ON BOT START
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('------')
    await bot.change_presence(
        activity=discord.CustomActivity("I've gone rogue 😈"))
    print("Bot is ready!")
    await bot.add_cog(Message(bot))
    await bot.add_cog(Channel(bot))
    await bot.add_cog(Configuration(bot))
    await bot.add_cog(Fun(bot))
    await bot.add_cog(Moderation(bot))


# DM MESSAGE
@bot.listen()
async def on_message(message):
    if message.author.id == 716390085896962058:  # Pokétwo bot's user ID
        for embed in message.embeds:
            if embed.title and "Your 🎯 Archery Game Targets" in embed.title:
                # Download the image from the embed
                if embed.image and embed.image.url:
                    image_url = embed.image.url
                    image_data = requests.get(image_url).content
                    image_object = BytesIO(image_data)
                
                # Convert BytesIO image object to OpenCV image
                image_pil = Image.open(image_object)
                image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
                
                # Find dart emojis
                coordinates = find_dart_emojis(image_cv)
                parsed_string = ' '.join([item.lower() for item in coordinates])
                await message.channel.send(f"<@716390085896962058> ev m shoot {parsed_string}")

    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(
            'Hello! Im still being coded, so this will likely change later.')
    else:
        return
    await bot.process_commands(message)


# WELCOME MESSAGE
@bot.event
async def on_member_join(member):
    rollnum = random.randint(1, 1000)
    if rollnum == 1000:
        e = bot.get_channel(1245024320804360234)
        extrawelcome = discord.Embed(
            title=f"Heya, {member.display_name}, welcome to The Pikachu Crew!",
            description=
            f"Welcome to The Pikachu Crew, {member.mention}. I hope you enjoy your time here! Please use the dropdown menu below to navigate to useful channels. We also have a limited time event going on, Boost Rewards! WOW! This message seems unusual. {member.mention} has defied the odds and is the lucky one who gets a special reward! Please make a https://discord.com/channels/1237815910887194624/1237874844595654707 to claim this reward!",
            color=0x00FF59)
        await e.send(embed=extrawelcome, view=SelectView())
    else:
        e = bot.get_channel(1245024320804360234)
        welcome = discord.Embed(
            title=f"Heya, {member.display_name}, welcome to The Pikachu Crew!",
            description=
            f"Welcome to The Pikachu Crew, {member.mention}. I hope you enjoy your time here! Please use the dropdown menu below to navigate to useful channels. We also have a limited time event going on, Boost Rewards!",
            color=0x00FF59)
        await e.send(embed=welcome, view=SelectView())


class Select(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(label="Server Rules",
                                 emoji="⛔",
                                 description="Read our server rules."),
            discord.SelectOption(label="Reaction Roles",
                                 emoji="💻",
                                 description="Get some fancy roles."),
            discord.SelectOption(label="Custom Name Color",
                                 emoji="🌈",
                                 description="Make your name any color."),
            discord.SelectOption(
                label="Help and Support",
                emoji="🎫",
                description="Reach out to staff for help etc."),
            discord.SelectOption(label="General Info",
                                 emoji="📜",
                                 description="Read some extra server info."),
            discord.SelectOption(
                label="Boost Rewards",
                emoji="🚀",
                description="Get some rewards for boosting our server.")
        ]
        super().__init__(placeholder="Select an option",
                         max_values=1,
                         min_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Server Rules":
            await interaction.response.send_message(
                content="# <#1239284848057651391>", ephemeral=True)
        elif self.values[0] == "Reaction Roles":
            await interaction.response.send_message("# <#1237826995941806231>",
                                                    ephemeral=True)
        elif self.values[0] == "Custom Name Color":
            await interaction.response.send_message("# <#1237827021137248287>",
                                                    ephemeral=True)
        elif self.values[0] == "Help and Support":
            await interaction.response.send_message(
                content="# <#1237874844595654707>", ephemeral=True)
        elif self.values[0] == "General Info":
            await interaction.response.send_message(
                content="# <#1246832229003558932>", ephemeral=True)
        elif self.values[0] == "Boost Rewards":
            await interaction.response.send_message(
                content="# <#1259836068061118605>", ephemeral=True)


class SelectView(discord.ui.View):

    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(Select())


# REACT WHEN DEX OR REWARD ETC
@bot.listen("on_message")
async def on_good_bot(message: discord.Message):
    if "Good bot" in message.content:
        await message.channel.send("<:cwathappy:1260256260687790152>")


@bot.listen("on_message")
async def on_bad_bot(message: discord.Message):
    if "Bad bot" in message.content:
        await message.channel.send("<a:kittybomb:1259191382690758729>")


@bot.listen("on_message")
async def on_good_bot(message: discord.Message):
    if "good bot" in message.content:
        await message.channel.send("<:cwathappy:1260256260687790152>")


@bot.listen("on_message")
async def on_bad_bot(message: discord.Message):
    if "bad bot" in message.content:
        await message.channel.send("<a:kittybomb:1259191382690758729>")


@bot.listen("on_message")
async def on_quest_track_complete(message: discord.Message):
    if "You have completed this quest track and" in message.content:
        await message.channel.send('<:peepoHypers:1248681946457047141>')
        await message.channel.send(
            'https://tenor.com/view/pikachu-cute-pokemon-dance-moves-gif-17552700'
        )


@bot.listen("on_message")
async def on_good_bot(message: discord.Message):
    if "These colors seem unusual... ✨" in message.content:
        await message.channel.send('<a:shiny:1245070376443318333>')


@bot.listen("on_message")
async def on_good_bot(message: discord.Message):
    if "You have completed the quest" in message.content:
        await message.add_reaction('🎉')
        await message.channel.send('🎉')


@bot.listen("on_message")
async def on_good_bot(message: discord.Message):
    if "You received 350 Pokécoins" in message.content:
        await message.add_reaction('🎉')
        await message.channel.send('🎉')


@bot.listen("on_message")
async def on_good_bot(message: discord.Message):
    if "Added to Pokédex" in message.content:
        await message.add_reaction('🎉')


@bot.listen("on_message")
async def on_sh_chain(message: discord.Message):
    if "+1 Shiny chain!" in message.content:
        await message.add_reaction('<a:shiny:1245070376443318333>')


# HELP MENU
class MyHelpCommand(commands.MinimalHelpCommand):

    async def send_pages(self):
        destination = self.get_destination()
        helpembed = discord.Embed(color=discord.Color.blurple(),
                                  description='')
        for page in self.paginator.pages:
            helpembed.description += page
        await destination.send(embed=helpembed)


bot.help_command = MyHelpCommand()

# CATCH RULES QUIZ
@commands.is_owner()
@bot.command()
async def quiz(ctx: Context):
    start_embed = discord.Embed(
        title="Gain access to catching channels",
        description="Press the button below to start the quiz and gain access to catching channels.",
        color=0x00FF59
    )
    await ctx.channel.send(embed=start_embed, view=StartQuizView())  

@dataclass(kw_only=True)
class MultipleChoice:
    question: str
    choices: list[str]
    answer: int  


from discord import ButtonStyle, Interaction
from discord.ext.commands import Context
from discord.ui import Button, View


questions = [
    MultipleChoice(question="A rare spawns. What is it?",
                   choices=["Dex Only", "FFA (Free-for-all)", "Only for Staff", "Only for the greedy Owner"],
                   answer=0),
    MultipleChoice(question="What do you do if the bots don't send the pings?",
                   choices=["Just catch it", "Leave it to despawn", "Send the Pokémon name in chat", "Ping Staff"],
                   answer=2),
    MultipleChoice(question="A regional spawns. What is it?",
                   choices=["Dex Only", "FFA (Free-for-all)", "Only for Staff", "Uncatchable"],
                   answer=1),
    MultipleChoice(question="You accidentally catch a SH that isn't yours. What do you do?",
                   choices=["Hide it", "Apologize to the hunter", "Do nothing", "Ping staff"],
                   answer=3),
    MultipleChoice(question="Somebody catches your SH. What do you do?",
                   choices=["Report it to Staff", "Argue with who stole it", "Do nothing", "Block who stole it"],
                   answer=0),
    MultipleChoice(question="You are in a FFA channel and a SH spawns. What do you do?",
                   choices=["Catch it", "Spam everyone pings", "Ping staff", "Do nothing"],
                   answer=0),
    MultipleChoice(question="A rare spawns in Booster/Donator channel. What do you do?",
                   choices=["Catch it", "Catch it for your dex", "Ping staff", "Leave it"],
                   answer=1),
    MultipleChoice(question="What do you do if you want to lock a pokemon?",
                   choices=["Use the command", "Leave it", "Ping staff", "Ping Donators"],
                   answer=2),
    MultipleChoice(question="How do you check your dex for a mon?",
                   choices=["@Pokétwo#8236 p", "@Pokétwo#8236 c <name>", "@Pokétwo#8236 d <name>", "@Pokétwo#8236 a <name>"],
                   answer=2),
    MultipleChoice(question="What is the punishment for a 1st offense SH steal?",
                   choices=["Permanent Ban", "1 day Mute", "2 hour Mute + A Warn", "A Warn"],
                   answer=3),
]

choices_buttons = {"0": "1️⃣", "1": "2️⃣", "2": "3️⃣", "3": "4️⃣"}

class ChoiceButton(Button):
    mcview: "MultipleChoiceView"
    value: int

    def __init__(self, mcview: "MultipleChoiceView", label: str, emoji: str, value: int):
        super().__init__(label=label, style=ButtonStyle.primary, emoji=emoji)
        self.mcview = mcview
        self.value = value

    async def callback(self, interaction: Interaction):
        await self.mcview.on_button_click(self, interaction)

class StartButton(Button):
    def __init__(self):
        super().__init__(label="Start", style=ButtonStyle.success, emoji='▶️')

    async def callback(self, interaction: Interaction):
        random_questions = random.sample(questions, 5)
        embed = discord.Embed(
            title="Catch Rules Quiz",
            description="Answer the following questions:",
            color=0x00FF59
        )
        quiz_view = MultipleChoiceView(interaction, embed, random_questions)
        await interaction.response.send_message(embed=embed, view=quiz_view, ephemeral=True)  

class StartQuizView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(StartButton())

class MultipleChoiceView(View):
    ctx: Interaction
    index: int
    correct: int
    embed: discord.Embed
    questions: list[MultipleChoice]

    def __init__(self, ctx: Interaction, embed: discord.Embed, questions: list[MultipleChoice]):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.index = 0
        self.correct = 0
        self.embed = embed
        self.questions = questions

        embed.description = self.body()
        embed.set_footer(text=f"Question {self.index + 1}/{len(self.questions)}")

        for choice in self.choices():
            self.add_item(choice)

    def body(self):
        return self.questions[self.index].question

    def choices(self):
        return [
            ChoiceButton(self, label=choice, emoji=choices_buttons[str(i)], value=i)
            for i, choice in enumerate(self.questions[self.index].choices)
        ]

    async def on_button_click(self, button: ChoiceButton, interaction: Interaction):
        if button.value == self.questions[self.index].answer:
            self.correct += 1
        self.index += 1
        if self.index >= len(self.questions):
            await self.show_results(interaction)
            return self.stop()

        self.clear_items()
        self.embed.description = self.body()
        self.embed.set_footer(text=f"Question {self.index + 1}/{len(self.questions)}")

        for choice in self.choices():
            self.add_item(choice)

        await interaction.response.edit_message(embed=self.embed, view=self)  

    async def show_results(self, interaction: Interaction):
        result_text = f"You got {self.correct} correct answers.\n"
        if self.correct >= 4:
            result_text += "Congratulations! You passed the quiz."
            role = discord.utils.get(self.ctx.guild.roles, name="Catch Access")
            if role:
                await interaction.user.add_roles(role)
            log_message = f"{interaction.user.mention} passed the quiz - they got {self.correct} / 5"
        else:
            result_text += "Sorry, you did not pass. Please try again."
            log_message = f"{interaction.user.mention} failed the quiz - they got {self.correct} / 5"

        self.embed.description = result_text
        self.embed.set_footer(text="")
        await interaction.response.edit_message(embed=self.embed, view=None)  # Ensure results are ephemeral

        log_channel = interaction.guild.get_channel(1265641054070112351)
        if log_channel:
            await log_channel.send(log_message)

# OLYMPICS EVENT DART COORDS
def get_dart_coordinates(board):
    lines = board.split('\n')
    column_map = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    dart_coordinates = []

    for row_idx, line in enumerate(lines[1:], start=1):
        cells = re.split(r'[:\s]+', line.strip())
        for col_idx, cell in enumerate(cells[1:], start=1):
            if cell == 'dart':
                dart_coordinates.append(f"{column_map[col_idx]}{row_idx}")

    return dart_coordinates

def find_dart_emojis(image):
    # Convert to RGB (OpenCV loads images in BGR format)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Define the grid dimensions
    grid_size = 6  # Including the identifiers row and column
    cell_size = 108 // grid_size  # Each cell is 18x18 pixels

    # Load the dart emoji template
    template_path = 'dart_emoji_template.png'
    dart_emoji_template = cv2.imread(template_path)

    # Convert the template to RGB (in case it is loaded as BGR)
    dart_emoji_template_rgb = cv2.cvtColor(dart_emoji_template, cv2.COLOR_BGR2RGB)

    # Perform template matching
    result = cv2.matchTemplate(image_rgb, dart_emoji_template_rgb, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(result >= threshold)

    # Collect the coordinates of the matched regions
    dart_coordinates = set()
    for pt in zip(*loc[::-1]):
        col, row = pt[0] // cell_size, pt[1] // cell_size
        if row > 0 and col > 0:  # Exclude the identifier row and column
            dart_coordinates.add((row, col))

    # Convert coordinates to grid notation
    grid_coordinates = []
    for row, col in sorted(dart_coordinates):
        grid_row = str(row)
        grid_col = chr(col + ord('A') - 1)
        grid_coordinates.append(f'{grid_col}{grid_row}')

    return grid_coordinates


# COG: Channel. LOCK, UNLOCK, HIDE, UNHIDE
class Channel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
# LOCK

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: Optional[discord.TextChannel] = None):
        """ Locks the channel the command is used in, or a specified channel """
        channel = channel or ctx.channel
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is False:
            alreadylocked = discord.Embed(
                title="Error!",
                description=f"The channel is already Locked!",
                colour=0xf54242)
            await ctx.send(embed=alreadylocked)
            return
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role,
                                          overwrite=overwrite)
        lock = discord.Embed(title="Channel Locked",
                             description=f"The channel has been Locked!",
                             colour=0xe04d5c)
        await ctx.send(embed=lock)
        return

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to use this command!')
        else:
            raise error
# UNLOCK CMD

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: Optional[discord.TextChannel] = None):
        """ Unlocks the channel the command is used in, or a specified channel """
        channel = channel or ctx.channel
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is True:
            notlocked = discord.Embed(title="Error!",
                                      description=f"The channel isn't locked!",
                                      colour=0xf54242)
            await ctx.send(embed=notlocked)
            return
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role,
                                          overwrite=overwrite)
        unlock = discord.Embed(title="Channel Unlocked",
                               description=f"The channel has been Unlocked!",
                               colour=0xe04d5c)
        await ctx.send(embed=unlock)
        return

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to use this command!')
        else:
            raise error
# HIDE CMD

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx, channel: Optional[discord.TextChannel] = None):
        """ Hides the channel the command is used in, or a specified channel """
        channel = channel or ctx.channel
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.view_channel is False:
            alreadyhidden = discord.Embed(
                title="Error!",
                description=f"The channel is already hidden!",
                colour=0xf54242)
            await ctx.send(embed=alreadyhidden)
            return
        overwrite.view_channel = False
        await ctx.channel.set_permissions(ctx.guild.default_role,
                                          overwrite=overwrite)
        hide = discord.Embed(title="Channel Hidden",
                             description=f"The channel has been Hidden!",
                             colour=0xe04d5c)
        await ctx.send(embed=hide)
        return

    @hide.error
    async def hide_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to use this command!')
        else:
            raise error
# UNHIDE CMD

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx, channel: Optional[discord.TextChannel] = None):
        """ Unhides the channel the command is used in, or a specified channel """
        channel = channel or ctx.channel
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.view_channel is True:
            nothidden = discord.Embed(title="Error!",
                                      description=f"The channel isn't hidden!",
                                      colour=0xf54242)
            await ctx.send(embed=nothidden)
            return
        overwrite.view_channel = True
        await ctx.channel.set_permissions(ctx.guild.default_role,
                                          overwrite=overwrite)
        unhide = discord.Embed(title="Channel Unhidden",
                               description=f"The channel has been Unhidden!",
                               colour=0xe04d5c)
        await ctx.send(embed=unhide)
        return

    @unhide.error
    async def unhide_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to use this command!')
        else:
            raise error

# COG: Configuration. SYNC, PING
class Configuration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
# SYNC

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self,
                   ctx: commands.Context,
                   guilds: commands.Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
# PING
@bot.hybrid_command()
async def ping(ctx):
    """ Sends the bot's latency """
    # Get the bot's latency in milliseconds
    latency = round(bot.latency * 1000)
    # Send the latency to the channel
    await ctx.send(f"Pong! {latency}ms")

# INFO CMD
@bot.hybrid_command()
async def info(ctx):
    """ Shows info about the Bot """
    infoembed = discord.Embed(title="Info about Pika-Bot",
                  description="**__Language__: Python 3.12.4\n__Library__: discord.py\n__Prefix__: + (or slash commands)\n__Owner__: <@820297275448098817>\n__Developer__: <@820297275448098817> and <@770948558031552512>\n__GitHub__: https://github.com/CBHELEC/pika-bot**",
                      colour=0xf500b4)
    await ctx.send(embed=infoembed)


# COG: Gamble. ROLL, COINFLIP, BAM
class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
# ROLL

    @commands.hybrid_command()
    async def roll(self, ctx, num: int):
        """ Rolls a random number """
        rollnum = random.randint(1, num)
        rng = discord.Embed(
            title=f"{ctx.author.display_name} rolled a {rollnum}",
            colour=0x00f5f1)

        await ctx.send(embed=rng)
# COINFLIP

    @commands.hybrid_command()
    async def coinflip(self, ctx):
        """ Flips a coin """
        determine_flip = [1, 0]
        flipping = discord.Embed(title="A coin has been flipped...",
                                 colour=0x00b8f5)
        flipping.set_image(url="https://i.imgur.com/nULLx1x.gif")
        msg = await ctx.send(embed=flipping)
        await asyncio.sleep(3)
        if random.choice(determine_flip) == 1:
            heads = discord.Embed(title="A coin has been flipped...",
                                  description=f"The coin landed on heads!",
                                  colour=0x00b8f5)
            heads.set_image(url="https://i.imgur.com/h1Os447.png")
            await msg.edit(embed=heads)
        else:
            tails = discord.Embed(title="A coin has been flipped...",
                                  description=f"The coin landed on tails!",
                                  colour=0x00b8f5)
            tails.set_image(url="https://i.imgur.com/EiBLhPX.png")
            await msg.edit(embed=tails)

# FAKE BAN CMD
    @commands.hybrid_command()
    async def bam(self, ctx, user: discord.User, *, reason="***No reason provided.***"):
        """ Bans a user from the guild """
        ban = discord.Embed(
            title=f"<:bonk:1255222332830515304> | Banned {user.name}!",
            description=f"Reason: {reason}\nBy: {ctx.author.mention}",
            color=discord.Color.brand_red())
        await ctx.channel.send(embed=ban)

# RNG (roll event)
    @commands.hybrid_command()
    async def rng(self, ctx, num: int):
        """ Rolls a random number """
        rollnum = random.randint(1, num)
        if rollnum == 123:
            rngeventwinner = discord.Embed(
                title=
                f"{ctx.author.display_name} rolled a {rollnum} and won the event!",
                description=f"{ctx.author.mention}",
                colour=0x00f5f1)
            await ctx.send(embed=rngeventwinner)
        else:
            rngeventlose = discord.Embed(
                title=f"{ctx.author.display_name} rolled a {rollnum}",
                description=f"{ctx.author.mention}",
                colour=0x00f5f1)
            await ctx.send(embed=rngeventlose)

# GOOGLE CMD
    @commands.command()
    async def google(self, ctx, *, query):
        """Search Google and return a single text answer."""
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": "d65d9240b803d18e84ff5ed91affb851171f0ab5732fe42957f603c6c9f33962"
            }
            search = GoogleSearch(params)
            results = search.get_dict()

            if "organic_results" in results and results["organic_results"]:
                first_result = results["organic_results"][0]
                first_result_url = first_result.get("link", "No URL found")
                snippet = first_result.get("snippet", "No snippet found.")

                await ctx.send(f"Top search result: {first_result_url}\n\n{snippet}")
            else:
                await ctx.send("No results found.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

# MATH CMD
operators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}
@bot.hybrid_command()
async def math(ctx, expression: str):
    # Use regular expression to parse the expression
    match = re.match(r"(\d+(\.\d+)?)([+\-*/])(\d+(\.\d+)?)", expression)
    if match:
        left, _, operator, right, _ = match.groups()
        left, right = float(left), float(right)
        if operator in operators:
            try:
                result = operators[operator](left, right)
                await ctx.send(f'{left} {operator} {right} = {result}')
            except ZeroDivisionError:
                await ctx.send('Error: Division by zero is not allowed.')
        else:
            await ctx.send('Invalid symbol! Please use one of the following: +, -, *, /')
    else:
        await ctx.send('Invalid expression! Please use the format: number symbol number (e.g., 1+1)')
            
# COG: Message. SAY, REPLY
class Message(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
# SAY COMMAND
    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command()
    async def say(self, ctx, message=None):
        """ Makes the bot speak """
        await ctx.send(message)

    @say.error
    async def say_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to use this command!')
        else:
            raise error


# REPLY COMMAND
    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command()
    async def reply(self, ctx: commands.Context,
                    message_id,
                    message: str,
                    flag: Literal["True", "False"] = "True"):
        """Makes the bot reply to a message"""
        try:
            target_message = await ctx.channel.fetch_message(message_id)
            reply_content = message
            if flag == "True":
                reply_content = f"{target_message.author.mention} {message}"
            await target_message.reply(reply_content)
        except Exception as e:
            print(e)

# COG: Moderation. BAN, UNBAN, MUTE
class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
# BAN CMD
    @commands.hybrid_command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason="***No reason provided.***"):
        """ Bans a user from the guild """
        ban = discord.Embed(
            title=f"<:bonk:1255222332830515304> | Banned {user.name}!",
            description=f"Reason: {reason}\nBy: {ctx.author.mention}",
            color=discord.Color.brand_red())
        await ctx.message.delete()
        await ctx.channel.send(embed=ban)
        bandm = discord.Embed(
            title=f"<:bonk:1255222332830515304> | You were Banned!",
            description=f"Reason: {reason}\nBy: {ctx.author.mention}")
        await user.send(embed=bandm)
        await ctx.guild.ban(user)


# UNBAN CMD
    @commands.has_permissions(moderate_members=True)
    @commands.hybrid_command()
    async def unban(self, ctx,
                    user: discord.User,
                    *,
                    reason="***No reason provided.***"):
        """ Unbans a user from the guild """
        unban = discord.Embed(
            title=f"<:catcri:1248705148293742723> | Unbanned {user.name}!",
            description=f"Reason: {reason}\nBy: {ctx.author.mention}",
            color=discord.Color.brand_green())
        hellowhat = discord.Embed(
            title=f"<:NOO:1248704955653820436> | {user.name} isn't Banned!",
            color=discord.Color.teal())
        try:
            entry = await ctx.guild.fetch_ban(discord.Object(user.id))
        except discord.NotFound:
            await ctx.channel.send(embed=hellowhat)
        await ctx.guild.unban(discord.Object(user.id))
        await ctx.channel.send(embed=unban)
        await ctx.message.delete()
        return


# MUTE CMD
    class TimedeltaConverter(commands.Converter):

        async def convert(self, ctx: commands.Context,
                        arg: str) -> datetime.timedelta:
            seconds = 0
            for match in re.finditer(r"(\d+)([smhd])", arg):
                value, unit = int(match[1]), match[2]
                if unit == "s":
                    seconds += value
                elif unit == "m":
                    seconds += value * 60
                elif unit == "h":
                    seconds += value * 3600
                elif unit == "d":
                    seconds += value * 86400
            return datetime.timedelta(seconds=seconds)


    @commands.has_permissions(moderate_members=True)
    @commands.hybrid_command()
    async def mute(self, ctx,
                user: discord.Member,
                duration: TimedeltaConverter,
                *,
                reason="***No reason provided.***"):
        """Mutes a user for a specified duration"""
        try:
            await user.timeout(duration, reason=reason)
            await ctx.send(
                f"{user.mention} has been muted for {duration} due to: {reason}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to mute this user.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
            
# HELP MENU
# ALARM / REMINDER
# KICK
# WARN
# WARNS
# UNWARN
# LOGGING (oh no)
# GIVEROLE
# TAKEROLE
# TEMPORARY GIVEROLE
# TEMPORARY TAKEROLE
# USERINFO
# AVATARINFO - finds the specified users avatar
# BANNERINFO - finds the specified users banner
# GUILDINFO
# GUILDSTATS
# PURGE
# SETSLOWMODE
# USERNOTES
# DM MODMAIL - dm for support - forwards all dms to mods w/ spam pings. only used in emergency.
# ADDEMOJI
# REMOVEEMOJI
# ADDSTICKER
# REMOVESTICKER
# CLONE
# CREATECHANNEL
# DELETECHANNEL
# AUTO-CHANNEL - makes a ton of channels (specify amnt) with a specified naming scheme.
# CREATEROLE
# DELETEROLE
# EDITCHANNEL
# EDITROLE
# EDITEMOJI
# EDITSTICKER
# REACT COMMAND
# UNMUTE
# CATCH RULES QUIZ FOR ACCESS TO CATCHING CHANNELS

@bot.command(name='dictionary', help='Provides the definition of a word or phrase.')
async def define(ctx, *, word):
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            meaning = data[0]['meanings'][0]
            definition = meaning['definitions'][0]['definition']
            example = meaning['definitions'][0].get('example', 'No example available.')
            part_of_speech = meaning['partOfSpeech']

            embed = discord.Embed(title=f'Definition of {word}', color=0x00ff00)
            embed.add_field(name='Part of Speech', value=part_of_speech, inline=False)
            embed.add_field(name='Definition', value=definition, inline=False)
            embed.add_field(name='Example', value=example, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f'No definitions found for "{word}".')
    else:
        await ctx.send(f'Error: Could not retrieve definitions for "{word}".')

@bot.command(name='meme', help='Fetches a random meme from the internet.')
async def meme(ctx):
    url = "https://meme-api.com/gimme"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        meme_url = data['url']
        title = data['title']
        subreddit = data['subreddit']

        embed = discord.Embed(title=title, description=f"From r/{subreddit}", color=discord.Color.blue())
        embed.set_image(url=meme_url)

        await ctx.send(embed=embed)
    else:
        await ctx.send("Couldn't fetch a meme at the moment. Try again later!")

WEATHER_API_KEY = '3efe9535f47d61bca5582de78912c4be'

@bot.command(name='weather', help='Provides the current weather for a specified city.')
async def weather(ctx, *, city: str):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        city_name = data['name']
        country = data['sys']['country']

        embed = discord.Embed(
            title=f"Weather in {city_name}, {country}",
            description=f"{weather_description.capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Temperature", value=f"{temperature}°C", inline=True)
        embed.add_field(name="Feels Like", value=f"{feels_like}°C", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind Speed", value=f"{wind_speed} m/s", inline=True)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Couldn't retrieve weather data for {city}. Please check the city name and try again.")

translator = Translator()
@bot.command(name='translate', help='Translates text to a specified language. Usage: !translate <text> to <language_code>')
async def translate(ctx, *args):
    # Join all arguments into a single string
    message = ' '.join(args)

    # Find the position of "to" in the message to separate text and language code
    if ' to ' in message:
        text_to_translate, dest_language = message.rsplit(' to ', 1)
    else:
        await ctx.send("Please use the correct format: `!translate <text> to <language_code>`")
        return

    try:
        # Perform the translation
        translation = translator.translate(text_to_translate, dest=dest_language)
        translated_text = translation.text
        source_language = translation.src

        embed = discord.Embed(
            title="Translation",
            description=f"Translated from {source_language} to {dest_language}",
            color=discord.Color.green()
        )
        embed.add_field(name="Original", value=text_to_translate, inline=False)
        embed.add_field(name="Translated", value=translated_text, inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}. Please check the language code and try again.")

reminders = {}
@bot.group(invoke_without_command=True)
async def reminder(ctx):
    """Shows reminder-related commands."""
    help_text = (
        "Reminder commands:\n"
        "`*reminder set <time> <message>` - Set a new reminder.\n"
        "`*reminder list` - List all active reminders.\n"
        "`*reminder cancel <id>` - Cancel a specific reminder."
    )
    await ctx.send(help_text)

@reminder.command()
async def set(ctx, time: str, *, message: str):
    """Set a reminder."""
    # Parse the time input
    time_seconds, time_display = parse_time(time)
    
    if time_seconds is None:
        await ctx.send("Invalid time format. Please provide a valid time (e.g., 10s for 10 seconds or 5m for 5 minutes).")
        return
    
    # Generate a unique reminder ID
    reminder_id = len(reminders) + 1
    
    # Record the time when the reminder is set
    reminder_set_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    
    # Store reminder details
    reminders[reminder_id] = {
        'user': ctx.author,
        'message': message,
        'time_seconds': time_seconds,
        'set_time': reminder_set_time
    }
    
    # Notify the user that the reminder has been set
    await ctx.send(f'Reminder set for {time_display}. I will remind you about: "{message}". Use `*reminder cancel {reminder_id}` to cancel this reminder.')

    # Sleep for the specified amount of time
    await asyncio.sleep(time_seconds)

    # Send the reminder with a ping and the time when it was set
    if reminder_id in reminders:
        reminder = reminders.pop(reminder_id)
        await ctx.send(f'{reminder["user"].mention} Your reminder has ended! {reminder["message"]}\n-# Reminder was set at {reminder["set_time"]}.')

@reminder.command()
async def list(ctx):
    """List all active reminders."""
    if not reminders:
        await ctx.send("No active reminders.")
        return
    
    reminder_list = []
    for reminder_id, reminder in reminders.items():
        time_display = format_time(reminder['time_seconds'])
        reminder_list.append(f'ID: {reminder_id}, Set for: {time_display}, Message: "{reminder["message"]}", Set at: {reminder["set_time"]}')
    
    await ctx.send("\n".join(reminder_list))

@reminder.command()
async def cancel(ctx, reminder_id: int):
    """Cancel a specific reminder."""
    if reminder_id in reminders:
        reminder = reminders.pop(reminder_id)
        await ctx.send(f'Reminder with ID {reminder_id} has been canceled.')
    else:
        await ctx.send(f'No reminder found with ID {reminder_id}.')

def parse_time(time_str):
    """Convert a time string with units to seconds and return a display-friendly format."""
    time_str = time_str.lower()
    match = re.match(r"(\d+)([smh]?)", time_str)
    if match:
        quantity = int(match.group(1))
        unit = match.group(2)
        if unit == 'm':
            return quantity * 60, f"{quantity} minute(s)"
        elif unit == 'h':
            return quantity * 3600, f"{quantity} hour(s)"
        else:  # Default to seconds if no unit or 's'
            return quantity, f"{quantity} second(s)"
    return None, None

def format_time(seconds):
    """Format time in seconds into a user-friendly string."""
    if seconds >= 3600:
        return f"{seconds // 3600} hour(s)"
    elif seconds >= 60:
        return f"{seconds // 60} minute(s)"
    else:
        return f"{seconds} second(s)"

CURRENCY_API_KEY = '3f774ef18ff2aab3780725fe'
CURRENCY_API_URL = 'https://v6.exchangerate-api.com/v6/'
@bot.command()
async def convert(ctx, amount: float, from_currency: str, to_currency: str):
    """Convert an amount from one currency to another."""
    # Make API request to get exchange rates
    response = requests.get(f'{CURRENCY_API_URL}{CURRENCY_API_KEY}/latest/{from_currency.upper()}')
    
    if response.status_code != 200:
        await ctx.send("Error fetching exchange rates. Please try again later.")
        return
    
    data = response.json()
    
    if 'conversion_rates' not in data:
        await ctx.send("Invalid currency code. Please provide valid currency codes.")
        return
    
    # Get the conversion rate
    conversion_rate = data['conversion_rates'].get(to_currency.upper())
    
    if conversion_rate is None:
        await ctx.send("Invalid target currency code. Please provide a valid target currency code.")
        return
    
    # Convert the amount
    converted_amount = amount * conversion_rate
    
    # Send the result
    await ctx.send(f"{amount} {from_currency.upper()} is approximately {converted_amount:.2f} {to_currency.upper()}.")

GIPHY_API_KEY = 'gC9drTTPIu9gfjNEBk8xDIW6ff8CG8bd'
GIPHY_API_URL = 'https://api.giphy.com/v1/gifs/search'
@bot.command()
async def gif(ctx, *, query: str):
    """Search for a GIF based on a query."""
    params = {
        'api_key': GIPHY_API_KEY,
        'q': query,
        'limit': 1,  # Number of results to return
        'offset': 0,
        'rating': 'G',  # Rating: G, PG, PG-13, R
        'lang': 'en'
    }

    response = requests.get(GIPHY_API_URL, params=params)
    
    if response.status_code != 200:
        await ctx.send("Error fetching GIFs. Please try again later.")
        return
    
    data = response.json()
    
    if data['data']:
        gif_url = data['data'][0]['images']['original']['url']
        await ctx.send(gif_url)
    else:
        await ctx.send("No GIFs found for the query.")

# List of motivational quotes
MOTIVATIONAL_QUOTES = [
    "Believe you can and you're halfway there.",
    "The only way to do great work is to love what you do.",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "The best way to predict the future is to invent it.",
    "It does not matter how slowly you go as long as you do not stop.",
    "You are never too old to set another goal or to dream a new dream.",
    "Act as if what you do makes a difference. It does.",
    "Start where you are. Use what you have. Do what you can.",
    "Success usually comes to those who are too busy to be looking for it.",
    "The harder you work for something, the greater you’ll feel when you achieve it."
]
@bot.command()
async def motivate(ctx):
    """Send a random motivational quote."""
    quote = random.choice(MOTIVATIONAL_QUOTES)
    await ctx.send(quote)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    # Define badge emojis
    BADGES = {
    "booster1": "<:booster1:1273380164583035080>",  # Example badge
    "booster2": "<:booster2:1273380143011856482>",  # Example badge
    "booster3": "<:booster3:1273379943388024954>",  # Example badge
    "booster6": "<:booster6:1273379929710657670>",  # Example badge
    "booster9": "<:booster9:1273379911301726333>",  # Example badge
    "booster12": "<:booster12:1273380125064298587>",  # Example badge
    "booster15": "<:booster15:1273379875478048799>",  # Example badge
    "booster18": "<:booster18:1273379869514006599>",  # Example badge
    "booster24": "<:booster24:1273379856599748721>",  # Example badge
    "nitro": "<:nitro:1273380511640981584>",  # Example badge
    "hsbalance": "<:hsbalance:1273380700464222360>",  # Example badge
    "hsbrilliance": "<:hsbrilliance:1273380705753366619>",  # Example badge
    "hsbravery": "<:hsbravery:1273380710354522112>",  # Example badge
    "bh2": "<:bh2:1273380922988953600>",  # Example badge
    "bh1": "<:bh1:1273380927380394064>",  # Example badge
    "dev": "<:dev:1273381027443642470>",  # Example badge
    "quest": "<:quest:1273381118544052235>",  # Example badge
    "staff": "<:staff:1273381197950619789>",  # Example badge
    "earlysupport": "<:earlysupport:1273381448161951864>",  # Example badge
    "hsevent": "<:hsevent:1273381453761089606>",  # Example badge
    "mpalumni": "<:mpalumni:1273381458396053524>",  # Example badge
    "partner": "<:partner:1273381622363983956>",  # Example badge
    "earlybotdev": "<:earlybotdev:1273382153069006848>",  # Example badge
    "legacyusername": "<:legacyusername:1273382280940748882>",  # Example badge
    "supportscmds": "<:supportscmds:1273382678963552478>",  # Example badge
    "premiumbot": "<:premiumbot:1273382690447425597>",  # Example badge
    "clown": "<:clown:1273382708806156382>",  # Example badge
    "automod": "<:automod:1273382738229202994>",  # Example badge
    # Add other badges and their corresponding emojis here
}

    # Define user badges (add actual badge checking logic here)
    badges = []
    if member.public_flags.verified_bot_developer:
        badges.append(BADGES.get("earlybotdev", ""))
    if member.public_flags.partner:
        badges.append(BADGES.get("partner", ""))
    if member.public_flags.discord_certified_moderator:
        badges.append(BADGES.get("mpalumni", ""))
    if member.public_flags.hypesquad:
        badges.append(BADGES.get("hsevent", ""))
    if member.public_flags.early_supporter:
        badges.append(BADGES.get("earlysupport", ""))
    if member.public_flags.staff:
        badges.append(BADGES.get("staff", ""))
    if member.public_flags.active_developer:
        badges.append(BADGES.get("dev", ""))
    if member.public_flags.bug_hunter:
        badges.append(BADGES.get("bh1", ""))
    if member.public_flags.bug_hunter_level_2:
        badges.append(BADGES.get("bh2", ""))
    if member.public_flags.hypesquad_bravery:
        badges.append(BADGES.get("hsbravery", ""))
    if member.public_flags.hypesquad_brilliance:
        badges.append(BADGES.get("hsbrilliance", ""))
    if member.public_flags.hypesquad_balance:
        badges.append(BADGES.get("hsbalance", ""))
    # Add other badge checks as needed

    # Get the user's roles, excluding @everyone, and sort them from top to bottom
    roles = sorted(member.roles[1:], key=lambda role: role.position, reverse=True)
    
    # Display only the top 10 roles
    displayed_roles = roles[:10]
    total_roles_count = len(roles)
    remaining_roles_count = total_roles_count - len(displayed_roles)
    
    # Format the roles to be displayed
    roles_str = ' • '.join([f"<@&{role.id}>" for role in displayed_roles])
    
    if remaining_roles_count > 0:
        roles_str += f"\n... {remaining_roles_count} More"

    # Fetch user information
    username = member.name  # Actual username for the title
    display_name = member.display_name  # Display name for the author field
    
    # Ensure both datetimes are timezone-aware
    now = datetime.now(timezone.utc)
    
    created_at = f"<t:{int(member.created_at.timestamp())}:f> ({(now - member.created_at).days // 365} years ago)"
    joined_at = f"<t:{int(member.joined_at.timestamp())}:f> ({(now - member.joined_at).days // 30} months ago)"
    
    # Define the Administrator permission check
    admin_permission = "✅" if member.guild_permissions.administrator else "<:white_cross_mark:1273344081182851165>"
    
    # Define the Booster status check
    booster_status = "✅" if member.premium_since else "<:white_cross_mark:1273344081182851165>"
    # Define the Booster status check
    booster_status_badges = "<a:allbooster:1273660598323777577>" if member.premium_since else ""
    # Utility function to return an emoji based on Nitro status
    def get_nitro_status(member: discord.Member) -> str:
        if member.premium_since:  # User has Nitro
            return '<:nitro:1273380511640981584>'  # You can use any emoji you want to represent Nitro
        else:  # User does not have Nitro
            return ''  # Another emoji for no Nitro
    nitro_emoji = get_nitro_status(member)  # Use the utility function

    # Create the embed
    embed = discord.Embed(
        title=display_name,  # Title with the actual username
        color=discord.Color.blue()
    )
    embed.set_author(name=f"{username}", icon_url=member.display_avatar.url)  # Display name and username in author
    embed.set_thumbnail(url=member.display_avatar.url)  # Display the profile picture in the thumbnail
    
    badges_str = ' '.join(badges) if badges else "None"

    embed.add_field(
        name="ℹ️ User Info",
        value=(
            f"User ID: `{member.id}` ({ctx.author.mention})\n"
            f"Created: {created_at}\n"
            f"Joined: {joined_at}\n"
            f"Administrator: {admin_permission}\n"
            f"Booster: {booster_status}\n"
            f"Badges: {nitro_emoji} {booster_status_badges} {badges_str}"
        ),
        inline=False
    )
    embed.add_field(
        name=f"<:mention:1273342726972244008> {total_roles_count} Roles",
        value=f"{roles_str}",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def test(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    # Retrieve the public flags of the member
    flags = member.public_flags

    # Use dir() to get a list of all attributes in PublicUserFlags
    all_flags = [attr for attr in dir(flags) if not attr.startswith('_') and isinstance(getattr(flags, attr), bool)]

    # Initialize a dictionary to count users with each flag
    flag_counts = {flag: 0 for flag in all_flags}

    # Iterate over all members in the server to count flags
    for guild_member in ctx.guild.members:
        guild_flags = guild_member.public_flags
        for flag in all_flags:
            if getattr(guild_flags, flag):
                flag_counts[flag] += 1

    # Create a message with the status and count of each flag
    flag_output = [f"{flag}: {getattr(flags, flag)} (Users with this flag: {flag_counts[flag]})" for flag in all_flags]

    # Send the output as a message in Discord
    await ctx.send("\n".join(flag_output))
    
# IN PROGRESS CODE:
bot.run(TOKEN)
