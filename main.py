import os
import random
import asyncio
import discord
from discord import Embed
from discord.ext import commands

# ═══════════════════════════════════════════
# ⚙️ CONFIGURACIÓN DEL BOT
# ═══════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True  # ⚠️ ¡NO OLVIDES ACTIVAR ESTO EN DISCORD!

bot = commands.Bot(command_prefix="!", intents=intents)

# ═══════════════════════════════════════════
# 🟢 CUANDO EL BOT SE ENCIENDE
# ═══════════════════════════════════════════
@bot.event
async def on_ready():
    print("\n" + "=" * 50)
    print(f"✅ BOT CONECTADO COMO: {bot.user}")
    print(f"🌐 SERVIDORES: {len(bot.guilds)}")
    print("📋 COMANDOS CARGADOS:")
    for comando in bot.commands:
        print(f"   ✓ !{comando.name}")
    print("=" * 50 + "\n")

# ═══════════════════════════════════════════
# ❌ MANEJO DE ERRORES (para ver qué falla)
# ═══════════════════════════════════════════
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"⚠️ Comando no encontrado: !{ctx.invoked_with}")
        return await ctx.send(f"❌ El comando `!{ctx.invoked_with}` no existe")
    print(f"❌ ERROR en !{ctx.command}: {error}")
    await ctx.send("⚠️ Ocurrió un error al ejecutar el comando")

# ═══════════════════════════════════════════
# 🏓 COMANDO DE PRUEBA
# ═══════════════════════════════════════════
@bot.command(name="ping")
async def ping_cmd(ctx):
    latencia = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latencia}ms")

# ═══════════════════════════════════════════
# 🎲 COMANDO DE APUESTA — VERSIÓN COMPLETA
# ═══════════════════════════════════════════
@bot.command(name="apuesta")
async def apuesta_completa(ctx, cantidad=None):
    # ─── PASO 1: Validar entrada ───
    if cantidad is None:
        return await ctx.send("❌ Usa: `!apuesta 100`")
    
    # ─── PASO 2: Convertir a número ───
    try:
        apostado = int(cantidad)
    except ValueError:
        return await ctx.send("❌ Escribe un número válido")
    
    if apostado <= 0:
        return await ctx.send("❌ La cantidad debe ser mayor a 0")
    
    # ─── PASO 3: Cálculos matemáticos REALES ───
    ganancia = apostado * 2
    total_recibido = apostado + ganancia
    
    # ─── PASO 4: Embed inicial (animación) ───
    embed_cargando = Embed(
        title="🎲 Lanzando moneda...",
        description=f"Apostaste: **{apostado}** monedas",
        color=0xFFD700
    )
    embed_cargando.set_thumbnail(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    embed_cargando.set_footer(text=ctx.author.display_name)
    
    # Enviar mensaje y GUARDARLO para editarlo después
    mensaje = await ctx.send(embed=embed_cargando)
    
    # ─── PASO 5: Esperar 2 segundos ───
    await asyncio.sleep(2)
    
    # ─── PASO 6: Embed final con resultado ───
    embed_resultado = Embed(
        title="✅ ¡GANASTE!",
        color=0x00FF00
    )
    embed_resultado.add_field(name="💰 Apostaste", value=f"{apostado}", inline=True)
    embed_resultado.add_field(name="💵 Ganancia", value=f"+{ganancia}", inline=True)
    embed_resultado.add_field(name="💎 Total", value=f"{total_recibido}", inline=True)
    embed_resultado.set_footer(text=ctx.author.display_name)
    
    # ─── PASO 7: EDITAR el mismo mensaje ───
    await mensaje.edit(embed=embed_resultado)

# ═══════════════════════════════════════════
# 🚀 INICIAR EL BOT
# ═══════════════════════════════════════════
bot.run(TOKEN)
