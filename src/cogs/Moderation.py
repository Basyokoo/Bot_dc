import discord
from discord.ext import commands
import asyncio
from .Data import Data

class Moderation(commands.Cog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot
        self.memberDc = {}
        self.mod = []
        self.data_file = Data("../data/mod.json")  # objet Data
        self.data = self.data_file.load_json()     # dictionnaire


    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre à bannir !")
            return

        for member in members:
            memb_id = str(member.id)
            if memb_id not in self.data["ban"]:
                try:
                    await member.ban(reason=reason)
                    await ctx.send(f"{member} a été banni !")
                    self.mod.append(self.memberDc["ban"].update({"member_id": memb_id, "reason": reason}))
                    self.memberDc.clear()
                except Exception as e:
                    await ctx.send(f"Impossible de bannir {member} : {e}")
            self.data["ban"] += self.mod
            self.remp_json(self.data)
            self.mod.clear()
            
    # cette methode permet de remplir le json de log de moderation
    async def remp_json(self):
        self.data_file.save_json(self.data)


    async def setup(bot):
        await bot.add_cog(Moderation(bot))