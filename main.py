import os
import discord
import music
import autre
from discord.ext import commands

cogs = [music,autre]

intents =  discord.Intents.default()
intents.members = True
intents.messages = True

client = commands.Bot(command_prefix="?",intents = intents)

for i in range(len(cogs)):
    cogs[i].setup(client)

@client.event
async def on_ready():
    print("Je suis "+client.user.name)
    print('Ready.')
    print('------------')

client.run(os.environ['token'])
