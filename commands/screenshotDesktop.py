import pyautogui
import discord
from discord import ApplicationContext
import uuid
import cv2
import random
import json
import os
from discord.ui import Button


PRONS_SERVER = 939105900977864725


def checkProblemNotEnd(fileID: int, problemID: int):
    with open(f"./data/problems/{fileID}/{problemID}.json", "r") as f:
        data = json.load(f)
    if data["problemEnd"] == -1:
        return True
    else:
        return False


def checkAlreadyGetProblemd(fileID: int, authorID: int):
    for filename in os.listdir(f"./data/problems/{fileID}"):
        filepath = f"./data/problems/{fileID}/{filename}"
        with open(filepath, "r") as f:
            data = json.load(f)
        if data["openProblemUser"] == authorID:
            return True

    return False


class PyautoguiID(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    def mosaic(self, src, ratio):
        """
        ### 모자이크 기능
        :param src: 이미지 소스
        :param ratio: 모자이크 비율
        :return: 모자이크가 처리된 이미지
        """
        small = cv2.resize(src, None, fx=ratio, fy=ratio,
                           interpolation=cv2.INTER_NEAREST)
        mosaic_img = cv2.resize(
            small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
        return mosaic_img

    def opencv_img_save(self, img, save_img_name):
        """
        ### 처리 이미지 저장 기능
        :param img: 저장할 이미지
        :param save_img_path: 이미지 저장 경로
        :param save_img_name: 저장할 이미지 명
        """
        cv2.imwrite(save_img_name, img)

    @discord.slash_command(name="화면스크린샷")
    async def WindowScreenshot(self, ctx: ApplicationContext):
        if ctx.guild.id != PRONS_SERVER:
            await ctx.respond("이 명령어는 프론즈 서버에서만 가능해요!")
            return

        FILE_ID = random.randint(1000000000, 9999999999)
        os.mkdir(f"./data/problems/{FILE_ID}")

        img = pyautogui.screenshot()
        filename = "./temp/" + str(str(uuid.uuid4()).replace("-", "")) + ".jpg"
        img.save(filename)

        original_img = cv2.imread(filename=filename)
        mosaic_img = self.mosaic(original_img, 0.03)
        mosaic_filename = "./temp/" + \
            str(str(uuid.uuid4()).replace("-", "")) + ".jpg"
        self.opencv_img_save(mosaic_img, mosaic_filename)

        async def get_original_image_button_callback(interaction: discord.interactions.Interaction):
            if checkAlreadyGetProblemd(fileID=FILE_ID, authorID=interaction.user.id):
                await interaction.response.send_message("당신은 이미 문제를 요청했었잖아요..!", ephemeral=True)
                return

            PROBLEM_ID = random.randint(1000000000, 9999999999)

            mnums = [random.randint(-1000, 1000), random.randint(-1000, 1000)]
            operators = ["+", "-", "×"]
            operator = operators[random.randrange(0, len(operators))]
            answer = 0
            if operator == "+":
                answer = mnums[0] + mnums[1]
            elif operator == "-":
                answer = mnums[0] - mnums[1]
            elif operator == "×":
                answer = mnums[0] * mnums[1]

            with open(f"./data/problems/{FILE_ID}/{PROBLEM_ID}.json", "w") as f:
                json.dump({"screenshotFilePath": filename, "PROBLEMID": PROBLEM_ID,
                          "problemEnd": -1, "openProblemUser": interaction.user.id,
                           "problem": {"n1": mnums[0], "n2": mnums[1], "operator": operator, "answer": answer}}, f, indent=2)

            async def answer_button_callback(interaction: discord.interactions.Interaction):
                if checkProblemNotEnd(FILE_ID, PROBLEM_ID):
                    with open(filename, "rb") as f:
                        file = discord.File(f, filename, spoiler=True)
                    await interaction.response.send_message("정답입니다!", file=file, ephemeral=True)
                    with open(f"./data/problems/{FILE_ID}/{PROBLEM_ID}.json", "r") as f:
                        data = json.load(f)
                    data["problemEnd"] = 0
                    with open(f"./data/problems/{FILE_ID}/{PROBLEM_ID}.json", "w") as f:
                        json.dump(data, f, indent=2)
                else:
                    await interaction.response.send_message("이미 문제를 푸셧습니다ㅋ", ephemeral=True)

            async def noAnswer_button_callback(interaction: discord.interactions.Interaction):
                if checkProblemNotEnd(FILE_ID, PROBLEM_ID):
                    embed = discord.Embed(title="오답입니다")
                    embed.set_footer(text="이걸 틀리냐? 정신병원 ㄱㄱ")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    with open(f"./data/problems/{FILE_ID}/{PROBLEM_ID}.json", "r") as f:
                        data = json.load(f)
                    data["problemEnd"] = 0
                    with open(f"./data/problems/{FILE_ID}/{PROBLEM_ID}.json", "w") as f:
                        json.dump(data, f, indent=2)
                else:
                    await interaction.response.send_message("이미 문제를 푸셧습니다ㅋ", ephemeral=True)

            select_answer_buttons = []
            random_answer_count = random.randint(0, 2)
            for i in range(0, 3):
                if i == random_answer_count:
                    label = answer
                    btn = Button(label=f"{label}")
                    btn.callback = answer_button_callback
                    select_answer_buttons.append(btn)
                else:
                    random_num = random.randint(-20, 20)
                    while random_num == 0:
                        random_num = random.randint(-20, 20)

                    label = answer + random_num
                    btn = Button(label=f"{label}")
                    btn.callback = noAnswer_button_callback
                    select_answer_buttons.append(btn)

            view = discord.ui.View(timeout=None)
            for answer_button in select_answer_buttons:
                view.add_item(answer_button)

            problem_embed = discord.Embed(
                title=f"({mnums[0]}) ​{operator} ​({mnums[1]})")
            await interaction.response.send_message(content="원본 이미지를 보려면 수학문제를 풀어야해요!", embed=problem_embed, view=view, ephemeral=True)

        get_original_image_button = discord.ui.Button(
            label="원본 이미지 보기", style=discord.ButtonStyle.grey)
        get_original_image_button.callback = get_original_image_button_callback

        view = discord.ui.View(timeout=None)
        view.add_item(get_original_image_button)

        with open(mosaic_filename, "rb") as f:
            file = discord.File(f, mosaic_filename, spoiler=True)
        await ctx.respond(content="이제 모자이크 된 이미지를 보내요!", file=file, view=view)


def setup(bot):
    bot.add_cog(PyautoguiID(bot))
