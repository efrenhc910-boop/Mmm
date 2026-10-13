# ==================================================
# BOT DE DISCORD — Versión Auditada y Corregida
# discord.py >= 2.5.2, Python 3.10+
# ==================================================

import os
import random
import asyncio
import json
import shutil
from datetime import datetime
import discord
from discord.ext import commands
from discord import Embed

# ==================================================
# ⚙️ CONFIGURACIÓN
# ==================================================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True
)

# Validar token antes de iniciar
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERROR: Variable de entorno DISCORD_TOKEN no está configurada")
    print("   → Configúrala en tu plataforma de alojamiento")
    exit(1)

# ==================================================
# 💾 SISTEMA DE ALMACENAMIENTO JSON — MEJORADO
# ==================================================
ARCHIVO_DATOS = "datos.json"
ARCHIVO_RESPALDO = "datos_respaldo.json"
_datos = {}
_bloqueo_archivo = asyncio.Lock()

def _cargar_datos():
    """Carga datos con respaldo preventivo si el archivo está corrupto"""
    global _datos
    
    # Intentar cargar archivo principal
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                _datos = json.load(f)
            print(f"✅ Datos cargados: {len(_datos)} registros")
            return
        except json.JSONDecodeError as e:
            print(f"⚠️ Archivo principal corrupto: {e}")
            
            # Intentar recuperar desde respaldo
            if os.path.exists(ARCHIVO_RESPALDO):
                try:
                    with open(ARCHIVO_RESPALDO, "r", encoding="utf-8") as f:
                        _datos = json.load(f)
                    print(f"✅ Restaurado desde respaldo")
                    # Recuperar respaldo como principal
                    shutil.copy2(ARCHIVO_RESPALDO, ARCHIVO_DATOS)
                    return
                except Exception as respaldo_err:
                    print(f"❌ Respaldo también falló: respaldo_err")
            
            # Si no hay respaldo válido, respaldar archivo corrupto con marca de tiempo
            marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_corrupto = f"datos_corruptos_{marca_tiempo}.json"
            try:
                os.rename(ARCHIVO_DATOS, archivo_corrupto)
                print(f"⚠️ Archivo corrupto guardado como: {archivo_corrupto}")
            except OSError:
                pass
    
    # Archivo no existe o no se pudo recuperar → iniciar vacío
    _datos = {}
    print("ℹ️ Iniciando con base de datos vacía")

def _guardar_datos_sincrono():
    """Escritura atómica: escribir a temporal y luego renombrar"""
    # Crear respaldo del archivo actual antes de sobrescribir
    if os.path.exists(ARCHIVO_DATOS):
        try:
            shutil.copy2(ARCHIVO_DATOS, ARCHIVO_RESPALDO)
        except Exception as e:
            print(f"⚠️ No se pudo crear respaldo: {e}")
    
    # Escribir a archivo temporal
    archivo_temp = f"{ARCHIVO_DATOS}.tmp"
    try:
        with open(archivo_temp, "w", encoding="utf-8") as f:
            json.dump(_datos, f, ensure_ascii=False, indent=2)
        
        # Renombrar de forma atómica
        if os.name == "nt":  # Windows no permite renombrar sobre existente
            if os.path.exists(ARCHIVO_DATOS):
                os.remove(ARCHIVO_DATOS)
        os.replace(archivo_temp, ARCHIVO_DATOS)
    except Exception as e:
        # Limpiar archivo temporal si falla
        if os.path.exists(archivo_temp):
            os.remove(archivo_temp)
        raise e

async def _guardar_datos():
    """Versión asíncrona con bloqueo para evitar escrituras simultáneas"""
    async with _bloqueo_archivo:
        await asyncio.to_thread(_guardar_datos_sincrono)

# ─── Operaciones económicas con validación ───

def _normalizar_id(user_id) -> str:
    """Convierte cualquier formato de ID a cadena consistente"""
    return str(user_id).strip()

def obtener_saldo(user_id) -> int:
    """Obtener saldo garantizando que sea entero"""
    clave = f"saldo_{_normalizar_id(user_id)}"
    valor = _datos.get(clave, 0)
    try:
        return max(0, int(valor))
    except (TypeError, ValueError):
        return 0

