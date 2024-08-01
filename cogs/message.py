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

# Assuming this is message.py
async def setup(bot):
    await bot.add_cog(Message(bot))