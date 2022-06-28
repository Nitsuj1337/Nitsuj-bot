import discord
from discord.ext import commands

class autre(commands.Cog):
  '''All the command for other stuff (rn reminder)'''
  def __init__(self, client):
    self.client = client
    self.rappels={}

  @commands.command(name = 'checkrappels',help="voir les rappels de quelqu'un",aliases=['cr'])
  async def checkrappel(self, ctx, user : discord.Member):
    if(user.id not in self.rappels):
      return await ctx.reply("Il n'y a pas de rappels pour cette personne.")
    embed=discord.Embed(color=discord.Color.blue())
    embed.set_author(name="Les rappels de " + user.display_name, icon_url=user.avatar_url)
    for index, value in enumerate(self.rappels[user.id].items(),start=1):
      embed.add_field(name="Rappel "+str((index)) + " : ", value= value[1], inline=False)
      print(value)
    await ctx.reply(embed=embed)

  @commands.command(name="rappel", help="ajouter un rappel pour quelqu'un")
  async def _rappel(self, ctx, user : discord.Member, *rappel):
    rappel = " ".join(map(str, rappel))
    if(user.id not in self.rappels):
      self.rappels[user.id] = { 1 : rappel}
      print(self.rappels)
    else:
      self.rappels[user.id][len(self.rappels[user.id])+1] = rappel
      print(self.rappels)
    await ctx.reply('Fait.')

def setup(client):
  client.add_cog(autre(client))
