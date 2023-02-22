import discord
from discord import ApplicationContext
import random
import json


def checkVoteNotEnd(voteID: int):
    with open(f"./data/votes/{voteID}.json", "r") as f:
        data = json.load(f)
    if data["voteEnd"] == -1:
        return True
    else:
        return False


def upVote(voteID: int, OorX: str, voteUserID: int):
    try:
        with open(f"./data/votes/{voteID}.json", "r") as f:
            data = json.load(f)

        data[OorX]["votes"] = data[OorX]["votes"] + 1
        data[OorX]["votedUser"].append(voteUserID)

        with open(f"./data/votes/{voteID}.json", "w") as f:
            data = json.dump(data, f, indent=2)

        return True
    except:
        return False


def checkAlreadyVotedUser(voteID: int, voteUserID: int):
    with open(f"./data/votes/{voteID}.json", "r") as f:
        data = json.load(f)

    allVotedUser: list = list(
        data["O"]["votedUser"]) + list(data["X"]["votedUser"])

    for userID in allVotedUser:
        if userID == voteUserID:
            return False

    return True


class Voting(discord.Cog):
    def __init__(self, bot): self.bot = bot

    @discord.slash_command(name="투표", description="투표 양식을 만들어줍니다!")
    @discord.option(name="votechannel", type=discord.TextChannel, description="투표를 올릴 채널을 선택해주세요")
    @discord.option(name="votemessage", type=str, description="투표할 것을 작성해주세요")
    async def voteSlash(self, ctx: ApplicationContext, votechannel: discord.TextChannel, votemessage: str):
        async def runVoteButton_callback(interaction: discord.interactions.Interaction):
            VOTEID = random.randint(1000000000, 9999999999)
            with open(f"./data/votes/{VOTEID}.json", "w") as f:
                json.dump({"voteValue": votemessage, "VOTEID": VOTEID, "voteEnd": -1, "openVoteUser": ctx.author.id, "O": {"votes": 0, "votedUser": []},
                          "X": {"votes": 0, "votedUser": []}}, f, indent=2)

            async def OButton_callback(interaction: discord.interactions.Interaction):
                if checkVoteNotEnd(VOTEID):
                    if checkAlreadyVotedUser(VOTEID, interaction.user.id):
                        if upVote(VOTEID, "O", interaction.user.id):

                            await interaction.response.send_message(
                                "투표 완료했습니다", ephemeral=True)
                    else:
                        await interaction.response.send_message(
                            "당신은 이미 투표했잖아요..!", ephemeral=True)
                        return
                else:
                    await interaction.response.send_message("이 투표는 이미 끝났어요..!", ephemeral=True)

            OButton = discord.ui.Button(
                label="찬성", style=discord.ButtonStyle.green)
            OButton.callback = OButton_callback

            async def XButton_callback(interaction: discord.interactions.Interaction):
                if checkVoteNotEnd(VOTEID):
                    if checkAlreadyVotedUser(VOTEID, interaction.user.id):
                        if upVote(VOTEID, "X", interaction.user.id):
                            await interaction.response.send_message(
                                "투표 완료했습니다", ephemeral=True)
                    else:
                        await interaction.response.send_message(
                            "당신은 이미 투표했잖아요..!", ephemeral=True)
                        return
                else:
                    await interaction.response.send_message("이 투표는 이미 끝났어요..!", ephemeral=True)

            async def EndVoteButton_callback(interaction: discord.interactions.Interaction):
                if checkVoteNotEnd(VOTEID):
                    with open(f"./data/votes/{VOTEID}.json", "r") as f:
                        data = json.load(f)

                    openVoteUser: int = data["openVoteUser"]

                    if interaction.user.id == openVoteUser:
                        with open(f"./data/votes/{VOTEID}.json", "r") as f:
                            data = json.load(f)

                        data["voteEnd"] = 0
                        with open(f"./data/votes/{VOTEID}.json", "w") as f:
                            json.dump(data, f, indent=2)

                        with open(f"./data/votes/{VOTEID}.json", "r") as f:
                            data = json.load(f)
                            OVotesCount = data["O"]["votes"]
                            OVotesUsers = data["O"]["votedUser"]
                            XVotesCount = data["X"]["votes"]
                            XVotesUsers = data["X"]["votedUser"]

                        embed = discord.Embed(
                            title="투표가 종료되었습니다", color=discord.Color.from_rgb(0, 255, 0))

                        OVotesUsersMention = ""
                        for user in OVotesUsers:
                            OVotesUsersMention += f"<@{user}>"
                        XVotesUsersMention = ""
                        for user in XVotesUsers:
                            XVotesUsersMention += f"<@{user}>"
                        embed.add_field(
                            name="찬성", value=OVotesUsersMention, inline=False)
                        embed.add_field(name="반대", value=XVotesUsersMention)
                        embed.set_footer(
                            text=f"찬성 {OVotesCount}명 반대 {XVotesCount}명")
                        embed.set_author(name=interaction.user.name,
                                         icon_url=interaction.user.display_avatar)
                        await interaction.response.send_message(embed=embed)
                    else:
                        await interaction.response.send_message(content="당신이 투표를 열지 않았잖아요..!", ephemeral=True)

                else:
                    await interaction.response.send_message("이미 투표가 끝났는데요...? 으에..?", ephemeral=True)

            XButton = discord.ui.Button(
                label="반대", style=discord.ButtonStyle.red)
            XButton.callback = XButton_callback

            EndVoteButton = discord.ui.Button(
                label="투표종료", style=discord.ButtonStyle.danger)
            EndVoteButton.callback = EndVoteButton_callback

            embed = discord.Embed(
                title=votemessage, color=discord.Color.from_rgb(0, 255, 0))
            embed.set_author(name=ctx.author.name,
                             icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="투표")
            view = discord.ui.View(
                timeout=None)
            view.add_item(OButton)
            view.add_item(XButton)
            view.add_item(EndVoteButton)
            await votechannel.send(embed=embed, view=view, content="")

            await interaction.response.edit_message(content="투표가 진행됐습니다", view=None)

        runVoteButton = discord.ui.Button(
            label="투표 진행", style=discord.ButtonStyle.green)
        runVoteButton.callback = runVoteButton_callback

        async def cancelVoteButton_callback(interaction: discord.interactions.Interaction):
            await interaction.response.edit_message(content="취소하셧습니다.", view=None)
            return

        cancelVoteButton = discord.ui.Button(
            label="취소", style=discord.ButtonStyle.red)
        cancelVoteButton.callback = cancelVoteButton_callback

        view = discord.ui.View()
        view.add_item(runVoteButton)
        view.add_item(cancelVoteButton)

        await ctx.respond(f"투표 메시지를 다시한번 확인해주세요.\n``{votemessage}``", ephemeral=True, view=view)


def setup(bot):
    bot.add_cog(Voting(bot))
