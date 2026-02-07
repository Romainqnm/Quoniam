import flet as ft
import threading
import time
import main as moteur_audio
import config
import random

def main(page: ft.Page):
    # --- CONFIGURATION ---
    page.title = "QUONIAM v4.9.1 Final Polish"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.padding = 0 
    
    # PALETTES DE COULEURS
    COLORS_ELEMENTS = ["#0f0c29", "#302b63", "#24243e"]
    COLORS_SAISONS  = ["#134E5E", "#71B280"] 
    COLORS_ATMOS    = ["#480048", "#C04848"] 

    # --- VARIABLES ---
    # CONTENEUR ANIMÉ
    icon_display = ft.Text("💧", size=50)
    
    # L'AURA (GLOW)
    glow_shadow = ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        color=ft.Colors.with_opacity(0.5, "cyan"),
        offset=ft.Offset(0, 0),
        blur_style="outer" 
    )

    container_icone = ft.Container(
        content=icon_display,
        alignment=ft.Alignment(0, 0), 
        scale=1.0, 
        rotate=ft.Rotate(0, alignment=ft.Alignment(0,0)), 
        shadow=glow_shadow,
        border_radius=100, 
        width=100,
        height=100,
        animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        animate_rotation=ft.Animation(1000, ft.AnimationCurve.LINEAR),
    )

    lbl_vitesse = ft.Text("50%", size=12)
    lbl_intensite = ft.Text("30%", size=12)
    lbl_gravite = ft.Text("0", size=12)
    lbl_chaos = ft.Text("20%", size=12)
    switch_auto = ft.Switch(value=False, active_color="#00E5FF")
    
    btn_play_content = ft.Text("▶  PLAY", color="white", weight="bold")
    btn_play_container = ft.Container(
        content=btn_play_content, padding=15, border_radius=30, 
        alignment=ft.Alignment(0, 0), width=200, ink=True,
        gradient=ft.LinearGradient(colors=["#56ab2f", "#a8e063"]) 
    )

    container_presets = ft.Container()
    
    # LE FOND LIQUIDE
    main_layout = ft.Container(
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=COLORS_ELEMENTS), 
        expand=True, 
        padding=20,
        animate=ft.Animation(2000, ft.AnimationCurve.EASE_OUT_CUBIC),
        content=None
    )

    # HELPER NEON
    def creer_separateur_neon(couleur="#00E5FF"):
        return ft.Container(
            width=120, height=2, bgcolor="#e0ffffff", border_radius=10,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=couleur, blur_style="outer"),
            margin=ft.Margin(left=0, top=15, right=0, bottom=15)
        )

    # --- HEADER ---
    def creer_header():
        return ft.Column([
            ft.Text("Q U O N I A M", size=30, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Text("F L U I D   D Y N A M I C S", size=10, weight=ft.FontWeight.W_300, color="#88ffffff"),
                margin=ft.Margin(left=0, top=5, right=0, bottom=0)
            ),
            creer_separateur_neon("#00E5FF")
        ], horizontal_alignment="center", spacing=0)

    # --- BOUCLE D'ANIMATION ---
    def animer_coeur():
        angle = 0
        while True:
            try:
                # Check if attached to page (safe check)
                if not container_icone.page:
                    time.sleep(0.5)
                    continue
                    
                if config.ETAT["actif"]:    
                    vitesse = config.ETAT["vitesse"]
                    intensite = config.ETAT["intensite"]
                    preset = config.ETAT["preset"]
                    
                    tempo_base = 2.0 - (vitesse / 55.0)
                    tempo = max(0.35, tempo_base)
                    
                    scale_max = 1.0 + (intensite / 250.0) 
                    
                    nervous_presets = ["feu", "cyber", "indus", "ete"]
                    if preset in nervous_presets:
                        container_icone.animate_scale = ft.Animation(int(tempo*500), ft.AnimationCurve.ELASTIC_OUT)
                    else:
                        container_icone.animate_scale = ft.Animation(int(tempo*900), ft.AnimationCurve.EASE_IN_OUT)

                    # ANIMATION LOGIC
                    # Pulse
                    if preset in ["eau", "terre", "printemps", "zen"]:
                         container_icone.scale = scale_max
                         container_icone.rotate.angle = 0
                    
                    # Spin
                    elif preset in ["espace", "vide", "cyber", "indus"]:
                        angle += 0.5 
                        container_icone.rotate.angle = angle
                        container_icone.scale = 1.0 # No pulse for spin

                    # Shake/Vibrate (Simulated by random small rotations/sales)
                    elif preset in ["feu", "ete"]:
                        container_icone.rotate.angle = random.uniform(-0.1, 0.1)
                        container_icone.scale = scale_max * random.uniform(0.95, 1.05)
                    
                    else: # Default hybrid
                        container_icone.scale = scale_max
                        container_icone.rotate.angle = 0

                    # Aura
                    container_icone.shadow.spread_radius = 5 + (intensite/10)
                    container_icone.shadow.color = ft.Colors.with_opacity(0.8, "white")
                    
                    container_icone.update()
                    time.sleep(tempo)
                    
                    # REST STATE
                    container_icone.scale = 1.0
                    if preset in ["espace", "vide", "cyber", "indus"]:
                         angle += 0.5
                         container_icone.rotate.angle = angle
                    else:
                         container_icone.rotate.angle = 0
                    
                    container_icone.shadow.spread_radius = 0
                    container_icone.shadow.color = ft.Colors.with_opacity(0.3, "white")
                    
                    container_icone.update()
                    time.sleep(tempo)
                else:
                    time.sleep(1.0)
            except Exception as e:
                # Silently ignore page attachment errors during startup/shutdown
                time.sleep(1.0)


    # --- LOGIQUE UI ---

    def update_ui():
        lbl_vitesse.value = f"{int(config.ETAT['vitesse'])}%"
        lbl_intensite.value = f"{int(config.ETAT['intensite'])}%"
        lbl_gravite.value = f"{int(config.ETAT['gravite'])}"
        lbl_chaos.value = f"{int(config.ETAT['chaos'])}%"
        
        p = config.ETAT["preset"]
        mapping_icones = {
            "eau": "💧", "air": "☁️", "feu": "🔥", "terre": "🌱", "espace": "🌌",
            "hiver": "❄️", "printemps": "🌸", "ete": "☀️", "automne": "🍂", "vide": "🌌",
            "zen": "🎋", "cyber": "🤖", "lofi": "☕", "jungle": "🦜", "indus": "🏭"
        }
        if p in mapping_icones:
            icon_display.value = mapping_icones[p]
        
        if config.ETAT["actif"]:
            btn_play_content.text = "⏸  PAUSE"
            btn_play_container.gradient = ft.LinearGradient(colors=["#ff416c", "#ff4b2b"])
        else:
            btn_play_content.text = "▶  PLAY"
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

    # --- NAVIGATION ---

    def charger_interface_controle(nom_collection):
        config.ETAT["collection"] = nom_collection
        
        if nom_collection == "elements":
            config.ETAT["preset"] = "eau"
            presets_controls = creer_boutons_elements()
            main_layout.gradient.colors = COLORS_ELEMENTS
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "cyan") 
            
        elif nom_collection == "saisons":
            config.ETAT["preset"] = "hiver"
            presets_controls = creer_boutons_saisons()
            main_layout.gradient.colors = COLORS_SAISONS
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "green") 
            
        else:
            config.ETAT["preset"] = "zen"
            presets_controls = creer_boutons_atmos()
            main_layout.gradient.colors = COLORS_ATMOS
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "purple") 
            
        container_presets.content = presets_controls
        
        main_layout.content = creer_contenu_controle()
        main_layout.update()
        
        config.ETAT["actif"] = True 
        update_ui()

    def retour_accueil(e):
        config.ETAT["collection"] = None
        config.ETAT["actif"] = False 
        
        main_layout.gradient.colors = COLORS_ELEMENTS
        main_layout.content = creer_contenu_accueil()
        main_layout.update()
        page.update()

    # --- VUES ---
    
    def creer_contenu_accueil():
        
        # Helper pour créer des icônes géométriques pures (CODE ONLY - NO ASSETS)
        def LiquidIcon(kind, color_start, color_end):
            if kind == "droplet": # Elements
                return ft.Container(
                    width=50, height=50,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1,1), end=ft.Alignment(1,-1),
                        colors=[color_start, color_end]
                    ),
                    border_radius=ft.border_radius.only(top_left=0, top_right=50, bottom_left=50, bottom_right=50),
                    rotate=ft.Rotate(0.785), # 45deg
                    shadow=ft.BoxShadow(blur_radius=10, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
                )
            elif kind == "leaf": # Seasons
                return ft.Container(
                    width=50, height=50,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0,1), end=ft.Alignment(0,-1),
                        colors=[color_start, color_end]
                    ),
                    border_radius=ft.border_radius.only(top_left=50, bottom_right=50, top_right=0, bottom_left=0),
                    shadow=ft.BoxShadow(blur_radius=10, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
                )
            elif kind == "orb": # Atmos
                return ft.Container(
                    width=50, height=50,
                    gradient=ft.RadialGradient(
                        colors=[color_end, color_start],
                    ),
                    border_radius=50,
                    border=ft.Border.all(2, ft.Colors.with_opacity(0.5, "white")),
                    shadow=ft.BoxShadow(blur_radius=15, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
                )
            return ft.Container()

        def carte(icon_kind, titre, sous_titre, code, color_theme, c1, c2):
            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=LiquidIcon(icon_kind, c1, c2),
                        padding=10,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(titre, weight="bold", size=16, color="white", text_align="center"),
                    ft.Text(sous_titre, size=11, color=ft.Colors.with_opacity(0.7, "white"), text_align="center")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=140, height=220,
                border_radius=30,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[
                        ft.Colors.with_opacity(0.15, "white"),
                        ft.Colors.with_opacity(0.05, "white"),
                    ],
                ),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
                shadow=ft.BoxShadow(
                    blur_radius=30,
                    spread_radius=-10,
                    color=color_theme,
                    offset=ft.Offset(0, 15)
                ),
                padding=20,
                margin=10,
                ink=True,
                on_click=lambda _: charger_interface_controle(code)
            )
        
        return ft.Column([
            ft.Container(height=40),
            creer_header(),
            ft.Container(height=40),
            ft.Text("CHOOSE YOUR WORLD", size=14, weight="bold", color=ft.Colors.with_opacity(0.5, "white")),
            ft.Container(height=20),
            ft.Row([
                carte("droplet", "ELEMENTS", "Nature & Raw Power", "elements", "cyan", "blue", "cyan"),
                carte("leaf", "SEASONS", "Time & Journey", "saisons", "green", "green", "yellow"),
                carte("orb", "ATMOS", "Mood & Abstraction", "atmos", "purple", "purple", "pink")
            ], alignment="center", wrap=True, spacing=10),
            ft.Container(expand=True),
            ft.Text("v5.0 Liquid Glass Edition", size=10, color="#44ffffff")
        ], horizontal_alignment="center")

    def creer_contenu_controle():
        bouton_retour = ft.Container(
            content=ft.Text("⬅️  BACK", size=12, weight="bold", color="white"),
            padding=10, border_radius=10, ink=True, on_click=retour_accueil
        )

        # TOP ACTION BAR
        def top_btn(text, code):
            is_active = config.ETAT["collection"] == code
            return ft.Container(
                content=ft.Text(text, size=10, weight="bold", color="white" if is_active else "#88ffffff"),
                padding=ft.Padding(left=10, top=5, right=10, bottom=5),
                border_radius=20,
                bgcolor="#33ffffff" if is_active else ft.Colors.TRANSPARENT,
                ink=True,
                on_click=lambda _: charger_interface_controle(code),
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            )

        top_bar = ft.Row([
            top_btn("ELEMENTS", "elements"),
            top_btn("SEASONS", "saisons"),
            top_btn("ATMOS", "atmos")
        ], alignment="center", spacing=5)

        header_nav = ft.Row([
            bouton_retour,
            ft.Container(expand=True),
            top_bar,
            ft.Container(expand=True),
            ft.Container(width=70) 
        ])

        return ft.Column([
            ft.Container(height=10),
            header_nav,
            ft.Container(height=10),
            container_icone, 
            creer_separateur_neon("#D500F9" if config.ETAT["collection"] == "atmos" else "#00E5FF"),
            
            # CONTRASTED CONTAINER FOR PRESETS
            ft.Container(
                content=container_presets,
                bgcolor=ft.Colors.with_opacity(0.1, "white"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
                border_radius=20,
                padding=20,
                blur=ft.Blur(10, 10),
                margin=ft.Margin(left=20, top=0, right=20, bottom=0)
            ),
            
            creer_separateur_neon("#D500F9" if config.ETAT["collection"] == "atmos" else "#00E5FF"),
            creer_panneau_sliders(),
            ft.Container(expand=True),
            btn_play_container,
            ft.Container(height=20),
        ], horizontal_alignment="center", scroll=ft.ScrollMode.HIDDEN)

    # --- HELPERS BOUTONS ---
    
    def btn_preset(icon, nom, code):
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=24),
                ft.Text(nom, size=10, color=ft.Colors.with_opacity(0.9, "white"), weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            data=code, 
            on_click=changer_preset,
            width=70, height=70,
            border_radius=15,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[
                    ft.Colors.with_opacity(0.1, "white"),
                    ft.Colors.with_opacity(0.02, "white"),
                ],
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, "white")),
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=-5,
                color=ft.Colors.with_opacity(0.5, "black"),
                offset=ft.Offset(0, 5)
            ),
            padding=5,
            ink=True
        )

    def creer_boutons_elements():
        return ft.Column([
            ft.Row([btn_preset("🌱", "Earth", "terre"), btn_preset("💧", "Water", "eau"), btn_preset("🔥", "Fire", "feu")], alignment="center"),
            ft.Container(height=5),
            ft.Row([btn_preset("☁️", "Air", "air"), btn_preset("🌌", "Space", "espace")], alignment="center")
        ])

    def creer_boutons_saisons():
        return ft.Column([
            ft.Row([btn_preset("❄️", "Winter", "hiver"), btn_preset("🌸", "Spring", "printemps"), btn_preset("☀️", "Summer", "ete")], alignment="center"),
            ft.Container(height=5),
            ft.Row([btn_preset("🍂", "Autumn", "automne"), btn_preset("🌌", "Void", "vide")], alignment="center")
        ])
    
    def creer_boutons_atmos():
        return ft.Column([
            ft.Row([btn_preset("🎋", "Zen", "zen"), btn_preset("🤖", "Cyber", "cyber"), btn_preset("☕", "LoFi", "lofi")], alignment="center"),
            ft.Container(height=5),
            ft.Row([btn_preset("🦜", "Jungle", "jungle"), btn_preset("🏭", "Indus", "indus")], alignment="center")
        ])

    def creer_panneau_sliders():
        switch_auto.on_change = toggle_auto
        def slider_row(label, key, emoji, display):
            return ft.Column([
                ft.Row([
                    ft.Container(content=ft.Text(emoji, size=16), width=30, alignment=ft.Alignment(0,0)),
                    ft.Text(label, size=12),
                    ft.Container(expand=True),
                    display
                ]),
                ft.Slider(min=0 if key!="gravite" else -2, max=100 if key!="gravite" else 2, 
                          divisions=100 if key!="gravite" else 4, 
                          value=config.ETAT[key], on_change=lambda e: changer_valeur(e, key),
                          active_color="white", inactive_color="#33ffffff", thumb_color="white")
            ], spacing=0)

        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Text("⏰", size=16), ft.Text("Auto Mode", size=12, weight="bold"), ft.Container(expand=True), switch_auto], alignment="center"),
                ft.Divider(color="#33ffffff"),
                slider_row("Speed", "vitesse", "🚀", lbl_vitesse),
                slider_row("Intensity", "intensite", "🌊", lbl_intensite),
                slider_row("Gravity", "gravite", "⚓", lbl_gravite),
                slider_row("Chaos", "chaos", "🎲", lbl_chaos),
            ], spacing=10),
            padding=15
        )

    # Lancement
    main_layout.content = creer_contenu_accueil()
    page.add(main_layout)
    
    # Threading correction: Start animation loop AFTER adding content to page
    thread_anim = threading.Thread(target=animer_coeur, daemon=True)
    thread_anim.start()

if __name__ == "__main__":
    print("Lancement v4.9.1 Final Polish...")
    thread_son = threading.Thread(target=moteur_audio.main, daemon=True)
    thread_son.start()
    ft.app(target=main)