from discord import TextChannel
from discord.ext import commands
import sqlite3
import emoji
import re

class ReactForRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("CREATE TABLE IF NOT EXISTS reactionroles(guildID INTEGER, messageID INTEGER, emote text, role INTEGER, UNIQUE(guildID, messageID, emote, role))")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_reaction_add(self, payload):
        print("working! flicks tongue")
        #do later
    
    @commands.command()
    async def reactionroles(self, ctx, arg):
        if not arg:
            await ctx.send("You must provide an arguement: Update, Add, Delete")
        match(arg.lower()):
            case "update":
                await self.update(ctx)
            case "add":
                await self.add(ctx)
            case "delete":
                await self.delete(ctx)
            case _:
                await ctx.send("You must provide an arguement: Update, Add, Delete")
    
    async def update(self, ctx):
        print()
        #todo

    async def add(self, ctx):
        await ctx.send("Link the channel the message will be in. EX: #general")

        def replyCheck(m):
            return m.channel == ctx.channel and m.author == ctx.author

        reply = await self.bot.wait_for('message', check = replyCheck)
        reply = re.sub(r'[^0-9]', '', reply.content)


        try:
            reply = int(reply)
        except ValueError:
            await ctx.send("Invalid channel link")
            return

        channel = ctx.guild.get_channel_or_thread(reply)

        if not channel:
            await ctx.send("Could not find channel")
            return
        
        await ctx.send("Send the message id of the message to be reacted to. EX: 789960857302859796")

        reply = await self.bot.wait_for('message', check = replyCheck)
        reply = reply.content

        try:
            reply = int(reply)
        except ValueError:
            await ctx.send("Invalid message id")
            return

        message = await channel.fetch_message(reply)

        if not message:
            await ctx.send("Could not find message")
            return
        
        values = []
        while True:
            await ctx.send("Send the emote you would like to link to a role or 'done' to finish")

            reply = await self.bot.wait_for('message', check = replyCheck)
            reply = reply.content.split()

            if reply[0].lower() == "done":
                break

            if not re.match(r"<a?:.+?:\d{18}>", reply[0]) and not reply[0] in emoji.EMOJI_DATA:
                await ctx.send("Message recieved was not an emote")
                return
            
            emote = reply[0]

            await ctx.send("@ the role to assign to this emote. EX: @member")

            reply = await self.bot.wait_for('message', check = replyCheck)
            reply = re.sub(r'[^0-9]', '', reply.content)

            try:
                reply = int(reply)
            except ValueError:
                print(reply)
                await ctx.send("Invalid role recieved from @")
                return
            
            role = ctx.guild.get_role(reply)

            if not role:
                await ctx.send("Invalid role, may be a bot role")
                return
            
            values.append((ctx.guild.id, message.id, emote, role.id))

        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.executemany("INSERT OR IGNORE INTO reactionroles VALUES(?,?,?,?)", values)

    async def delete(self, ctx):
        print()
        #todo

async def setup(bot):
    await bot.add_cog(ReactForRoles(bot))