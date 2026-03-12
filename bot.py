import discord
from discord.ext import commands, tasks
from discord import app_commands
from mcstatus import JavaServer
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

# Make bot show MOBILE status
bot._connection._client_properties = {
    "$os": "android",
    "$browser": "Discord Android",
    "$device": "Discord Android"
}

server = JavaServer.lookup(SERVER_ADDRESS)

# -------------------------
# BOT READY
# -------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    update_status.start()
    print(f"✅ Bot Online: {bot.user}")

# -------------------------
# AUTO STATUS UPDATE
# -------------------------

@tasks.loop(seconds=30)
async def update_status():

    try:
        status = server.status()
        players = status.players.online

        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.CustomActivity(
                name=f"📱 {players} Players | /status"
            )
        )

    except:

        await bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.CustomActivity(
                name="🔴 Server Offline"
            )
        )

# -------------------------
# /server
# -------------------------

@bot.tree.command(name="server", description="Show server IP and port")
async def server_info(interaction: discord.Interaction):

    ip, port = SERVER_ADDRESS.split(":")

    embed = discord.Embed(
        title="🌍 Minecraft Server",
        color=0x3498db
    )

    embed.add_field(name="IP", value=ip, inline=True)
    embed.add_field(name="Port", value=port, inline=True)

    embed.set_footer(text="Hosted on Aternos")

    await interaction.response.send_message(embed=embed)

# -------------------------
# /status
# -------------------------

@bot.tree.command(name="status", description="Check server status")
async def status(interaction: discord.Interaction):

    try:
        status = server.status()

        embed = discord.Embed(
            title="🟢 Server Online",
            color=0x2ecc71
        )

        embed.add_field(
            name="👥 Players",
            value=f"{status.players.online}/{status.players.max}",
            inline=True
        )

        embed.add_field(
            name="🏓 Ping",
            value=f"{round(status.latency)} ms",
            inline=True
        )

        embed.add_field(
            name="🧩 Version",
            value=status.version.name,
            inline=True
        )

        embed.add_field(
            name="📜 MOTD",
            value=status.description,
            inline=False
        )

    except:

        embed = discord.Embed(
            title="🔴 Server Offline",
            description="The Minecraft server is currently offline.",
            color=0xe74c3c
        )

    await interaction.response.send_message(embed=embed)

# -------------------------
# /players
# -------------------------

@bot.tree.command(name="players", description="List online players")
async def players(interaction: discord.Interaction):

    try:
        query = server.query()

        if query.players.names:
            player_list = "\n".join(query.players.names)
        else:
            player_list = "No players online"

        embed = discord.Embed(
            title="👥 Online Players",
            description=player_list,
            color=0x9b59b6
        )

    except:

        embed = discord.Embed(
            title="❌ Cannot fetch players",
            description="Server offline or query disabled.",
            color=0xe74c3c
        )

    await interaction.response.send_message(embed=embed)

# -------------------------
# /ping
# -------------------------

@bot.tree.command(name="ping", description="Check Minecraft server latency")
async def ping(interaction: discord.Interaction):

    try:
        status = server.status()

        embed = discord.Embed(
            title="🏓 Server Ping",
            description=f"{round(status.latency)} ms",
            color=0xf1c40f
        )

    except:

        embed = discord.Embed(
            title="🔴 Server Offline",
            color=0xe74c3c
        )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
