from discord.ext import commands
from discord import app_commands
import discord
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
    
    async def get_message(self, interaction : discord.Interaction, channel, message_id):
        channel_id = re.sub(r'[^0-9]', '', channel)

        try:
            channel_id = int(channel_id)
        except ValueError:
            await interaction.followup.send("Invalid channel link")
            return

        channel = interaction.guild.get_channel_or_thread(channel_id)

        if not channel:
            await interaction.followup.send("Could not find channel or reply was not a channel")
            return

        try:
            message_id = int(message_id)
        except ValueError:
            await interaction.followup.send("Invalid message id")
            return

        message = await channel.fetch_message(message_id)

        if not message:
            await interaction.followup.send("Could not find message or reply was not a valid message ID")
            return

        return message

    async def wait_reply(self, interaction : discord.Interaction):
        return await self.bot.wait_for('message', check = lambda m: m.channel == interaction.channel and interaction.user.id == m.author.id, timeout=30)

    @app_commands.command(
        name = "rr_remove_all",
        description = "Removes all react-for-roles from message in the provided channel with given id"
    )
    @app_commands.describe(
        channel = "Channel where message is located ex: #general",
        message_id = "ID of message to remove all react-for-roles from"
    )
    @app_commands.checks.has_permissions(administrator = True)
    async def rr_remove_all(self, interaction: discord.Interaction, channel : str, message_id : str):
        message = await self.get_message(interaction, channel, message_id)

        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("DELETE FROM reactionroles WHERE guildID={} and messageID={}".format(interaction.guild_id, message.id))
        
        await interaction.response.send_message("All react for roles removed from message 🦎")
    
    @app_commands.command(
        name = "rr_add",
        description = "Begins the process of adding react-for-roles to message in provided channel with given id"
    )
    @app_commands.describe(
        channel = "Channel where message is located ex: #general",
        message_id = "ID of message to add react-for-roles to"
    )
    @app_commands.checks.has_permissions(administrator = True)
    async def rr_add(self, interaction : discord.Interaction, channel : str, message_id : str):
        message = await self.get_message(interaction, channel, message_id)
        values = []
        while True:
            if interaction.response.is_done():
                await interaction.followup.send("Send the emote you would like to link to a role or 'done' to finish")
            else:
                await interaction.response.send_message("Send the emote you would like to link to a role or 'done' to finish")
            try:
                reply = await self.wait_reply(interaction)
            except TimeoutError:
                await interaction.followup.send("Request timed out, cancelling")
                return
            
            reply = reply.content.split()

            if reply[0].lower() == "done":
                break

            if not re.match(r"<a?:.+?:\d{18}>", reply[0]) and not reply[0] in emoji.EMOJI_DATA:
                await interaction.reponse.send_message("Reply recieved was not an emote")
                return
            
            emote = reply[0]

            await interaction.followup.send("@ the role to assign to this emote. EX: @member")

            try:
                reply = await self.wait_reply(interaction)
            except TimeoutError:
                await interaction.followup.send("Request timed out, cancelling")
                return
            
            reply = re.sub(r'[^0-9]', '', reply.content)

            try:
                reply = int(reply)
            except ValueError:
                print(reply)
                await interaction.followup.send("Reply recieved was not a valid role")
                return
            
            role = interaction.guild.get_role(reply)

            if not role:
                await interaction.followup.send("Invalid role, may be a bot role, or I don't have permission to get that role")
                return
            
            values.append((interaction.guild.id, message.id, emote, role.id))

        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.executemany("INSERT OR IGNORE INTO reactionroles VALUES(?,?,?,?)", values)
        
        await interaction.followup.send("Your react for roles have been added 🦎")

    @app_commands.command(
        name = "rr_delete",
        description = "Begins the process of deleting react-for-roles from message in provided channel with given id"
    )
    @app_commands.describe(
        channel = "Channel where message is located ex: #general",
        message_id = "ID of message to delete react-for-roles from"
    )
    @app_commands.checks.has_permissions(administrator = True)
    async def rr_delete(self, interaction : discord.Interaction, channel : str, message_id : str):
        message = await self.get_message(interaction, channel, message_id)
        
        while True:
            if interaction.response.is_done():
                await interaction.followup.send("Send the emote to delete roles for or 'done'")
            else:
                await interaction.response.send_message("Send the emote to delete roles for or 'done'")

            try:
                reply = await self.wait_reply(interaction)
            except TimeoutError:
                await interaction.followup.send("Request timed out, cancelling")
                return
            
            reply = reply.content.split()

            if reply[0].lower() == "done":
                break

            if not re.match(r"<a?:.+?:\d{18}>", reply[0]) and not reply[0] in emoji.EMOJI_DATA:
                await interaction.followup.send("Reply recieved was not an emote")
                return
            
            emote = reply[0]

            while True:
                await interaction.followup.send("@ the role to remove from this emote or 'done'. (use 'all' to delete all)")

                try:
                    reply = await self.wait_reply(interaction)
                except TimeoutError:
                    await interaction.followup.send("Request timed out, cancelling")
                    return
                
                if reply.content.lower() == "done":
                    break
                
                if reply.content.lower() == "all":
                    with sqlite3.connect("database.db") as con:
                        db = con.cursor()
                        db.execute("DELETE FROM reactionroles WHERE guildID={} and messageID={} and emote='{}'".format(interaction.guild.id, message.id, emote))
                    await interaction.followup.send("All roles removed from emote 🦎")
                    break
                
                reply = re.sub(r'[^0-9]', '', reply.content)

                try:
                    reply = int(reply)
                except ValueError:
                    print(reply)
                    await interaction.followup.send("Reply recieved was not a valid role")
                    return
                
                role = interaction.guild.get_role(reply)

                if not role:
                    await interaction.followup.send("Invalid role, may be a bot role, or I don't have permission to get that role")
                    return
                
                with sqlite3.connect("database.db") as con:
                    db = con.cursor()
                    db.execute("DELETE FROM reactionroles WHERE guildID={} and messageID={} and emote='{}' and role={}".format(interaction.guild.id, message.id, emote, role.id))
            await interaction.followup.send("Selected roles have been deleted from emote 🦎")

async def setup(bot):
    await bot.add_cog(ReactForRoles(bot))