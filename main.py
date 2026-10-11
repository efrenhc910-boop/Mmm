import os
import json
import discord
from discord.ext import commands
from keep_alive import keep_alive

# ── CONFIGURACIÓN ──
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# ── RUTA DEL ARCHIVO ──
ARCHIVO_ORO = "goldcoins.json"

# ── CARGAR DATOS AL INICIAR ──
def cargar_datos():
    if os.path.exists(ARCHIVO_ORO):
        with open(ARCHIVO_ORO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(ARCHIVO_ORO, "w", encoding="utf-8") as f:
        json.dump(datos, datos, indent=2)

# Cargar todo al arrancar
goldcoins = cargar_datos()

# Admins y fundadores (pon tu ID aquí)
admins = {}
founders = {}
# TU_ID_AQUI = tu ID de Discord como número
# admins[TU_ID_AQUI] = 5
# founders[TU_ID_AQUI] = 10

# ── EVENTO ──
@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user}")

# ── COMANDO .oro ──
@bot.command(name="oro", aliases=["gold", "coins"])
async def oro_cmd(ctx):
    uid = str(ctx.author.id)
    saldo = goldcoins.get(uid, 0)
    await ctx.send(f"Tienes `{saldo:,}` monedas de oro 💰")

# ── COMANDO .reset ──
@bot.command(name="reset")
async def reset_cmd(ctx, usuario: discord.User = None):
    uid = str(ctx.author.id)
    
    es_admin = admins.get(ctx.author.id) == 5
    es_founder = founders.get(ctx.author.id) == 10
    if not es_admin and not es_founder:
        return await ctx.send("❌ No eres admin del bot")
    
    if usuario is None:
        goldcoins[uid] = 10000
        guardar_datos(goldcoins)
        await ctx.send(f"✅ Tu saldo ha sido restablecido a `{goldcoins[uid]:,}` 💰")
        return
    
    goldcoins[str(usuario.id)] = 10000
    guardar_datos(goldcoins)
    await ctx.send(f"✅ Saldo de {usuario.mention} → `{goldcoins[str(usuario.id)]:,}` 💰")

keep_alive()
bot.run(os.getenv("TOKEN"))
