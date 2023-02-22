import discord
from discord import ApplicationContext
import yaml
from asyncio import *
from urllib.error import HTTPError, URLError
from modules.papagoRequestClass import dataProcessStream


with open('config.yml') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

###############################################################
# Naver Open API application ID
client_id = keys['Keys']['client_id']
# Naver Open API application token
client_secret = keys['Keys']['client_secret']
# stream Instane
streamInstance = dataProcessStream(client_id, client_secret)
###############################################################


class Translate(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.streamInstance = dataProcessStream(client_id, client_secret)

        self.NOT_TRSTEXT = "단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요."

    def makeEmbed(self, resultPackage) -> discord.Embed:
        if resultPackage['status']["code"] < 300:
            embed = discord.Embed(
                title=f"Translate | {resultPackage['data']['ntl']['name']} -> {resultPackage['data']['tl']['name']}", description="", color=0x5CD1E5)
            embed.add_field(name=f"{resultPackage['data']['ntl']['name']} to translate",
                            value=resultPackage['data']['ntl']['text'], inline=False)
            embed.add_field(name=f"Translated {resultPackage['data']['tl']['name']}",
                            value=resultPackage['data']['tl']['text'], inline=False)
            return embed
        else:
            embed = discord.Embed(
                title="Error Code", description=resultPackage['status']['code'], color=0x5CD1E5)
            return embed

    # start up translate

    @discord.slash_command(name="번역", description="한국어, 일본어, 중국어, 영어 4가지 언어 번역 가능")
    @discord.option("trslang", type=str, description="번역하실 언어를 선택해주세요",
                    choices=["한영번역", "영한번역", "한일번역", "일한번역", "한중번역", "중한번역", "일영번역", "영일번역", "영중번역", "중영번역", "중일번역", "일중번역"])
    @discord.option("trstext", type=str, description="번역할 텍스트를 입력해주세요")
    async def translateSlash(self, ctx: ApplicationContext, trslang: str, trstext: str):
        try:
            resultPackage = self.streamInstance.returnQuery(
                trstext, trslang)
            resultEmbed = self.makeEmbed(resultPackage)
            await ctx.respond(embed=resultEmbed)
        except HTTPError as e:
            await ctx.respond(f"Translate Failed. HTTPError Occured : {e}")


def setup(bot):
    bot.add_cog(Translate(bot))
