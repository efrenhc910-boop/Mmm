import json
import asyncio
import os
import traceback

# Ruta ABSOLUTA (sin importar desde dónde ejecute el host)
ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos.json")

_lock = None
_datos = {}

def _get_lock():
    """Lock lazy: se crea la primera vez que se necesita (seguro en cualquier entorno)."""
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock

def _cargar():
    global _datos
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            _datos = json.load(f)
        print(f"[guardado] ✅ Datos cargados: {len(_datos)} entradas")
    except FileNotFoundError:
        _datos = {}
        print("[guardado] ℹ️ No existe datos.json, se creará automáticamente")
    except Exception as e:
        print(f"[guardado] ❌ ERROR al cargar datos.json: {e}")
        traceback.print_exc()
        _datos = {}

_cargar()

def _guardar_ahora():
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(_datos, f, ensure_ascii=False, indent=2)

async def get_balance(user_id: str) -> int:
    async with _get_lock():
        return int(_datos.get(f"saldo:{user_id}", 0))

async def set_balance(user_id: str, valor: int):
    async with _get_lock():
        _datos[f"saldo:{user_id}"] = int(valor)
        _guardar_ahora()

async def get_var(nombre: str, user_id: str, default=0):
    async with _get_lock():
        return _datos.get(f"{nombre}:{user_id}", default)

async def set_var(nombre: str, user_id: str, valor):
    async with _get_lock():
        _datos[f"{nombre}:{user_id}"] = valor
        _guardar_ahora()
