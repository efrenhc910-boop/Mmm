import json
import asyncio

ARCHIVO_DATOS = "datos.json"
_lock = asyncio.Lock()
_datos = {}

def _cargar():
    global _datos
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            _datos = json.load(f)
    except FileNotFoundError:
        _datos = {}

_cargar()

async def get_balance(user_id: str) -> int:
    async with _lock:
        return _datos.get(f"saldo:{user_id}", 0)

async def set_balance(user_id: str, valor: int):
    async with _lock:
        _datos[f"saldo:{user_id}"] = valor
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(_datos, f, ensure_ascii=False, indent=2)

async def get_var(nombre: str, user_id: str, default=0):
    async with _lock:
        return _datos.get(f"{nombre}:{user_id}", default)

async def set_var(nombre: str, user_id: str, valor):
    async with _lock:
        _datos[f"{nombre}:{user_id}"] = valor
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(_datos, f, ensure_ascii=False, indent=2)
