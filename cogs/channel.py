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

# Assuming this is channel.py
async def setup(bot):
    await bot.add_cog(Channel(bot))