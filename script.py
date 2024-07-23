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
    await bot.add_cog(Configuration(bot))
    await bot.add_cog(Gamble(bot))
    await bot.add_cog(ChannelCog(bot))


# DM MESSAGE
@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(
            'Hello! Im still being coded, so this will likely change later.')
    else:
        return
    await bot.process_commands(message)


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

    @commands.hybrid_command()
    async def ping(self, ctx):
        """ Replies with the Bot's latency """
        await ctx.send(f"Pong! {int(bot.latency*1000)}ms")


# LOGGING IN DISCORD
#@bot.event
#async def on_message_delete(message):
#    z = bot.get_channel(1255214396951498883)
#    embed = discord.Embed(title = f"{message.author}'s Message was Deleted", description = f"Deleted Message: {message.content}\nAuthor: {message.author.mention}\nLocation: {message.channel.mention}", timestamp = datetime.now(), color = discord.Colour.red())
#    await z.send(embed = embed)


# COG: Gamble. ROLL, COINFLIP
class Gamble(commands.Cog):

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


# COG: Channel Management. LOCK, UNLOCK, HIDE, UNHIDE
class ChannelCog(commands.Cog, name="Channel Management"):

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


# BAN CMD
@bot.hybrid_command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, *, reason="***No reason provided.***"):
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
@bot.hybrid_command()
async def unban(ctx,
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
@bot.hybrid_command()
async def mute(ctx,
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


# SAY COMMAND
@commands.has_permissions(manage_messages=True)
@bot.hybrid_command()
async def say(ctx, message=None):
    """ Makes the bot speak """
    await ctx.send(message)


@say.error
async def say_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You do not have permission to use this command!')
    else:
        raise error


# REPLY COMMAND
@commands.has_permissions(manage_messages=True)
@bot.hybrid_command()
async def reply(ctx: commands.Context,
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


# RNG (roll event)
@bot.hybrid_command()
async def rng(ctx, num: int):
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


# FAKE BAN CMD
@bot.hybrid_command()
async def bam(ctx, user: discord.User, *, reason="***No reason provided.***"):
    """ Bans a user from the guild """
    ban = discord.Embed(
        title=f"<:bonk:1255222332830515304> | Banned {user.name}!",
        description=f"Reason: {reason}\nBy: {ctx.author.mention}",
        color=discord.Color.brand_red())
    await ctx.channel.send(embed=ban)


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
        else:
            result_text += "Sorry, you did not pass. Please try again."

        self.embed.description = result_text
        self.embed.set_footer(text="")
        await interaction.response.edit_message(embed=self.embed, view=None)



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