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
        # Si el archivo se corrompe por cierres abruptos en Fadehost, retorna vacío seguro
        return {}

def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error al guardar datos.json: {e}")

_datos = cargar_datos()

# Funciones seguras para leer y escribir datos
async def get_balance(user_id):
    val = _datos.get(f"saldo:{str(user_id)}", 0)
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

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
    raise RuntimeError("❌ Variable DISCORD_TOKEN no encontrada en el entorno de Fadehost.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# ═══════════════════════════════════════════════
# 🟢 EVENTO: BOT ENCENDIDO
# ═══════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    print(f"💾 Datos cargados: {len(_datos)} entradas en disco")
    print("──────────────────────────────")

# ═══════════════════════════════════════════════
# 🔧 COMANDOS BÁSICOS
# ═══════════════════════════════════════════════
@bot.command(name="test")
async def test_cmd(ctx):
    await ctx.send(f"¡Hola {ctx.author.name}! 👋 Funcionando correctamente en Fadehost.")

@bot.command(name="ping")
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
    
    # ─── LÍMITE MÁXIMO GLOBAL ───
    saldo_actual = await get_balance(user_id)
    if saldo_actual >= 100000000:
        await ctx.send("❌ No puedes apostar — Has superado el límite máximo de 100 millones.")
        return
    
    # ─── VALIDAR ENTRADA ───
    if cantidad is None:
        await ctx.send("❌ Uso correcto: `.apuesta 10000` o `.apuesta all`")
        return
    
    # ─── ACEPTAR "ALL" ───
    if cantidad.lower() == "all":
        apuesta = saldo_actual
    else:
        try:
            apuesta = int(cantidad)
        except ValueError:
            await ctx.send("❌ Debes introducir una cantidad numérica válida o escribir `all`.")
            return
    
    # ─── MÍNIMO Y SALDO SUFICIENTE ───
    if apuesta < 11:
        await ctx.send("❌ La apuesta mínima permitida es de `11` monedas de oro.")
        return
    if saldo_actual < apuesta:
        await ctx.send("❌ No tienes suficientes monedas de oro para realizar esta apuesta.")
        return
    
    # ─── LÍMITE DINÁMICO POR TRAMOS ───
    limite = 30000
    if saldo_actual >= 100000:
        limite = 300000
    if saldo_actual >= 300000:
        limite = 500000
    if saldo_actual >= 500000:
        limite = 1000000
    if saldo_actual >= 1000000:
        limite = 1000000
    
    if apuesta > limite:
        apuesta = limite
    
    # ─── DESCONTAR APUESTA INICIAL ───
    await set_balance(user_id, saldo_actual - apuesta)
    
    # ─── SISTEMA DE PIEDAD ───
    piedad_guardada = await get_var("Piedad", user_id)
    probabilidad_extra = int(piedad_guardada) * 10
    umbral_victoria = 500 - probabilidad_extra
    if umbral_victoria < 1:
        umbral_victoria = 1
    
    # ─── LANZAR MONEDA ───
    roll = random.randint(1, 1000)
    
    # ─── ANIMACIÓN INICIAL ───
    embed = Embed(title="🎲 COINFLIP", color=0xFFD700)
    embed.set_image(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    mensaje = await ctx.send(embed=embed)
    
    await ctx.channel.typing()
    
    # Refrescar saldo post-descuento para cálculos exactos
    saldo_actual = await get_balance(user_id)
    
    # ─── X5 MEGA PREMIO ───
    if roll == 1000:
        victorias = int(await get_var("Victorias", user_id)) + 1
        multiplicador = 2.0 + ((victorias - 1) * 0.5)
        
        await set_var("Victorias", user_id, victorias)
        await set_var("Derrotas", user_id, 0)
        await set_var("Piedad", user_id, 0)
        await set_var("Multiplicador", user_id, multiplicador)
        
        premio = int(apuesta * 5 * multiplicador)
        nuevo_saldo = saldo_actual + premio
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
        nuevo_saldo = saldo_actual + premio
        await set_balance(user_id, nuevo_saldo)
        
        embed = Embed(title="🏆 Victoria", color=0x00FF66)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **APUESTA**
➥ `{apuesta:,}` monedas de oro

💰 **PREMIO**
➥ `+{premio:,}` monedas de oro

📈 **MULTIPLICADOR**
➥ `x{multiplicador:.1f}

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
        
        nuevo_saldo = saldo_actual  # Ya se había descontado al inicio
        
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

# ═══════════════════════════════════════════════
# 🚀 INICIAR EL BOT
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    bot.run(TOKEN)
