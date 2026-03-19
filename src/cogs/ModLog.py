import discord
from discord.ext import commands
from utils.Data import Data
from utils.base_cog import BaseCog 

class ModLog(BaseCog):
    """Cog pour la modération : Check de perm ajout etc..."""

    def __init__(self, bot):
        self.bot = bot
        self.data_file = Data("./data/modperm.json")
        self.data = self.data_file.load_json()
        super().__init__(bot, self.data, self.data_file)

    # -------------------- ON READY --------------------
    @commands.Cog.listener()
    async def on_ready(self):
        self.load_perms()
        print("Permissions chargees !")

    # -------------------- LOAD PERMS --------------------
    def load_perms(self):
        # Supprime les guilds où le bot n'est plus présent
        guilds_actives = [str(guild.id) for guild in self.bot.guilds]
        for guild_id in list(self.data.keys()):
            if guild_id not in guilds_actives:
                del self.data[guild_id]

        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            self.ensure_guild(guild_id)
            for member in guild.members:
                if member.bot:
                    continue
                member_id = str(member.id)
                self.ensure_member(guild_id, member_id, member)
                self.data[guild_id]["user"][member_id]["permissions"] = self.get_permissions(member)
        self.data_file.save_json(self.data)

    # -------------------- GET PERMISSIONS --------------------
    def get_permissions(self, member: discord.Member) -> list:
        perms = member.guild_permissions
        return [perm for perm, value in perms if value]

    # -------------------- CHECK PERM --------------------
    @commands.command(name="ChkPerm")
    async def chk_perm(self, ctx, members: commands.Greedy[discord.Member]):
        await self.cog_before_invoke(ctx)
        if not members:
            return await ctx.send("Il faut entrer au moins un membre !")

        guild_id = str(ctx.guild.id)
        self.ensure_guild(guild_id)

        for member in members:
            member_id = str(member.id)
            self.ensure_member(guild_id, member_id, member)
            perms = self.data[guild_id]["user"][member_id]["permissions"]
            perms_str = "\n".join([f"- {p}" for p in perms]) or "Aucune permission"
            await ctx.send(
                f"**{member.display_name}** (`{member_id}`)\n"
                f"**Permissions :**\n{perms_str}"
            )

    # -------------------- ENSURE MEMBER --------------------
    def ensure_member(self, guild_id: str, memb_id: str, member: discord.Member = None):
        if memb_id not in self.data[guild_id]["user"]:
            self.data[guild_id]["user"][memb_id] = {
                "is_special": self.is_special(member) if member else False,
                "name": member.name if member else "inconnu",
                "display_name": member.display_name if member else "inconnu",
                "permissions": []
            }

# -------------------- Setup --------------------
async def setup(bot):
    await bot.add_cog(ModLog(bot))