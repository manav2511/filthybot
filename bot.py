import asyncio
import json
import os
import sqlite3
import sys

import discord
import requests
from discord.ext import commands
from osuapi import OsuApi, ReqConnector

from functions import *

#Read APIs
with open("token.txt") as Token_read:
    TOKEN = Token_read.readline().strip()
with open("osuapikey.txt") as api_read:
    apicode = api_read.readline().strip()


#Initialize SQLite3
conn = sqlite3.connect('osu.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS USERS(DISCORD_ID INTEGER PRIMARY KEY,
    OSU_ID INTEGER,
    DAYS INTEGER,
    TOTAL INTEGER)""")


api = OsuApi(apicode, connector=ReqConnector())

client = commands.Bot(command_prefix='f!')


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


@client.command(pass_context=True) #Completed with Rich embed. 
async def osu(context, *param):
    if len(param) == 0:
        c.execute("SELECT * FROM USERS WHERE DISCORD_ID = ?",(context.message.author.id,))
        data=c.fetchone()
        user_id = data[1]
        embed = display_profile(user_id)
        await client.send_message(context.message.channel, embed=embed)
    elif len(param) == 1:
        embed = display_profile(param)
        await client.send_message(context.message.channel, embed=embed)
    else:
        for var in param:
            embed = display_profile(var)
            await client.send_message(context.message.channel, embed=embed)

@client.command(pass_context=True)
async def top(context, *params):
    (user, amt) = params_seperator(context, *params)
    embed = Top_Scores(user, amt)
    await client.send_message(context.message.channel, embed=embed)


@client.command(pass_context=True) #Completed With Rich Embed.
async def recent(context, *params):
    (user, amt) = params_seperator(context, *params)
    embed = recent_Scores(user, amt)
    await client.send_message(context.message.channel, embed=embed)

@client.command(pass_context = True)
async def setDB(ctx, param):    
    discord_id = ctx.message.author.id
    osu_id = api.get_user(param)[0].user_id
    c.execute("SELECT * FROM USERS WHERE DISCORD_ID = ?",(discord_id,))
    data=c.fetchone()
    if data is None:
        c.execute("INSERT INTO USERS(DISCORD_ID, OSU_ID, DAYS, TOTAL) VALUES (?, ?, 0, 0)",(discord_id, osu_id))
        conn.commit()
        tit = 'succesfully set {} IGN as {}'.format(ctx.message.author, param)
        em = discord.Embed(title=tit, colour=0xDEADBF)
        await client.say(embed=em)
    else:
        await client.say("Record Already Exists")

@client.command(pass_context = True)
async def compare(ctx, user1, user2):
	em = check(user1, user2)
	await client.send_message(ctx.message.channel, embed=em)
	
@client.command(pass_context = True)
async def topr(context, *params):
    (user, amt)=params_seperator(context, *params)
    em=recent_top(user, amt)
    await client.send_message(context.message.channel, embed=em)


client.run(TOKEN)
