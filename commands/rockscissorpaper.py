import discord
from discord import ApplicationContext
import random
import json
import datetime


class RockScissorPaperGameView(discord.ui.View):
    def __init__(self, users: list[discord.User], ctx: ApplicationContext):
        super().__init__(timeout=None)
        self.users = users
        self.ctx = ctx

        self.GAME_ID = random.randint(1000000000, 9999999999)
        with open(f"./data/games/{self.GAME_ID}.json", "w") as f:
            initData = {
                users[0].id: [],
                users[1].id: []
            }
            json.dump(initData, f)

        self.SCISSOR_ID = 0
        self.ROCK_ID = 1
        self.PAPER_ID = 2
        self.emojis = ["✌️", "✊", "🖐️"]

        self.isNotEnded = True

    scissor_emoji = "✌️"
    rock_emoji = "✊"
    paper_emoji = "🖐️"

    def selCallback(self, select: int, userID: int):
        usersID: list[int] = [self.users[0].id, self.users[1].id]
        if userID in usersID:
            with open(f"./data/games/{self.GAME_ID}.json", "r") as f:
                data = json.load(f)
            userGameResult = data[str(userID)]
            if len(userGameResult) == 0:
                data[str(userID)].append(select)

                with open(f"./data/games/{self.GAME_ID}.json", "w") as f:
                    json.dump(data, f)
                return True
            elif len(userGameResult) == 1:
                return False
        else:
            return False

    def checkAllSelected(self):
        usersID: list[int] = [self.users[0].id, self.users[1].id]
        with open(f"./data/games/{self.GAME_ID}.json", "r") as f:
            data = json.load(f)

        if len(data[str(usersID[0])]) == 1:
            if (len([data[str(usersID[1])]]) == 1):
                return True
            else:
                return False
        else:
            return False

    def ending(self):
        if self.isNotEnded:
            self.isNotEnded = False
            usersID: list[int] = [self.users[0].id, self.users[1].id]
            with open(f"./data/games/{self.GAME_ID}.json", "r") as f:
                data = json.load(f)

            user0_action = data[str(usersID[0])][0]
            user1_action = data[str(usersID[1])][0]
            result = 0
            '''
            Result 구분
            0: 비김
            1: 유저 0이 이김
            -1 유저 1이 이김
            '''

            if user0_action == user1_action:
                result = 0  # 비김
            elif user0_action == self.ROCK_ID:  # User0이 주먹을 냈다면
                if user1_action == self.SCISSOR_ID:  # User1이 가위를 냈다면
                    result = 1  # User0 승리
                else:  # User1이 보자기를 냈다면
                    result = -1  # User1 승리
            elif user0_action == self.PAPER_ID:  # User0이 보자기을 냈다면
                if user1_action == self.ROCK_ID:  # User1이 주먹를 냈다면
                    result = 1  # User0 승리
                else:  # User1이 가위를 냈다면
                    result = -1  # User1 승리
            elif user0_action == self.SCISSOR_ID:  # User0이 가위을 냈다면
                if user1_action == self.PAPER_ID:  # User1이 보자기를 냈다면
                    result = 1  # User0 승리
                else:  # User1이 주먹를 냈다면
                    result = -1  # User1 승리

            embed = discord.Embed(
                title="", description="")
            if result == 0:
                embed.description += f"```asciidoc\n📢 결과 발표 📢\n================\n[공동승리]\n- {self.users[0].name}\n- {self.users[1].name}```"
                embed.description += f"{self.users[0].mention}님이\{self.emojis[user0_action]}\n{self.users[1].mention}님이\{self.emojis[user1_action]}으로 비겼습니다"
                embed.set_author(
                    name="비겼습니다", icon_url=self.ctx.author.display_avatar)
            elif result == 1:  # self.users[0] win
                embed.description += f"```asciidoc\n📢 결과 발표 📢\n================\n[승리]\n- {self.users[0].name}\n[패배]\n- {self.users[1].name}```"
                embed.description += f"{self.users[0].mention}님이\{self.emojis[user0_action]}\n{self.users[1].mention}님이\{self.emojis[user1_action]}으로 {self.users[0].mention}님이 승리하셧습니다"
                embed.set_author(
                    name=f"{self.users[0].name} 승리", icon_url=self.users[0].display_avatar)
            elif result == -1:  # self.users[1] win
                embed.description += f"```asciidoc\n📢 결과 발표 📢\n================\n[승리]\n- {self.users[1].name}\n[패배]\n- {self.users[0].name}```"
                embed.description += f"{self.users[0].mention}님이\{self.emojis[user0_action]}\n{self.users[1].mention}님이\{self.emojis[user1_action]}으로\n{self.users[1].mention}님이 승리하셧습니다"
                embed.set_author(
                    name=f"{self.users[1].name} 승리", icon_url=self.users[1].display_avatar)
            embed.set_footer(text="게임이 종료되었어요")
            embed.timestamp = datetime.datetime.now()
            return embed
        else:
            return False

    async def processing_interaction(self, interaction: discord.interactions.Interaction, select: int):
        if self.selCallback(select, interaction.user.id):
            usersID: list[int] = [self.users[0].id, self.users[1].id]
            for userID in usersID:
                if userID == interaction.user.id:
                    usersID.remove(userID)
                    break
                continue

            await interaction.response.send_message(f"<@{usersID[0]}>님 과의 가위바위보게임에서 {self.emojis[select]}를 선택하셧습니다", ephemeral=True)

            if self.checkAllSelected():
                embed = self.ending()
                if embed == False:
                    return
                else:
                    await interaction.message.reply(content=None, embed=embed, view=None)
        else:
            await interaction.response.defer()

    @ discord.ui.button(label="가위", emoji=scissor_emoji)
    async def scissorButton_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        await self.processing_interaction(
            interaction=interaction, select=self.SCISSOR_ID)

    @discord.ui.button(label="바위", emoji=rock_emoji)
    async def rockButton_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        await self.processing_interaction(
            interaction=interaction, select=self.ROCK_ID)

    @discord.ui.button(label="보", emoji=paper_emoji)
    async def paperButton_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        await self.processing_interaction(
            interaction=interaction, select=self.PAPER_ID)


