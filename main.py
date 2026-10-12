import os
import json
import random
import discord
from discord import Embed
from discord.ext import commands

# ═══════════════════════════════════════════════
# 💾 SISTEMA DE GUARDADO PERMANENTE (datos.json)
# ═══════════════════════════════════════════════
ARCHIVO_DATOS = "datos.json"

def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {}
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            contenido = f.read()
            if not contenido.strip():
                return {}
            return json.loads(contenido)
    except (json.JSONDecodeError, Exception):
        return {}

def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error al guardar datos.json: {e}")

_datos = cargar_datos()

async def get_balance(user_id):
    key = f"saldo:{str(user_id)}"
    if key not in _datos:
        # Dar un saldo inicial de prueba de 50,000 monedas si es nuevo
        _datos[key] = 50000
        guardar_datos(_datos)
    try:
        return int(_datos.get(key, 50000))
    except (TypeError, ValueError):
        return 50000

async def set_balance(user_id, valor):
    _datos[f"saldo:{str(user_id)}"] = int(valor)
    guardar_datos(_datos)

async def get_var(nombre, user_id):
    val = _datos.get(f"{nombre}:{str(user_id)}", 0)
    try:
        return float(val) if "." in str(val) else int(val)
    except (TypeError, ValueError):
        return 0

async def set_var(nombre, user_id, valor):
    _datos[f"{nombre}:{str(user_id)}"] = valor
    guardar_datos(_datos)

# ═══════════════════════════════════════════════
# ⚙️ CONFIGURACIÓN DEL BOT
# ═══════════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ Variable DISCORD_TOKEN no encontrada.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"💾 Datos cargados: {len(_datos)} entradas en disco")
    print("──────────────────────────────")

@bot.command(name="ping", aliases=["pong"])
async def ping_cmd(ctx):
    await ctx.send(f"🏓 Pong! Latencia: {round(bot.latency * 1000)}ms")

@bot.command(name="saldo")
async def saldo_cmd(ctx):
    user_id = str(ctx.author.id)
    saldo = await get_balance(user_id)
    await ctx.send(f"💰 **{ctx.author.display_name}**, tu saldo actual es de **{saldo:,}** monedas de oro.")

# ═══════════════════════════════════════════════
# 🎲 COMANDO DE APUESTA (COINFLIP)
# ═══════════════════════════════════════════════
@bot.command(name="apuesta")
async def apuesta_cmd(ctx, cantidad=None):
    user_id = str(ctx.author.id)
    
    saldo_actual = await get_balance(user_id)
    
    # Validar entrada
    if cantidad is None:
        await ctx.send("❌ Uso correcto: `.apuesta 1000` o `.apuesta all`")
        return
    
    # Manejar "all"
    if cantidad.lower() == "all":
        apuesta = saldo_actual
    else:
        try:
            apuesta = int(cantidad)
        except ValueError:
            await ctx.send("❌ Debes introducir una cantidad numérica válida o escribir `all`.")
            return
    
    # Validaciones básicas
    if apuesta < 11:
        await ctx.send("❌ La apuesta mínima permitida es de `11` monedas de oro.")
        return
    if saldo_actual < apuesta:
        await ctx.send(f"❌ No tienes suficientes monedas. Tu saldo actual es de `{saldo_actual:,}`.")
        return
    
    # Descontar apuesta inicial
    nuevo_saldo_inicial = saldo_actual - apuesta
    await set_balance(user_id, nuevo_saldo_inicial)
    
    # Sistema de piedad
    piedad_guardada = await get_var("Piedad", user_id)
    probabilidad_extra = int(piedad_guardada) * 10
    umbral_victoria = 500 - probabilidad_extra
    if umbral_victoria < 1:
        umbral_victoria = 1
    
    # Lanzar moneda
    roll = random.randint(1, 1000)
    
    # Animación
    embed = Embed(title="🎲 COINFLIP", color=0xFFD700)
    embed.set_image(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    mensaje = await ctx.send(embed=embed)
    
    await ctx.channel.typing()
    
    # Refrescar saldo actual de base de datos
    saldo_base = await get_balance(user_id)
    
    # ─── X5 MEGA PREMIO ───
    if roll == 1000:
        victorias = int(await get_var("Victorias", user_id)) + 1
        multiplicador = 2.0 + ((victorias - 1) * 0.5)
        
        await set_var("Victorias", user_id, victorias)
        await set_var("Derrotas", user_id, 0)
        await set_var("Piedad", user_id, 0)
        await set_var("Multiplicador", user_id, multiplicador)
        
        premio = int(apuesta * 5 * multiplicador)
        nuevo_saldo = saldo_base + premio
        await set_balance(user_id, nuevo_saldo)
        
        embed = Embed(title="💎 ***X5 — EXTREMADAMENTE RARO***", color=0xC0C0FF)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
💎 **MULTIPLICADOR**
➥ `x{5 * multiplicador:.1f}`

🪙 **PREMIO**
➥ `+{premio:,}` monedas de oro
━━━━━━━━━━━━━━━━━━━━
***¡Has conseguido el multiplicador más raro!***

💰 **SALDO ACTUAL**
➥ `{nuevo_saldo:,}` monedas de oro
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)
    
    # ─── VICTORIA ───
    elif roll > umbral_victoria:
        victorias = int(await get_var("Victorias", user_id)) + 1
        multiplicador = 2.0 + ((victorias - 1) * 0.5)
        
        await set_var("Victorias", user_id, victorias)
        await set_var("Derrotas", user_id, 0)
        await set_var("Piedad", user_id, 0)
        await set_var("Multiplicador", user_id, multiplicador)
        
        premio = int(apuesta * multiplicador)
        nuevo_saldo = saldo_base + premio
        await set_balance(user_id, nuevo_saldo)
        
        embed = Embed(title="🏆 Victoria", color=0x00FF66)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **APUESTA**
➥ `{apuesta:,}` monedas de oro

💰 **PREMIO**
➥ `+{premio:,}` monedas de oro

📈 **MULTIPLICADOR**
➥ `x{multiplicador:.1f}`

💰 **SALDO ACTUAL**
➥ `{nuevo_saldo:,}` monedas de oro
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)
    
    # ─── DERROTA ───
    else:
        derrotas = int(await get_var("Derrotas", user_id)) + 1
        piedad_actual = int(piedad_guardada)
        if derrotas >= 2:
            piedad_actual += 10
        
        await set_var("Derrotas", user_id, derrotas)
        await set_var("Victorias", user_id, 0)
        await set_var("Multiplicador", user_id, 2.0)
        await set_var("Piedad", user_id, piedad_actual)
        
        nuevo_saldo = saldo_base  # El saldo ya se había descontado al inicio
        
        embed = Embed(title="❌ ***DERROTA***", color=0xFF0000)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **PERDISTE**
➥ `-{apuesta:,}` monedas de oro
━━━━━━━━━━━━━━━━━━━━
***La fortuna no estuvo de tu lado.***

💰 **SALDO ACTUAL**
➥ `{nuevo_saldo:,}` monedas de oro

🍀 **PIEDAD ACUMULADA**
➥ `{piedad_actual}%` extra de probabilidad
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
