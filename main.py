import discord
from flask import Flask
import threading
import os
import asyncio

# ── CARGAR TOKEN ──
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ ERROR: No se encontró la variable TOKEN en Render")
    exit(1)

# ── FLASK — Mantener activo ──
app = Flask(__name__)

@app.route('/')
def activo():
    return "✅ Bot activo y funcionando"

def iniciar_flask():
    app.run(host='0.0.0.0', port=8080)

# ── CONFIGURACIÓN DEL BOT ──
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("✅——————————————————————")
    print(f"✅ Conectado como: {client.user}")
    print(f"✅ ID del bot: {client.user.id}")
    print("✅ Bot en línea 🟢")
    print("✅——————————————————————")

# ── INICIAR FLASK EN SEGUNDO PLANO ──
hilo = threading.Thread(target=iniciar_flask)
hilo.daemon = True
hilo.start()

# ── ARRANCAR EL BOT CON REINTENTO SI HAY BAN DE IP (HTTP 429) ──
async def iniciar_bot():
    mientras_intentando = True
    mientras_intentando = True
    while mientras_intentando:
        try:
            await client.start(TOKEN)
            mientras_intentando = False
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print("⚠️ IP Bloqueada por Discord (Rate Limit / Error 429). Esperando 60 segundos antes de reintentar...")
                await asyncio.sleep(60)
            else:
                raise e

if __name__ == "__main__":
    asyncio.run(iniciar_bot())
