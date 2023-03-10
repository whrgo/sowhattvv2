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

    @discord.ui.button(label="λ μ§ μλ ₯", style=discord.ButtonStyle.gray, emoji="π")
    async def inputDateCallback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        await interaction.response.send_message(content="μ΄κΈ°λ₯μ μμ§ μ€λΉμ€μ μμ΄μ!", ephemeral=True)

    @discord.ui.button(label="μ΄μ ", emoji="π", style=discord.ButtonStyle.green)
    async def yesterdayButtonCallback(self, button: discord.ui.Button, interaction: discord.interactions.Interaction):
        yesterday = date.today() - timedelta(1)
        filename = getFilename(yesterday)
        getFileData(filename=filename)

    @discord.ui.button(label="μ€λ", emoji="π", style=discord.ButtonStyle.primary)
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
    @discord.commands.slash_command(name="μ²΄ν¬", description="μΆμμ²΄ν¬λ₯Ό ν  μ μμ΄μ!")
    @discord.option(name="λ©μμ§", type=str, description="μΆμμ²΄ν¬μ λ©μμ§λ₯Ό λ¨κΈΈ μ μμ΄μ!")
    async def doAttendance(self, ctx: ApplicationContext, λ©μμ§: str):
        if saveAttendanceJson(λ©μμ§, ctx.author.id):
            embed = discord.Embed(
                title="", description=λ©μμ§,
                color=discord.Color.from_rgb(0, 255, 0))
            embed.set_author(
                name="μΆμμ²΄ν¬ μλ£!", icon_url=ctx.author.display_avatar)
            embed.timestamp = datetime.now()
            embed.set_footer(text=ctx.author.name)
            await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="", description="",
                color=discord.Color.from_rgb(255, 0, 0))
            embed.set_author(
                name="λΉμ μ μ΄λ―Έ μΆμμ²΄ν¬λ₯Ό νμμμ..!", icon_url=ctx.author.display_avatar)
            embed.timestamp = datetime.now()
            await ctx.respond(embed=embed)

    @discord.commands.slash_command(name="νμΈ", description="μΆμμ μΈμ  νλμ§ νμΈν  μ μμ΄μ!")
    async def checkAttendance(self, ctx: ApplicationContext):
        await ctx.respond("> μ΄λλ μ μΆμ νμΈ νν©μ νμΈνμ€κ±΄κ°μ..?β€", view=checkAttendanceView())


def setup(bot: discord.Bot):
    bot.add_application_command(
        AttendanceCheckSlashGroup(name="μΆμ", description="νλ‘ μ¦μ­μμ μΆμμ²΄ν¬ κ΄λ ¨ λͺλ Ήμ΄λ€μ΄μμ!"))
