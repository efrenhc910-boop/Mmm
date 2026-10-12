import os
import asyncio
import discord
from discord import Embed
from discord.ext import commands

# ═══════════════════════════════════════════
# ⚙️ CONFIGURACIÓN
# ═══════════════════════════════════════════
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ═══════════════════════════════════════════
# 🟢 BOT ENCENDIDO
# ═══════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Conectado: {bot.user}")
    print(f"📋 Comandos: {[c.name for c in bot.commands]}")

# ═══════════════════════════════════════════
# ❌ MANEJO DE ERRORES (para que no sean silenciosos)
# ═══════════════════════════════════════════
@bot.event
async def on_command_error(ctx, error):
    print(f"❌ ERROR: {error}")
    await ctx.send(f"⚠️ Error: {error}")

# ═══════════════════════════════════════════
# 🧪 COMANDO DE PRUEBA
# ═══════════════════════════════════════════
@bot.command(name="ping")
async def ping_cmd(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

# ═══════════════════════════════════════════
# 🎲 APUESTA BÁSICA (calcula y duplica de verdad)
# ═══════════════════════════════════════════
@bot.command(name="apuesta")
async def apuesta_cmd(ctx, cantidad=None):
    # PASO 1: Validar que el usuario escribió un número
    if cantidad is None:
        return await ctx.send("❌ Escribe: `!apuesta 100`")
    
    # PASO 2: Convertir texto a número (para poder multiplicar)
    try:
        apostado = int(cantidad)
    except ValueError:
        return await ctx.send("❌ Escribe un número válido")
    
    if apostado <= 0:
        return await ctx.send("❌ La cantidad debe ser mayor a 0")
    
    # PASO 3: Cálculo REAL con variables
    ganancia = apostado * 2          # ← Aquí se duplica de verdad
    total = apostado + ganancia      # ← Total que recibe el usuario
    
    # PASO 4: Crear embed inicial (la "animación")
    embed_inicial = Embed(
        title="🎲 Lanzando moneda...",
        description=f"Apostaste: **{apostado}** monedas",
        color=0xFFD700  # Dorado
    )
    embed_inicial.set_footer(text=ctx.author.display_name)
    
    # Enviar el mensaje y guardarlo para editarlo después
    mensaje = await ctx.send(embed=embed_inicial)
    
    # PASO 5: Esperar 2 segundos (simula el giro)
    await asyncio.sleep(2)
    
    # PASO 6: Crear embed final con el resultado calculado
    embed_final = Embed(
        title="✅ ¡GANASTE!",
        description=f"""
🪙 Apostaste: **{apostado}**
💰 Ganancia: **+{ganancia}**
💎 Total recibido: **{total}**
        """,
        color=0x00FF00  # Verde
    )
    embed_final.set_footer(text=ctx.author.display_name)
    
    # PASO 7: EDITAR el mismo mensaje (no enviar uno nuevo)
    await mensaje.edit(embed=embed_final)

# ═══════════════════════════════════════════
# 🚀 INICIAR BOT
# ═══════════════════════════════════════════
bot.run(TOKEN)
