import discord
from discord import ApplicationContext


class Say(discord.Cog):
    @discord.slash_command(name="말해", description="말 따라함ㅇ")
    async def repeat(self, ctx: ApplicationContext, message: str):
        await ctx.respond(message)


def setup(bot):
    bot.add_cog(Say(bot))
