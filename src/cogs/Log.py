import discord
from discord.ext import commands
from utils.Data import Data 
import asyncio
from utils.base_cog import BaseCog

class Log(BaseCog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/log.json")
        self.data = self.data_file.load_json()
        super().__init__(bot, data, data_file)


    # ---------------- CHECK_USER ----------------
    # commadne qui permet d'avoir toute les informations d'un utilisateur
    # heure passer en vocal, nombre de message envoyer ...
    @commands.command(name="check")
    async def check_user(self, ctx, members: commands.Greedy[discord.Member]):
        if not members:
            await ctx.send("Il faut entrer au moin un utilisateur !")
        

    # -------------------- ENSURE MEMBER --------------------
    # s'assure que le membre est present dans le json
    def ensure_member(self, memb_id: str, member: discord.Member = None):
        """Crée l'entrée d'un membre dans le JSON s'il n'existe pas"""
        

# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))