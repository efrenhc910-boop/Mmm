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

# ✅ case_insensitive = True → !Adm, !aDm, !dONA funcionan igual
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True
)

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

    embed = Embed(
        title="<a:Crown1:1548943482561765476>  BÓVEDA DE ORO",
        description="",
        color=0xFFD700
    )
    embed.add_field(
        name="<a:money:1548943165040496793> Monedas de Oro",
        value=f"```yaml\n{saldo:,}\n```",
        inline=False
    )
    embed.set_footer(
        text=f"Revisado por: {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url
    )
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════
# 🎲 !apuesta — Corregido
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
            f"<a:fail:1548936569098866758> No tienes suficiente dinero.\n"
            f"<a:money:1548943165040496793> Tu saldo: **{saldo_actual:,}**"
        )

    # ✅ Se descuenta INMEDIATAMENTE al apostar
    await establecer_saldo(user_id, saldo_actual - apostado)

    # 🎲 Animación — Lanzando moneda
    embed_espere = Embed(
        title="<a:NewFlame:1548943658521202780>  LANZANDO MONEDA...",
        description=f"""

<a:PinkFlameFlicker:1547845151844470807> **Apostaste:** `{apostado:,}` monedas
<:CROWN:1547845401355227257> **Saldo después de apostar:** `{saldo_actual - apostado:,}`

<a:time:1548940539335024660> Espera un momento...
        """,
        color=0x9B59B6
    )
    embed_espere.set_footer(text=f"Buena suerte, {nombre}! 🍀")
    mensaje = await ctx.send(embed=embed_espere)
    await asyncio.sleep(2)

    # 50% Ganar / 50% Perder
    if random.choice([True, False]):
        # ✅ ¡GANASTE! → Recibes el doble (tu apuesta + ganancia)
        ganancia_total = apostado * 2
        await agregar_saldo(user_id, ganancia_total)
        saldo_nuevo = await obtener_saldo(user_id)

        embed = Embed(
            title="<a:Vip:1548936294489391167>  ¡VICTORIA!",
            description=f"""

<a:money:1548943165040496793> **Apostaste:** `{apostado:,}`
<a:visa:1548943205368860742> **Ganancia neta:** `+{apostado:,}`
<a:Regalo:1548971616883712051> **Recibes:** `+{ganancia_total:,}`
<:CROWN:1547845401355227257> **Saldo actual:** `{saldo_nuevo:,}`

<a:chido:1548939480302620672> ¡Felicidades, {nombre}! ¡Ganaste el doble!
            """,
            color=0x00FF66
        )
    else:
        # ❌ ¡PERDISTE! → No recuperas lo apostado
        saldo_nuevo = await obtener_saldo(user_id)

        embed = Embed(
            title="<a:fail:1548936569098866758>  DERROTA",
            description=f"""

<a:money:1548943165040496793> **Apostaste:** `{apostado:,}`
<:bad:1548942828195938354> **Perdiste:** `-{apostado:,}`
<:CROWN:1547845401355227257> **Saldo actual:** `{saldo_nuevo:,}`

<:sad:1548943352882528256> Ánimo, {nombre}! ¡La suerte cambia!
            """,
            color=0xFF4444
        )

    await mensaje.edit(embed=embed)

