import discord
from discord.ext import commands
from utils.Data import Data 
import asyncio
from utils.base_cog import BaseCog
from datetime import datetime, timedelta
import time

class Moderation(BaseCog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/mod.json")
        self.data_file2 = Data("./data/join.json")
        self.data = self.data_file.load_json()
        self.data2 = self.data_file2.load_json()
        super().__init__(bot, self.data, self.data_file)

    # -------------------- ENSURE MEMBER --------------------
    def ensure_member(self, guild_id: str, memb_id: str, member: discord.Member = None):
        """Crée l'entrée d'un membre dans le JSON s'il n'existe pas"""
        if memb_id not in self.data[guild_id]["user"]:
            self.data[guild_id]["user"][memb_id] = {
                "is_special": self.is_special(member) if member else False,
                "name": member.name if member else "inconnu",
                "display_name": member.display_name if member else "inconnu",
                "warns count": 0,
                "bans count": 0,
                "mutes count": 0,
                "kicks count": 0,
                "unmute time": 0,
                "bans": [],
                "warns": [],
                "mutes": [],
                "kicks": []
            }

# -------------------- APPLY_BAN --------------------
async def apply_ban(self, member, reason):
    try:
        await member.ban(reason=reason)
        return None
    except Exception as e:
        return e

# -------------------- BAN --------------------
@commands.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
    if not members:
        await ctx.send("Veuillez entrer au moins un membre à bannir !")
        return

    if not reason:
        reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

    guild_id = str(ctx.guild.id)
    self.ensure_guild(guild_id)

    for member in members:
        memb_id = str(member.id)
        self.ensure_member(guild_id, memb_id, member)

        erreur = await self.apply_ban(member, reason)

        if erreur:
            await ctx.send(f"Impossible de bannir {member} : {erreur}")
            continue

        await ctx.send(f"{member} a été banni !")

        self.data[guild_id]["user"][memb_id]["bans count"] += 1
        self.data[guild_id]["user"][memb_id]["bans"].append({
            "reason": reason,
            "moderator": str(ctx.author) + "  /  " + str(ctx.author.id)
        })

        for gid in self.data2:
            if memb_id not in self.data2[gid]["user"]:
                self.data2[gid]["user"][memb_id] = {
                    "is_special": self.is_special(member),
                    "name": member.name,
                    "display_name": member.display_name,
                    "is Banned": False
                }
            self.data2[gid]["user"][memb_id]["is Banned"] = True

    self.data_file.save_json(self.data)
    self.data_file2.save_json(self.data2)

    # -------------------- PARDON --------------------
    @commands.command(name="pardon")
    async def pardon(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        guild_id = str(ctx.guild.id)
        self.ensure_guild(guild_id)

        for member in members:
            memb_id = str(member.id)
            if memb_id not in self.data[guild_id]["user"]:
                await ctx.send(f"Le membre {member} n'a pas d'antécédent sur ce serveur !")
            else:
                self.data[guild_id]["user"][memb_id]["bans"] = []
                self.data[guild_id]["user"][memb_id]["warns"] = []
                self.data[guild_id]["user"][memb_id]["mutes"] = []
                self.data[guild_id]["user"][memb_id]["bans count"] = 0
                self.data[guild_id]["user"][memb_id]["warns count"] = 0
                self.data[guild_id]["user"][memb_id]["mutes count"] = 0
                self.data[guild_id]["user"][memb_id]["unmute time"] = 0

                await ctx.send(f"Le/La membre {member} a été pardonné(e)")

        self.data_file.save_json(self.data)

    # -------------------- WARN --------------------
    @commands.command(name="warn")
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        guild_id = str(ctx.guild.id)
        self.ensure_guild(guild_id)

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(guild_id, memb_id, member)

            self.data[guild_id]["user"][memb_id]["warns count"] += 1
            self.data[guild_id]["user"][memb_id]["warns"].append({
                "reason": reason,
                "moderator": str(ctx.author) + "  /  " + str(ctx.author.id)
            })

            warn_count = self.data[guild_id]["user"][memb_id]["warns count"]
            await ctx.send(f"{member.mention} a été warn ! Nombre de warns : {warn_count}")

            if warn_count > 5 and warn_count <= 10:
                await self._apply_mute(guild_id, member, ctx, duration=5, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 10 and warn_count <= 15:
                await self._apply_mute(guild_id, member, ctx, duration=10, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 15 and warn_count <= 20:
                await self._apply_mute(guild_id, member, ctx, duration=20, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 20 and warn_count <= 25:
                await self._apply_mute(guild_id, member, ctx, duration=30, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 25 and warn_count <= 30:
                await self._apply_mute(guild_id, member, ctx, duration=60, reason=f"Trop de warns ({warn_count})")

        self.data_file.save_json(self.data)

    # -------------------- KICK --------------------
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre à kick !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        guild_id = str(ctx.guild.id)
        self.ensure_guild(guild_id)

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(guild_id, memb_id, member)

            try:
                await member.kick(reason=reason)
                await ctx.send(f"{member} a été kick !")

                self.data[guild_id]["user"][memb_id]["kicks count"] += 1
                self.data[guild_id]["user"][memb_id]["kicks"].append({
                    "reason": reason,
                    "moderator": str(ctx.author) + "  /  " + str(ctx.author.id)
                })

            except Exception as e:
                await ctx.send(f"Impossible de kick {member} : {e}")

        self.data_file.save_json(self.data)

    # -------------------- MUTE --------------------
    @commands.command(name="mute")
    async def mute(self, ctx, members: commands.Greedy[discord.Member], duration: int, *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        guild_id = str(ctx.guild.id)
        self.ensure_guild(guild_id)

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(guild_id, memb_id, member)
            await self._apply_mute(guild_id, member, ctx, duration, reason)

    # -------------------- APPLY_MUTE --------------------
    async def _apply_mute(self, guild_id: str, member: discord.Member, ctx=None, duration=5, reason="Pas de raison fourni !"):
        memb_id = str(member.id)
        self.ensure_member(guild_id, memb_id, member)

        guild = member.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if not muted_role:
            muted_role = await guild.create_role(
                name="Muted",
                permissions=discord.Permissions(send_messages=False, speak=False)
            )
            for channel in guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)

        await member.add_roles(muted_role, reason=reason)

        unmute_time = datetime.now() + timedelta(minutes=duration)

        self.data[guild_id]["user"][memb_id]["mutes count"] += 1
        self.data[guild_id]["user"][memb_id]["unmute time"] = unmute_time
        self.data[guild_id]["user"][memb_id]["mutes"].append({
            "duration": duration,
            "unmute time": str(unmute_time),
            "reason": reason,
            "moderator": str(ctx.author) + "  /  " + str(ctx.author.id) if ctx else "system"
        })

        self.data_file.save_json(self.data)

        if ctx:
            await ctx.send(f"{member.mention} a été mute pendant {duration} minutes !")

    # --------------------- MUTE SCHEDULER ---------------------
    async def mute_scheduler(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.now()

            for guild_id in self.data:
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue

                for memb_id in self.data[guild_id]["user"]:
                    unmute_time = self.data[guild_id]["user"][memb_id]["unmute time"]

                    if unmute_time != 0 and now >= unmute_time:
                        member = guild.get_member(int(memb_id))
                        if not member:
                            self.data[guild_id]["user"][memb_id]["unmute time"] = 0
                            continue

                        await self.unmute(guild_id, member, "Unmute par le système")

            await asyncio.sleep(30)

    # --------------------- UNMUTE ---------------------
    async def unmute(self, guild_id, member: discord.Member, reason=None):
        mute_role = discord.utils.get(member.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
        self.data[guild_id]["user"][str(member.id)]["unmute time"] = 0
        self.data_file.save_json(self.data)
        print(f"{member} a été unmute automatiquement.")

    # --------------------- UNMUTE_COM ---------------------
    @commands.command(name="unmute")
    async def unmute_com(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("il faut entrer des membres !")
            return

        if reason is None:
            reason = f"Pas de raison fourni par le modérateur {ctx.author.display_name}"

        guild_id = str(ctx.guild.id)
        self.ensure_guild(guild_id)

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(guild_id, memb_id, member)
            await self.unmute(guild_id, member, reason)


# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))