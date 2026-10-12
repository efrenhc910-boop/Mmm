import os
import importlib.util
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ Variable DISCORD_TOKEN no encontrada")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

def cargar_comando(nombre_archivo):
    ruta = f"{nombre_archivo}.py"
    spec = importlib.util.spec_from_file_location(nombre_archivo, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

cmd_ping = cargar_comando("cmd_ping")
cmd_test = cargar_comando("cmd_test")
cmd_saldo = cargar_comando("cmd_saldo")
cmd_apuesta = cargar_comando("cmd_apuesta")

@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"📂 Comandos cargados: ping, test, saldo, apuesta")
    print("──────────────────────────────")

@bot.command(name="ping")
async def ping_cmd(ctx):
    await cmd_ping.ejecutar(ctx)

@bot.command(name="test")
async def test_cmd(ctx):
    await cmd_test.ejecutar(ctx)

@bot.command(name="saldo")
async def saldo_cmd(ctx):
    await cmd_saldo.ejecutar(ctx)

@bot.command(name="apuesta")
async def apuesta_cmd(ctx, cantidad=None):
    await cmd_apuesta.ejecutar(ctx, cantidad)

bot.run(TOKEN)
