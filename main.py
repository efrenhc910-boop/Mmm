import os
import random
import json
import asyncio
from flask import Flask
import threading
import discord
from discord.ext import commands

# ── CARGAR TOKEN DE LAS VARIABLES DE ENTORNO ──
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ ERROR: No se encontró la variable TOKEN en el entorno.")
    exit(1)

# ── FLASK — Mantener activo en Render ──
app = Flask(__name__)

@app.route('/')
def activo():
    return "✅ Bot de apuestas activo y funcionando"

def iniciar_flask():
    app.run(host='0.0.0.0', port=8080)

# ── CONFIGURACIÓN DE BASE DE DATOS LOCAL (JSON) ──
DB_FILE = "database.json"

def cargar_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def obtener_usuario(user_id):
    db = cargar_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {
            "goldcoins": 1000,  # Monedas iniciales por defecto
            "Victorias": 0,
            "Derrotas": 0,
            "Piedad": 0,
            "Multiplicador": 2
        }
        guardar_db(db)
    return db[uid]

def guardar_usuario(user_id, datos):
    db = cargar_db()
    db[str(user_id)] = datos
    guardar_db(db)

# ── CONFIGURACIÓN DEL BOT CON SOPORTE PARA CUALQUIER MAYÚSCULA/MINÚSCULA ──
intents = discord.Intents.default()
intents.message_content = True
# case_insensitive=True permite que .apuesta, .ApUeStA, .APUESTA funcionen por igual
bot = commands.Bot(command_prefix=".", intents=intents, case_insensitive=True)

# Control de Cooldowns manual en memoria
cooldowns = {}

@bot.event
async def on_ready():
    print("✅——————————————————————")
    print(f"✅ Conectado como: {bot.user}")
    print(f"✅ ID del bot: {bot.user.id}")
    print("✅ Bot de Apuestas en línea 🟢")
    print("✅——————————————————————")

