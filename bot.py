import discord
from discord.ext import commands, tasks
from discord import app_commands
from mcstatus import JavaServer
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

server = JavaServer.lookup(SERVER_ADDRESS)

# ---------------------------
# BOT READY
# ---------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    update_status.start()
    print(f"Bot Online: {bot.user}")

# ---------------------------
# AUTO STATUS UPDATE
# ---------------------------

@tasks.loop(seconds=30)
async def update_status():
    try:
        status = server.status()
        players = status.players.idle

        activity = discord.CustomActivity(
            name=f"🟢 {players} Players"
        )

        await bot.change_presence(
            status=discord.Status.online,
            activity=activity
        )

    except:
        activity = discord.CustomActivity(
            name="🔴 Server Offline"
        )

        await bot.change_presence(
            status=discord.Status.dnd,
            activity=activity
        )

# ---------------------------
# /server COMMAND
# ---------------------------

@bot.tree.command(name="server", description="Show Minecraft server IP")
async def server_info(interaction: discord.Interaction):

    ip, port = SERVER_ADDRESS.split(":")

    embed = discord.Embed(
        title="🌍 Minecraft Server",
        color=0x2ecc71
    )

    embed.add_field(name="IP", value=ip, inline=True)
    embed.add_field(name="Port", value=port, inline=True)

    embed.set_footer(text="Hosted on Aternos")

    await interaction.response.send_message(embed=embed)

# ---------------------------
# /status COMMAND
# ---------------------------

@bot.tree.command(name="status", description="Check server status")
async def status(interaction: discord.Interaction):

    try:
        status = server.status()

        players = f"{status.players.online}/{status.players.max}"
        latency = round(status.latency)
        motd = status.description
        version = status.version.name

        embed = discord.Embed(
            title="🟢 Server Online",
            color=0x2ecc71
        )

        embed.add_field(name="👥 Players", value=players, inline=True)
        embed.add_field(name="🏓 Ping", value=f"{latency} ms", inline=True)
        embed.add_field(name="🧩 Version", value=version, inline=True)
        embed.add_field(name="📜 MOTD", value=motd, inline=False)

    except:

        embed = discord.Embed(
            title="🔴 Server Offline",
            description="The server is currently offline.",
            color=0xe74c3c
        )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
