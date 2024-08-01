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

# Assuming this is moderation.py
async def setup(bot):
    await bot.add_cog(Moderation(bot))