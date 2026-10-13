# ═══════════════════════════════════════════
# ⭕ !rallado — TRES EN RAYA ❌ (CORREGIDO)
# ═══════════════════════════════════════════
@bot.command(name="rallado")
async def rallado_cmd(ctx, oponente: discord.Member = None):
    jugador1 = ctx.author  # ❌ Empieza quien escribe el comando
    jugador2 = oponente

    # Validaciones
    if not jugador2:
        return await ctx.send("❌ Uso: `!rallado @usuario`")
    if jugador2 == jugador1:
        return await ctx.send("❌ No puedes jugar contra ti mismo.")
    if jugador2.bot:
        return await ctx.send("❌ No puedes jugar contra un bot.")

    # Estado del juego
    tablero = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 0=vacío, 1=❌, 2=⭕
    turno = 1
    juego_activo = True
    mensaje_juego = None

    # Vista con botones persistentes
    class TableroView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)
            self.actualizar_botones()

        def actualizar_botones(self):
            self.clear_items()
            for i in range(9):
                if tablero[i] == 1:
                    etiqueta = "❌"
                    desactivado = True
                elif tablero[i] == 2:
                    etiqueta = "⭕"
                    desactivado = True
                else:
                    etiqueta = "⬜"
                    desactivado = False
                
                btn = discord.ui.Button(
                    label=etiqueta,
                    custom_id=f"casilla_{i}",
                    disabled=desactivado,
                    row=i // 3
                )
                btn.callback = self.crear_callback(i)
                self.add_item(btn)

        def crear_callback(self, indice):
            async def callback(interaction: discord.Interaction):
                nonlocal turno, juego_activo, mensaje_juego

                if not juego_activo:
                    await interaction.response.defer()
                    return

                # Verificar turno y jugador
                if turno == 1 and interaction.user != jugador1:
                    await interaction.response.send_message("❌ No es tu turno.", ephemeral=True)
                    return
                if turno == 2 and interaction.user != jugador2:
                    await interaction.response.send_message("❌ No es tu turno.", ephemeral=True)
                    return

                # Casilla ocupada
                if tablero[indice] != 0:
                    await interaction.response.defer()
                    return

                # Colocar ficha
                tablero[indice] = turno

                # Verificar ganador
                combinaciones = [
                    [0,1,2], [3,4,5], [6,7,8],
                    [0,3,6], [1,4,7], [2,5,8],
                    [0,4,8], [2,4,6]
                ]
                ganador = None
                for a, b, c in combinaciones:
                    if tablero[a] == tablero[b] == tablero[c] != 0:
                        ganador = tablero[a]
                        break

                if ganador:
                    juego_activo = False
                    vista_final = TableroView()
                    vista_final.disable_all_items()
                    ganador_user = jugador1 if ganador == 1 else jugador2
                    simbolo = "❌" if ganador == 1 else "⭕"
                    embed = Embed(
                        title=f"🎉 ¡{simbolo} {ganador_user.display_name} GANA!",
                        color=0x00FF66
                    )
                    await interaction.response.edit_message(embed=embed, view=vista_final)
                    return

                # Verificar empate
                if all(c != 0 for c in tablero):
                    juego_activo = False
                    vista_final = TableroView()
                    vista_final.disable_all_items()
                    embed = Embed(
                        title="🤝 ¡EMPATE!",
                        color=0xFFD700
                    )
                    await interaction.response.edit_message(embed=embed, view=vista_final)
                    return

                # Cambiar turno
                turno = 2 if turno == 1 else 1
                sig_jugador = jugador1 if turno == 1 else jugador2
                sig_simbolo = "❌" if turno == 1 else "⭕"
                vista_nueva = TableroView()
                embed = Embed(
                    title="⭕ TRES EN RAYA ❌",
                    description=f"¡Es turno de **{sig_simbolo} {sig_jugador.mention}**!",
                    color=0x9B59B6
                )
                await interaction.response.edit_message(embed=embed, view=vista_nueva)

            return callback

    # Mensaje inicial
    vista_inicio = TableroView()
    embed_inicio = Embed(
        title="⭕ TRES EN RAYA ❌",
        description=f"""
🎮 **Partida entre:**
❌ {jugador1.mention}
⭕ {jugador2.mention}

👉 **Empieza {jugador1.mention} (❌)** ¡Es tu turno!
        """,
        color=0x9B59B6
    )
    mensaje_juego = await ctx.send(embed=embed_inicio, view=vista_inicio)
