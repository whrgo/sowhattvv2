import discord
from discord import ApplicationContext
import json


class createProfileModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="프로필을 작성할자의 이름을 입력하세요."))
        self.add_item(discord.ui.InputText(
            label="프로필 설명을 입력해주세요.", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        profileName = self.children[0].value
        profileDesc = self.children[1].value
        with open("./data/profile.json", "r", encoding="utf-8") as f:
            format_data = json.load(f)

        formatted_data = {
            "profileName": profileName,
            "profileDesc": profileDesc
        }

        format_data['profiles'].append(formatted_data)

        with open("./data/profile.json", 'w', encoding="utf-8") as f:
            json.dump(obj=format_data, fp=f,  indent=4, ensure_ascii=False)

        embed = discord.Embed(title=f"프로필을 생성했습니다",
                              color=discord.Color.from_rgb(0, 255, 0))
        embed.add_field(name="프로필 이름", value=self.children[0].value)
        embed.add_field(name="프로필 설명", value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])


class editProfileModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="프로필을 수정할자의 이름을 입력하세요."))
        self.add_item(discord.ui.InputText(
            label="수정할 프로필 설명을 입력해주세요.", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        profileName = self.children[0].value
        profileDesc = self.children[1].value

        with open("./data/profile.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        profileData = data['profiles']

        for i in range(0, len(profileData)):
            if profileData[i]["profileName"] == profileName:
                beforeProfileDesc = data['profiles'][i]['profileDesc']
                data['profiles'][i]['profileDesc'] = profileDesc

                with open("./data/profile.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                embed = discord.Embed(title=f"수정완료: {profileName}",
                                      color=discord.Color.from_rgb(0, 255, 0))
                embed.add_field(
                    name="수정 전", value=beforeProfileDesc)
                embed.add_field(
                    name="수정 후", value=profileDesc)
                await interaction.response.send_message(embeds=[embed])
                return

        embed = discord.Embed(title="해당 프로필을 찾지 못했습니다!")
        embed.add_field(name=profileName, value=profileDesc)
        await interaction.response.send_message(embeds=[embed])


class deleteProfileView(discord.ui.View):
    options = []
    with open("./data/profile.json", "r", encoding="utf-8") as f:
        data = dict(json.load(f))

    data = data["profiles"]
    for e in data:
        profileName = e["profileName"]
        profileDesc = e["profileDesc"]
        options.append(discord.SelectOption(
            label=profileName, description=profileDesc))

    @ discord.ui.select(
        placeholder="삭제할 프로필을 선택해주세요",
        min_values=1,
        max_values=1,
        options=options
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        profileName = select.values[0]

        with open("./data/profile.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        profileData = data['profiles']

        for i in range(0, len(profileData)):
            if profileData[i]["profileName"] == profileName:
                profileDesc = profileData[i]["profileDesc"]

                data['profiles'].remove(profileData[i])
                with open("./data/profile.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                embed = discord.Embed(title=f"프로필을 삭제했습니다!",
                                      color=discord.Color.from_rgb(0, 255, 0))
                embed.add_field(
                    name=f"\"{profileName}\" 프로필을 삭제했습니다", value="", inline=False)
                await interaction.response.send_message(embeds=[embed])
                return


class deleteProfileModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="프로필을 삭제할자의 이름을 입력하세요."))

    async def callback(self, interaction: discord.Interaction):
        profileName = self.children[0].value

        with open("./data/profile.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        profileData = data['profiles']

        for i in range(0, len(profileData)):
            if profileData[i]["profileName"] == profileName:
                profileDesc = profileData[i]["profileDesc"]

                data['profiles'].remove(profileData[i])
                with open("./data/profile.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                embed = discord.Embed(title=f"프로필을 삭제했습니다!",
                                      color=discord.Color.from_rgb(0, 255, 0))
                embed.add_field(
                    name=f"\"{profileName}\" 프로필을 삭제했습니다", value="", inline=False)
                await interaction.response.send_message(embeds=[embed])
                return

        embed = discord.Embed(title=f"해당 프로필을 찾지 못했습니다",
                              color=discord.Color.from_rgb(255, 0, 0))
        await interaction.response.send_message(embeds=[embed])


def listProfile():
    with open("./data/profile.json", 'r', encoding="utf-8") as f:
        data = json.load(f)

    if len(data["profiles"]) == 0:
        return False

    message = ""

    embed = discord.Embed(title="프로필 리스트")

    for i in range(0, len(data['profiles'])):
        profileName = data['profiles'][i]['profileName']
        profileDesc = data['profiles'][i]['profileDesc']
        embed.add_field(name=profileName, value=profileDesc)

    return embed


class Profile(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ discord.slash_command(name="프로필", description="사용자 프로필을 지정할 수 있습니다")
    @ discord.option("type", description="프로필 관련된 명령어를 골라주세요", type=str, choices=["생성", "수정", "삭제", "리스트", "보기"])
    async def profileMain(self, ctx: discord.ApplicationContext, type: str):
        choices = ["생성", "수정", "삭제", "리스트", "보기"]
        if type == choices[0]:  # 생성
            modal = createProfileModal(title="프로필 생성")
            await ctx.send_modal(modal)
        elif type == choices[1]:  # 수정
            modal = editProfileModal(title="프로필 수정")
            await ctx.send_modal(modal)
        elif type == choices[2]:  # 삭제
            await ctx.respond(content="삭제할 프로필을 골라주세요", view=deleteProfileView(), ephemeral=True)
        elif type == choices[3]:  # 리스트
            value = listProfile()
            if value == False:
                await ctx.respond(content="프로필이 비어있습니다:)", ephemeral=True)
            else:
                await ctx.respond(embed=value)
        elif type == choices[4]:  # 보기
            await ctx.respond(content="나중에 만들거임 귀찮음 ㅋ..ㅎ", ephemeral=True)


def setup(bot):
    bot.add_cog(Profile(bot))
