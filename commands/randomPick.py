import discord
import random


class RandomPick(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="골라", description="띄어쓰기로 구분")
    async def pickrandom(self, ctx: discord.ApplicationContext, arguments: str):
        args = arguments.split(" ")
        args_len = len(args)
        for arg in args:
            if arg == "":
                args.remove(arg)

        if args_len == 1:
            await ctx.respond("> **어떻게 한개중에 랜덤으로 골르나요** 😢")
            return
        elif args_len >= 2:
            randomNumber = random.randrange(0, len(args))
            finallArg = args[randomNumber]
            args_string = ""
            for arg in args:
                args_string += f"``{arg}``  "
            await ctx.respond(f"> **다음 {args_len}개중에서 저는 **``{finallArg}``**이 더 좋은거 같아요!**\n> {args_string}")


def setup(bot):
    bot.add_cog(RandomPick(bot))
