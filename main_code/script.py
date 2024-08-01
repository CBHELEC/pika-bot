import asyncio
import dataclasses
import datetime
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
from googlesearch import search
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import requests

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

@bot.event
async def setup_hook():
    for ext in extensions:
        await bot.load_extension(ext)
extensions = [
    "cogs.configuration",
    "cogs.fun",
    "cogs.channel"
    "cogs.moderation"
    "cogs.message"
]


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

# IN PROGRESS CODE:
bot.run(TOKEN)
