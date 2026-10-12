import random
import asyncio
import traceback
from discord import Embed
import guardado

# Lock por usuario: evita que la MISMA persona apueste dos veces al mismo tiempo
_locks_usuarios = {}

def _lock_usuario(user_id: str) -> asyncio.Lock:
    if user_id not in _locks_usuarios:
        _locks_usuarios[user_id] = asyncio.Lock()
    return _locks_usuarios[user_id]

async def ejecutar(ctx, cantidad=None):
    """Punto de entrada principal. Captura TODA excepción para que no sea silenciosa."""
    user_id = str(ctx.author.id)
    lock = _lock_usuario(user_id)

    if lock.locked():
        return await ctx.send("⏳ Ya tienes una apuesta en curso. Espera a que termine.")

    async with lock:
        try:
            await _ejecutar_real(ctx, cantidad, user_id)
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO en apuesta de {ctx.author} ({user_id}): {e}")
            traceback.print_exc()
            print("──────────────────────────────")
            try:
                await ctx.send("⚠️ Ocurrió un error interno al procesar tu apuesta.")
            except Exception:
                pass

async def _ejecutar_real(ctx, cantidad, user_id):
    # ─── Leer saldo ───
    saldo_actual = await guardado.get_balance(user_id)
    print(f"[apuesta] saldo={saldo_actual}, cantidad_recibida={cantidad!r}")

    # ─── Límite global de 100M ───
    if saldo_actual >= 100_000_000:
        return await ctx.send("❌ No puedes apostar — Superaste el límite de 100 millones.")

    # ─── Validar entrada ───
    if cantidad is None:
        return await ctx.send("❌ Usa: `.apuesta 10000` o `.apuesta all`")

    cantidad_str = str(cantidad).strip().lower()

    if cantidad_str == "all":
        apuesta = saldo_actual
    else:
        try:
            apuesta = int(cantidad_str)
        except (ValueError, TypeError):
            return await ctx.send("❌ Debes introducir una cantidad válida o escribir `all`.")

    if apuesta <= 0:
        return await ctx.send("❌ La apuesta debe ser mayor a 0.")

    # ─── Límites dinámicos (tabla oficial, simplificada) ───
    if saldo_actual >= 500_000:
        limite = 1_000_000
    elif saldo_actual >= 300_000:
        limite = 500_000
    elif saldo_actual >= 100_000:
        limite = 300_000
    else:
        limite = 30_000

    apuesta = min(apuesta, limite)

    # ─── Validaciones finales ───
    if apuesta < 11:
        return await ctx.send("❌ La apuesta mínima es de `11` monedas de oro.")
    if saldo_actual < apuesta:
        return await ctx.send("❌ No tienes suficientes monedas de oro.")

    # ─── Descontar apuesta (UNA sola vez) ───
    await guardado.set_balance(user_id, saldo_actual - apuesta)

    # ─── Sistema de piedad ───
    piedad = await guardado.get_var("Piedad", user_id) or 0
    # piedad=0 → umbral=500 → 50% victoria | piedad=10 → umbral=400 → 60% | etc.
    umbral = max(1, 500 - (piedad * 10))

    # ─── Lanzar moneda (1-1000) ───
    roll = random.randint(1, 1000)
    print(f"[apuesta] roll={roll}, umbral={umbral}, piedad={piedad}, apuesta={apuesta}")

    # ─── Embed de animación ───
    embed = Embed(title="🎲 COINFLIP", color=0xFFD700)
    embed.set_image(url="https://media.tenor.com/tDFO-BkP8P4AAAAj/moneda-girandox12-coin.gif")
    mensaje = await ctx.send(embed=embed)

    # ⏳ Esperar a que se vea la animación
    await asyncio.sleep(2.3)

    # ═══════════════════════════════════════
    # 💎 X5 — Premio máximo (roll == 1000 → 0.1%)
    # ═══════════════════════════════════════
    if roll == 1000:
        victorias = (await guardado.get_var("Victorias", user_id) or 0) + 1
        multiplicador = 2 + ((victorias - 1) * 0.5)
        await guardado.set_var("Victorias", user_id, victorias)
        await guardado.set_var("Derrotas", user_id, 0)
        await guardado.set_var("Piedad", user_id, 0)
        await guardado.set_var("Multiplicador", user_id, multiplicador)

        premio = int(apuesta * 5 * multiplicador)
        nuevo_saldo = (saldo_actual - apuesta) + premio
        await guardado.set_balance(user_id, nuevo_saldo)

        embed = Embed(title="💎 ***X5 — EXTREMADAMENTE RARO***", color=0xC0C0FF)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
💎 **MULTIPLICADOR**
➥ `x{5 * multiplicador:.1f}`
🪙 **PREMIO**
➥ `+{premio:,}` monedas de oro
━━━━━━━━━━━━━━━━━━━━
💰 **SALDO ACTUAL**
➥ `{nuevo_saldo:,}` monedas de oro"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)

    # ═══════════════════════════════════════
    # 🏆 Victoria normal
    # ═══════════════════════════════════════
    elif roll > umbral:
        victorias = (await guardado.get_var("Victorias", user_id) or 0) + 1
        multiplicador = 2 + ((victorias - 1) * 0.5)
        await guardado.set_var("Victorias", user_id, victorias)
        await guardado.set_var("Derrotas", user_id, 0)
        await guardado.set_var("Piedad", user_id, 0)
        await guardado.set_var("Multiplicador", user_id, multiplicador)

        premio = int(apuesta * multiplicador)
        nuevo_saldo = (saldo_actual - apuesta) + premio
        await guardado.set_balance(user_id, nuevo_saldo)

        embed = Embed(title="🏆 Victoria", color=0x00FF66)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **APUESTA** ➥ `{apuesta:,}`
💰 **PREMIO** ➥ `+{premio:,}`
📈 **MULTIPLICADOR** ➥ `x{multiplicador:.1f}`
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)

    # ═══════════════════════════════════════
    # ❌ Derrota
    # ═══════════════════════════════════════
    else:
        derrotas = (await guardado.get_var("Derrotas", user_id) or 0) + 1
        piedad_nueva = piedad
        if derrotas >= 2:
            piedad_nueva += 10

        await guardado.set_var("Derrotas", user_id, derrotas)
        await guardado.set_var("Victorias", user_id, 0)
        await guardado.set_var("Piedad", user_id, piedad_nueva)
        await guardado.set_var("Multiplicador", user_id, 2)

        nuevo_saldo = saldo_actual - apuesta

        embed = Embed(title="❌ ***DERROTA***", color=0xFF0000)
        embed.description = f"""━━━━━━━━━━━━━━━━━━━━
🪙 **PERDISTE** ➥ `-{apuesta:,}`
💰 **SALDO ACTUAL** ➥ `{nuevo_saldo:,}`
🍀 **PIEDAD** ➥ `{piedad_nueva}%` extra
━━━━━━━━━━━━━━━━━━━━"""
        embed.set_footer(text=ctx.author.display_name)
        await mensaje.edit(embed=embed)
