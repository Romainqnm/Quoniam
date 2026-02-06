import flet as ft
import threading
import main as moteur_audio
import config

def main(page: ft.Page):
    # --- CONFIGURATION FENÊTRE ---
    page.title = "QUONIAM Clean Glass v1.7"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 850
    page.padding = 0 
    
    # Fond Dégradé
    gradient_bg = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=["#0f0c29", "#302b63", "#24243e"]
    )

    # --- STYLE "FAKE GLASS" ---
    def glass_container(content, padding=20):
        return ft.Container(
            content=content,
            padding=padding,
            border_radius=20,
            bgcolor="#15ffffff",
            border=ft.border.all(1, "#33ffffff"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color="#44000000",
            )
        )

    # --- LOGIQUE ---
    def update_ui():
        lbl_vitesse.value = f"{int(config.ETAT['vitesse'])}%"
        lbl_intensite.value = f"{int(config.ETAT['intensite'])}%"
        lbl_gravite.value = f"Octave {int(config.ETAT['gravite']):+d}"
        lbl_chaos.value = f"{int(config.ETAT['chaos'])}%"
        
        if config.ETAT["actif"]:
            btn_play_content.text = "⏸  PAUSE"
            btn_play_container.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=["#ff416c", "#ff4b2b"]
            )
        else:
            btn_play_content.text = "▶  REPRENDRE"
            btn_play_container.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=["#56ab2f", "#a8e063"]
            )
        page.update()

    def changer_valeur(e, cle):
        config.ETAT[cle] = e.control.value
        update_ui()

    def changer_preset(e):
        code = e.control.data
        config.ETAT["preset"] = code
        if code == "eau": txt_icone.value = "💧"
        elif code == "air": txt_icone.value = "☁️"
        elif code == "feu": txt_icone.value = "🔥"
        update_ui()

    def toggle_play(e):
        config.ETAT["actif"] = not config.ETAT["actif"]
        update_ui()

    # --- COMPOSANTS UI ---
    
    header = ft.Column([
        ft.Text("QUONIAM", size=35, font_family="Roboto Mono", weight="w200", color="white"),
        ft.Text("Ambient Engine", size=12, color="#99ffffff"),
    ], horizontal_alignment="center")

    txt_icone = ft.Text("💧", size=60)

    # BOUTONS PRESETS
    def btn_preset(icon, nom, code):
        return ft.Container(
            content=ft.Column([ft.Text(icon, size=24), ft.Text(nom, size=10, color="white")], alignment="center"),
            data=code, on_click=changer_preset,
            width=80, height=80, border_radius=15,
            bgcolor="#1affffff",
            ink=True,
            border=ft.border.all(1, "#1affffff")
        )

    presets = ft.Row([
        btn_preset("💧", "Eau", "eau"),
        btn_preset("☁️", "Air", "air"),
        btn_preset("🔥", "Feu", "feu")
    ], alignment="center", spacing=15)

    # SLIDERS
    def slider_row(label, key, min_v, max_v, div, emoji, value_display):
        return ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(emoji, size=16),
                    width=30, 
                    # CORRECTIF 1 : Alignment(0,0) au lieu de .center
                    alignment=ft.Alignment(0, 0)
                ),
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

    lbl_vitesse = ft.Text("50%", size=12, weight="bold")
    lbl_intensite = ft.Text("30%", size=12, weight="bold")
    lbl_gravite = ft.Text("Octave 0", size=12, weight="bold")
    lbl_chaos = ft.Text("20%", size=12, weight="bold")

    controls_panel = glass_container(
        ft.Column([
            slider_row("Vitesse", "vitesse", 0, 100, 100, "🚀", lbl_vitesse),
            slider_row("Intensité", "intensite", 0, 100, 100, "🌊", lbl_intensite),
            ft.Divider(color="#1affffff"),
            slider_row("Gravité", "gravite", -2, 2, 4, "⚓", lbl_gravite),
            slider_row("Chaos", "chaos", 0, 100, 100, "🎲", lbl_chaos),
        ], spacing=20)
    )

    btn_play_content = ft.Text("⏸  PAUSE", color="white", weight="bold")
    
    btn_play_container = ft.Container(
        content=btn_play_content,
        on_click=toggle_play,
        padding=15,
        border_radius=30,
        # CORRECTIF 2 : Alignment(0,0) au lieu de .center
        alignment=ft.Alignment(0, 0),
        width=200,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
            colors=["#ff416c", "#ff4b2b"]
        ),
        shadow=ft.BoxShadow(blur_radius=20, color="#66ff4b2b"),
        ink=True 
    )

    main_layout = ft.Container(
        gradient=gradient_bg,
        expand=True,
        padding=30,
        content=ft.Column([
            ft.Container(height=40),
            header,
            ft.Container(height=30),
            txt_icone,
            ft.Container(height=30),
            presets,
            ft.Container(height=30),
            controls_panel,
            ft.Container(expand=True),
            btn_play_container,
            ft.Container(height=40),
        ], horizontal_alignment="center")
    )

    page.add(main_layout)
    update_ui()

# --- LANCEMENT ---
if __name__ == "__main__":
    print("Lancement de l'interface Clean Glass (v1.7)...")
    thread_son = threading.Thread(target=moteur_audio.main, daemon=True)
    thread_son.start()
    ft.app(target=main)