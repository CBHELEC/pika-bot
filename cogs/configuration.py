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
    async def ping(self, ctx, bot):
        """ Replies with the Bot's latency """
        await ctx.send(f"Pong! {int(bot.latency*1000)}ms")

# INFO CMD
    @commands.hybrid_command()
    async def info(self, ctx):
        """ Shows info about the Bot """
        infoembed = discord.Embed(title="Info about Pika-Bot",
                      description="**__Language__: Python 3.12.4\n__Library__: discord.py\n__Prefix__: + (or slash commands)\n__Owner__: <@820297275448098817>\n__Developer__: <@820297275448098817> and <@770948558031552512>\n__GitHub__: https://github.com/CBHELEC/pika-bot**",
                      colour=0xf500b4)
        await ctx.send(embed=infoembed)

# Assuming this is configuration.py
async def setup(bot):
    await bot.add_cog(Configuration(bot))
