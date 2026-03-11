import os
import discord
from discord.ext import commands
from discord import app_commands
from mcstatus import JavaServer
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Connect to Minecraft server
server = JavaServer(SERVER_IP, SERVER_PORT)

# When bot starts
@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{SERVER_IP}"
        )
    )

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")


# -----------------------
# /server command
# -----------------------
@bot.tree.command(name="server", description="Show Minecraft server IP and port")
async def server_info(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🌍 Minecraft Server",
        color=discord.Color.green()
    )

    embed.add_field(name="IP", value=SERVER_IP, inline=True)
    embed.add_field(name="Port", value=SERVER_PORT, inline=True)
    embed.set_footer(text="Hosted on Aternos")

    await interaction.response.send_message(embed=embed)


# -----------------------
# /status command
# -----------------------
@bot.tree.command(name="status", description="Check server status and TPS")
async def status(interaction: discord.Interaction):

    try:
        status = server.status()

        players = f"{status.players.online}/{status.players.max}"
        latency = round(status.latency)

        embed = discord.Embed(
            title="🟢 Server Online",
            color=discord.Color.green()
        )

        embed.add_field(name="Players", value=players, inline=True)
        embed.add_field(name="Ping", value=f"{latency} ms", inline=True)
        embed.add_field(name="TPS", value="~20 (Estimated)", inline=True)

        embed.set_footer(text="Minecraft Server Status")

    except:
        embed = discord.Embed(
            title="🔴 Server Offline",
            description="The Minecraft server is currently offline.",
            color=discord.Color.red()
        )

    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)