async def establecer_saldo(user_id, cantidad: int):
    """Establecer saldo con validación"""
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValueError("La cantidad debe ser un número entero")
    
    if cantidad < 0:
        raise ValueError("El saldo no puede ser negativo")
    
    clave = f"saldo_{_normalizar_id(user_id)}"
    async with _bloqueo_archivo:
        _datos[clave] = cantidad
        await _guardar_datos()

async def agregar_saldo(user_id, cantidad: int):
    """Agregar/quitar saldo con validación y límite inferior a 0"""
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValueError("La cantidad debe ser un número entero")
    
    if cantidad == 0:
        return
    
    clave = f"saldo_{_normalizar_id(user_id)}"
    
    async with _bloqueo_archivo:
        actual = obtener_saldo(user_id)
        nuevo = max(0, actual + cantidad)
        _datos[clave] = nuevo
        await _guardar_datos()
        return nuevo

# Cargar al iniciar
_cargar_datos()

# ==================================================
# 🟢 EVENTOS DEL BOT
# ==================================================
@bot.event
async def on_ready():
    if not hasattr(bot, "_listo"):
        bot._listo = True
        print(f"\n✅ Conectado como: {bot.user}")
        print(f"🌐 Servidores: {len(bot.guilds)}")
        print(f"📋 Comandos cargados: {len(bot.commands)}\n")

