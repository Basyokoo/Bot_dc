import discord
from discord.ext import commands
from .Data import Data
import asyncio

class Moderation(commands.Cog):
    """Cog pour la modération : ban, mute, warn..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/mod.json")
        self.data = self.data_file.load_json()

        # Assure que la clé "user" existe
        if "user" not in self.data:
            self.data["user"] = {}

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

            try:
                await member.ban(reason=reason)
                await ctx.send(f"{member} a été banni !")

                # Crée l'utilisateur dans le JSON si inexistant
                if memb_id not in self.data["user"]:
                    self.data["user"][memb_id] = {
                        "warn count": 0,
                        "bans count": 0,
                        "mute count": 0,
                        "bans": [],
                        "warns": [],
                        "mutes": []
                    }

                # Ajouter le ban dans l'historique
                self.data["user"][memb_id]["bans count"] += 1
                self.data["user"][memb_id]["bans"].append({
                    "reason": reason,
                    "moderator": str(ctx.author.id)
                })

            except Exception as e:
                await ctx.send(f"Impossible de bannir {member} : {e}")

        self.remp_json()

    # -------------------- WARN --------------------
    @commands.command(name="warn")
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        if not members:
            await ctx.send("Veuillez entrer au moins un membre !")
            return

        if not reason or reason == None:
            reason = f"Pas de raison fourni par le moderateur : {ctx.author}"

        for member in members:
            memb_id = str(member.id)
            if memb_id not in self.data["user"]:
                self.data["user"][memb_id] = {
                    "warn count": 0,
                    "bans count": 0,
                    "mute count": 0,
                    "bans": [],
                    "warns": [],
                    "mutes": []
                }

            # Ajouter le warn
            self.data["user"][memb_id]["warn count"] += 1
            self.data["user"][memb_id]["warns"].append({
                "reason": reason,
                "moderator": str(ctx.author.id)
            })

            warn_count = self.data["user"][memb_id]["warn count"]
            await ctx.send(f"{member.mention} a été warn ! Nombre de warns : {warn_count}")

            # Auto-mute si >5 warns
            if warn_count > 5 and warn_count <= 10:
                await self._apply_mute(member, ctx, duration=5, reason="Trop de warns")
            
            if warn_count > 10 and warn_count <= 15:
                await self._apply_mute(member, ctx, duration=10, reason="Trop de warns")

            if warn_count > 15 and warn_count <= 20:
                await self._apply_mute(member, ctx, duration=20, reason="Trop de warns")

            if warn_count > 20 and warn_count <= 25:
                await self._apply_mute(member, ctx, duration=30, reason="Trop de warns")

            if warn_count > 25 and warn_count <= 30:
                await self._apply_mute(member, ctx, duration=60, reason="Trop de warns")


        self.remp_json()

    # -------------------- MUTE --------------------
    async def _apply_mute(self, member: discord.Member, ctx=None, duration=5, reason="Pas de raison fourni !"):
        memb_id = str(member.id)

        if memb_id not in self.data["user"]:
            self.data["user"][memb_id] = {
                "warn count": 0,
                "bans count": 0,
                "mute count": 0,
                "bans": [],
                "warns": [],
                "mutes": []
            }

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

        # Log mute
        self.data["user"][memb_id]["mute count"] += 1
        self.data["user"][memb_id]["mutes"].append({
            "duration": duration,
            "reason": reason,
            "moderator": str(ctx.author.id) if ctx else "system"
        })

        self.remp_json()

        if ctx:
            await ctx.send(f"{member.mention} a été mute pendant {duration} minutes !")

        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)

        if ctx:
            await ctx.send(f"{member.mention} n'est plus mute !")

    # -------------------- JSON --------------------
    def remp_json(self):
        self.data_file.save_json(self.data)

# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))