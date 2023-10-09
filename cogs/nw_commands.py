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
    @app_commands.checks.has_any_role(["894362725470339112","903525457394290708"])
    async def nw_promote(self, interaction : Interaction, member : Member):
        print("command launched")
        guild = interaction.guild
        print(guild)
        role = guild.get_role("931247395600216086")
        print(role)
        await member.add_roles(role)
        await interaction.response.send_message("Member successfully promoted to dreadworlder")
    
    @app_commands.command(
        name = "nw_promote_consul",
        description = "Promotes a new world member to consul"
    )
    @app_commands.describe(
        member = "member to be promoted"
    )
    @app_commands.checks.has_role("903525457394290708")
    async def nw_promote_consul(self, interaction : Interaction, member : Member):
        print("consul command launched")
        guild = interaction.guild
        role = await guild.get_role("894362725470339112")
        await member.add_roles(role)
        return

async def setup(bot):
    await bot.add_cog(NW_Commands())