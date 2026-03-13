import discord
from discord.ext import commands 
import asyncio
import signal
import time
from cogs.Data import Data

TOKEN = Data("./data/token.json").load_json()["token"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="*", intents=intents)

    async def setup_hook(self):
        # Charger les cogs avant le login
        for cog in ["Moderation"]:
            await self.load_extension(f"cogs.{cog}")

bot = MyBot()

@bot.event
async def on_ready():
    testmess = bot.get_channel(1481952817856909315)
    if testmess is not None:
        await testmess.send("Hi !")
    else:
        print("Erreur : le canal n'a pas été trouvé")
    print(f"Cogs chargés : {bot.cogs}")  # <- Affiche tous les cogs



bot.run(TOKEN)