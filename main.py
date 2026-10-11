import discord
from flask import Flask
import threading
import os

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

# ── ARRANCAR EL BOT ──
client.run(TOKEN)