class RockScissorPaperView(discord.ui.View):
    def __init__(self, ctx: ApplicationContext):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="참가하기", emoji="🙌", style=discord.ButtonStyle.green)
    async def joinButton_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        if self.ctx.author.id == interaction.user.id:
            await interaction.response.defer()
            return

        embed = discord.Embed(
            title=f"",
            color=discord.Color.from_rgb(228, 149, 76),
            description=f"✌🏻✊🏻🖐🏻!\n{self.ctx.author.mention} **VS** {interaction.user.mention}\n> 밑에 버튼 '가위', '바위', '보'중에 하나를 선택해주세요!")
        embed.set_author(name="유저끼리 가위바위보",
                         icon_url=self.ctx.author.display_avatar)
        embed.set_footer(text="두 유저 모두 선택하면 바로 결과를 발표합니다")
        users: list[discord.User] = [self.ctx.user, interaction.user]
        await interaction.response.edit_message(view=RockScissorPaperGameView(users=users, ctx=self.ctx), embed=embed, content=f"{users[0].mention} {users[1].mention}")

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancelButton_callback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        original_message = self.ctx

        if original_message.author.id != interaction.user.id:
            await interaction.response.defer()
            return
        else:
            embed = discord.Embed(title="이 가위바위보는 취소되었어요ㅠㅠ")
            embed.set_footer(text=original_message.author.name,
                             icon_url=original_message.author.display_avatar)
            await interaction.response.edit_message(content=None, view=None, embed=embed)
            return


class RockScissorPaper(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.rock_emoji = "✊🏻"
        self.scissor_emoji = "✌🏻"
        self.paper_emoji = "🖐🏻"

    @discord.slash_command(name="가위바위보", description="가위바위보를 할 수 있어요!")
    async def rsp(self, ctx: ApplicationContext):
        embed = discord.Embed(
            title=f"",
            color=discord.Color.from_rgb(228, 149, 76),
            description=f"✌🏻✊🏻🖐🏻!\n{ctx.author.mention}**님과 가위바위보를 해요!**\n> 밑에 *'참가하기'* 버튼을 눌러 {ctx.author.mention}님과 같이 가위바위보를 할 수 있어요!")
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_author(name="유저끼리 가위바위보", icon_url=ctx.author.display_avatar)
        embed.set_footer(text="'참가하기' 버튼을 누르면 바로 시작해요!")
        await ctx.respond(content=f"{ctx.author.mention}", embed=embed, view=RockScissorPaperView(ctx=ctx))


def setup(bot):
    bot.add_cog(RockScissorPaper(bot))
