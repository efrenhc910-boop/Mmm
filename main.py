import os
import json
import random
import asyncio
import traceback
import discord
from discord import Embed
from discord.ext import commands

# ═══════════════════════════════════════════════
# 💾 SISTEMA DE GUARDADO PERMANENTE
# ═══════════════════════════════════════════════
ARCHIVO_DATOS = "datos.json"
_lock = asyncio.Lock()
_datos = {}

def _cargar_datos():
    global _datos
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            _datos = json.load(f)
        print(f"✅ Datos cargados: {len(_datos)} entradas")
    except FileNotFoundError:
        _datos = {}
        print("ℹ️ datos.json no existe, se creará al guardar")
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        _datos = {}

def _guardar_ahora():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(_datos, f, ensure_ascii=False, indent=2)

async def get_balance(user_id: str) -> int:
    async with _lock:
        return int(_datos.get(f"saldo:{user_id}", 0))

async def set_balance(user_id: str, valor: int):
    async with _lock:
        _datos[f"saldo:{user_id}"] = int(valor)
        _guardar_ahora()

async def get_var(nombre: str, user_id: str, default=0):
    async with _lock:
        return _datos.get(f"{nombre}:{user_id}", default)

async def set_var(nombre: str, user_id: str, valor):
    async with _lock:
        _datos[f"{nombre}:{user_id}"] = valor
        _guardar_ahora()

_cargar_datos()

# ═══════════════════════════════════════════════
# ⚙️ CONFIGURACIÓN DEL BOT
# ═══════════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN no está configurado")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# ═══════════════════════════════════════════════
# 🟢 EVENTO: BOT LISTO
# ═══════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Conectado como: {bot.user}")
    print(f"📂 Comandos: {sorted([c.name for c in bot.commands])}")
    print("──────────────────────────────")

# ═══════════════════════════════════════════════
# ❌ MANEJO DE ERRORES
# ═══════════════════════════════════════════════
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"⚠️ Comando no encontrado: {ctx.invoked_with}")
        return
    print(f"\n❌ ERROR en .{ctx.command}:")
    traceback.print_exception(type(error), error, error.__traceback__)
    await ctx.send("⚠️ Ocurrió un error al ejecutar el comando.")

# ═══════════════════════════════════════════════
# 🔒 ANTI-DOBLE APUESTA POR USUARIO
# ═══════════════════════════════════════════════
_apuesta_en_curso = set()

# ═══════════════════════════════════════════════
# 🧪 COMANDOS BÁSICOS
# ═══════════════════════════════════════════════
@bot.command(name="ping")
async def ping_cmd(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

@bot.command(name="test")
async def test_cmd(ctx):
    await ctx.send(f"¡Hola {ctx.author.name}! ✅")

@bot.command(name="saldo")
async def saldo_cmd(ctx):
    saldo = await get_balance(str(ctx.author.id))
    await ctx.send(f"💰 Tu saldo: **{saldo:,}** monedas de oro")

# ═══════════════════════════════════════════════
# 🎲 COMANDO DE APUESTA
# ═══════════════════════════════════════════════
@bot.command(name="apuesta")
async def apuesta_cmd(ctx, cantidad=None):
    user_id = str(ctx.author.id)

    # Evitar doble apuesta simultánea
    if user_id in _apuesta_en_curso:
        return await ctx.send("⏳ Ya tienes una apuesta en curso, espera...")
    
    _apuesta_en_curso.add(user_id)
    try:
        await _procesar_apuesta(ctx, cantidad, user_id)
    finally:
        _apuesta_en_curso.discard(user_id)

async def _procesar_apuesta(ctx, cantidad, user_id):
    saldo_actual = await get_balance(user_id)

    # Límite de 100M
    if saldo_actual >= 100_000_000:
        return await ctx.send("❌ No puedes apostar — Superaste 100M de monedas.")

    # Sin argumento
    if cantidad is None:
        return await ctx.send("❌ Usa: `.apuesta 10000` o `.apuesta all`")

    # Opción ALL
    if str(cantidad).strip().lower() == "all":
        apuesta = saldo_actual
    else:
        try:
            apuesta = int(cantidad)
        except ValueError:
            return await ctx.send("❌ Escribe un número o `all`.")

    if apuesta <= 0:
        return await ctx.send("❌ Cantidad inválida.")

    # Límites dinámicos
    if saldo_actual >= 500_000:
        limite = 1_000_000
    elif saldo_actual >= 300_000:
        limite = 500_000
    elif saldo_actual >= 100_000:
        limite = 300_000
    else:
        limite = 30_000

    apuesta = min(apuesta, limite)

    # Validaciones
    if apuesta < 11:
        return await ctx.send("❌ Mínimo: 11 monedas.")
    if saldo_actual < apuesta:
        return await ctx.send("❌ No tienes suficientes monedas.")

    # Descontar apuesta
    await set_balance(user_id, saldo_actual - apuesta)

    # Sistema de piedad
    piedad = await get_var("Piedad", user_id) or 0
    umbral = max(1, 500 - (piedad * 10))
    roll = random.randint(1, 1000)

    # Animación
    embed = Embed(title="🎲 COINFLIP", color=0xFFD700)
    embed.set_image(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    mensaje = await ctx.send(embed=embed)
    
    await asyncio.sleep(2.3)

    # 💎 X5 PREMIO MÁXIMO
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
💎 **MULTIPLICADOR**
➥ `x{5 * multiplicador:.1f}`
🪙 **PREMIO**
➥ `+{premio:,}` monedas de oro
━━━━━━━━━━━━━━━━━━━━
💰 **SALDO**
➥ `{nuevo_saldo:,}` monedas de oro"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)

    # 🏆 VICTORIA
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
📈 **MULTIPLICADOR** ➥ `x{multiplicador:.1f}`
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)

    # ❌ DERROTA
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
🍀 **PIEDAD** ➥ `{piedad_nueva}%` extra
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)

# ═══════════════════════════════════════════════
# 🚀 INICIAR
# ═══════════════════════════════════════════════
bot.run(TOKEN)
