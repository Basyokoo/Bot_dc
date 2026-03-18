import discord
from discord.ext import commands
from utils.Data import Data 
import asyncio
from utils.base_cog import BaseCog

class Moderation(BaseCog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/mod.json")
        self.data = self.data_file.load_json()
        super().__init__(bot, self.data, self.data_file)

    # -------------------- BAN --------------------
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre à bannir !")
            return
        
        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(memb_id, member)

            try:
                await member.ban(reason=reason)
                await ctx.send(f"{member} a été banni !")

                self.data["server"]["user"][memb_id]["bans count"] += 1
                self.data["server"]["user"][memb_id]["bans"].append({
                    "reason": reason,
                    "moderator": str(ctx.author)+"  /  "+str(ctx.author.id)
                })

            except Exception as e:
                await ctx.send(f"Impossible de bannir {member} : {e}")

        self.remp_json()

    # -------------------- PARDON --------------------
    @commands.command(name="pardon")
    async def pardon(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        for member in members:
            memb_id = str(member.id)
            if memb_id not in self.data["server"]["user"]:
                await ctx.send(f"Le membre {member} n'as pas d'antécédent sur ce serveur !")
            else:
                self.data["server"]["user"][memb_id]["bans"] = []
                self.data["server"]["user"][memb_id]["warns"] = []
                self.data["server"]["user"][memb_id]["mutes"] = []
                self.data["server"]["user"][memb_id]["bans count"] = 0
                self.data["server"]["user"][memb_id]["warns count"] = 0
                self.data["server"]["user"][memb_id]["mutes count"] = 0

                await ctx.send(f"Le/La membre {member} a été pardonné(e)")

        self.remp_json()

    # -------------------- WARN --------------------
    @commands.command(name="warn")
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(memb_id, member)

            self.data["server"]["user"][memb_id]["warns count"] += 1
            self.data["server"]["user"][memb_id]["warns"].append({
                "reason": reason,
                "moderator": str(ctx.author)+"  /  "+str(ctx.author.id)
            })

            warn_count = self.data["server"]["user"][memb_id]["warns count"]
            await ctx.send(f"{member.mention} a été warn ! Nombre de warns : {warn_count}")

            if warn_count > 5 and warn_count <= 10:
                await self._apply_mute(member, ctx, duration=5, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 10 and warn_count <= 15:
                await self._apply_mute(member, ctx, duration=10, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 15 and warn_count <= 20:
                await self._apply_mute(member, ctx, duration=20, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 20 and warn_count <= 25:
                await self._apply_mute(member, ctx, duration=30, reason=f"Trop de warns ({warn_count})")
            elif warn_count > 25 and warn_count <= 30:
                await self._apply_mute(member, ctx, duration=60, reason=f"Trop de warns ({warn_count})")

        self.remp_json()

    # -------------------- KICK --------------------
    # permet d'expulser les membres choisit
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre à kick !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(memb_id, member)

            try:
                await member.kick(reason=reason)
                await ctx.send(f"{member} a été kick !")

                self.data["server"]["user"][memb_id]["kicks count"] += 1
                self.data["server"]["user"][memb_id]["kicks"].append({
                    "reason": reason,
                    "moderator": str(ctx.author)+"  /  "+str(ctx.author.id)
                })

            except Exception as e:
                await ctx.send(f"Impossible de kick {member} : {e}")

        self.remp_json()

    # -------------------- MUTE --------------------
    @commands.command(name="mute")
    async def mute(self, ctx, members: commands.Greedy[discord.Member], duration: int, *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        for member in members:
            memb_id = str(member.id)
            self.ensure_member(memb_id, member)

            await self._apply_mute(member, ctx, duration, reason)

    # -------------------- APPLY_MUTE --------------------
    async def _apply_mute(self, member: discord.Member, ctx=None, duration=5, reason="Pas de raison fourni !"):
        memb_id = str(member.id)
        self.ensure_member(memb_id, member)

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

        self.data["server"]["user"][memb_id]["mutes count"] += 1
        self.data["server"]["user"][memb_id]["mutes"].append({
            "duration": duration,
            "reason": reason,
            "moderator": str(ctx.author)+"  /  "+str(ctx.author.id) if ctx else "system"
        })

        self.remp_json()

        if ctx:
            await ctx.send(f"{member.mention} a été mute pendant {duration} minutes !")

        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)

        if ctx:
            await ctx.send(f"{member.mention} n'est plus mute !")

    # -------------------- ENSURE MEMBER --------------------
    def ensure_member(self, memb_id: str, member: discord.Member = None):
        """Crée l'entrée d'un membre dans le JSON s'il n'existe pas"""
        if memb_id not in self.data["server"]["user"]:
            self.data["server"]["user"][memb_id] = {
                "is_special": self.is_special(member) if member else False,
                "name": member.name if member else "inconnu",
                "display_name": member.display_name if member else "inconnu",
                "warns count": 0,
                "bans count": 0,
                "mutes count": 0,
                "kicks count": 0,
                "bans": [],
                "warns": [],
                "mutes": [],
                "kicks": []
            }

# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))