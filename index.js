const { Client, GatewayIntentBits, EmbedBuilder, ActivityType, PresenceUpdateStatus, REST, Routes, SlashCommandBuilder } = require('discord.js');
const util = require('minecraft-server-util');

// --- CONFIGURATION ---
const CONFIG = {
    IP: 'play.block.ooguy.com', // Your Dynu Domain
    PORT: 57589,               // Your Aternos Port from the image
    TOKEN: process.env.TOKEN,   // Set this in Railway Variables
    CLIENT_ID: process.env.CLIENT_ID // Set this in Railway Variables
};

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// 1. Define Slash Commands
const commands = [
    new SlashCommandBuilder()
        .setName('status')
        .setDescription('Check if the Minecraft server is online'),
    new SlashCommandBuilder()
        .setName('server')
        .setDescription('Get the IP and Port to join the server')
].map(command => command.toJSON());

// 2. Register Commands & Startup
client.once('ready', async () => {
    const rest = new REST({ version: '10' }).setToken(CONFIG.TOKEN);
    try {
        console.log('Registering slash commands...');
        await rest.put(Routes.applicationCommands(CONFIG.CLIENT_ID), { body: commands });
        console.log(`Logged in as ${client.user.tag} and commands registered!`);
    } catch (error) {
        console.error('Error registering commands:', error);
    }

    // 3. Status Loop (Updates every 30 seconds)
    setInterval(async () => {
        try {
            const status = await util.status(CONFIG.IP, CONFIG.PORT);
            client.user.setPresence({
                activities: [{ 
                    name: `🟢 ${status.players.online}/${status.players.max} Players`, 
                    type: ActivityType.Custom 
                }],
                status: PresenceUpdateStatus.Online, 
            });
        } catch {
            client.user.setPresence({
                activities: [{ name: '🔴 Server Offline', type: ActivityType.Custom }],
                status: PresenceUpdateStatus.DoNotDisturb,
            });
        }
    }, 30000);
});

// 4. Command Interactions
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    if (interaction.commandName === 'status') {
        await interaction.deferReply();
        try {
            const result = await util.status(CONFIG.IP, CONFIG.PORT);
            const embed = new EmbedBuilder()
                .setTitle('📊 Server Status')
                .setColor('#2ecc71')
                .addFields(
                    { name: 'Status', value: '🟢 Online', inline: true },
                    { name: 'Players', value: `${result.players.online}/${result.players.max}`, inline: true },
                    { name: 'Ping', value: `${result.roundTripLatency}ms`, inline: true },
                    { name: 'Version', value: result.version.name || 'Minecraft' }
                )
                .setTimestamp();
            await interaction.editReply({ embeds: [embed] });
        } catch {
            await interaction.editReply('❌ **Server is Offline.** (Aternos servers turn off when empty).');
        }
    }

    if (interaction.commandName === 'server') {
        const embed = new EmbedBuilder()
            .setTitle('🎮 Connection Details')
            .setColor('#3498db')
            .setDescription(`Join the server using the info below:`)
            .addFields(
                { name: 'Domain', value: `\`${CONFIG.IP}\``, inline: true },
                { name: 'Port', value: `\`${CONFIG.PORT}\``, inline: true },
                { name: 'Full Address', value: `\`${CONFIG.IP}:${CONFIG.PORT}\`` }
            );
        await interaction.reply({ embeds: [embed] });
    }
});

client.login(CONFIG.TOKEN);
