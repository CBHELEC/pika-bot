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
from serpapi import GoogleSearch
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import requests
from bs4 import BeautifulSoup

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
                "api_key": "No Thanks"
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

# Assuming this is fun.py
async def setup(bot):
    await bot.add_cog(Fun(bot))
