import discord
from discord.ext import commands
from utils.Data import Data
from utils.base_cog import BaseCog 
import asyncio
import time

class Log(BaseCog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/log.json")
        self.data = self.data_file.load_json()
        self.voice_sessions = {}
        super().__init__(bot, self.data, self.data_file)

    # -------------------- ENSURE MEMBER --------------------
    # s'assure que le membre est present dans le json
    def ensure_member(self, memb_id: str, member: discord.Member = None):
        """Crée l'entrée d'un membre dans le JSON s'il n'existe pas"""
        if memb_id not in self.data["server"]["user"]:
            self.data["server"]["user"][memb_id] = {
                "is_special": self.is_special(member) if member else False,
                "name": member.name if member else "inconnu",
                "display_name": member.display_name if member else "inconnu",
                "messages count": 0,
                "vocal seconds count": 0,
            }

    # ---------------- CHECK_USER ----------------
    # commadne qui permet d'avoir toute les informations d'un utilisateur
    # heure passer en vocal, nombre de message envoyer ...
    @commands.command(name="check")
    async def check_user(self, ctx, members: commands.Greedy[discord.Member]):
        if not members:
            await ctx.send("Il faut entrer au moin un utilisateur !")

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(memb_id, member)

            total = int(self.data["server"]["user"][memb_id]["vocal seconds count"])
            hours   = total // 3600
            minutes = (total % 3600) // 60
            seconds = total % 60

            await ctx.send(
                f"👤 **{member.display_name}** (`{memb_id}`)\n"
                f"💬 Messages envoyés : `{self.data['server']['user'][memb_id]['messages count']}`\n"
                f"🎙️ Temps en vocal : `{hours}h {minutes}m {seconds}s`"
            )

    # ----------------- LISTENER -----------------
    # Listener qui permet de compter les messages envoyer
    # ----------------- ON MESSAGE -----------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        self.ensure_guild(guild_id)

        member_id = str(message.author.id)
        self.ensure_member(member_id, message.author)

        self.data["server"]["user"][member_id]["messages count"] += 1
        self.data_file.save_json(self.data)


    # ----------------- ON VOICE -----------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        guild_id = str(member.guild.id)
        self.ensure_guild(guild_id)

        member_id = str(member.id)
        self.ensure_member(member_id, member)

        # Rejoint un vocal
        if before.channel is None and after.channel is not None:
            self.voice_sessions[member_id] = time.time()

        # Quitte un vocal
        elif before.channel is not None and after.channel is None:
            if member_id in self.voice_sessions:
                duree = time.time() - self.voice_sessions[member_id]
                self.data["server"]["user"][member_id]["vocal seconds count"] += duree
                del self.voice_sessions[member_id]
                self.data_file.save_json(self.data)



# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Log(bot))