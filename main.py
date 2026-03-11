import discord
from discord import app_commands
import os
import asyncio
from mcstatus import JavaServer

# --- CONFIGURATION ---
# Using your details from the screenshots
IP = "play.block.ooguy.com"
PORT = 57589
TOKEN = os.getenv('TOKEN')

class AternosBot(discord.Client):
    def __init__(self):
        # Setting up the bot with default intents
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This syncs your slash commands (/status, /server) automatically
        await self.tree.sync()
        print(f"Slash commands synced for {self.user}")

    async def on_ready(self):
        print(f'Logged in as {self.user}!')
        # Start the background status updater
        self.loop.create_task(self.update_presence_loop())

    async def update_presence_loop(self):
        while True:
            try:
                # Lookup the Minecraft server
                server = await JavaServer.async_lookup(f"{IP}:{PORT}")
                status = await server.async_status()
                
                # Custom Activity: Player Count
                # Status: Idle (Yellow Moon)
                await self.change_presence(
                    status=discord.Status.idle,
                    activity=discord.CustomActivity(name=f"🟢 {status.players.online}/{status.players.max} playing")
                )
            except:
                # If server is offline: Red Dot (DnD)
                await self.change_presence(
                    status=discord.Status.dnd,
                    activity=discord.CustomActivity(name="🔴 Server Offline")
                )
            # Wait 30 seconds before checking again
            await asyncio.sleep(30)

client = AternosBot()

@client.tree.command(name="status", description="Get live server statistics")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        server = await JavaServer.async_lookup(f"{IP}:{PORT}")
        query = await server.async_status()
        
        embed = discord.Embed(title="📊 Server Status", color=discord.Color.gold())
        embed.add_field(name="Connection", value="🟢 Online", inline=True)
        embed.add_field(name="Players", value=f"{query.players.online}/{query.players.max}", inline=True)
        embed.add_field(name="Latency", value=f"{int(query.latency)}ms", inline=True)
        embed.set_footer(text="Aternos Live Monitor")
        
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ The server is currently **Offline**.")

@client.tree.command(name="server", description="Show the IP and Port")
async def server_info(interaction: discord.Interaction):
    embed = discord.Embed(title="🎮 Join the Server", color=discord.Color.blue())
    embed.add_field(name="Address", value=f"`{IP}`", inline=True)
    embed.add_field(name="Port", value=f"`{PORT}`", inline=True)
    embed.description = f"Full Join Link: `{IP}:{PORT}`"
    await interaction.response.send_message(embed=embed)

# Run the bot
if TOKEN:
    client.run(TOKEN)
else:
    print("ERROR: No TOKEN found in Environment Variables!")
