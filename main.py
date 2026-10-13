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
intents.message_content = True  # ⚠️ ¡ACTIVA ESTO EN EL PORTAL DE DISCORD!

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True
)
bot.uptime = discord.utils.utcnow()

# ═══════════════════════════════════════════
# 🟢 ENCENDIDO
# ═══════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"\n✅ Conectado: {bot.user}")
    print(f"📋 Comandos: {[c.name for c in bot.commands]}\n")

# ═══════════════════════════════════════════
# 🔄 EVENTO DE MENCIÓN — CORREGIDO
# ═══════════════════════════════════════════
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)
    
    # Mostrar stats al mencionar al bot
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        ctx = await bot.get_context(message)
        if not ctx.valid:
            await stats_cmd(ctx)

# ═══════════════════════════════════════════
# 📊 !stats — COMANDO INDEPENDIENTE
# ═══════════════════════════════════════════
@bot.command(name="stats")
async def stats_cmd(ctx):
    colores_neon = [
        0xFF0055, 0x00F0FF, 0x7000FF, 0xFF00F7, 0x00FF66,
        0xFFB700, 0xFF5722, 0x00E5FF, 0x9D00FF, 0xFF0033
    ]
    color = random.choice(colores_neon)
    nombre_bot = str(bot.user)
    tiempo_activo = f"En línea desde {discord.utils.format_dt(bot.uptime, style='R')}"
    
    embed = Embed(
        title=f"# 𝙎𝙩𝙖𝙩𝙨 𝙙𝙚 {nombre_bot}",
        description=f"""
### 📊 𝙄𝙣𝙛𝙤𝙧𝙢𝙖𝙘𝙞𝙤́𝙣 𝙂𝙚𝙣𝙚𝙧𝙖𝙡
> 🤖 **𝙉𝙤𝙢𝙗𝙧𝙚:** `{nombre_bot}`
> 👑 **𝘾𝙧𝙚𝙖𝙙𝙤𝙧:** `𝕰𝖝𝖙𝖊𝖗𝖒𝖎𝖓𝖆𝖙𝖔𝖗`
> ⏳ **𝙏𝙞𝙚𝙢𝙥𝙤 𝘼𝙘𝙩𝙞𝙫𝙤:** `{tiempo_activo}`
        """,
        color=color
    )
    # ✅ Imagen de stats
    embed.set_thumbnail(url="https://c.tenor.com/a6432ghaSToAAAAC/tenor.gif")
    embed.set_footer(
        text=f"Solicitado por {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url
    )
    embed.timestamp = discord.utils.utcnow()
    
    # 🔑 TU ID DE SERVIDOR
    ID_SERVIDOR = 1545945054378598470
    
    # Obtener o crear invitación automáticamente
    try:
        servidor = bot.get_guild(ID_SERVIDOR)
        enlace_servidor = "https://discord.gg/TU_ENLACE_PERMANENTE"
        
        if servidor:
            enlaces = await servidor.invites()
            for inv in enlaces:
                if inv.max_age == 0 and inv.max_uses == 0:
                    enlace_servidor = inv.url
                    break
            
            if enlace_servidor == "https://discord.gg/TU_ENLACE_PERMANENTE":
                canal = servidor.system_channel or next(iter(servidor.channels))
                nueva_inv = await canal.create_invite(
                    max_age=0,
                    max_uses=0,
                    unique=False,
                    reason="Invitación permanente del bot"
                )
                enlace_servidor = nueva_inv.url
    except Exception as e:
        enlace_servidor = "https://discord.gg/TU_ENLACE_PERMANENTE"
    
    view = discord.ui.View(timeout=None)
    
    @discord.ui.button(label="Mi DC", emoji="🥇", style=discord.ButtonStyle.gray)
    async def servidor_btn(interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"¡Únete a mi servidor!\n{enlace_servidor}", ephemeral=True)
    
    view.add_item(servidor_btn)
    
    await ctx.send(embed=embed, view=view)

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
    embed.set_thumbnail(url="https://media.tenor.com/n4DonP_Qv1MAAAAi/make-it-rain-money.gif")
    embed.set_footer(
        text=f"Revisado por: {ctx.author.display_name}",
        icon_url=ctx.author.avatar.url
    )
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
            f"<a:fail:1548936569098866758> No tienes suficiente dinero.\n"
            f"<a:money:1548943165040496793> Tu saldo: **{saldo_actual:,}**"
        )

    await establecer_saldo(user_id, saldo_actual - apostado)

    embed_espere = Embed(
        title="<a:NewFlame:1548943658521202780>  LANZANDO MONEDA...",
        description=f"""

<a:PinkFlameFlicker:1547845151844470807> **Apostaste:** `{apostado:,}` monedas
<:CROWN:1547845401355227257> **Saldo después de apostar:** `{saldo_actual - apostado:,}`

<a:time:1548940539335024660> Espera un momento...
        """,
        color=0x9B59B6
    )
    # ✅ Imagen de moneda girando
    embed_espere.set_thumbnail(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    embed_espere.set_footer(text=f"Buena suerte, {nombre}! 🍀")
    mensaje = await ctx.send(embed=embed_espere)
    await asyncio.sleep(2)

    if random.choice([True, False]):
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
# 💸 !dona
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
# 🔧 !adm
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

# ═══════════════════════════════════════════
# 📌 AQUÍ ABAJO PEGA TUS COMANDOS NUEVOS 👇
# ═══════════════════════════════════════════

@bot.command(name="ranking", aliases=["top"])
async def ranking_cmd(ctx):
    lista_usuarios = []
    
    # Recorrer TODOS los registros del JSON
    for clave, cantidad in _datos.items():
        # Intentar extraer el ID del usuario de distintas formas
        user_id = None
        
        # Formato: "saldo_123456789"
        if clave.startswith("saldo_"):
            id_parte = clave.replace("saldo_", "")
            try:
                user_id = int(id_parte)
            except ValueError:
                continue
        # Formato directo: "123456789"
        else:
            try:
                user_id = int(clave)
            except ValueError:
                continue
        
        # Validar cantidad
        try:
            monedas = int(cantidad)
            if monedas > 0:
                lista_usuarios.append((-monedas, user_id, monedas))
        except (ValueError, TypeError):
            continue
    
    # Ordenar y tomar top 10
    lista_usuarios.sort()
    top10 = lista_usuarios[:10]
    
    medallas = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    descripcion = ""
    
    for i, (_, user_id, monedas) in enumerate(top10, 1):
        try:
            usuario = await bot.fetch_user(user_id)
            nombre = usuario.display_name
        except:
            nombre = f"Usuario #{i}"
        
        descripcion += f"{medallas[i-1]} **#{i} — {nombre}**\n➥ **{monedas:,}** monedas de oro\n\n"
    
    if not descripcion:
        descripcion = "😕 No hay usuarios con monedas todavía.\n\n💡 Si sabes que sí hay, revisa el formato de las claves en datos.json"
    
    embed = Embed(
        title="🏆 Ranking de monedas de oro",
        description=descripcion.strip(),
        color=0xFFD700
    )
    embed.set_footer(text="★★• Ranking — Más ricos primero")
    
    await ctx.send(embed=embed)








# ═══════════════════════════════════════════
# 🚀 INICIAR
# ═══════════════════════════════════════════
bot.run(TOKEN)
