from discord.ext import commands
from discord import app_commands, Member, VoiceState, Interaction, StageChannel, VoiceChannel, PermissionOverwrite, abc
import sqlite3

class TemporaryChannels(commands.Cog):

    def __init__(self):
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("CREATE TABLE IF NOT EXISTS tempchannelbases(guildID INTEGER, channelID INTEGER, UNIQUE(guildID, channelID))")
            db.execute("CREATE TABLE IF NOT EXISTS tempchannels(guildID INTEGER, channelID INTEGER, userID INTEGER,  UNIQUE(guildID, channelID, userID))")
    
    @commands.Cog.listener("on_guild_channel_delete")
    async def channel_deleted(self, channel : abc.GuildChannel):
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("DELETE FROM tempchannelbases WHERE guildID={} and channelID={}".format(channel.guild.id, channel.id))
            db.execute("DELETE FROM tempchannels WHERE guildID={} and channelID={}".format(channel.guild.id, channel.id))
        
    @commands.Cog.listener("on_voice_state_update")
    async def voice_state_update(self, member : Member, before : VoiceState, after : VoiceState):
        if isinstance(after.channel, StageChannel):
            return

        if before.channel != None:
            rows = 0
            with sqlite3.connect("database.db") as con:
                db = con.cursor()
                rows = db.execute("SELECT COUNT(*) FROM tempchannels WHERE guildID={} AND channelID={} AND userID={}".format(member.guild.id, before.channel.id, member.id)).fetchone()[0]
            
            if rows > 0:
                await self.handle_abandonded_temp_channel(member, before.channel)
        
        if after.channel != None:
            rows = 0
            with sqlite3.connect("database.db") as con:
                db = con.cursor()
                rows = db.execute("SELECT COUNT(*) FROM tempchannelbases WHERE guildID={} AND channelID={}".format(member.guild.id, after.channel.id)).fetchone()[0]
            
            if rows <= 0:
                return
            
            vc : VoiceChannel = await member.guild.create_voice_channel(
                member.display_name + "'s temp channel", 
                reason=None, 
                category=after.channel.category, 
                position=after.channel.position + 1,
                bitrate=after.channel.bitrate,
                user_limit=after.channel.user_limit,
                rtc_region=None)
            
            po : PermissionOverwrite = PermissionOverwrite()
            po.add_reactions = True
            po.attach_files = True
            po.external_emojis = True
            po.external_stickers = True
            po.move_members = True
            po.mute_members = True
            po.manage_channels = True
            po.manage_messages = True
            po.read_message_history = True
            po.read_messages = True
            po.connect = True
            po.speak = True
            po.stream = True
            po.view_channel = True

            with sqlite3.connect("database.db") as con:
                db = con.cursor()
                db.execute("INSERT OR IGNORE INTO tempchannels VALUES(?,?,?)", (member.guild.id, vc.id, member.id))
            
            await vc.set_permissions(member,overwrite=po)

            await member.move_to(vc)
        
    @app_commands.command(
        name = "tc_add",
        description = "Adds a channel where temporary voice channels can be created"
    )
    @app_commands.describe(
        channel_id = "ID of the channel to become the base for creating temporary channels"
    )
    @app_commands.checks.has_permissions(administrator = True)
    async def tc_add(self, interaction : Interaction, channel_id : str):
        try:
            channel_id = int(channel_id)
        except ValueError:
            await interaction.followup.send("Invalid channel link")
            return

        channel = interaction.guild.get_channel_or_thread(channel_id)

        if not channel:
            await interaction.followup.send("Could not find channel or reply was not a channel")
            return
        
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("INSERT OR IGNORE INTO tempchannelbases VALUES(?,?)", (interaction.guild_id, int(channel_id)))
        
        await interaction.response.send_message("Your temporary channel base has been set 🦎")

    @app_commands.command(
        name = "tc_remove",
        description = "Removes a channel where temporary voice channels can be created"
    )
    @app_commands.describe(
        channel_id = "ID of the channel to be removed as a base for creating temporary channels"
    )
    @app_commands.checks.has_permissions(administrator = True)
    async def tc_remove(self, interaction : Interaction, channel_id : str):
        try:
            channel_id = int(channel_id)
        except ValueError:
            await interaction.followup.send("Invalid channel link")
            return

        channel = interaction.guild.get_channel_or_thread(channel_id)

        if not channel:
            await interaction.followup.send("Could not find channel or reply was not a channel")
            return
        
        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("DELETE FROM tempchannelbases WHERE guildID={} and channelID={}".format(channel.guild.id, channel.id))
        
        await interaction.response.send_message("Your temporary channel base has been removed 🦎")

    async def handle_abandonded_temp_channel(self, member: Member, channel : VoiceChannel):

        if len(channel.members) <= 0:
            await channel.delete()
            return
        
        await channel.set_permissions(member, overwrite=None)

        po : PermissionOverwrite = PermissionOverwrite()
        po.add_reactions = True
        po.attach_files = True
        po.external_emojis = True
        po.external_stickers = True
        po.move_members = True
        po.mute_members = True
        po.manage_channels = True
        po.manage_messages = True
        po.read_message_history = True
        po.read_messages = True
        po.connect = True
        po.speak = True
        po.stream = True
        po.view_channel = True

        new_member = channel.members[0]
        await channel.set_permissions(new_member, overwrite=po)

        with sqlite3.connect("database.db") as con:
            db = con.cursor()
            db.execute("UPDATE tempchannels SET userID ={} WHERE guildID={} AND channelID={} AND userID={}".format(new_member.id, member.guild.id, channel.id, member.id))

async def setup(bot):
    await bot.add_cog(TemporaryChannels())

