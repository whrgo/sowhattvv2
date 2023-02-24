import discord
from discord import ApplicationContext
import asyncio
import json
from datetime import date, timedelta, datetime
from arrow import Arrow

PATH = "./data/attendance/"


class checkAttendanceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="날짜 입력", style=discord.ButtonStyle.gray, emoji="📅")
    async def inputDateCallback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        await interaction.response.send_message(content="이기능은 아직 준비중에 있어요!", ephemeral=True)

    @discord.ui.button(label="어제", emoji="📅", style=discord.ButtonStyle.green)
    async def yesterdayButtonCallback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        yesterday = date.today() - timedelta(1)
        filename = getFilename(yesterday)
        getFileData(filename=filename)

    @discord.ui.button(label="오늘", emoji="📅", style=discord.ButtonStyle.primary)
    async def todayButtonCallback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        today = date.today()
        getFilename(today)


def getFileData(filename: str):
    try:
        file = open(f"{PATH}{filename}", "r")
    except FileNotFoundError:
        return False

    embed = discord.Embed(title="", description="")

    data = json.load(file)
    for userData in data["checked"]:
        userID: int = data["checked"][userData]["userID"]
        msg = data["checked"][userData]["message"]
        # embed.add_field(name=)


def makeTimestamp(datetime: datetime):
    int_timestamp = datetime.timestamp()
    int_timestamp = int(int_timestamp)
    return f"<t:{int_timestamp}>"


def getFilename(dt):
    year = str(dt.year)[2:]
    month = dt.month
    if month < 10:
        month = "0" + str(month)
    else:
        month = str(month)
    day = dt.day
    if day < 10:
        day = "0" + str(month)
    else:
        day = str(day)
    filename = f"{year}{month}{day}.json"
    return filename


def initAttendanceJson(filename: str):
    with open(f"{PATH}{filename}", "w") as f:
        json.dump({"checked": {}}, f, indent=2)
    f = open(f"{PATH}{filename}", "r")

    return f


def checkAlreadyChecked(data, userID, filename):
    with open(f"{PATH}{filename}", "r") as f:
        data = json.load(f)

    for checkedUser in data["checked"]:
        if data["checked"][checkedUser]["userID"] == userID:
            return False
    return True


def saveAttendanceJson(message: str, userID: int):
    filename = getFilename(datetime.now())
    try:
        file = open(f"{PATH}{filename}", "r")
    except FileNotFoundError:
        file = initAttendanceJson(filename=filename)
    data = json.load(file)
    if checkAlreadyChecked(data, userID, filename):
        # TODO: add data
        data["checked"][userID] = {"userID": userID, "message": message}
        with open(f"{PATH}{filename}", "w") as f:
            json.dump(data, f, indent=2)
        return True
    else:
        return False


class AttendanceCheckSlashGroup(discord.commands.SlashCommandGroup):
    @discord.commands.slash_command(name="체크", description="출석체크를 할 수 있어요!")
    @discord.option(name="메시지", type=str, description="출석체크에 메시지를 남길 수 있어요!")
    async def doAttendance(self, ctx: ApplicationContext, 메시지: str):
        if saveAttendanceJson(메시지, ctx.author.id):
            embed = discord.Embed(
                title="", description=메시지,
                color=discord.Color.from_rgb(0, 255, 0))
            embed.set_author(
                name="출석체크 완료!", icon_url=ctx.author.display_avatar)
            embed.timestamp = datetime.now()
            embed.set_footer(text=ctx.author.name)
            await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="", description="",
                color=discord.Color.from_rgb(255, 0, 0))
            embed.set_author(
                name="당신은 이미 출석체크를 했잖아요..!", icon_url=ctx.author.display_avatar)
            embed.timestamp = datetime.now()
            await ctx.respond(embed=embed)

    @discord.commands.slash_command(name="확인", description="출석을 언제 했는지 확인할 수 있어요!")
    async def checkAttendance(self, ctx: ApplicationContext):
        await ctx.respond("> 어느날의 출석 확인 현황을 확인하실건가요..?❤", view=checkAttendanceView())


def setup(bot: discord.Bot):
    bot.add_application_command(
        AttendanceCheckSlashGroup(name="출석", description="프론즈섭에서 출석체크 관련 명령어들이에요!"))
