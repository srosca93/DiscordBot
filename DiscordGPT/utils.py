import boto3
import os
import json


local_dev = True

secret_names = {
    "discord": {
        "aws": {"secret_name": "discord_token", "secret_key": "DISCORD_TOKEN"},
        "local": "DISCORD_TOKEN",
    },
    "openai": {
        "aws": {"secret_name": "open_ai_key", "secret_key": "OPEN_AI_KEY"},
        "local": "OPENAI_API_KEY",
    },
}


def get_secret(secret_name, secret_key):
    region_name = "us-west-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    response = json.loads(client.get_secret_value(SecretId=secret_name)["SecretString"])
    return response[secret_key]


def get_token(name):
    if local_dev:
        return os.environ.get(secret_names[name]["local"])
    else:
        return get_secret(secret_names[name]["secret_name"]["secret_key"])


async def get_messages(channel, num_messages):
    if channel.permissions_for(channel.guild.me).read_messages:
        messages = []
        async for message in channel.history(limit=num_messages, oldest_first=False):
            messages.insert(0, message)
    return messages