# ═══════════════════════════════════════════
# 💸 !dona — Transferir monedas
# ═══════════════════════════════════════════
@bot.command(name="dona")
async def dona_cmd(ctx, *args):
    if len(args) < 2:
        return await ctx.send(
            "<a:alarm:1548935861020663811> Uso: `!dona @usuario 1000` o `!dona 1000 @usuario`"
        )
    
    mencion = ctx.message.mentions[0] if ctx.message.mentions else None
    if not mencion:
        return await ctx.send("<a:alarm:1548935861020663811> Debes mencionar a un usuario.")
    
    cantidad = None
    for arg in args:
        if arg.isdigit():
            cantidad = int(arg)
            break
    
    if cantidad is None:
        return await ctx.send("❌ Debes introducir una cantidad válida.")
    
    if cantidad <= 0:
        return await ctx.send("<a:alarm:1548935861020663811> La cantidad debe ser mayor a `0`.")
    
    saldo_remitente = await obtener_saldo(str(ctx.author.id))
    
    if saldo_remitente < cantidad:
        return await ctx.send(
            f"<a:alarm:1548935861020663811> No tienes suficientes monedas de oro.\n"
            f"💰 Tu saldo: **{saldo_remitente:,}**"
        )
    
    if mencion.id == ctx.author.id:
        return await ctx.send("<a:alarm:1548935861020663811> No puedes darte monedas de oro a ti mismo.")
    
    await establecer_saldo(str(ctx.author.id), saldo_remitente - cantidad)
    saldo_destino = await obtener_saldo(str(mencion.id))
    await establecer_saldo(str(mencion.id), saldo_destino + cantidad)
    saldo_nuevo = await obtener_saldo(str(ctx.author.id))
    
    embed = Embed(
        title="<a:emoji_45:1548971921738305556>  ENTREGA COMPLETADA",
        description="━━━━━━━━━━━━━━━━━━━━",
        color=0xFFD700
    )
    embed.add_field(
        name="👤 REMITENTE",
        value=f"➥ {ctx.author.display_name}",
        inline=False
    )
    embed.add_field(
        name="<a:Regalo:1548971616883712051> DESTINATARIO",
        value=f"➥ {mencion.display_name}",
        inline=False
    )
    embed.add_field(
        name="<a:emoji_45:1548971921738305556> CANTIDAD ENTREGADA",
        value=f"➥ `{cantidad:,}` monedas de oro",
        inline=False
    )
    embed.add_field(
        name="<a:emoji_45:1548971921738305556> TU SALDO ACTUAL",
        value=f"➥ `{saldo_nuevo:,}` monedas de oro",
        inline=False
    )
    embed.set_footer(text="The Most Wanted Corporation")
    
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════
# 🔧 !adm — SOLO TÚ
# ═══════════════════════════════════════════
@bot.command(name="adm")
async def adm_cmd(ctx, usuario=None, cantidad=None):
    MI_ID = "1430296740753313875"

    if str(ctx.author.id) != MI_ID:
        return await ctx.send("<a:fail:1548936569098866758> No tienes permiso para usar este comando")

    if usuario is None or cantidad is None:
        return await ctx.send("<a:alarm:1548935861020663811> Uso: `!adm @usuario 5000`")

    if not ctx.message.mentions:
        return await ctx.send("<a:alarm:1548935861020663811> Menciona a un usuario")

    try:
        cantidad = int(cantidad)
    except ValueError:
        return await ctx.send("<a:alarm:1548935861020663811> Escribe un número válido")

    if cantidad <= 0:
        return await ctx.send("<a:alarm:1548935861020663811> La cantidad debe ser mayor a 0")

    mencion = ctx.message.mentions[0]
    await agregar_saldo(str(mencion.id), cantidad)
    saldo_nuevo = await obtener_saldo(str(mencion.id))

    embed = Embed(
        title="<:BlueCrown:1547845636840230976>  PANEL DE ADMINISTRACIÓN",
        description=f"<a:Regalo:1548971616883712051> Dinero agregado exitosamente",
        color=0x9B59B6
    )
    embed.add_field(
        name="<a:Vip:1548936294489391167> Usuario",
        value=f"{mencion.mention}",
        inline=False
    )
    embed.add_field(
        name="<a:money:1548943165040496793> Cantidad Agregada",
        value=f"`+{cantidad:,}`",
        inline=False
    )
    embed.add_field(
        name="<:CROWN:1547845401355227257> Nuevo Saldo",
        value=f"`{saldo_nuevo:,}`",
        inline=False
    )
    embed.set_footer(
        text=f"Ejecutado por: {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url
    )

    await ctx.send(embed=embed)

# alch nosé 
bot.run(TOKEN)
