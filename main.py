import os
import json
import random
import asyncio
import discord
from discord import Embed
from discord.ext import commands

# ═══════════════════════════════════════════════
# 💾 SISTEMA DE DATOS
# ═══════════════════════════════════════════════
ARCHIVO_DATOS = "datos.json"
_datos = {}
_datos_lock = asyncio.Lock()

def _cargar_datos():
    global _datos
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            _datos = json.load(f)
        print(f"✅ Datos cargados")
    except FileNotFoundError:
        _datos = {}
        print("ℹ️ Archivo de datos nuevo")
    except Exception as e:
        print(f"❌ Error cargando: {e}")
        _datos = {}

def _guardar_datos():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(_datos, f, ensure_ascii=False, indent=2)

async def get_balance(user_id: str) -> int:
    async with _datos_lock:
        return int(_datos.get(f"saldo:{user_id}", 0))

async def set_balance(user_id: str, valor: int):
    async with _datos_lock:
        _datos[f"saldo:{user_id}"] = int(valor)
        _guardar_datos()

async def get_var(nombre: str, user_id: str, default=0):
    async with _datos_lock:
        return _datos.get(f"{nombre}:{user_id}", default)

async def set_var(nombre: str, user_id: str, valor):
    async with _datos_lock:
        _datos[f"{nombre}:{user_id}"] = valor
        _guardar_datos()

_cargar_datos()

# ═══════════════════════════════════════════════
# ⚙️ BOT
# ═══════════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ═══════════════════════════════════════════════
# 🟢 ENCENDIDO
# ═══════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"\n✅ BOT CONECTADO: {bot.user}")
    print("📋 COMANDOS CARGADOS:")
    for cmd in bot.commands:
        print(f"   ✓ !{cmd.name}")
    print("──────────────────────────────\n")

# ═══════════════════════════════════════════════
# ❌ ERRORES
# ═══════════════════════════════════════════════
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"❌ Comando no encontrado: {ctx.invoked_with}")
        await ctx.send(f"❌ Comando `!{ctx.invoked_with}` no existe")
        return
    print(f"❌ Error: {error}")
    await ctx.send("⚠️ Error interno")

# ═══════════════════════════════════════════════
# 🧪 COMANDOS BÁSICOS
# ═══════════════════════════════════════════════
@bot.command(name="ping")
async def ping_cmd(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

@bot.command(name="test")
async def test_cmd(ctx):
    await ctx.send(f"¡Hola {ctx.author.name}! ✅ Funcionando correctamente.")

@bot.command(name="saldo")
async def saldo_cmd(ctx):
    print(f"[COMANDO SALDO] Ejecutado por {ctx.author}")
    saldo = await get_balance(str(ctx.author.id))
    await ctx.send(f"💰 Tu saldo es: **{saldo:,}** monedas de oro")

_apuesta_en_curso = set()

@bot.command(name="apuesta")
async def apuesta_cmd(ctx, cantidad=None):
    print(f"[COMANDO APUESTA] Ejecutado por {ctx.author} — cantidad: {cantidad}")
    user_id = str(ctx.author.id)
    
    if user_id in _apuesta_en_curso:
        return await ctx.send("⏳ Espera a que termine tu apuesta anterior")
    
    if cantidad is None:
        return await ctx.send("❌ Usa: `!apuesta 10000` o `!apuesta all`")
    
    saldo_actual = await get_balance(user_id)
    
    if saldo_actual >= 100_000_000:
        return await ctx.send("❌ No puedes apostar — Superaste 100M")
    
    cantidad_str = str(cantidad).strip().lower()
    if cantidad_str == "all":
        apuesta = saldo_actual
    else:
        try:
            apuesta = int(cantidad_str)
        except ValueError:
            return await ctx.send("❌ Escribe un número o `all`")
    
    if apuesta <= 0:
        return await ctx.send("❌ Cantidad inválida")
    
    # Límites
    if saldo_actual >= 500_000:
        limite = 1_000_000
    elif saldo_actual >= 300_000:
        limite = 500_000
    elif saldo_actual >= 100_000:
        limite = 300_000
    else:
        limite = 30_000
    
    apuesta = min(apuesta, limite)
    
    if apuesta < 11:
        return await ctx.send("❌ Mínimo: 11 monedas")
    if saldo_actual < apuesta:
        return await ctx.send("❌ No tienes suficientes monedas")
    
    # Procesar apuesta
    _apuesta_en_curso.add(user_id)
    try:
        await set_balance(user_id, saldo_actual - apuesta)
        
        piedad = await get_var("Piedad", user_id) or 0
        umbral = max(1, 500 - (piedad * 10))
        roll = random.randint(1, 1000)
        
        embed = Embed(title="🎲 COINFLIP", color=0xFFD700)
        embed.set_image(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
        mensaje = await ctx.send(embed=embed)
        await asyncio.sleep(2.3)
        
        if roll == 1000:
            victorias = (await get_var("Victorias", user_id) or 0) + 1
            multiplicador = 2 + ((victorias - 1) * 0.5)
            await set_var("Victorias", user_id, victorias)
            await set_var("Derrotas", user_id, 0)
            await set_var("Piedad", user_id, 0)
            premio = int(apuesta * 5 * multiplicador)
            nuevo_saldo = saldo_actual - apuesta + premio
            await set_balance(user_id, nuevo_saldo)
            
            embed = Embed(title="💎 ***X5 — EXTREMADAMENTE RARO***", color=0xC0C0FF)
            embed.description = f"""━━━━━━━━━━━━━━━━━━━━
💎 **MULTIPLICADOR** ➥ `x{5 * multiplicador:.1f}`
🪙 **PREMIO** ➥ `+{premio:,}`
💰 **SALDO** ➥ `{nuevo_saldo:,}`"""
            await mensaje.edit(embed=embed)
        
        elif roll > umbral:
            victorias = (await get_var("Victorias", user_id) or 0) + 1
            multiplicador = 2 + ((victorias - 1) * 0.5)
            await set_var("Victorias", user_id, victorias)
            await set_var("Derrotas", user_id, 0)
            await set_var("Piedad", user_id, 0)
            premio = int(apuesta * multiplicador)
            nuevo_saldo = saldo_actual - apuesta + premio
            await set_balance(user_id, nuevo_saldo)
            
            embed = Embed(title="🏆 Victoria", color=0x00FF66)
            embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **APUESTA** ➥ `{apuesta:,}`
💰 **PREMIO** ➥ `+{premio:,}`
📈 **MULTIPLICADOR** ➥ `x{multiplicador:.1f}`"""
            await mensaje.edit(embed=embed)
        
        else:
            derrotas = (await get_var("Derrotas", user_id) or 0) + 1
            piedad_nueva = piedad + (10 if derrotas >= 2 else 0)
            await set_var("Derrotas", user_id, derrotas)
            await set_var("Victorias", user_id, 0)
            await set_var("Piedad", user_id, piedad_nueva)
            nuevo_saldo = saldo_actual - apuesta
            
            embed = Embed(title="❌ ***DERROTA***", color=0xFF0000)
            embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **PERDISTE** ➥ `-{apuesta:,}`
💰 **SALDO** ➥ `{nuevo_saldo:,}`
🍀 **PIEDAD** ➥ `{piedad_nueva}%` extra"""
            await mensaje.edit(embed=embed)
    finally:
        _apuesta_en_curso.discard(user_id)

# ═══════════════════════════════════════════════
# 🚀 INICIAR
# ═══════════════════════════════════════════════
bot.run(TOKEN)
