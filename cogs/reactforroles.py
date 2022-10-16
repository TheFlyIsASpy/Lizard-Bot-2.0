from discord.ext import commands
import sqlite3
import emoji
import re
from asyncio import TimeoutError

class ReactForRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("CREATE TABLE IF NOT EXISTS reactionroles(guildID INTEGER, messageID INTEGER, emote text, role INTEGER, UNIQUE(guildID, messageID, emote, role))")

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_reaction_add(self, payload):
        rows = []
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            rows = db.execute("SELECT * FROM reactionroles WHERE guildID={} AND messageID={} AND emote='{}'".format(payload.guild_id, payload.message_id, payload.emoji)).fetchall()
        
        if len(rows) <= 0:
            return
        
        roles = []
        for r in rows:
            roles.append(payload.member.guild.get_role(r[3]))
        
        await payload.member.add_roles(*roles)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reactionroles(self, ctx, arg):
        if not arg:
            await ctx.send("You must provide an arguement: Add, Delete, RemoveAll")
        match(arg.lower()):
            case "removeall":
                await self.remove_all(ctx)
            case "add":
                await self.add(ctx)
            case "delete":
                await self.delete(ctx)
            case _:
                await ctx.send("You must provide an arguement: Add, Delete, RemoveAll")
    
    async def wait_reply(self, ctx):
        return await self.bot.wait_for('message', check = lambda m: m.channel == ctx.channel and ctx.author == m.author, timeout=30)
    
    async def get_message(self, ctx):
        await ctx.send("Link the channel the message is in. EX: #general")

        try:
            reply = await self.wait_reply(ctx)
        except TimeoutError:
            await ctx.send("Request timed out, cancelling")
            return

        reply = re.sub(r'[^0-9]', '', reply.content)

        try:
            reply = int(reply)
        except ValueError:
            await ctx.send("Invalid channel link")
            return

        channel = ctx.guild.get_channel_or_thread(reply)

        if not channel:
            await ctx.send("Could not find channel or reply was not a channel")
            return
        
        await ctx.send("Right click, copy ID, and send the message ID of the message to be reacted to. EX: 789960857302859796")

        try:
            reply = await self.wait_reply(ctx)
        except TimeoutError:
            await ctx.send("Request timed out, cancelling")
            return

        reply = reply.content

        try:
            reply = int(reply)
        except ValueError:
            await ctx.send("Invalid message id")
            return

        message = await channel.fetch_message(reply)

        if not message:
            await ctx.send("Could not find message or reply was not a valid message ID")
            return
        
        return message

    async def add(self, ctx):
        
        message = await self.get_message(ctx)

        values = []
        while True:
            await ctx.send("Send the emote you would like to link to a role or 'done' to finish")

            try:
                reply = await self.wait_reply(ctx)
            except TimeoutError:
                await ctx.send("Request timed out, cancelling")
                return
            
            reply = reply.content.split()

            if reply[0].lower() == "done":
                break

            if not re.match(r"<a?:.+?:\d{18}>", reply[0]) and not reply[0] in emoji.EMOJI_DATA:
                await ctx.send("Reply recieved was not an emote")
                return
            
            emote = reply[0]

            await ctx.send("@ the role to assign to this emote. EX: @member")

            try:
                reply = await self.wait_reply(ctx)
            except TimeoutError:
                await ctx.send("Request timed out, cancelling")
                return
            
            reply = re.sub(r'[^0-9]', '', reply.content)

            try:
                reply = int(reply)
            except ValueError:
                print(reply)
                await ctx.send("Reply recieved was not a valid role")
                return
            
            role = ctx.guild.get_role(reply)

            if not role:
                await ctx.send("Invalid role, may be a bot role, or I don't have permission to get that role")
                return
            
            values.append((ctx.guild.id, message.id, emote, role.id))

        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.executemany("INSERT OR IGNORE INTO reactionroles VALUES(?,?,?,?)", values)
        
        await ctx.send("Your react for roles have been added 🦎")

    async def delete(self, ctx): 
        message = await self.get_message(ctx)
        
        while True:
            await ctx.send("Send the emote to delete roles for or 'done'")

            try:
                reply = await self.wait_reply(ctx)
            except TimeoutError:
                await ctx.send("Request timed out, cancelling")
                return
            
            reply = reply.content.split()

            if reply[0].lower() == "done":
                break

            if not re.match(r"<a?:.+?:\d{18}>", reply[0]) and not reply[0] in emoji.EMOJI_DATA:
                await ctx.send("Reply recieved was not an emote")
                return
            
            emote = reply[0]

            while True:
                await ctx.send("@ the role to remove from this emote or 'done'. (use 'all' to delete all)")

                try:
                    reply = await self.wait_reply(ctx)
                except TimeoutError:
                    await ctx.send("Request timed out, cancelling")
                    return
                
                if reply.content.lower() == "done":
                    break;
                
                if reply.content.lower() == "all":
                    with sqlite3.connect("database.db") as con:
                        db = con.cursor()
                        db.execute("DELETE FROM reactionroles WHERE guildID={} and messageID={} and emote='{}'".format(ctx.guild.id, message.id, emote))
                    await ctx.send("All roles removed from emote 🦎")
                    break
                
                reply = re.sub(r'[^0-9]', '', reply.content)

                try:
                    reply = int(reply)
                except ValueError:
                    print(reply)
                    await ctx.send("Reply recieved was not a valid role")
                    return
                
                role = ctx.guild.get_role(reply)

                if not role:
                    await ctx.send("Invalid role, may be a bot role, or I don't have permission to get that role")
                    return
                
                with sqlite3.connect("database.db") as con:
                    db = con.cursor()
                    db.execute("DELETE FROM reactionroles WHERE guildID={} and messageID={} and emote='{}' and role={}".format(ctx.guild.id, message.id, emote, role.id))
            await ctx.send("Selected roles have been deleted from emote 🦎")
        
    async def remove_all(self, ctx):
        while True:
            message = await self.get_message(ctx)

            with sqlite3.connect("database.db") as con:
                db = con.cursor()
                db.execute("DELETE FROM reactionroles WHERE guildID={} and messageID={}".format(ctx.guild.id, message.id))
            
            await ctx.send("All react for roles removed from message 🦎. Type r to remove another")

            try:
                reply = await self.wait_reply(ctx)
            except TimeoutError:
                return
            
            if not reply.content.lower() == "r":
                break
            


            



            

async def setup(bot):
    await bot.add_cog(ReactForRoles(bot))