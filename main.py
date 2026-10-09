import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user}")

# Aquí irán tus comandos

keep_alive()
bot.run(os.getenv("TOKEN"))
