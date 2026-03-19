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
    def ensure_member(self, guild_id: str, memb_id: str, member: discord.Member = None):
        """Crée l'entrée d'un membre dans le JSON s'il n'existe pas"""
        if memb_id not in self.data[guild_id]["user"]:
            self.data[guild_id]["user"][memb_id] = {
                "is_special": self.is_special(member) if member else False,
                "name": member.name if member else "inconnu",
                "display_name": member.display_name if member else "inconnu",
                "messages count": 0,
                "vocal seconds count": 0,
                "activite": []
            }

    # ---------------- CHECK_USER ----------------
    @commands.command(name="check")
    async def check_user(self, ctx, members: commands.Greedy[discord.Member]):
        if not members:
            await ctx.send("Il faut entrer au moins un utilisateur !")
            return

        for member in members:
            memb_id = str(member.id)
            guild_id = str(ctx.guild.id)
            self.ensure_guild(guild_id)
            self.ensure_member(guild_id, memb_id, member)

            total = int(self.data[guild_id]["user"][memb_id]["vocal seconds count"])
            hours   = total // 3600
            minutes = (total % 3600) // 60
            seconds = total % 60

            await ctx.send(
                f"👤 **{member.display_name}** (`{memb_id}`)\n"
                f"💬 Messages envoyés : `{self.data[guild_id]['user'][memb_id]['messages count']}`\n"
                f"🎙️ Temps en vocal : `{hours}h {minutes}m {seconds}s`"
            )

    # ----------------- ON MESSAGE -----------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        self.ensure_guild(guild_id)
        member_id = str(message.author.id)
        self.ensure_member(guild_id, member_id, message.author)

        self.data[guild_id]["user"][member_id]["messages count"] += 1

        if message.content and message.content[0] == '!':
            command_name = message.content[1:].split()[0]
            command = self.bot.get_command(command_name)
            if command and command.cog_name == "Moderation":
                self.data[guild_id]["user"][member_id]["activite"].append(
                    ("moderation", message.content)
                )

        self.data_file.save_json(self.data)


    # pour les commandes slash (/)
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.application_command:
            return
        if interaction.user.bot:
            return

        guild_id = str(interaction.guild_id)
        self.ensure_guild(guild_id)
        member_id = str(interaction.user.id)
        self.ensure_member(guild_id, member_id, interaction.user)

        command_name = interaction.data.get("name", "inconnu")
        self.data[guild_id]["user"][member_id]["activite"].append(
            ("slash", f"/{command_name}")
        )

        self.data_file.save_json(self.data)

    # ----------------- ON VOICE -----------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        
        guild_id = str(member.guild.id)
        self.ensure_guild(guild_id)

        member_id = str(member.id)
        self.ensure_member(guild_id, member_id, member)

        # Rejoint un vocal
        if before.channel is None and after.channel is not None:
            self.voice_sessions[member_id] = time.time()

        # Quitte un vocal
        elif before.channel is not None and after.channel is None:
            if member_id in self.voice_sessions:
                duree = time.time() - self.voice_sessions[member_id]
                self.data[guild_id]["user"][member_id]["vocal seconds count"] += duree
                del self.voice_sessions[member_id]
                self.data_file.save_json(self.data)

    # ----------------- CHK_ACTI -----------------
    @commands.command(name="chkActi")
    async def activity(self, ctx, members: commands.Greedy[discord.Member]):
        if not members:
            await ctx.send("il faut insérer un membre !")
            return 

        for member in members:
            memb_id = str(member.id)
            guild_id = str(ctx.guild.id)
            self.ensure_guild(guild_id)
            self.ensure_member(guild_id, memb_id, member)

            activite = self.data[guild_id]["user"][memb_id]["activite"]
            if not activite:
                activite_str = "Aucune activité enregistrée."
            else:
                activite_str = "\n".join(
                    f"- {type_cmd} : `{cmd}`" for type_cmd, cmd in activite
                )

            await ctx.send(
                f"Voici l'activité du membre : {member.display_name}\n"
                f"{activite_str}"
            )


# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Log(bot))