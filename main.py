import os
import discord
from discord.ext import commands

# Obtener el token desde las variables de entorno
TOKEN = os.getenv("DISCORD_TOKEN")

# Verificar que el token exista
if not TOKEN:
    raise RuntimeError("❌ No se encontró la variable DISCORD_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento: Bot encendido
@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    print("──────────────────────────────")

# Comando de prueba
@bot.command(name="test")
async def test_command(ctx):
    await ctx.send(f"¡Hola {ctx.author.name}! 👋 Funcionando correctamente.")

# Comando ping
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latencia: {round(bot.latency * 1000)}ms")

# Iniciar el bot
bot.run(TOKEN)