@bot.event
async def on_command_error(ctx, error):
    """Manejo amigable de errores de comandos"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Comando no encontrado. Usa `!ayuda` si está disponible.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan argumentos. Revisa el uso del comando.")
    else:
        print(f"⚠️ Error en comando {ctx.command}: {error}")
        await ctx.send("❌ Ocurrió un error al ejecutar el comando. Inténtalo de nuevo.")

# ==================================================
# 📋 COMANDOS BÁSICOS
# ==================================================
@bot.command(name="test")
async def test_cmd(ctx):
    await ctx.send("¡Hola! 👋 El bot funciona correctamente.")

@bot.command(name="saldo")
async def saldo_cmd(ctx):
    saldo = obtener_saldo(ctx.author.id)
    embed = Embed(
        title="💰 Tu Saldo",
        description=f"Tienes **{saldo:,}** monedas de oro.",
        color=0xFFD700
    )
    await ctx.send(embed=embed)

# ==================================================
# ⭕ !rallado — TRES EN RAYA ❌ — VERSIÓN CORREGIDA
# ==================================================
COMBINACIONES_GANADORAS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontales
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Verticales
    [0, 4, 8], [2, 4, 6]               # Diagonales
]

class PartidaTerminada(Exception):
    pass

class TableroView(discord.ui.View):
    def __init__(self, jugador1, jugador2, mensaje_original=None):
        super().__init__(timeout=300)
        self.jugador1 = jugador1
        self.jugador2 = jugador2
        self.tablero = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.turno = 1  # 1 = jugador1, 2 = jugador2
        self.juego_activo = True
        self.mensaje_original = mensaje_original
        self._actualizar_botones()

    def _actualizar_botones(self):
        self.clear_items()
        for i in range(9):
            if self.tablero[i] == 1:
                etiqueta = "❌"
                desactivado = True
            elif self.tablero[i] == 2:
                etiqueta = "⭕"
                desactivado = True
            else:
                etiqueta = "⬜"
                desactivado = not self.juego_activo
            
            btn = discord.ui.Button(
                label=etiqueta,
                custom_id=f"casilla_{i}",
                disabled=desactivado,
                row=i // 3
            )
            btn.callback = self._crear_callback(i)
            self.add_item(btn)

    def _obtener_simbolo(self, jugador_numero):
        return "❌" if jugador_numero == 1 else "⭕"

    def _hay_ganador(self):
        for a, b, c in COMBINACIONES_GANADORAS:
            if self.tablero[a] == self.tablero[b] == self.tablero[c] != 0:
                return self.tablero[a]
        return None

    def _es_empate(self):
        return all(casilla != 0 for casilla in self.tablero)

    async def _finalizar_partida(self, resultado, ganador_obj=None):
        self.juego_activo = False
        self._actualizar_botones()
        self.stop()
        
        if resultado == "ganador":
            simbolo = self._obtener_simbolo(ganador_obj[0])
            ganador_user = ganador_obj[1]
            embed = Embed(
                title=f"🎉 ¡{simbolo} {ganador_user.display_name} GANA!",
                description="¡Partida terminada!",
                color=0x00FF66
            )
        elif resultado == "empate":
            embed = Embed(
                title="🤝 ¡EMPATE!",
                description="El tablero está lleno y nadie ganó.",
                color=0xFFD700
            )
        else:  # timeout
            embed = Embed(
                title="⏱️ PARTIDA EXPIRADA",
                description="No hubo movimiento en 5 minutos. Partida cancelada.",
                color=0x999999
            )
        
        try:
            await self.mensaje_original.edit(embed=embed, view=self)
        except discord.NotFound:
            pass  # El mensaje ya no existe
        except discord.HTTPException:
            pass

    def _crear_callback(self, indice):
        async def callback(interaction: discord.Interaction):
            if not self.juego_activo:
                await interaction.response.defer()
                return

            # Validar turno y jugador
            if self.turno == 1 and interaction.user != self.jugador1:
                await interaction.response.send_message("❌ No es tu turno.", ephemeral=True)
                return
            if self.turno == 2 and interaction.user != self.jugador2:
                await interaction.response.send_message("❌ No es tu turno.", ephemeral=True)
                return

            # Casilla ocupada
            if self.tablero[indice] != 0:
                await interaction.response.defer()
                return

            # Colocar ficha
            self.tablero[indice] = self.turno

            # Verificar ganador
            ganador = self._hay_ganador()
            if ganador:
                ganador_user = self.jugador1 if ganador == 1 else self.jugador2
                await self._finalizar_partida("ganador", (ganador, ganador_user))
                await interaction.response.edit_message(view=self)
                return

            # Verificar empate
            if self._es_empate():
                await self._finalizar_partida("empate")
                await interaction.response.edit_message(view=self)
                return

            # Cambiar turno
            self.turno = 2 if self.turno == 1 else 1
            jugador_actual = self.jugador1 if self.turno == 1 else self.jugador2
            simbolo = self._obtener_simbolo(self.turno)
            
            self._actualizar_botones()
            embed = Embed(
                title="⭕ TRES EN RAYA ❌",
                description=f"¡Es turno de **{simbolo} {jugador_actual.mention}**!",
                color=0x9B59B6
            )
            
            try:
                await interaction.response.edit_message(embed=embed, view=self)
            except discord.NotFound:
                self.juego_activo = False
                self.stop()
            
        return callback

    async def on_timeout(self):
        """Se ejecuta automáticamente cuando pasan los 300s"""
        if self.juego_activo:
            await self._finalizar_partida("tiempo")

@bot.command(name="rallado")
async def rallado_cmd(ctx, oponente: discord.Member = None):
    # Validaciones
    if oponente is None:
        return await ctx.send("❌ Uso: `!rallado @usuario`")
    if oponente == ctx.author:
        return await ctx.send("❌ No puedes jugar contra ti mismo.")
    if oponente.bot:
        return await ctx.send("❌ No puedes jugar contra un bot.")
    
    # Crear vista personalizada
    vista = TableroView(jugador1=ctx.author, jugador2=oponente)
    
    embed_inicio = Embed(
        title="⭕ TRES EN RAYA ❌",
        description=f"""
🎮 **Partida entre:**
❌ {ctx.author.mention}
⭕ {oponente.mention}

👉 **Empieza {ctx.author.mention} (❌)** ¡Es tu turno!
        """,
        color=0x9B59B6
    )
    
    mensaje = await ctx.send(embed=embed_inicio, view=vista)
    vista.mensaje_original = mensaje

# ==================================================
# 🚀 INICIAR BOT
# ==================================================
print("🔄 Iniciando bot...")
bot.run(TOKEN)
