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

# Comando que funciona con CUALQUIER combinación de mayúsculas/minúsculas
@bot.command(name="hola", case_insensitive=True)
async def hola_cmd(ctx):
    await ctx.send("hola.")

keep_alive()
bot.run(os.getenv("TOKEN"))
