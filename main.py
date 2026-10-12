import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ Variable DISCORD_TOKEN no encontrada en las variables de entorno")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"🌐 Servidores activos: {len(bot.guilds)}")
    print("──────────────────────────────")

@bot.command(name="test")
async def test_command(ctx):
    await ctx.send(f"¡Hola {ctx.author.name}! 👋 El bot funciona correctamente.")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latencia: {round(bot.latency * 1000)}ms")

bot.run(TOKEN)
