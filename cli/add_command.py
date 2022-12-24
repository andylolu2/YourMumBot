import json
import os

import click
import dotenv
import requests

DISCORD_API = "https://discord.com/api/v10"


def header(bot_token: str):
    return {"Authorization": f"Bot {bot_token}"}


def post(endpoint: str, bot_token: str, json_: dict):
    url = DISCORD_API + endpoint
    return requests.post(url, headers=header(bot_token), json=json_)


def get(endpoint: str, bot_token: str):
    url = DISCORD_API + endpoint
    return requests.get(url, headers=header(bot_token))


def delete(endpoint: str, bot_token: str):
    url = DISCORD_API + endpoint
    return requests.delete(url, headers=header(bot_token))


def pprint(obj):
    if isinstance(obj, (dict, list)):
        print(json.dumps(obj, indent=2))
    else:
        print(obj)


@click.group()
@click.pass_context
@click.option("--prod", default=False, is_flag=True)
def cli(ctx: click.Context, prod: bool):
    ctx.ensure_object(dict)

    if prod:
        dotenv.load_dotenv(".prod.env")
    else:
        dotenv.load_dotenv(".dev.env")

    ctx.obj["APP_ID"] = os.environ["DISCORD_APP_ID"]
    ctx.obj["BOT_TOKEN"] = os.environ["DISCORD_BOT_TOKEN"]


@cli.command()
@click.pass_context
@click.option("-g", "--guild-id", required=True)
@click.option("-f", "--command-file", required=True)
def add_guild_command(ctx: click.Context, guild_id, command_file):
    # https://discord.com/developers/docs/interactions/application-commands#create-guild-application-command
    app_id = ctx.obj["APP_ID"]
    bot_token = ctx.obj["BOT_TOKEN"]
    endpoint = f"/applications/{app_id}/guilds/{guild_id}/commands"

    with open(command_file, "r") as f:
        json_ = json.load(f)

    response = post(endpoint, bot_token, json_)
    pprint(response.json())


@cli.command()
@click.pass_context
@click.option("-g", "--guild-id", required=True)
@click.option("-i", "--command-id", required=True)
def delete_guild_command(ctx: click.Context, guild_id, command_id):
    # https://discord.com/developers/docs/interactions/application-commands#delete-guild-application-command
    app_id = ctx.obj["APP_ID"]
    bot_token = ctx.obj["BOT_TOKEN"]
    endpoint = f"/applications/{app_id}/guilds/{guild_id}/commands/{command_id}"

    response = delete(endpoint, bot_token)
    if response.ok:
        pprint(response)
    else:
        pprint(response.json())


@cli.command()
@click.pass_context
@click.option("-g", "--guild-id", required=True)
def get_guild_commands(ctx: click.Context, guild_id):
    # https://discord.com/developers/docs/interactions/application-commands#get-guild-application-commands
    app_id = ctx.obj["APP_ID"]
    bot_token = ctx.obj["BOT_TOKEN"]
    endpoint = f"/applications/{app_id}/guilds/{guild_id}/commands"

    response = get(endpoint, bot_token)
    pprint(response.json())


@cli.command()
@click.pass_context
@click.option("-f", "--command-file", required=True)
def add_global_command(ctx: click.Context, command_file):
    # https://discord.com/developers/docs/interactions/application-commands#create-global-application-command
    app_id = ctx.obj["APP_ID"]
    bot_token = ctx.obj["BOT_TOKEN"]
    endpoint = f"/applications/{app_id}/commands"

    with open(command_file, "r") as f:
        json_ = json.load(f)

    response = post(endpoint, bot_token, json_)
    pprint(response.json())


@cli.command()
@click.pass_context
@click.option("-i", "--command-id", required=True)
def delete_global_command(ctx: click.Context, command_id):
    # https://discord.com/developers/docs/interactions/application-commands#delete-global-application-command
    app_id = ctx.obj["APP_ID"]
    bot_token = ctx.obj["BOT_TOKEN"]
    endpoint = f"/applications/{app_id}/commands/{command_id}"

    response = delete(endpoint, bot_token)
    if response.ok:
        pprint(response)
    else:
        pprint(response.json())


@cli.command()
@click.pass_context
def get_global_commands(ctx: click.Context):
    # https://discord.com/developers/docs/interactions/application-commands#get-global-application-commands
    app_id = ctx.obj["APP_ID"]
    bot_token = ctx.obj["BOT_TOKEN"]
    endpoint = f"/applications/{app_id}/commands"

    response = get(endpoint, bot_token)
    pprint(response.json())


if __name__ == "__main__":
    cli()
