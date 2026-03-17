from discord.ext import commands
from .Data import Data

class BaseCog(commands.Cog):
    def __init__(self, bot, data, data_file):
        self.bot = bot
        self.data = data
        self.data_file = data_file

    async def cog_before_invoke(self, ctx):
        guild_id = str(ctx.guild.id)
        if not self.check("id", guild_id):
            self.gen_json(guild_id)
        memb_id = str(ctx.author.id)
        self.ensure_member(memb_id, ctx.author)
        self.remp_json()

    def check(self, key, value):
        if "server" not in self.data:
            return False
        if key not in self.data["server"]:
            return False
        return self.data["server"][key] == value

    def gen_json(self, guild_id):
        if "server" not in self.data:
            self.data["server"] = {"id": guild_id, "user": {}}
        else:
            self.data["server"]["user"] = {}

    def remp_json(self):
        self.data_file.save_json(self.data)