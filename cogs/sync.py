from typing import Literal, Optional
from discord.ext import commands
from discord.ext.commands import Greedy, Context # or a subclass of yours
import discord

class Sync(commands.Cog):
    @commands.command()
    @commands.has_permissions(administrator=True)
    
    async def sync(
    self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        """
            ~ syncs commands currently on guild
            ^ removes commands from guild.
            * copies all global commands to guild then syncs
        """
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx: Context):
        print("refreshing")
        await ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync()
        print("refreshing complete")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: Context, type: Optional[Literal["guild", "global"]]):
        if type.lower() == "guild":
            await ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
        elif type.lower() == "global":
            await ctx.bot.tree.clear_commands(guild=None)
            await ctx.bot.tree.sync()



async def setup(bot):
    await bot.add_cog(Sync())