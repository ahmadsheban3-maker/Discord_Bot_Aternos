const { Client, GatewayIntentBits, EmbedBuilder, ActivityType, PresenceUpdateStatus, REST, Routes, SlashCommandBuilder } = require('discord.js');
const util = require('minecraft-server-util');

// --- SETTINGS FROM YOUR IMAGES ---
const IP = 'play.block.ooguy.com';
const PORT = 57589;
const TOKEN = process.env.TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// 1. Setup Slash Commands
const commands = [
    new SlashCommandBuilder().setName('status').setDescription('Check server status'),
    new SlashCommandBuilder().setName('server').setDescription('Get join info')
].map(cmd => cmd.toJSON());

client.once('ready', async () => {
    console.log(`Bot logged in as ${client.user.tag}`);
    
    // Register Commands
    const rest = new REST({ version: '10' }).setToken(TOKEN);
    try {
        await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });
        console.log('Commands registered successfully.');
    } catch (err) { console.error(err); }

    // 2. Status Loop (Idle/Yellow Moon)
    setInterval(async () => {
        try {
            const status = await util.status(IP, PORT);
            client.user.setPresence({
                activities: [{ 
                    name: `🟢 ${status.players.online}/${status.players.max} playing`, 
                    type: ActivityType.Custom 
                }],
                status: PresenceUpdateStatus.Idle, // Yellow Moon
            });
        } catch {
            client.user.setPresence({
                activities: [{ name: '🔴 Server Offline', type: ActivityType.Custom }],
                status: PresenceUpdateStatus.DoNotDisturb, // Red Dot
            });
        }
    }, 30000);
});

// 3. Command Responses
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    if (interaction.commandName === 'status') {
        await interaction.deferReply();
        try {
            const data = await util.status(IP, PORT);
            const embed = new EmbedBuilder()
                .setTitle('📊 Server Status')
                .setColor('#f1c40f') // Yellow to match Idle status
                .addFields(
                    { name: 'Status', value: '🟢 Online', inline: true },
                    { name: 'Players', value: `${data.players.online}/${data.players.max}`, inline: true },
                    { name: 'Ping', value: `${data.roundTripLatency}ms`, inline: true }
                );
            await interaction.editReply({ embeds: [embed] });
        } catch {
            await interaction.editReply('❌ Server is currently **Offline**.');
        }
    }

    if (interaction.commandName === 'server') {
        const embed = new EmbedBuilder()
            .setTitle('🎮 How to Join')
            .setColor('#3498db')
            .addFields(
                { name: 'IP', value: `\`${IP}\``, inline: true },
                { name: 'Port', value: `\`${PORT}\``, inline: true }
            );
        await interaction.reply({ embeds: [embed] });
    }
});

client.login(TOKEN);
