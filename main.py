import os
import json
import random
import asyncio
import discord
from discord import Embed
from discord.ext import commands

# ═══════════════════════════════════════════
# 💾 SISTEMA DE DATOS
# ═══════════════════════════════════════════
ARCHIVO_DATOS = "datos.json"
_datos = {}
_bloqueo = asyncio.Lock()

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
        print(f"❌ Error: {e}")
        _datos = {}

def _guardar_datos():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(_datos, f, ensure_ascii=False, indent=2)

async def obtener_saldo(user_id: str) -> int:
    async with _bloqueo:
        return int(_datos.get(f"saldo:{user_id}", 0))

async def establecer_saldo(user_id: str, cantidad: int):
    async with _bloqueo:
        _datos[f"saldo:{user_id}"] = int(cantidad)
        _guardar_datos()

async def agregar_saldo(user_id: str, cantidad: int):
    async with _bloqueo:
        clave = f"saldo:{user_id}"
        actual = int(_datos.get(clave, 0))
        _datos[clave] = actual + int(cantidad)
        _guardar_datos()

_cargar_datos()

# ═══════════════════════════════════════════
# ⚙️ CONFIGURACIÓN
# ═══════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ═══════════════════════════════════════════
# 🟢 ENCENDIDO
# ═══════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"\n✅ Conectado: {bot.user}")
    print(f"📋 Comandos: {[c.name for c in bot.commands]}\n")

# ═══════════════════════════════════════════
# 💰 !saldo
# ═══════════════════════════════════════════
@bot.command(name="saldo")
async def saldo_cmd(ctx):
    saldo = await obtener_saldo(str(ctx.author.id))
    embed = Embed(title="🏦 TU SALDO", color=0xFFD700)
    embed.add_field(name="Monedas de oro", value=f"**{saldo:,}**", inline=False)
    embed.set_footer(text=ctx.author.display_name)
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════
# 🎲 !apuesta
# ═══════════════════════════════════════════
@bot.command(name="apuesta")
async def apuesta_cmd(ctx, cantidad=None):
    user_id = str(ctx.author.id)
    nombre = ctx.author.display_name

    if cantidad is None:
        return await ctx.send("❌ Uso: `!apuesta 100`")
    
    try:
        apostado = int(cantidad)
    except ValueError:
        return await ctx.send("❌ Escribe un número válido")
    
    if apostado <= 0:
        return await ctx.send("❌ Debe ser mayor a 0")
    
    saldo_actual = await obtener_saldo(user_id)
    
    if saldo_actual < apostado:
        return await ctx.send(
            f"❌ No tienes suficiente dinero.\n"
            f"💰 Tu saldo: **{saldo_actual:,}**"
        )
    
    # Descontar apuesta
    await establecer_saldo(user_id, saldo_actual - apostado)
    
    # Animación
    embed_espere = Embed(
        title="🎲 Lanzando moneda...",
        description=f"Apostaste: **{apostado:,}**",
        color=0xFFD700
    )
    embed_espere.set_footer(text=nombre)
    mensaje = await ctx.send(embed=embed_espere)
    await asyncio.sleep(2)
    
    # 50% Ganar / 50% Perder
    if random.choice([True, False]):
        # ✅ GANAR
        ganancia = apostado * 2
        await agregar_saldo(user_id, ganancia)
        saldo_nuevo = await obtener_saldo(user_id)
        
        embed = Embed(title="✅ ¡GANASTE!", color=0x00FF00)
        embed.add_field(name="💰 Apostaste", value=f"{apostado:,}", inline=True)
        embed.add_field(name="💵 Ganaste", value=f"+{ganancia:,}", inline=True)
        embed.add_field(name="💎 Saldo actual", value=f"{saldo_nuevo:,}", inline=True)
        embed.set_footer(text=f"{nombre} 🎉")
    else:
        # ❌ PERDER
        saldo_nuevo = await obtener_saldo(user_id)
        
        embed = Embed(title="❌ ¡PERDISTE!", color=0xFF0000)
        embed.add_field(name="💰 Apostaste", value=f"{apostado:,}", inline=True)
        embed.add_field(name="💵 Perdiste", value=f"-{apostado:,}", inline=True)
        embed.add_field(name="💎 Saldo actual", value=f"{saldo_nuevo:,}", inline=True)
        embed.set_footer(text=f"{nombre} 😢")
    
    await mensaje.edit(embed=embed)

# ═══════════════════════════════════════════
# 🔧 !adm — SOLO TÚ
# ═══════════════════════════════════════════
@bot.command(name="adm")
async def adm_cmd(ctx, usuario=None, cantidad=None):
    # ⚠️ PON TU ID DE DISCORD AQUÍ ABAJO
    MI_ID = "1430296740753313875"
    
    if str(ctx.author.id) != MI_ID:
        return await ctx.send("❌ No tienes permiso para usar este comando")
    
    if usuario is None or cantidad is None:
        return await ctx.send("❌ Uso: `!adm @usuario 5000`")
    
    if not ctx.message.mentions:
        return await ctx.send("❌ Menciona a un usuario")
    
    try:
        cantidad = int(cantidad)
    except ValueError:
        return await ctx.send("❌ Escribe un número válido")
    
    if cantidad <= 0:
        return await ctx.send("❌ La cantidad debe ser mayor a 0")
    
    mencion = ctx.message.mentions[0]
    await agregar_saldo(str(mencion.id), cantidad)
    saldo_nuevo = await obtener_saldo(str(mencion.id))
    
    embed = Embed(title="🔧 ADMIN — Dinero agregado", color=0x9B59B6)
    embed.add_field(name="👤 Usuario", value=f"{mencion.mention}", inline=False)
    embed.add_field(name="💵 Cantidad", value=f"+{cantidad:,}", inline=False)
    embed.add_field(name="💰 Nuevo saldo", value=f"{saldo_nuevo:,}", inline=False)
    
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════
# 🚀 INICIAR
# ═══════════════════════════════════════════
bot.run(TOKEN)
