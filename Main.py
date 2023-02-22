import discord
import os
import yaml

with open('config.yml') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

###############################################################
token = keys['Keys']['discordAPIToken']
###############################################################

bot = discord.Bot()

for i in os.listdir("commands"):
    if i.endswith(".py"):
        bot.load_extension(f"commands.{i.replace('.py','')}")


@bot.event
async def on_ready():
    print("bot is now online")


if __name__ == '__main__':
    bot.run(token)
