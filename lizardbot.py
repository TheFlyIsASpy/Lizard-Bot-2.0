import discord
import json

class LizardBotClient(discord.Client):
    async def on_ready(self):
        print(f"Lizard has been warmed and ready to eat bug as {self.user}")
    
    async def on_message(self, message):
        if message.user == self.user:
            return
        #add a command to set react for roll message
        print(message.content)
    
    async def on_reaction_add(self, reaction, user):
        return #implement this
    
if __name__ == "__main__":
    f = open("config.json")
    config_data = json.load(f)

    token = ""
    if config_data["token"]:
        token = config_data["token"]
    

    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True

    bot = LizardBotClient(intents=intents)
    bot.run(token)