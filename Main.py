import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import youtube_dl

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
API_TOKEN=os.getev(Token)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        except youtube_dl.utils.DownloadError as e:
            raise ValueError("Invalid YouTube URL or video not found.") from e

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(executable="C:\\Users\\Manish Singh Rawat\\Desktop\\New folder (4)\\ffmpeg-2023-07-16-git-c541ecf0dc-full_build\\bin\\ffmpeg.exe", source=filename), data=data)


@bot.command(name='play_song', help='To play song')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return

    voice_channel = ctx.message.author.voice.channel
    if not ctx.voice_client:
        await voice_channel.connect()

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop)
        except ValueError as e:
            await ctx.send(str(e))
            return
        
        ctx.voice_client.play(player)


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()

@bot.command(name='info', help='Displays information about the bot')
async def info(ctx):
    total_servers = len(bot.guilds)
    server_names = "\n".join([guild.name for guild in bot.guilds])

    info_message = f"**Bot Name:** {bot.user.name}\n" \
                  f"**Total Servers:** {total_servers}\n" \
                  f"**List of Servers:**\n{server_names}"

    await ctx.send(info_message)

@bot.command(name='list_members', help='Lists all members and their roles in the server')
async def list_members(ctx):
    server = ctx.message.guild

    member_info = []
    for member in server.members:
        roles = ', '.join([role.name for role in member.roles if not role.is_default()])
        member_info.append(f"**{member.name.upper()}**: {roles}")

    members_with_roles = "\n".join(member_info)

    await ctx.send(f"**Members and Their Roles in the Server:**\n{members_with_roles}")
    
if __name__ == "__main__":
    bot.run("")
