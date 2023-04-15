import requests
import discord
from discord.ext import commands
import openai

import utils
import gpt

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")


def to_upper(argument):
    return argument.upper()


@bot.command()
async def up(ctx, *, content: to_upper):
    await ctx.send(content)


@bot.command()
async def generate(ctx, *args):
    prompt = " ".join(args)
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_data = download_image(response["data"][0]["url"])
    if image_data is not None:
        with open("downloaded_image.png", "wb") as f:
            f.write(image_data)
        await ctx.send(file=discord.File("downloaded_image.png"))
    else:
        await ctx.send("Failed to download the image.")


@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check for messages starting with "!"
    if message.content.startswith("!"):
        # Process commands
        await bot.process_commands(message)

    else:

        gpt_response = await gpt.prompt(bot, message)

        # Send the response
        if gpt_response:
            await message.channel.send(gpt_response)


openai.api_key = utils.get_token("openai")
bot.run(utils.get_token("discord"))
