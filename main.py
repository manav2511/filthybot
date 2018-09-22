import os
import sys
import traceback

import discord
from discord.ext import commands

import constants
import database

initial_modules = ['modules.simple', 'modules.osu']

constants = constants.Constants()
database = database.Database(constants.DATABASE)
client = commands.Bot(command_prefix=constants.PREFIX)
client.database = database

if __name__ == '__main__':
    for module in initial_modules:
        try:
            client.load_extension(module)
            print("Loaded {}".format(module))
        except Exception as e:
            print("Failed to load module {}".format(module))
            traceback.print_exc()

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

@client.event
async def on_ready():
    ready_message = "Logged in as " + client.user.name + "\n ID:" + str(client.user.id)
    print(ready_message)

@client.command(name="load")
async def load(ctx, module_name : str):
    #Loads a module.
    try:
        client.load_extension(module_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(module_name))

@client.command(name="unload")
async def unload(ctx, module_name : str):
    #Unloads an extension.
    client.unload_extension(module_name)
    await ctx.send("{} unloaded.".format(module_name))


@client.command(name='shutdown')
async def shutdown(ctx):
    await client.logout()


@client.command(name='restart')
async def restart(ctx):
    restart_program()
    await client.close()

client.run(database.get_discord_auth())



# @client.command(pass_context=True)
# async def start_track(context):
#     counter = 0
#     while not client.is_closed:
#         counter += 1
#         await client.say("Before Track: " + str(counter))
#         scores = track()
#         # Xavier you need to print all the scores in the list along with the IGN of the player who made the score
#         await client.send_message(context.message.channel, "After track: " + str(counter))
#         await asyncio.sleep(120)
