import flet as ft
import threading
import time
import main as moteur_audio
import config

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
    txt_icone = ft.Text("💧", size=50)
    
    # L'AURA (GLOW)
    glow_shadow = ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        color=ft.Colors.with_opacity(0.5, "cyan"),
        offset=ft.Offset(0, 0),
        blur_style="outer" 
    )

    # CONTENEUR ANIMÉ
    container_icone = ft.Container(
        content=txt_icone,
        alignment=ft.Alignment(0, 0), 
        scale=1.0, 
        rotate=ft.Rotate(0, alignment=ft.Alignment(0,0)), 
        shadow=glow_shadow,
        # LE FIX EST ICI : On arrondit les angles au max pour faire un cercle
        # Un cercle qui tourne sur lui-même ne montre pas de coins !
        border_radius=100, 
        width=100, # On fixe une taille pour être sûr que c'est un rond parfait
        height=100,
        
        animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        animate_rotation=ft.Animation(1000, ft.AnimationCurve.LINEAR),
    )

    lbl_vitesse = ft.Text("50%", size=12)
    lbl_intensite = ft.Text("30%", size=12)
    lbl_gravite = ft.Text("0", size=12)
    lbl_chaos = ft.Text("20%", size=12)
    switch_auto = ft.Switch(value=False, active_color="#00E5FF")
    
    btn_play_content = ft.Text("▶  LECTURE", color="white", weight="bold")
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

    # --- HEADER ---
    def creer_header():
        return ft.Column([
            ft.Text("Q U O N I A M", size=30, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Text("F L U I D   D Y N A M I C S", size=10, weight=ft.FontWeight.W_300, color="#88ffffff"),
                margin=ft.margin.only(top=5)
            ),
            ft.Container(width=40, height=2, bgcolor="#44ffffff", margin=ft.margin.only(top=15, bottom=5), border_radius=10)
        ], horizontal_alignment="center", spacing=0)

    # --- BOUCLE D'ANIMATION ---
    def animer_coeur():
        angle = 0
        while True:
            if config.ETAT["collection"] is not None and config.ETAT["actif"]:
                
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

                # PHASE 1 : SYSTOLE
                container_icone.scale = scale_max
                
                presets_tournants = ["espace", "vide", "cyber", "indus", "zen"]
                if preset in presets_tournants:
                    angle += 0.5 
                    container_icone.rotate.angle = angle
                else:
                    container_icone.rotate.angle = 0
                
                # Aura
                container_icone.shadow.spread_radius = 5 + (intensite/10)
                container_icone.shadow.color = ft.Colors.with_opacity(0.8, "white")
                
                container_icone.update()
                time.sleep(tempo)
                
                # PHASE 2 : DIASTOLE
                container_icone.scale = 1.0
                
                if preset in presets_tournants:
                    angle += 0.5
                    container_icone.rotate.angle = angle
                
                container_icone.shadow.spread_radius = 0
                container_icone.shadow.color = ft.Colors.with_opacity(0.3, "white")
                
                container_icone.update()
                time.sleep(tempo)
                
            else:
                time.sleep(1.0)

    thread_anim = threading.Thread(target=animer_coeur, daemon=True)
    thread_anim.start()

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
            txt_icone.value = mapping_icones[p]
        
        if config.ETAT["actif"]:
            btn_play_content.text = "⏸  PAUSE"
            btn_play_container.gradient = ft.LinearGradient(colors=["#ff416c", "#ff4b2b"])
        else:
            btn_play_content.text = "▶  LECTURE"
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
        def carte(emoji, titre, sous_titre, code):
            return ft.Container(
                content=ft.Column([
                    ft.Text(emoji, size=35),
                    ft.Text(titre, weight="bold", size=12),
                    ft.Text(sous_titre, size=9, color="#88ffffff")
                ], alignment="center"),
                width=100, height=140, bgcolor="#1affffff", border_radius=20,
                ink=True, on_click=lambda _: charger_interface_controle(code),
                border=ft.Border.all(1, "#33ffffff")
            )
        
        return ft.Column([
            ft.Container(height=40),
            creer_header(),
            ft.Container(height=60),
            ft.Text("CHOISISSEZ VOTRE MONDE", size=12, color="#88ffffff"),
            ft.Container(height=20),
            ft.Row([
                carte("🌱", "ÉLÉMENTS", "Nature", "elements"),
                carte("❄️", "SAISONS", "Voyage", "saisons"),
                carte("🎋", "ATMOS", "Exotique", "atmos")
            ], alignment="center", spacing=15),
            ft.Container(expand=True),
            ft.Text("v4.9.1 Final Polish", size=10, color="#44ffffff")
        ], horizontal_alignment="center")

    def creer_contenu_controle():
        bouton_retour = ft.Container(
            content=ft.Text("⬅️  RETOUR", size=12, weight="bold", color="white"),
            padding=10, border_radius=10, ink=True, on_click=retour_accueil
        )

        header_nav = ft.Row([
            bouton_retour,
            ft.Container(expand=True),
            ft.Text("CONTROLLER", size=12, weight="bold"),
            ft.Container(expand=True),
            ft.Container(width=70) 
        ])

        return ft.Column([
            ft.Container(height=10),
            header_nav,
            ft.Container(height=10),
            container_icone, 
            ft.Container(height=20),
            container_presets, 
            ft.Container(height=20),
            creer_panneau_sliders(),
            ft.Container(expand=True),
            btn_play_container,
            ft.Container(height=20),
        ], horizontal_alignment="center", scroll=ft.ScrollMode.HIDDEN)

    # --- HELPERS BOUTONS ---
    
    def btn_preset(icon, nom, code):
        return ft.Container(
            content=ft.Column([ft.Text(icon, size=20), ft.Text(nom, size=9, color="white")], alignment="center"),
            data=code, on_click=changer_preset,
            width=60, height=60, border_radius=15, bgcolor="#1affffff", ink=True, 
            border=ft.Border.all(1, "#1affffff")
        )

    def creer_boutons_elements():
        return ft.Column([
            ft.Row([btn_preset("🌱", "Terre", "terre"), btn_preset("💧", "Eau", "eau"), btn_preset("🔥", "Feu", "feu")], alignment="center"),
            ft.Container(height=5),
            ft.Row([btn_preset("☁️", "Air", "air"), btn_preset("🌌", "Espace", "espace")], alignment="center")
        ])

    def creer_boutons_saisons():
        return ft.Column([
            ft.Row([btn_preset("❄️", "Hiver", "hiver"), btn_preset("🌸", "Print.", "printemps"), btn_preset("☀️", "Été", "ete")], alignment="center"),
            ft.Container(height=5),
            ft.Row([btn_preset("🍂", "Automne", "automne"), btn_preset("🌌", "Vide", "vide")], alignment="center")
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
                ft.Row([ft.Text("⏰", size=16), ft.Text("Mode Auto", size=12, weight="bold"), ft.Container(expand=True), switch_auto], alignment="center"),
                ft.Divider(color="#33ffffff"),
                slider_row("Vitesse", "vitesse", "🚀", lbl_vitesse),
                slider_row("Intensité", "intensite", "🌊", lbl_intensite),
                slider_row("Gravité", "gravite", "⚓", lbl_gravite),
                slider_row("Chaos", "chaos", "🎲", lbl_chaos),
            ], spacing=10),
            padding=15
        )

    # Lancement
    main_layout.content = creer_contenu_accueil()
    page.add(main_layout)

if __name__ == "__main__":
    print("Lancement v4.9.1 Final Polish...")
    thread_son = threading.Thread(target=moteur_audio.main, daemon=True)
    thread_son.start()
    ft.app(target=main)