@bot.command(name="apuesta")
async def apuesta(ctx, *, arg: str = None):
    # ── MENCION Y CONFIGURACIÓN INICIAL ──
    author_id = str(ctx.author.id)
    datos = obtener_usuario(author_id)
    
    # Validar límite máximo global de monedas
    if datos["goldcoins"] >= 100000000:
        await ctx.reply("❌ No puedes apostar — Superaste el límite de monedas.")
        return

    # Validar entrada vacía
    if not arg:
        await ctx.reply("<a:alarm:1548935861020663811> Uso: `.apuesta 10000` o `.apuesta all`")
        return

    # ── COOLDOWN DE 6 SEGUNDOS ──
    import time
    tiempo_actual = time.time()
    ultimo_uso = cooldowns.get(author_id, 0)
    tiempo_restante = 6 - (tiempo_actual - ultimo_uso)
    if tiempo_restante > 0:
        await ctx.reply(f"<a:alarm:1548935861020663811> Espera **{int(tiempo_restante)}s** para volver a apostar.")
        return
    cooldowns[author_id] = tiempo_actual

    # ── PROCESAR APUESTA Y SALDO ──
    saldo_actual = datos["goldcoins"]
    arg_lower = arg.strip().lower()

    if arg_lower == "all":
        apuesta_val = saldo_actual
    else:
        try:
            apuesta_val = int(arg)
        except ValueError:
            await ctx.reply("<a:alarm:1548935861020663811> Debes introducir una cantidad válida o escribir `all`.")
            return

    # ── LÍMITE DINÁMICO ──
    limite = 30000
    if saldo_actual >= 100000:
        limite = 300000
    if saldo_actual >= 300000:
        limite = 500000
    if saldo_actual >= 500000:
        limite = 1000000
    if saldo_actual >= 1000000:
        limite = 1000000

    if apuesta_val > limite:
        apuesta_val = limite

    # Validaciones finales de la apuesta
    if apuesta_val < 11:
        await ctx.reply("<a:alarm:1548935861020663811> La apuesta mínima es de `11` monedas de oro.")
        return
    if saldo_actual < apuesta_val:
        await ctx.reply("<a:alarm:1548935861020663811> No tienes suficientes monedas de oro.")
        return

    # ── CÁLCULO DE PROBABILIDAD CON PIEDAD ──
    piedad_guardada = datos["Piedad"]
    probabilidad_extra = piedad_guardada * 10
    umbral_victoria = 500 - probabilidad_extra
    if umbral_victoria < 1:
        umbral_victoria = 1

    # Descontar apuesta y tirar dado
    saldo_actual -= apuesta_val
    datos["goldcoins"] = saldo_actual
    guardar_usuario(author_id, datos)

    roll = random.randint(1, 1000)

    # ── MENSAJE DE ANIMACIÓN INICIAL ──
    titulo_animacion = random.choice(["COINFLIP", "COINFLIPS"])
    embed = discord.Embed(title=f"***{titulo_animacion}***", color=0xFFD700)
    embed.set_image(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    
    mensaje_embed = await ctx.reply(embed=embed)
    
    # Simular tiempo de espera de animación (entre 4 y 8 segundos)
    tiempo_espera = random.randint(4, 8)
    await asyncio.sleep(tiempo_espera)

    # Recargar datos actualizados
    datos = obtener_usuario(author_id)

    # ── X5 MEGA PREMIO (Roll == 1000) ──
    if roll == 1000:
        datos["Victorias"] += 1
        victorias_actuales = datos["Victorias"]
        multiplicador_actual = 2 + ((victorias_actuales - 1) * 0.5)

        datos["Derrotas"] = 0
        datos["Piedad"] = 0
        datos["Multiplicador"] = multiplicador_actual

        premio = apuesta_val * 5 * multiplicador_actual
        datos["goldcoins"] += premio
        guardar_usuario(author_id, datos)

        mult_total = 5 * multiplicador_actual

        embed_final = discord.Embed(
            description=f"━━━━━━━━━━━━━━━━━━━━\n# ***X5 — EXTREMADAMENTE RARO***\n\n💎 **MULTIPLICADOR**\n➥ `x{mult_total}`\n\n🪙 **PREMIO**\n➥ `+{f'{premio:,}'.replace(',', '.')}` monedas de oro\n━━━━━━━━━━━━━━━━━━━━\n***¡Has conseguido el multiplicador más raro!***\n\n💰 **SALDO ACTUAL**\n➥ `{f'{datos[\"goldcoins\"]:,}'.replace(',', '.')}` monedas de oro\n━━━━━━━━━━━━━━━━━━━━",
            color=0xC0C0FF
        )
        embed_final.set_footer(text=f"★★• {ctx.author.display_name}")
        await mensaje_embed.edit(embed=embed_final)

    # ── VICTORIA X2 (Roll > umbral_victoria) ──
    elif roll > umbral_victoria:
        datos["Victorias"] += 1
        victorias_actuales = datos["Victorias"]
        multiplicador_actual = 2 + ((victorias_actuales - 1) * 0.5)

        datos["Derrotas"] = 0
        datos["Piedad"] = 0
        datos["Multiplicador"] = multiplicador_actual

        premio = apuesta_val * multiplicador_actual
        datos["goldcoins"] += premio
        guardar_usuario(author_id, datos)

        embed_final = discord.Embed(
            description=f"# Victoria 🏆\n━━━━━━━━━━━━━━━━━━━━\n🪙 **APUESTA**\n➥ `{f'{apuesta_val:,}'.replace(',', '.')}` monedas de oro\n\n💰 **PREMIO**\n➥ `+{f'{premio:,}'.replace(',', '.')}` monedas de oro\n\n📈 **MULTIPLICADOR**\n➥ `x{multiplicador_actual}`\n━━━━━━━━━━━━━━━━━━━━",
            color=0x00FF66
        )
        embed_final.set_footer(text=f"★★• {ctx.author.display_name}")
        await mensaje_embed.edit(embed=embed_final)

    # ── DERROTA ──
    else:
        datos["Derrotas"] += 1
        piedad_actual = datos["Piedad"]

        if datos["Derrotas"] >= 2:
            piedad_actual += 10

        datos["Victorias"] = 0
        datos["Multiplicador"] = 2
        datos["Piedad"] = piedad_actual
        guardar_usuario(author_id, datos)

        embed_final = discord.Embed(
            description=f"━━━━━━━━━━━━━━━━━━━━\n# ***DERROTA***\n\n🪙 **MONEDAS DE ORO PERDIDAS**\n➥ `-{f'{apuesta_val:,}'.replace(',', '.')}`\n━━━━━━━━━━━━━━━━━━━━\n***La fortuna no estuvo de tu lado.***\n\n💰 **SALDO ACTUAL**\n➥ `{f'{datos[\"goldcoins\"]:,}'.replace(',', '.')}` monedas de oro\n\n🍀 **PIEDAD ACUMULADA**\n➥ `{piedad_actual}%` extra de probabilidad\n━━━━━━━━━━━━━━━━━━━━",
            color=0xFF0000
        )
        embed_final.set_footer(text=f"★★• {ctx.author.display_name}")
        await mensaje_embed.edit(embed=embed_final)

# ── INICIAR FLASK Y BOT ──
if __name__ == "__main__":
    hilo = threading.Thread(target=iniciar_flask)
    hilo.daemon = True
    hilo.start()
    
    bot.run(TOKEN)
