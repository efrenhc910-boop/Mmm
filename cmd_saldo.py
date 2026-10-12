import guardado

async def ejecutar(ctx):
    saldo = await guardado.get_balance(str(ctx.author.id))
    await ctx.send(f"💰 Tu saldo es: **{saldo:,}** monedas de oro")
