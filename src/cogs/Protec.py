import discord
from discord.ext import commands
from utils.Data import Data 
import asyncio
from utils.base_cog import BaseCog
from datetime import datetime, timedelta
import time

class Protec(BaseCog):
    """Cog pour la modération : Check de perm ajout etc..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/join.json")
        self.data = self.data_file.load_json()
        super().__init__(bot, self.data, self.data_file)

    
    # -------------------- ON READY --------------------
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in bot.guilds:
            ensure_guild(str(guild.id))
            for member in guild.members:
                ensure_member(str(guild.id),str(member.id),member)



    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        member_id = str(member.id)
        
        ensure_guild(guild_id)

        ensure_member(guild_id,member_id,member)

        if (self.data[guild_id]["user"][memb_id]["is Banned"] == True) :
            Mod = self.bot.cogs.get("Moderation")
            if Mod:
                await Mod.apply_ban(member_id,"Banni automatiquement par le système (banni dans un autre serveur)")
        

    # -------------------- ENSURE MEMBER --------------------
    def ensure_member(self, guild_id: str, memb_id: str, member: discord.Member = None):
        """
        Crée l'entrée d'un membre dans le JSON s'il n'existe pas dans ce dernier
        """
        
        if memb_id not in self.data[guild_id]["user"]:
            self.data[guild_id]["user"][memb_id] = {
                "is_special": self.is_special(member) if member else False,
                "name": member.name if member else "inconnu",
                "display_name": member.display_name if member else "inconnu",
                "is_Banned" : False
            }


# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Protec(bot))