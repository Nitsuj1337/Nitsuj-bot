import yt_dlp
import discord
from discord.ext import commands

FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -probesize 10M'
}
YDL_OPTIONS = {
        'format': 'bestaudio',
        'extractaudio': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
}

class music(commands.Cog):

    '''All the command for music'''

    def __init__(self, client):
      self.client = client
      self.queue = {}
      self.playing = []

    def check_queue(self,ctx,guild_id):
      if self.queue[guild_id][1] != []:
        voice = ctx.guild.voice_client
        print(self.queue[guild_id])
        source = self.queue[guild_id][1]
        if len(self.queue[guild_id]) == 1:
          self.queue[guild_id][1] = []
        elif len(self.queue[guild_id]) == 2:
            self.queue[guild_id][1] = self.queue[guild_id][2]
            self.queue[guild_id][2] = []
        else:
          for index,music in enumerate(self.queue[guild_id],start=2):
            if music == []:
              break
            self.queue[guild_id][index-1] = self.queue[guild_id][index]
            self.queue[guild_id][index] = []
        print(self.queue[guild_id])
        voice.play(source[0], after=lambda x=0: self.check_queue(ctx,guild_id))
        self.playing = [source[1],source[2]]
        return
      '''if self.queue[guild_id][1] == [] and self.queue[guild_id][2] != None or self.queue[guild_id][1] == [] and self.queue[guild_id][2] != [] :
        for info,i in range(2,len(self.queue[guild_id])):
          self.queue[guild_id][i-1] = self.queue[guild_id][i]
          self.queue[guild_id][i] = []
        return'''
      self.playing = []
      return

    @commands.command(name="join",help='Rejoins le salon.')
    async def join_voc(self, ctx):
      if ctx.author.voice is None:
        return await ctx.send("Vous n'??tes pas dans un salon vocal.")
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      if ctx.author.voice.channel != ctx.voice_client.channel:
        await ctx.voice_client.move_to(voice_channel)

    @commands.command(help='Quitte le salon.')
    async def dc(self, ctx):
      try:
        await ctx.voice_client.disconnect()
        return await ctx.send('Au revoir.')
      except AttributeError:
        return await ctx.send('Je ne suis pas dans un salon vocal.')

    @commands.command(help="Jouer une musique (titre/lien), ?p marche aussi.",aliases=['p'])
    async def play(self, ctx, *url):
      url = " ".join(map(str, url))
      await self.join_voc(ctx)
      vc = ctx.voice_client
      with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info: #search
          url2 = info['entries'][0]['url']
          uploader = info['entries'][0]['uploader']
          title = info['entries'][0]['title']
        elif 'formats' in info: #url
          url2 = info["formats"][0]['url']
          uploader = info['uploader']
          title = info['title']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        if vc.is_playing():
          guild_id = ctx.message.guild.id
          if(guild_id not in self.queue):
            self.queue[guild_id] = {1 : [source,title,uploader]}
            print(self.queue)
          else:
            for index,music in enumerate(self.queue[guild_id].values(),start=1):
              if music == [] :
                self.queue[guild_id][index] = [source,title,uploader]
            print(self.queue)
          return await ctx.send(f"{title} de {uploader} est ajout?? a la queue.")
        vc.play(source, after=lambda x=0: self.check_queue(ctx, ctx.message.guild.id))
        vc.is_playing()
        await ctx.send(f"La musique qui va ??tre jou?? est '{title}' de '{uploader}'.")
        self.playing = [title,uploader]

    @commands.command(help="Change le volume du bot.")
    async def volume(self, ctx, volume: int):
      if ctx.voice_client is None:
        return await ctx.send("Je ne suis pas dans un salon vocal.")
      ctx.voice_client.source.volume = volume / 100
      await ctx.send(f"Volume chang?? ?? {volume}%")

    @commands.command(help='Met en pause la musique.')
    async def pause(self, ctx):
      if ctx.voice_client is None:
        return await ctx.send("Je ne suis pas dans un salon vocal.")
      if ctx.voice_client.is_playing():
        await ctx.voice_client.pause()
        return await ctx.send('Mis en pause.')
      try:
        await ctx.voice_client.resume()
      except TypeError:
        return await ctx.send("Il n'y a pas de musique en cours.")
      return await ctx.send('Repris')

    @commands.command(help='Arrete la/les musique en cours.')
    async def stop(self, ctx):
      if ctx.voice_client is None:
        return await ctx.send("Je ne suis pas dans un salon vocal.")
      if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        return await ctx.send('Arr??t??.')
      await ctx.send("Il n'y a pas de musique.")

    @commands.command(name='nowplaying',help='Affiche la musique en cours. (?np marche) ',aliases=['np'])
    async def playing(self,ctx):
      if ctx.voice_client is None:
        return await ctx.send("Je ne suis pas dans un salon vocal.")
      if self.playing == []:
        return await ctx.send("Il n'y a pas de musique en cours.")
      return await ctx.send(f"La musique en cours est '{self.playing[0]}' de '{self.playing[1]}'")

    @commands.command(help="Montre les musiques dans la queue",aliases=["q"])
    async def queue(self,ctx):
      if(ctx.message.guild.id not in self.queue):
        return await ctx.reply("Il n'y a pas de musique dans la queue.")
      embed=discord.Embed(color=discord.Color.blue())
      embed.set_author(name="Musique dans la queue : ")
      for song_info,i in enumerate(self.queue[ctx.message.guild.id],1):
        embed.add_field(name="Musique n??"+str((i)) + ": ", value= f"'{self.queue[ctx.message.guild.id][i][1]}' de '{song_info[2]}' ",inline=False)
      await ctx.send(embed=embed)


def setup(client):
  client.add_cog(music(client))