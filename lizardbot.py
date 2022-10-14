import asyncio
from discord.ext import commands
import discord
import json
import os

class LizardBotClient(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True

        super().__init__(intents=intents, command_prefix=["<@932816670756577281> ", "<@!932816670756577281> "])

    async def on_ready(self):
        print(f"Lizard has been warmed and ready to eat bug as {self.user}")

async def load_extentions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def startup():
    async with bot:
        await load_extentions()
        await bot.start(token)
    
if __name__ == "__main__":
    f = open("config.json")
    config_data = json.load(f)

    token = ""
    if config_data["token"]:
        token = config_data["token"]

    bot = LizardBotClient()

    asyncio.run(startup())