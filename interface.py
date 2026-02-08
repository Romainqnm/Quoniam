import flet as ft
import threading
import time
import main as moteur_audio
import config
import random
import base64
import assets_library as assets

def main(page: ft.Page):
    # --- CONFIGURATION ---
    page.title = "QUONIAM v10.0"
    page.theme_mode = "dark"
    page.bgcolor = "#1a1a1a"
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True
    page.window_width = 450
    page.window_height = 800
    page.padding = 0 
    
    # PALETTES DE COULEURS
    COLORS_ACCUEIL  = ["#0f0c29", "#302b63", "#24243e"]
    COLORS_ELEMENTS = ["#b71c1c", "#d32f2f", "#f44336"] # Fire Red
    COLORS_SAISONS  = ["#1b5e20", "#388e3c", "#4caf50"] # Earth Green
    COLORS_ATMOS    = ["#4a148c", "#7b1fa2", "#9c27b0"] # Gemstone Purple 

    # MAP THEMES (Preset -> Kind, C1, C2)
    PRESET_THEMES = {
        # Elements
        "terre": ("leaf", "#4caf50", "#2e7d32"),
        "eau": ("droplet", "#00bcd4", "#0288d1"),
        "feu": ("droplet", "#ff5722", "#ffeb3b"),
        "air": ("orb", "#b0bec5", "#ffffff"),
        "espace": ("orb", "#311b92", "#673ab7"),
        # Saisons
        "hiver": ("orb", "#81d4fa", "#ffffff"),
        "printemps": ("leaf", "#f48fb1", "#c5e1a5"),
        "ete": ("orb", "#ff9800", "#ffeb3b"),
        "automne": ("leaf", "#a1887f", "#ff7043"),
        "vide": ("orb", "#000000", "#4a148c"),
        # Atmos
        "zen": ("leaf", "#81c784", "#c8e6c9"),
        "cyber": ("orb", "#00e676", "#2979ff"),
        "lofi": ("orb", "#d7ccc8", "#795548"),
        "jungle": ("leaf", "#1b5e20", "#4caf50"),
        "indus": ("orb", "#607d8b", "#ff5722"),
        # Instruments
        "instruments": ("note", "#ff9800", "#ffca28")
    }

    # --- HELPERS UI (GLOBAL) ---
    def LiquidIcon(kind, color_start, color_end, scale=1.0):
        size = 50 * scale
        if kind == "droplet": # Liquid / Fire
            return ft.Container(
                width=size, height=size,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1,1), end=ft.Alignment(1,-1),
                    colors=[color_start, color_end]
                ),
                border_radius=ft.border_radius.only(top_left=0, top_right=size, bottom_left=size, bottom_right=size),
                rotate=ft.Rotate(0.785), # 45deg
                shadow=ft.BoxShadow(blur_radius=10*scale, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
            )
        elif kind == "leaf": # Nature
            return ft.Container(
                width=size, height=size,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0,1), end=ft.Alignment(0,-1),
                    colors=[color_start, color_end]
                ),
                border_radius=ft.border_radius.only(top_left=size, bottom_right=size, top_right=0, bottom_left=0),
                shadow=ft.BoxShadow(blur_radius=10*scale, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
            )
        elif kind == "note": # Music Mode - restored Geometric Vinyl
            offset_y = 0
            if scale > 1.2: offset_y = 10 # Adjust for main bubble
            
            # Geometric Primitive: Vinyl Record / Gold Disc
            # Using only Containers with Border Radius and HEX COLORS
            return ft.Container(
                width=size, height=size,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1,-1), end=ft.Alignment(1,1),
                    colors=[color_start, color_end]
                ),
                border_radius=size,
                alignment=ft.Alignment(0,0),
                content=ft.Container(
                    width=size*0.6, height=size*0.6,
                    border_radius=size,
                    border=ft.Border.all(2*scale, ft.Colors.with_opacity(0.8, "#FFFFFF")), # Safe Hex White
                    content=ft.Container(
                        width=size*0.2, height=size*0.2,
                        bgcolor="#FFFFFF", # Safe Hex White
                        border_radius=size,
                    )
                ),
                border=ft.Border.all(2*scale, ft.Colors.with_opacity(0.5, "#FFFFFF")),
                shadow=ft.BoxShadow(blur_radius=15*scale, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
            )
        elif kind == "orb": # Abstract
            return ft.Container(
                width=size, height=size,
                gradient=ft.RadialGradient(
                    colors=[color_end, color_start],
                ),
                border_radius=size,
                border=ft.Border.all(2*scale, ft.Colors.with_opacity(0.5, "white")),
                shadow=ft.BoxShadow(blur_radius=15*scale, color=color_start, offset=ft.Offset(0,0), blur_style="outer")
            )
        return ft.Container()

    # --- VARIABLES ---
    # CONTENEUR ANIMÉ
    # Initial placeholder
    icon_content = LiquidIcon("droplet", "#00bcd4", "#0288d1", scale=1.5)
    icon_display = ft.Container(content=icon_content, alignment=ft.Alignment(0,0))
    
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

    # --- PARTICLE SYSTEM (v6) ---
    class Particle:
        def __init__(self, page_width, page_height):
            self.page_width = page_width
            self.page_height = page_height
            self.size = random.randint(5, 15)
            self.x = random.uniform(0, page_width)
            self.y = random.uniform(0, page_height)
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.5, 0.5)
            self.opacity = random.uniform(0.1, 0.4)
            self.color = "white"
            
            self.container = ft.Container(
                width=self.size, height=self.size,
                bgcolor=self.color,
                border_radius=50,
                left=self.x, top=self.y,
                opacity=self.opacity,
                animate_position=ft.Animation(2000, ft.AnimationCurve.LINEAR),
                animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
            )

        def update(self, theme_mode):
            # Update Position
            self.x += self.vx * 10
            self.y += self.vy * 10
            
            # Wrap around screen
            if self.x > self.page_width: self.x = 0
            if self.x < 0: self.x = self.page_width
            if self.y > self.page_height: self.y = 0
            if self.y < 0: self.y = self.page_height
            
            self.container.left = self.x
            self.container.top = self.y
            
            # Theme Behavior
            if theme_mode == "elements": # Rising Bubbles
                self.vy = random.uniform(-2.0, -0.5)
                self.vx = random.uniform(-0.5, 0.5)
                
                # Sync color with preset
                p = config.ETAT["preset"] # Fix UnboundLocalError
                if p in PRESET_THEMES:
                    kind, c1, c2 = PRESET_THEMES[p]
                    if random.random() < 0.5: self.container.bgcolor = c1
                    else: self.container.bgcolor = c2

            elif theme_mode == "saisons": # Falling Petals
                self.vy = random.uniform(0.5, 2.0)
                self.vx = random.uniform(-1.0, 1.0)
                self.container.width = random.randint(5, 15)
                self.container.height = self.container.width
                
                # Sync color with preset
                p = config.ETAT["preset"]
                if p in PRESET_THEMES:
                    kind, c1, c2 = PRESET_THEMES[p]
                    self.container.bgcolor = c1 if random.random() < 0.5 else c2

            elif theme_mode == "atmos": # Cyber/Static
                # Sync color with preset
                p = config.ETAT["preset"]
                if p in PRESET_THEMES:
                    kind, c1, c2 = PRESET_THEMES[p]
                    self.container.bgcolor = c1 if random.random() < 0.5 else c2

                if random.random() < 0.1: # Flicker move
                    self.x = random.uniform(0, self.page_width)
                    self.y = random.uniform(0, self.page_height)
                
            else: # Home / Default (Slow float)
                self.container.bgcolor = "white"
                self.vx = random.uniform(-0.5, 0.5)
                self.vy = random.uniform(-0.5, 0.5)

    particles = [Particle(450, 800) for _ in range(20)]
    particle_layer = ft.Stack([p.container for p in particles])

    def animer_fond():
        while True:
            current_theme = "home"
            if config.ETAT["collection"] == "elements": current_theme = "elements"
            elif config.ETAT["collection"] == "saisons": current_theme = "saisons"
            elif config.ETAT["collection"] == "atmos": current_theme = "atmos"
            
            for p in particles:
                p.update(current_theme)
            
            try:
                page.update()
            except: pass
            time.sleep(0.1)

    threading.Thread(target=animer_fond, daemon=True).start()

    # --- UI COMPONENTS ---
    
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
    
    # WRAPPER PRINCIPAL (STACK)
    # Layer 0: Gradient Background
    bg_gradient = ft.Container(
        gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=COLORS_ACCUEIL), 
        expand=True,
        animate=ft.Animation(2000, ft.AnimationCurve.EASE_OUT_CUBIC)
    )
    
    # Layer 1: Particles (particle_layer)
    # Layer 2: Main Content (Will be set in main_layout_stack.controls)
    
    # TITLE BAR REMOVED PER USER REQUEST
    # The application will remain frameless but without custom controls for now.

    main_layout_stack = ft.Stack(
        [
            bg_gradient,
            particle_layer,
            ft.Container(expand=True) # Placeholder for content
        ],
        expand=True
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
        
        # Update Main Icon based on Preset Theme
        if p in PRESET_THEMES:
            kind, c1, c2 = PRESET_THEMES[p]
            # Recreate the icon with new parameters
            new_icon = LiquidIcon(kind, c1, c2, scale=1.5)
            icon_display.content = new_icon
            
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

    def update_central_icon_for_preset(preset_code):
        if preset_code not in PRESET_THEMES: return
        kind, c1, c2 = PRESET_THEMES[preset_code]
        container_icone.content = LiquidIcon(kind, c1, c2, scale=1.0)
        # Also update particles color if needed (optional, handled by update_ui loop mostly)
        container_icone.update()

    def charger_interface_controle(nom_collection):
        config.ETAT["collection"] = nom_collection
        
        if nom_collection == "elements":
            config.ETAT["preset"] = "feu" # Changed to Fire as default for Red theme
            presets_controls = creer_boutons_elements()
            bg_gradient.gradient.colors = COLORS_ELEMENTS
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "red") 
            container_icone.content = LiquidIcon("droplet", "#b71c1c", "#f44336", scale=1.0) # Reset to Fire/Droplet
            
        elif nom_collection == "saisons":
            config.ETAT["preset"] = "terre" # Changed to Earth as default for Green theme
            presets_controls = creer_boutons_saisons()
            bg_gradient.gradient.colors = COLORS_SAISONS
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "green") 
            container_icone.content = LiquidIcon("leaf", "#1b5e20", "#4caf50", scale=1.0) # Reset to Leaf
            
        elif nom_collection == "instruments":
            config.ETAT["mode_orchestre"] = True
            config.ETAT["preset"] = None # No single preset
            if "instruments_actifs" not in config.ETAT: config.ETAT["instruments_actifs"] = []
            
            presets_controls = creer_boutons_instruments()
            bg_gradient.gradient.colors = ["#3e2723", "#5d4037", "#795548"] # Bronze/Gold theme
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "orange") 
            container_icone.content = LiquidIcon("note", "#ff9800", "#ffca28", scale=1.0) # New Note Icon
            
        else:
            config.ETAT["preset"] = "zen"
            presets_controls = creer_boutons_atmos()
            bg_gradient.gradient.colors = COLORS_ATMOS
            container_icone.shadow.color = ft.Colors.with_opacity(0.5, "purple") 
            container_icone.content = LiquidIcon("orb", "#4a148c", "#9c27b0", scale=1.0) # Reset to Orb 
            
        container_presets.content = presets_controls
        
        main_layout_stack.controls[2].content = creer_contenu_controle()
        page.update()
        
        config.ETAT["actif"] = True 
        update_ui()

    def retour_accueil(e):
        config.ETAT["collection"] = None
        config.ETAT["actif"] = False 
        config.ETAT["mode_orchestre"] = False # Disable Orchestra mode 
        
        bg_gradient.gradient.colors = COLORS_ACCUEIL
        main_layout_stack.controls[2].content = creer_contenu_accueil()
        page.update()
        page.update()



    # --- VUES ---
    
    def creer_contenu_accueil():
        def carte(icon_kind, titre, sous_titre, code, color_theme, c1, c2):
            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=LiquidIcon(icon_kind, c1, c2, scale=1.0),
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
        
        # Liste explicite pour éviter tout élément fantôme
        liste_cartes = [
            carte("droplet", "ELEMENTS", "Nature & Raw Power", "elements", "cyan", "blue", "cyan"),
            carte("leaf", "SEASONS", "Time & Journey", "saisons", "green", "green", "yellow"),
            carte("orb", "ATMOS", "Mood & Abstraction", "atmos", "purple", "purple", "pink"),
            carte("note", "ORCHESTRA", "Create Harmony", "instruments", "#FF9800", "#FFD700", "#8D6E63")
        ]

        return ft.Column([
            ft.Container(height=40),
            creer_header(),
            ft.Container(height=40),
            ft.Text("CHOOSE YOUR WORLD", size=14, weight="bold", color=ft.Colors.with_opacity(0.5, "white")),
            ft.Container(height=20),
            ft.Row(controls=liste_cartes, alignment="center", wrap=True, spacing=10),
            ft.Container(expand=True),
            ft.Text("v9.0 Emotional Intelligence", size=10, color="#44ffffff")
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
            top_btn("ATMOS", "atmos"),
            top_btn("ORCHESTRA", "instruments")
        ], alignment="center", spacing=5)

        header_nav = ft.Container(
            content=ft.Row([
                bouton_retour,
                ft.Container(expand=True),
                ft.Text("Q U O N I A M", size=18, weight="bold", color="white", font_family="Verdana"), # Stylized Title
                ft.Container(expand=True),
                top_bar,
                ft.Container(width=10) 
            ], alignment="center"),
            bgcolor=ft.Colors.with_opacity(0.4, "black"), # Dark Glass Effect
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
            border_radius=20,
            padding=10,
            blur=ft.Blur(10, 10),
            margin=ft.Margin(left=10, top=0, right=10, bottom=0)
        )

        return ft.Column([
            ft.Container(height=10),
            header_nav,
            ft.Container(height=10),
            container_icone, 
            creer_separateur_neon("#D500F9" if config.ETAT["collection"] == "atmos" else "#00E5FF"),
            
            # CONTRASTED CONTAINER FOR PRESETS
            ft.Container(
                content=container_presets,
                bgcolor=ft.Colors.with_opacity(0.4, "black"), # Darker background for contrast
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
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
    
    def btn_preset(kind, nom, code, c1, c2):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=LiquidIcon(kind, c1, c2, scale=0.4),
                    alignment=ft.Alignment(0,0),
                    height=25
                ),
                ft.Text(nom, size=10, color=ft.Colors.with_opacity(0.9, "white"), weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            data=code, 
            on_click=lambda e: [changer_preset(e), update_central_icon_for_preset(code)],
            width=70, height=70,
            border_radius=15,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0),
                end=ft.Alignment(1.0, 1.0),
                colors=[
                    ft.Colors.with_opacity(0.1, "white"),
                    ft.Colors.with_opacity(0.02, "white"),
                ],
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, "white")),
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=-5,
                color=c1,
                offset=ft.Offset(0, 5)
            ),
            padding=5,
            ink=True
        )

    def creer_boutons_elements():
        return ft.Column([
            ft.Row([
                btn_preset("leaf", "Earth", "terre", "#4caf50", "#2e7d32"), 
                btn_preset("droplet", "Water", "eau", "#00bcd4", "#0288d1"), 
                btn_preset("droplet", "Fire", "feu", "#ff5722", "#ffeb3b")
            ], alignment="center"),
            ft.Container(height=5),
            ft.Row([
                btn_preset("orb", "Air", "air", "#b0bec5", "#ffffff"), 
                btn_preset("orb", "Space", "espace", "#311b92", "#673ab7")
            ], alignment="center")
        ])

    def creer_boutons_saisons():
        return ft.Column([
            ft.Row([
                btn_preset("orb", "Winter", "hiver", "#81d4fa", "#ffffff"), 
                btn_preset("leaf", "Spring", "printemps", "#f48fb1", "#c5e1a5"), 
                btn_preset("orb", "Summer", "ete", "#ff9800", "#ffeb3b")
            ], alignment="center"),
            ft.Container(height=5),
            ft.Row([
                btn_preset("leaf", "Autumn", "automne", "#a1887f", "#ff7043"), 
                btn_preset("orb", "Void", "vide", "#000000", "#4a148c")
            ], alignment="center")
        ])
    
    def creer_boutons_atmos():
        return ft.Column([
            ft.Row([
                btn_preset("orb", "Zen", "zen", "#81c784", "#c8e6c9"), 
                btn_preset("orb", "Cyber", "cyber", "#00e676", "#2979ff"), 
                btn_preset("orb", "LoFi", "lofi", "#d7ccc8", "#795548")
            ], alignment="center"),
            ft.Container(height=5),
            ft.Row([
                btn_preset("leaf", "Jungle", "jungle", "#1b5e20", "#4caf50"), 
                btn_preset("orb", "Indus", "indus", "#607d8b", "#ff5722")
            ], alignment="center")
        ])

    def creer_boutons_instruments():
        def toggle_inst(e):
            inst = e.control.data
            actifs = config.ETAT.get("instruments_actifs", [])
            
            if inst in actifs:
                actifs.remove(inst)
                e.control.bgcolor = ft.Colors.TRANSPARENT
                e.control.border = ft.Border.all(1, ft.Colors.with_opacity(0.5, "#FFFFFF")) # White Hex
                e.control.shadow.color = ft.Colors.TRANSPARENT
                e.control.content.controls[0].color = "#FFFFFF" # Icon White
            else:
                actifs.append(inst)
                e.control.bgcolor = ft.Colors.with_opacity(0.2, "#FFD700") # Gold Hex
                e.control.border = ft.Border.all(1, "#FFD700") # Gold Hex
                e.control.shadow.color = "#FF9800" # Orange Hex
                e.control.content.controls[0].color = "#FFD700" # Icon Gold
                
            config.ETAT["instruments_actifs"] = actifs
            e.control.update()

        def get_asset(code):
            mapping = {
                # STRINGS
                "violon": assets.SVG_VIOLIN, "violoncelle": assets.SVG_CELLO, "contrebasse": assets.SVG_CONTRABASS,
                "guitare": assets.SVG_GUITAR, "basse": assets.SVG_BASS, "harpe": assets.SVG_HARP,
                # WINDS
                "flute": assets.SVG_FLUTE, "clarinette": assets.SVG_CLARINET, 
                "hautbois": assets.SVG_OBOE, "trompette": assets.SVG_TRUMPET, "cor": assets.SVG_HORN, "cuivres": assets.SVG_TRUMPET, # Fallback
                # KEYS
                "piano": assets.SVG_PIANO, "orgue": assets.SVG_ORGAN,
                # PERCUSSION
                "timbales": assets.SVG_DRUM, "batterie": assets.SVG_DRUM
            }
            return mapping.get(code, assets.SVG_NOTE)

        def btn_inst(nom, code):
            est_actif = code in config.ETAT.get("instruments_actifs", [])
            svg_content = get_asset(code)
            b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            
            # Safe Hex Color for Icon
            icon_color = "#FFD700" if est_actif else "#FFFFFF"

            return ft.Container(
                content=ft.Column([
                    ft.Image(src=f"data:image/svg+xml;base64,{b64}", width=30, height=30, color=icon_color, animate_scale=200),
                    ft.Text(nom, size=10, color="white", weight="bold")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                data=code,
                on_click=toggle_inst,
                padding=10,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.5, icon_color)),
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.2, "#FFD700") if est_actif else ft.Colors.TRANSPARENT,
                shadow=ft.BoxShadow(blur_radius=10, color="#FF9800" if est_actif else ft.Colors.TRANSPARENT),
                ink=True,
                animate_scale=200,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                width=80, height=80 # Fixed size for grid alignment
            )

        def section(titre, instruments_list):
            return ft.Column([
                ft.Text(titre, size=12, weight="bold", color="#88ffffff"),
                ft.Row([btn_inst(n, c) for n, c in instruments_list], alignment="center", wrap=True, spacing=10)
            ], horizontal_alignment="center", spacing=5)

        def change_emotion(e):
            val = e.control.value
            
            # Check if it's a custom profile
            if val.startswith("profile_"):
                profile_name = val.replace("profile_", "")
                if profile_name in config.ETAT.get("custom_profiles", {}):
                    data = config.ETAT["custom_profiles"][profile_name]
                    # Load state
                    config.ETAT["bpm"] = data.get("bpm", 120)
                    config.ETAT["instruments_actifs"] = data.get("actifs", [])
                    config.ETAT["chaos"] = data.get("chaos", 100)
                    config.ETAT["gravite"] = data.get("gravite", 0)
                    config.ETAT["emotion"] = "custom" # Lock emotion logic to avoid override
                    print(f"📂 Profil chargé : {profile_name}")
                    return

            config.ETAT["emotion"] = val
            config.ETAT["target_emotion"] = val 
            if val == "aleatoire":
                 config.ETAT["last_emotion_switch"] = 0 
        
        # Build Options List dynamically
        opts = [
            ft.dropdown.Option("aleatoire", "🎲  Random Flow"),
            ft.dropdown.Option("joyeux", "☀️  Joy & Light"),
            ft.dropdown.Option("melancolique", "🌧️  Melancholy"),
            ft.dropdown.Option("action", "⚔️  Action & Epic"),
            ft.dropdown.Option("suspense", "🕵️  Suspense"),
            ft.dropdown.Option("epique", "🏰  Majestic"),
        ]
        
        # Add Custom Profiles to Dropdown
        for name in config.ETAT.get("custom_profiles", {}):
            opts.append(ft.dropdown.Option(f"profile_{name}", f"👤 {name}"))

        emotion_selector = ft.Dropdown(
            options=opts,
            value=config.ETAT.get("emotion", "aleatoire"),
            width=250,
            text_size=12,
            height=40,
            bgcolor="#222222", # v10.0 darker background
            border_color=ft.Colors.with_opacity(0.2, "white"),
            border_radius=10,
            color="white"
        )
        emotion_selector.on_change = change_emotion
        # --- PROFILE MANAGEMENT (v10.1) ---
        
        # Helper: Custom Overlay Dialog
        def show_dialog(title, content, actions):
            def close_dialog(e):
                main_layout_stack.controls.pop() # Remove last item (the dialog)
                page.update()

            dialog_container = ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight="bold", color="white"),
                    ft.Container(height=10),
                    content,
                    ft.Container(height=20),
                    ft.Row(actions + [
                        ft.Container(content=ft.Text("CANCEL", color="#88ffffff"), on_click=close_dialog, padding=10, ink=True)
                    ], alignment="end")
                ], width=300, spacing=0),    
                bgcolor="#222222",
                border=ft.Border.all(1, "#44ffffff"),
                border_radius=15,
                padding=20,
                shadow=ft.BoxShadow(blur_radius=20, color="black"),
                alignment=ft.alignment.center
            )
            
            overlay = ft.Container(
                content=dialog_container,
                bgcolor=ft.Colors.with_opacity(0.8, "black"),
                alignment=ft.alignment.center,
                expand=True,
                ink=False # Block clicks through
            )
            
            main_layout_stack.controls.append(overlay)
            page.update()

        def save_profile_click(e):
            txt_name = ft.TextField(label="Profile Name", value=f"My Profile {len(config.ETAT.get('custom_profiles', {})) + 1}", border_color="white", color="white")
            
            def confirm_save(e):
                name = txt_name.value.strip()
                if not name: return
                
                # Save Logic
                profile_data = {
                    "bpm": config.ETAT.get("bpm", 120),
                    "actifs": list(config.ETAT.get("instruments_actifs", [])),
                    "chaos": config.ETAT.get("chaos", 100),
                    "gravite": config.ETAT.get("gravite", 0)
                }
                
                if "custom_profiles" not in config.ETAT: config.ETAT["custom_profiles"] = {}
                config.ETAT["custom_profiles"][name] = profile_data
                
                # Update Dropdown
                update_dropdown()
                
                print(f"💾 Profil sauvegardé : {name}")
                main_layout_stack.controls.pop()
                page.update()

            show_dialog("Save Profile", txt_name, [
                ft.Container(content=ft.Text("SAVE", color="#4caf50", weight="bold"), on_click=confirm_save, padding=10, ink=True)
            ])

        def rename_profile_click(e):
            val = emotion_selector.value
            if not val or not val.startswith("profile_"): return
            old_name = val.replace("profile_", "")
            
            txt_name = ft.TextField(label="New Name", value=old_name, border_color="white", color="white")
            
            def confirm_rename(e):
                new_name = txt_name.value.strip()
                if not new_name or new_name == old_name: return
                
                # Rename Logic
                data = config.ETAT["custom_profiles"].pop(old_name)
                config.ETAT["custom_profiles"][new_name] = data
                
                update_dropdown(selected=f"profile_{new_name}")
                main_layout_stack.controls.pop()
                page.update()

            show_dialog("Rename Profile", txt_name, [
                ft.Container(content=ft.Text("RENAME", color="#ff9800", weight="bold"), on_click=confirm_rename, padding=10, ink=True)
            ])
            
        def delete_profile_click(e):
            val = emotion_selector.value
            if not val or not val.startswith("profile_"): return
            name = val.replace("profile_", "")
            
            def confirm_delete(e):
                if name in config.ETAT["custom_profiles"]:
                    del config.ETAT["custom_profiles"][name]
                
                update_dropdown(selected="aleatoire")
                main_layout_stack.controls.pop()
                page.update()

            show_dialog("Delete Profile?", ft.Text(f"Are you sure you want to delete '{name}'?", color="#ccffffff"), [
                ft.Container(content=ft.Text("DELETE", color="#f44336", weight="bold"), on_click=confirm_delete, padding=10, ink=True)
            ])

        def update_dropdown(selected=None):
            # Rebuild Options
            opts = [
                ft.dropdown.Option("aleatoire", "🎲  Random Flow"),
                ft.dropdown.Option("joyeux", "☀️  Joy & Light"),
                ft.dropdown.Option("melancolique", "🌧️  Melancholy"),
                ft.dropdown.Option("action", "⚔️  Action & Epic"),
                ft.dropdown.Option("suspense", "🕵️  Suspense"),
                ft.dropdown.Option("epique", "🏰  Majestic"),
            ]
            for name in config.ETAT.get("custom_profiles", {}):
                opts.append(ft.dropdown.Option(f"profile_{name}", f"👤 {name}"))
            
            emotion_selector.options = opts
            if selected: emotion_selector.value = selected
            emotion_selector.update()
            update_manage_buttons()

        def update_manage_buttons():
            val = emotion_selector.value
            is_custom = val and val.startswith("profile_")
            btn_rename.visible = is_custom
            btn_delete.visible = is_custom
            btn_rename.update()
            btn_delete.update()

        def on_dropdown_change(e):
            change_emotion(e)
            update_manage_buttons()

        emotion_selector.on_change = on_dropdown_change

        # UI Elements
        btn_save = ft.Container(content=ft.Text("💾 SAVE", color="#88ffffff", size=10, weight="bold"), on_click=save_profile_click, tooltip="Save New Profile", padding=8, border_radius=10, ink=True, border=ft.Border.all(1, "#33ffffff"))
        
        btn_rename = ft.Container(content=ft.Text("✏️", size=12), on_click=rename_profile_click, tooltip="Rename", padding=8, border_radius=10, ink=True, visible=False)
        btn_delete = ft.Container(content=ft.Text("🗑️", size=12), on_click=delete_profile_click, tooltip="Delete", padding=8, border_radius=10, ink=True, visible=False)

        return ft.Column([
            ft.Text("ORCHESTRA", size=18, weight="bold", color="white"),
            ft.Row([emotion_selector, btn_save, btn_rename, btn_delete], alignment="center"),
            ft.Container(height=5),
            
            # STRINGS SECTIONS
            section("STRINGS", [("Violin", "violon"), ("Cello", "violoncelle"), ("Bass", "contrebasse"), ("Harp", "harpe"), ("Guitar", "guitare")]),
            ft.Divider(color="#22ffffff"),
            
            # WINDS SECTION
            section("WINDS & BRASS", [("Flute", "flute"), ("Clarinet", "clarinette"), ("Oboe", "hautbois"), ("Horn", "cor"), ("Brass", "cuivres")]),
            ft.Divider(color="#22ffffff"),
            
            # KEYS & PERCUSSION SECTION (Mixed Row)
            ft.Row([
                ft.Column([
                    ft.Text("KEYS", size=12, weight="bold", color="#88ffffff"),
                    ft.Row([btn_inst("Piano", "piano"), btn_inst("Organ", "orgue")], spacing=5)
                ], horizontal_alignment="center"),
                ft.Container(width=10),
                ft.Column([
                    ft.Text("PERCUSSION", size=12, weight="bold", color="#88ffffff"),
                    ft.Row([btn_inst("Timpani", "timbales"), btn_inst("Drums", "batterie")], spacing=5)
                ], horizontal_alignment="center")
            ], alignment="center"),
            
        ], horizontal_alignment="center", spacing=15)

    def creer_panneau_sliders():
        switch_auto.tooltip = "Enable Auto-Drifting (Emotions change over time)"
        switch_auto.on_change = toggle_auto
        
        # BPM Control Logic
        def change_bpm(delta):
            current = config.ETAT.get("bpm", 120)
            new_bpm = max(40, min(200, current + delta))
            config.ETAT["bpm"] = new_bpm
            lbl_bpm.value = f"{new_bpm} BPM"
            lbl_bpm.update()
            
        lbl_bpm = ft.Text(f"{config.ETAT.get('bpm', 120)} BPM", size=14, weight="bold")
        
        # --- BLOCS DE CONTROLE ---
        def creer_bloc(titre, icon_name, controls, color="#1a1a1a"):
             return ft.Container(
                 content=ft.Column([
                     ft.Row([ft.Icon(name=icon_name, size=18, color="white"), ft.Text(titre, size=12, weight="bold", color="#ddffffff")], spacing=10),
                     ft.Container(height=5),
                     ft.Column(controls, spacing=10)
                 ]),
                 padding=15,
                 bgcolor=color,
                 border_radius=15,
                 border=ft.Border.all(1, "#11ffffff")
             )

        # 1. RHYTHM BLOCK
        row_bpm = ft.Row([
            ft.Text("Tempo", size=12),
            ft.Container(expand=True),
            ft.Container(content=ft.Text("-", color="white", size=20), on_click=lambda e: change_bpm(-5), padding=5, border_radius=15, ink=True, bgcolor="#33000000"),
            ft.Container(width=10),
            lbl_bpm,
            ft.Container(width=10),
            ft.Container(content=ft.Text("+", color="white", size=20), on_click=lambda e: change_bpm(5), padding=5, border_radius=15, ink=True, bgcolor="#33000000"),
        ], alignment="center")

        def slider_row(label, key, icon_name, display):
            return ft.Column([
                ft.Row([
                    ft.Icon(name=icon_name, size=16, color="#88ffffff"),
                    ft.Text(label, size=12),
                    ft.Container(expand=True),
                    display
                ]),
                ft.Slider(min=0 if key!="gravite" else -2, max=100 if key!="gravite" else 2, 
                          divisions=100 if key!="gravite" else 4, 
                          value=config.ETAT[key], on_change=lambda e: changer_valeur(e, key),
                          active_color="white", inactive_color="#33ffffff", thumb_color="white")
            ], spacing=0)

        # 2. AUTO MODE BLOCK (Moved from Header)
        # Description text for the auto mode
        txt_auto = ft.Text("The AI will gently drift parameters over time, creating an evolving soundscape.", size=10, color="#88ffffff", italic=True)
        
        return ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([ft.Icon(name="tune", color="white"), ft.Text("Advanced Controls", size=14, color="white")], alignment="center"),
                controls=[
                    ft.Container(height=10),
                    
                    # AUTO MODE
                    creer_bloc("AUTO-DRIFT", "autorenew", [
                        ft.Row([
                            ft.Text("Enable Auto-Drifting", size=12),
                            ft.Container(expand=True),
                            switch_auto
                        ], alignment="center"),
                        txt_auto
                    ], color="#22ffffff"), # Neutral Dark Grey
                    
                    ft.Container(height=10),

                    # RHYTHM & CHAOS
                    creer_bloc("RHYTHM & FLOW", "waves", [
                        row_bpm,
                        slider_row("Chaos / Randomness", "chaos", "shuffle", lbl_chaos)
                    ], color="#22ffffff"), # Neutral Dark Grey
                    
                    ft.Container(height=10),
                    
                    # PHYSICS
                    creer_bloc("ENVIRONMENT", "public", [ # 'public' is Earth icon
                         slider_row("Intensity", "intensite", "flash_on", lbl_intensite),
                         slider_row("Gravity", "gravite", "arrow_downward", lbl_gravite),
                    ], color="#22ffffff"), # Neutral Dark Grey

                ],
                collapsed_text_color="#88ffffff",
                text_color="white",
                icon_color="white"
            ),
            bgcolor=ft.Colors.with_opacity(0.1, "black"),
            border_radius=15,
            padding=5
        )

    # Lancement
    main_layout_stack.controls[2].content = creer_contenu_accueil()
    page.add(main_layout_stack)
    
    # Threading correction: Start animation loop AFTER adding content to page
    thread_anim = threading.Thread(target=animer_coeur, daemon=True)
    thread_anim.start()

if __name__ == "__main__":
    print("Lancement v4.9.1 Final Polish...")
    thread_son = threading.Thread(target=moteur_audio.main, daemon=True)
    thread_son.start()
    ft.app(target=main)