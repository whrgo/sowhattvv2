import discord
from discord import ApplicationContext
import json


class enrollWebhookModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(
            label="웹후크 이름을 입력해주세요", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(
            label="웹후크 링크를 입력해주세요"))

    async def callback(self, interaction: discord.Interaction):
        enrollName = self.children[0].value
        webhookLink = self.children[1].value

        if not webhookLink.startswith("https://"):
            embed = discord.Embed(title=f"웹후크 링크가 아니에요!",
                                  color=discord.Color.from_rgb(255, 0, 0))
            await interaction.response.send_message(embeds=[embed])
            return

        with open("./data/webhookEnrolls.json", "r", encoding="utf-8") as f:
            data = dict(json.load(f))

        data[enrollName] = webhookLink

        with open("./data/webhookEnrolls.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        embed = discord.Embed(title=f"웹후크를 등록했습니다",
                              color=discord.Color.from_rgb(0, 255, 0))
        embed.add_field(
            name=self.children[0].value, value=self.children[1].value)
        await interaction.response.send_message(embeds=[embed])


class deleteWebhookView(discord.ui.View):
    options = []
    with open("./data/webhookEnrolls.json", "r", encoding="utf-8") as f:
        data = dict(json.load(f))

    for e in data:
        webhookName = str(e)
        webhookLink = str(data[e])[:60] + "..."
        options.append(discord.SelectOption(
            label=webhookName, description=webhookLink))

    @discord.ui.select(
        placeholder="삭제할 웹후크를 선택해주세요",
        min_values=1,
        max_values=1,
        options=options
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        selected_webhook = select.values[0]

        with open("./data/webhookEnrolls.json", "r", encoding="utf-8") as f:
            data = dict(json.load(f))

        del data[selected_webhook]
        with open("./data/webhookEnrolls.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        embed = discord.Embed(title=f"웹후크를 삭제했습니다",
                              color=discord.Color.from_rgb(0, 255, 0), description=selected_webhook)
        await interaction.response.send_message(content="", view=None, embeds=[embed])


def listWebhookView():
    embed = discord.Embed(
        title="웹후크 등록리스트", color=discord.Color.from_rgb(0, 255, 0))
    with open("./data/webhookEnrolls.json", "r", encoding="utf-8") as f:
        data = dict(json.load(f))
    for e in data:
        embed.add_field(name=str(e), value=str(data[e]))

    return embed


class Webhook(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="웹훅", description="웹훅 관련 명령어")
    @discord.option("type", description="프로필 관련된 명령어를 골라주세요", type=str, choices=["등록", "삭제", "등록리스트", "전송"])
    async def webhookMain(self, ctx: ApplicationContext, type: str):
        choices = ["등록", "삭제", "등록리스트", "전송"]
        if type == choices[0]:  # 등록
            modal = enrollWebhookModal(title="웹훅 등록")
            await ctx.send_modal(modal)
        elif type == choices[1]:  # 삭제
            with open("./data/webhookEnrolls.json", "r", encoding="utf-8") as f:
                data = dict(json.load(f))
            if len(data) == 0:
                await ctx.respond("등록된 웹후크가 없습니다", ephemeral=True)
                return
            await ctx.respond(content="삭제할 웹후크를 선택해주세요", view=deleteWebhookView(), ephemeral=True)
        elif type == choices[2]:  # 등록리스트
            with open("./data/webhookEnrolls.json", "r", encoding="utf-8") as f:
                data = dict(json.load(f))
            if len(data) == 0:
                await ctx.respond("등록된 웹후크가 없습니다", ephemeral=True)
                return
            embed = listWebhookView()
            await ctx.respond(embed=embed)
        elif type == choices[3]:
            await ctx.respond("귀찮아서 나중에 만들게요!")
            pass


def setup(bot):
    bot.add_cog(Webhook(bot))
