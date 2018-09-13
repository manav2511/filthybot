import os
import sys

import discord
from discord.ext import commands

import requests
from functions import *

from osuapi import OsuApi, ReqConnector

Token_read = open("token.txt")
api_read = open("osuapikey.txt")


TOKEN = Token_read.readline().strip()
apicode = api_read.readline().strip()

import json


api = OsuApi(apicode, connector=ReqConnector())

client = commands.Bot(command_prefix = 'f!')

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)


@client.event
async def on_ready():
    ready_message = "Logged in as " + client.user.name + "\n ID:" + client.user.id
    print(ready_message)


@client.command()
async def ping():
    await client.say('pong')


@client.command()
async def shutdown():
    await client.logout()


@client.command()
async def restart():
    restart_program()
    await client.close()


@client.command(pass_context=True)
async def osu(context, param='xD'):
    if param != 'xD':
        em = display(param)
    else:
        with open('records.json') as f:
            data = json.load(f)
        id = data[context.message.author.id]["user_id"]
        print(id)
        em = display(id)
    await client.send_message(context.message.channel, embed=em)


@client.command(pass_context=True)
async def top(context, user, amt=5):
    scores = api.get_user_best(user,limit=amt)
    em = scoredisp(user, scores, amt)
    await client.send_message(context.message.channel, embed=em)

@client.command(pass_context=True)
async def recent(context, param, amt=5):
    scores = api.get_user_recent(param,limit=amt)
    em = recentdisp(param, scores, amt)
    await client.send_message(context.message.channel, embed=em)

@client.command(pass_context=True)
async def set(ctx,param):
    ''' Sets a username.
    many usernames can be set to one discord iD and every time this command is
    called, number of days of filthy farmer gets reset
    '''
    try:
        user_id=api.get_user(param)[0].user_id
        discord_id=ctx.message.author.id   # Discord id
        new_data = {
            'user_id': user_id,
            'days': 0,   # Days of filthy farmer left
            'total': 0  # Total days of filthy farmer earned
        }

        with open('records.json') as f:
            data = json.load(f)
        data[str(discord_id)] = new_data
        with open('records.json', 'w') as f:
            json.dump(data, f, indent=2)
        tit = 'succesfully set {} IGN as {}'.format(ctx.message.author, param)
        em = discord.Embed(title= tit, colour=0xDEADBF)
        await client.say(embed=em)

    except IndexError:
        await client.say('invalid username')


    


client.run(TOKEN)
