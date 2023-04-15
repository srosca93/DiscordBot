import openai
import utils


async def chatgpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

async def prompt(bot, message):

    # Check if the bot is mentioned
    if bot.user in message.mentions:
        messages = await utils.get_messages(message.channel, 100)

        prompt = (
            "You are a lighthearted, funny discord bot. The following is the last"
            " 100 messages in the channel. Each message begins with a username"
            f" followed by a colon. Your username is {bot.user.name}\n"
        )
        for message in messages:
            prompt += str(message.author) + ":" + message.content + "\n"

        prompt += (
            "You have been prompted with: "
            + message.content.replace(f"<@{bot.user.id}>", "").strip()
            + "\n"
        )
        prompt += (
            "Generate a reply but omit the prefix containing your username and"
            " colon and don't add quotes around your reply"
        )

        # Generate a response using ChatGPT
        return await chatgpt_response(prompt)
