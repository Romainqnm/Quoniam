import flet as ft
import threading
import main as moteur_audio
import config

def main(page: ft.Page):
    # CONFIGURATION
    page.title = "QUONIAM v2.3 Premium"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    # On réduit la hauteur par défaut pour que ça rentre partout
    page.window_height = 800 
    page.padding = 0 
    
    gradient_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
        colors=["#0f0c29", "#302b63", "#24243e"]
    )

    # --- HEADER ---
    header = ft.Column([
        ft.Text(
            "Q U O N I A M", 
            size=30, 
            weight=ft.FontWeight.BOLD,
            color="white",
            text_align=ft.TextAlign.CENTER,
        ),
        ft.Container(
            content=ft.Text(
                "L I V I N G   A T M O S P H E R E", 
                size=10, 
                weight=ft.FontWeight.W_300,
                color="#88ffffff"
            ),
            margin=ft.margin.only(top=5)
        ),
        ft.Container(
            width=40, height=2, bgcolor="#44ffffff",
            margin=ft.margin.only(top=15, bottom=5), # Marges réduites
            border_radius=10
        )
    ], horizontal_alignment="center", spacing=0)

    # --- UI ELEMENTS ---
    txt_icone = ft.Text("💧", size=50) # Un peu plus petit (60 -> 50)
    lbl_vitesse = ft.Text("50%", size=12, weight="bold")
    lbl_intensite = ft.Text("30%", size=12, weight="bold")
    lbl_gravite = ft.Text("Octave 0", size=12, weight="bold")
    lbl_chaos = ft.Text("20%", size=12, weight="bold")
    
    btn_play_content = ft.Text("⏸  PAUSE", color="white", weight="bold")
    btn_play_container = ft.Container(
        content=btn_play_content, padding=15, border_radius=30, 
        alignment=ft.Alignment(0, 0), width=200,
        gradient=ft.LinearGradient(colors=["#ff416c", "#ff4b2b"]),
        ink=True 
    )

    # --- LOGIQUE ---
    def update_ui():
        lbl_vitesse.value = f"{int(config.ETAT['vitesse'])}%"
        lbl_intensite.value = f"{int(config.ETAT['intensite'])}%"
        lbl_gravite.value = f"Octave {int(config.ETAT['gravite']):+d}"
        lbl_chaos.value = f"{int(config.ETAT['chaos'])}%"
        
        p = config.ETAT["preset"]
        if p == "eau": txt_icone.value = "💧"
        elif p == "air": txt_icone.value = "☁️"
        elif p == "feu": txt_icone.value = "🔥"
        elif p == "terre": txt_icone.value = "🌱"
        elif p == "espace": txt_icone.value = "🌌"
        
        if config.ETAT["actif"]:
            btn_play_content.text = "⏸  PAUSE"
            btn_play_container.gradient = ft.LinearGradient(colors=["#ff416c", "#ff4b2b"])
        else:
            btn_play_content.text = "▶  REPRENDRE"
            btn_play_container.gradient = ft.LinearGradient(colors=["#56ab2f", "#a8e063"])
            
        switch_auto.value = config.ETAT["mode_auto"]
        page.update()

    def changer_valeur(e, cle):
        config.ETAT[cle] = e.control.value
        update_ui()

    def changer_preset(e):
        config.ETAT["mode_auto"] = False
        config.ETAT["preset"] = e.control.data
        update_ui()
        
    def toggle_auto(e):
        config.ETAT["mode_auto"] = e.control.value
        update_ui()

    def toggle_play(e):
        config.ETAT["actif"] = not config.ETAT["actif"]
        update_ui()
    
    btn_play_container.on_click = toggle_play

    # --- ASSEMBLAGE ---
    def btn_preset(icon, nom, code):
        return ft.Container(
            content=ft.Column([ft.Text(icon, size=24), ft.Text(nom, size=10, color="white")], alignment="center"),
            data=code, on_click=changer_preset,
            width=65, height=65, border_radius=15, # Un peu plus compact (70 -> 65)
            bgcolor="#1affffff", ink=True, border=ft.border.all(1, "#1affffff")
        )

    presets_row1 = ft.Row([
        btn_preset("🌱", "Terre", "terre"),
        btn_preset("💧", "Eau", "eau"),
        btn_preset("🔥", "Feu", "feu"),
    ], alignment="center", spacing=10)
    
    presets_row2 = ft.Row([
        btn_preset("☁️", "Air", "air"),
        btn_preset("🌌", "Espace", "espace"),
    ], alignment="center", spacing=10)

    def slider_row(label, key, min_v, max_v, div, emoji, value_display):
        return ft.Column([
            ft.Row([
                ft.Container(content=ft.Text(emoji, size=16), width=30, alignment=ft.Alignment(0, 0)),
                ft.Text(label, size=12, color="white"),
                ft.Container(expand=True),
                value_display
            ]),
            ft.Slider(
                min=min_v, max=max_v, divisions=div, value=config.ETAT[key],
                on_change=lambda e: changer_valeur(e, key),
                active_color="white", inactive_color="#33ffffff", thumb_color="white"
            )
        ], spacing=0)

    switch_auto = ft.Switch(value=False, on_change=toggle_auto, active_color="#00E5FF")

    controls_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("⏰", size=16), 
                ft.Text("Adaptation Circadienne (Auto)", size=12, weight="bold"),
                ft.Container(expand=True),
                switch_auto 
            ], alignment="center"),
            ft.Divider(color="#33ffffff"),
            slider_row("Vitesse", "vitesse", 0, 100, 100, "🚀", lbl_vitesse),
            slider_row("Intensité", "intensite", 0, 100, 100, "🌊", lbl_intensite),
            slider_row("Gravité", "gravite", -2, 2, 4, "⚓", lbl_gravite),
            slider_row("Chaos", "chaos", 0, 100, 100, "🎲", lbl_chaos),
        ], spacing=10), # Espacement réduit dans le panneau (15 -> 10)
        padding=15 # Padding réduit (20 -> 15)
    )

    main_layout = ft.Container(
        gradient=gradient_bg, expand=True, padding=20, # Padding global réduit (30 -> 20)
        content=ft.Column([
            # LE FIX SCROLL : On active le scroll caché
            # Si l'écran est petit, tu pourras descendre avec la souris
            ft.Container(height=20), 
            header,
            ft.Container(height=20),
            txt_icone,
            ft.Container(height=20),
            presets_row1,
            ft.Container(height=5),
            presets_row2,
            ft.Container(height=20),
            controls_panel,
            ft.Container(expand=True),
            btn_play_container,
            ft.Container(height=20),
        ], horizontal_alignment="center", scroll=ft.ScrollMode.HIDDEN) 
    )

    page.add(main_layout)
    update_ui()

if __name__ == "__main__":
    print("Lancement v2.3 Premium Compact...")
    thread_son = threading.Thread(target=moteur_audio.main, daemon=True)
    thread_son.start()
    ft.app(target=main)