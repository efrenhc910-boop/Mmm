async def ejecutar(ctx):
    await ctx.send(f"🏓 Pong! Latencia: {round(ctx.bot.latency * 1000)}ms")
