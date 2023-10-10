from discord.ext import commands
from discord import app_commands, Interaction, Member

class NW_Commands(commands.Cog):
    @app_commands.command(
        name = "nw_promote",
        description = "Promotes a new world member to Dreadworlder. Gives access to guild locked channels."
    )
    @app_commands.describe(
        member = "member to be promoted"
    )
    @app_commands.checks.has_any_role(894362725470339112,903525457394290708)
    async def nw_promote(self, interaction : Interaction, member : Member):

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Unable to fetch guild")
            return
        
        role = guild.get_role(931247395600216086)

        if not role:
            await interaction.response.send_message("Unable to fetch dreadworlder role")
            return
        
        if role in member.roles:
            await interaction.response.send_message(member.display_name + " is already dreadworlder")
            return
               
        try:
            await member.add_roles(role)
        except Exception as e:
            await interaction.response.send_message("Failed to promote " + member.display_name + " to dreadworlder. Exception: " + e)
            return

        await interaction.response.send_message(member.display_name + " successfully promoted to dreadworlder")

    @app_commands.command(
        name = "nw_promote_consul",
        description = "Promotes a new world member to consul"
    )
    @app_commands.describe(
        member = "member to be promoted"
    )
    @app_commands.checks.has_role(903525457394290708)
    async def nw_promote_consul(self, interaction : Interaction, member : Member):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Unable to fetch guild")
            return
        
        role = guild.get_role(894362725470339112)

        if not role:
            await interaction.response.send_message("Unable to fetch consul role")
            return
        
        if role in member.roles:
            await interaction.response.send_message(member.display_name + " is already a consul")
            return
               
        try:
            await member.add_roles(role)
        except Exception as e:
            await interaction.response.send_message("Failed to promote " + member.display_name + " to consul. Exception: " + e)
        
        await interaction.response.send_message(member.display_name + " successfully promoted to consul")

async def setup(bot):
    await bot.add_cog(NW_Commands())