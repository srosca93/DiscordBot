import os
import json
import requests
import discord
from discord.ext import commands
import openai
import boto3


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_secret(secret_name, secret_key):
    region_name = "us-west-1"

    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name
    )
    
    response = json.loads(client.get_secret_value(SecretId=secret_name)["SecretString"])
    return response[secret_key]


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

async def get_messages(channel, num_messages):
    if channel.permissions_for(channel.guild.me).read_messages:
        messages = []
        async for message in channel.history(limit=num_messages, oldest_first=False):
            messages.insert(0,message)
    return messages


async def chatgpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')


@bot.command()
async def generate(ctx, *args):
    prompt = ' '.join(args)
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_data = download_image(response["data"][0]["url"])
        if image_data is not None:
            with open("downloaded_image.png", "wb") as f:
                f.write(image_data)
            await ctx.send(file=discord.File("downloaded_image.png"))
        else:
            await ctx.send("Failed to download the image.")
    except:
        await ctx.send("Invalid prompt")


@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check for messages starting with "!"
    if message.content.startswith('!'):
        # Process commands
        await bot.process_commands(message)

    else:
        # Check if the bot is mentioned
        if bot.user in message.mentions:

            messages = await get_messages(message.channel, 100)

            prompt = f"You are a lighthearted, funny discord bot. The following is the last 100 messages in the channel. Each message begins with a username followed by a colon. Your username is {bot.user.name}\n"
            for message in messages:
                prompt += str(message.author) + ":" + message.content + "\n"

            prompt += "You have been prompted with: " + message.content.replace(f'<@{bot.user.id}>', '').strip() + "\n"
            prompt += "Generate a reply but omit the prefix containing your username and colon and don't add quotes around your reply"

            # Generate a response using ChatGPT
            gpt_response = await chatgpt_response(prompt)

            # Send the response
            await message.channel.send(gpt_response)

DISCORD_TOKEN = get_secret("discord_token","DISCORD_TOKEN")
openai.api_key = get_secret("open_ai_key","OPEN_AI_KEY")

bot.run(DISCORD_TOKEN)
