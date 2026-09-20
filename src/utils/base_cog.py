from discord.ext import commands
from .Data import Data
import discord

class BaseCog(commands.Cog):
    def __init__(self, bot, data, data_file):
        self.bot = bot
        self.data = data
        self.data_file = data_file

    async def cog_before_invoke(self, ctx):
        guild_id = str(ctx.guild.id)
        if not self.check(guild_id):
            self.gen_json(guild_id)
        memb_id = str(ctx.author.id)
        self.ensure_member(guild_id, memb_id, ctx.author)
        self.data_file.save_json(self.data)

    def ensure_guild(self, guild_id: str):
        if not self.check(guild_id):
            self.gen_json(guild_id)
            self.data_file.save_json(self.data)

    def check(self, guild_id: str):
        return guild_id in self.data and "user" in self.data[guild_id]

    def gen_json(self, guild_id: str):
        if guild_id not in self.data:
            self.data[guild_id] = {"user": {}}
        else:
            if "user" not in self.data[guild_id]:
                self.data[guild_id]["user"] = {}

    def remp_json(self):
        self.data_file.save_json(self.data)

    def is_special(self, member: discord.Member) -> bool:
        perms = member.guild_permissions
        return any([
            perms.administrator,
            perms.ban_members,
            perms.kick_members,
            perms.manage_messages,
            perms.manage_roles,
            perms.mute_members,
            perms.manage_channels,
        ])
    
    #def check_