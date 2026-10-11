import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"✅ BOT CONECTADO: {bot.user}")
    print(f"✅ Prefijo: .")
    print(f"✅ Intents activados: message_content={intents.message_content}")
    print(f"✅ Comandos cargados: {[c.name for c in bot.commands]}")
    print("=" * 40)

# Detecta TODO lo que se escribe en canales
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"📩 Mensaje recibido: '{message.content}' de {message.author}")
    await bot.process_commands(message)

@bot.command(name="hola")
async def hola_cmd(ctx):
    print(f"✅ Comando .hola ejecutado por {ctx.author}")
    await ctx.send("hola.")

keep_alive()
bot.run(os.getenv("TOKEN"))
