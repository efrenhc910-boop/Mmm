import os
import sys
import traceback
import discord
from discord.ext import commands

# Asegurar que el directorio del script esté en sys.path (CRÍTICO para imports)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cmd_ping
import cmd_test
import cmd_saldo
import cmd_apuesta

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ Variable DISCORD_TOKEN no encontrada en las variables de entorno")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# ═══════════════════════════════════════════════
# 🟢 EVENTO: BOT ENCENDIDO
# ═══════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    print(f"📂 Comandos registrados: {sorted([c.name for c in bot.commands])}")
    print("──────────────────────────────")

# ═══════════════════════════════════════════════
# ❌ CAPTURA DE ERRORES (antes eran silenciosos)
# ═══════════════════════════════════════════════
@bot.event
async def on_command_error(ctx, error):
    print(f"\n❌ ERROR en comando '.{ctx.command}' ejecutado por {ctx.author}:")
    traceback.print_exception(type(error), error, error.__traceback__)
    print("──────────────────────────────")

    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Falta un argumento. Ejemplo: `.{ctx.command.name} 10000`")
    else:
        await ctx.send(f"⚠️ Error interno al ejecutar `.{ctx.command.name}`. Revisa la consola del bot.")

# ═══════════════════════════════════════════════
# 📝 REGISTRO DE COMANDOS
# ═══════════════════════════════════════════════
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
    print(f"[apuesta] {ctx.author} ({ctx.author.id}) → .apuesta {cantidad}")
    await cmd_apuesta.ejecutar(ctx, cantidad)

bot.run(TOKEN)
