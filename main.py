# ==================================================
# LIBRERÍAS — No tocar, cargan las herramientas
# ==================================================
import discord              # Conecta con Discord
from flask import Flask     # Mantiene el bot activo 24/7
import threading            # Ejecuta tareas en paralelo
import os                   # Lee el token de forma SEGURA desde Render

# ==================================================
# TOKEN — Se carga de forma OCULTA desde Render
# ==================================================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ERROR: No se encontró la variable TOKEN en Render")
    print("⚠️  Asegúrate de agregar TOKEN como variable de entorno en Render")
    exit(1)

# ==================================================
# FLASK — Evita que Render apague el bot
# ==================================================
app = Flask(__name__)

@app.route('/')
def mantener_activo():
    return "✅ Bot activo y seguro 24/7"

def servidor_flask():
    app.run(host="0.0.0.0", port=8080)

# ==================================================
# CONFIGURACIÓN DEL BOT
# ==================================================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ==================================================
# AL CONECTARSE
# ==================================================
@client.event
async def on_ready():
    print("✅——————————————————————")
    print(f"✅ Conectado como: {client.user}")
    print(f"✅ ID del bot: {client.user.id}")
    print("✅ Bot encendido 24/7 🟢")
    print("✅——————————————————————")

# ==================================================
# TUS COMANDOS — Agrega o quita aquí
# ==================================================
@client.event
async def on_message(mensaje):
    # Ignorar mensajes del propio bot
    if mensaje.author == client.user:
        return

    # Convertir a minúsculas → .HoLa / .hOLa / .HOLA → todos funcionan ✅
    texto = mensaje.content.lower()

    # Comando: .hola (cualquier combinación de mayúsculas funciona)
    if texto == ".hola":
        await mensaje.channel.send("hola.")

    # Comando: test
    if texto == "test":
        await mensaje.channel.send("hola 👋")

    # Comando: cf
    if texto == "cf":
        await mensaje.channel.send("🎲 Sistema de apuestas activo")

    # Comando: aventura
    if texto == "aventura":
        await mensaje.channel.send("⚔️ ¡Aventura iniciada!")

    # Aquí puedes agregar más comandos
    # if texto == ".comando":
    #     await mensaje.channel.send("respuesta")

# ==================================================
# INICIAR TODO — No tocar
# ==================================================
hilo = threading.Thread(target=servidor_flask)
hilo.daemon = True
hilo.start()

client.run(TOKEN)
