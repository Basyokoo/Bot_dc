import discord
from discord.ext import commands
import asyncio

class Moderation(commands.Cog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre à bannir !")
            return

        for member in members:
            try:
                await member.ban(reason=reason)
                await ctx.send(f"{member} a été banni !")
            except Exception as e:
                await ctx.send(f"Impossible de bannir {member} : {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))