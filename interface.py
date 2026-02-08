import flet as ft
import threading
import time
import main as moteur_audio
import config
import random
import base64
import assets_library as assets
import os # v13.0 fix
import math # v13.3 fix for visualizer

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
                border_radius=ft.BorderRadius.only(top_left=0, top_right=size, bottom_left=size, bottom_right=size),
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
                border_radius=ft.BorderRadius.only(top_left=size, bottom_right=size, top_right=0, bottom_left=0),
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

    # Helper for SVGs (Moved to Global Scope v13.3)
    def get_ui_icon(svg_content, color="white", size=18):
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return ft.Image(src=f"data:image/svg+xml;base64,{b64}", width=size, height=size, color=color)

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
                animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
                animate_scale=ft.Animation(200, ft.AnimationCurve.BOUNCE_OUT) # v13.3: Visualizer pulse
            )

        def update(self, theme_mode):
            # v13.3: Audio-Reactive Visualizer Logic
            # Pulse size based on audio intensity
            intensity = config.ETAT.get("intensite", 30)
            bpm = config.ETAT.get("bpm", 120)
            
            # Simple rhythmic pulse
            pulse = math.sin(time.time() * (bpm / 60.0) * math.pi) 
            scale_factor = 1.0 + (intensity / 100.0 * 0.5) + (pulse * 0.2)
            self.container.scale = scale_factor
            
            # Speed Factor
            speed_factor = 1.0 + (intensity / 100.0)

            # Update Position
            self.x += self.vx * 10 * speed_factor
            self.y += self.vy * 10 * speed_factor
            
            # Wrap around screen
            
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
                # v13.3 Fix: Update only the layer, not the whole page (Concurrency Crash Fix)
                particle_layer.update()
            except: pass
            time.sleep(0.1)

    # --- GLOBAL AUDIO PLAYER (v13.0 - Pygame Backend) ---
    # --- GLOBAL AUDIO PLAYER (v13.3 - Dual Channel Crossfade) ---
    class GlobalAudioPlayer:
        def __init__(self):
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.set_num_channels(8) # Ensure enough channels
                self.mixer = pygame.mixer
                
                # Reserve channels 0 and 1 for ambience crossfading
                self.chan_a = pygame.mixer.Channel(0)
                self.chan_b = pygame.mixer.Channel(1)
                
                self.has_pygame = True
                print("✅ Pygame Audio System Initialized (Dual Channel Mode)")
            except Exception as e:
                print(f"❌ Pygame Init Failed: {e}")
                self.has_pygame = False

            self.current_src = None
            self.active_channel = None # 'A' or 'B' or None
            self.is_muted = False
            self.is_paused = False
            self.volume = 0.4 
            
        def play_ambience(self, preset_key):
            if not self.has_pygame: return
            
            # Resolve file path
            src = config.AUDIO_FILES.get(preset_key)
            print(f"🔊 Playing Audio Request: '{preset_key}' -> Path: '{src}'")
            
            if not src or not os.path.exists(src):
                print(f"⚠️ Audio File Missing: {src}")
                return

            if src == self.current_src and not self.is_paused:
                return # Already playing this track

            # Determine Channels for Crossfade
            # If nothing playing, start on A.
            # If A playing, start B and fade A.
            # If B playing, start A and fade B.
            
            target_channel = self.chan_a
            fade_out_channel = None
            
            if self.active_channel == 'A':
                target_channel = self.chan_b
                fade_out_channel = self.chan_a
            elif self.active_channel == 'B':
                target_channel = self.chan_a
                fade_out_channel = self.chan_b
                
            print(f"🔄 Crossfade: {self.active_channel} -> {'B' if target_channel == self.chan_b else 'A'} (Src: {src})")

            try:
                sound = self.mixer.Sound(src)
                target_channel.set_volume(0 if self.is_muted else self.volume)
                target_channel.play(sound, loops=-1, fade_ms=3000) # 3s Fade In
                
                if fade_out_channel:
                    fade_out_channel.fadeout(3000) # 3s Fade Out
                    
                self.current_src = src
                self.active_channel = 'B' if target_channel == self.chan_b else 'A'
                self.is_paused = False
                
            except Exception as e:
                print(f"⚠️ Error playing {src}: {e}")
                
        def toggle_mute(self):
            self.is_muted = not self.is_muted
            target_vol = 0 if self.is_muted else self.volume
            
            if self.has_pygame:
                self.chan_a.set_volume(target_vol)
                self.chan_b.set_volume(target_vol)
            return self.is_muted

        def set_volume(self, vol_percent):
            # vol_percent 0-100 map to 0.0-1.0
            self.volume = val_map(vol_percent, 0, 100, 0, 1)
            if not self.has_pygame: return
            
            if not self.is_muted:
                self.chan_a.set_volume(self.volume)
                self.chan_b.set_volume(self.volume)

        def toggle_pause(self):
            if not self.has_pygame: return
            
            if self.is_paused:
                self.chan_a.unpause()
                self.chan_b.unpause()
                self.is_paused = False
            else:
                self.chan_a.pause()
                self.chan_b.pause()
                self.is_paused = True
            return self.is_paused

    # Val map helper
    def val_map(v, in_min, in_max, out_min, out_max):
        return (v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    # INSTANCE GLOBALE (Moved up for scope visibility)
    global_audio = GlobalAudioPlayer()

    threading.Thread(target=animer_fond, daemon=True).start()

    # --- UI COMPONENTS ---
    # ...
    
    lbl_vitesse = ft.Text("50%", size=12)
    lbl_intensite = ft.Text("30%", size=12)
    lbl_gravite = ft.Text("0", size=12)
    lbl_gravite = ft.Text("0", size=12)
    lbl_chaos = ft.Text("20%", size=12)
    lbl_bpm = ft.Text("120 BPM", size=14, weight="bold") # v11.0: Global for Auto-Drift Sync
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

                    # ANIMATION LOGIC (v12.0: Rhythmic Breathing)
                    current_scale = container_icone.scale
                    
                    # 1. BEAT (Expansion rapide)
                    if preset in ["eau", "terre", "printemps", "zen", "ete", "feu", "automne", "jungle", "lofi"]:
                         # Heartbeat effect
                         container_icone.scale = scale_max
                         container_icone.animate_scale = ft.Animation(100, ft.AnimationCurve.EASE_OUT) # Quick expand
                         container_icone.update()
                         
                         time.sleep(0.15) # Hold peak slightly
                         
                         # 2. DECAY (Relachement lent synchronisé au tempo)
                         container_icone.scale = 1.0
                         container_icone.animate_scale = ft.Animation(int(tempo * 800), ft.AnimationCurve.EASE_IN_OUT) # Slow decay
                         container_icone.update()
                    
                    # Special Spin Logic (Space/Cyber)
                    elif preset in ["espace", "vide", "cyber", "indus"]:
                        angle += 1.0 
                        container_icone.rotate.angle = angle
                        container_icone.scale = 1.0 # No pulse for spin
                        container_icone.update()

                    # Aura Pulse
                    container_icone.shadow.spread_radius = 5 + (intensite/8)
                    container_icone.shadow.color = ft.Colors.with_opacity(0.6, "white")
                    container_icone.update()
                    
                    # Wait for next beat (approximate)
                    sleep_time = max(0.4, tempo - 0.15)
                    time.sleep(sleep_time)
                    
                    # Rest of cycle cleanup
                    container_icone.shadow.spread_radius = 2
                    container_icone.shadow.color = ft.Colors.with_opacity(0.2, "white")
                    container_icone.update()
                else:
                    time.sleep(1.0)
            except Exception as e:
                # Silently ignore page attachment errors during startup/shutdown
                time.sleep(1.0)
            
            # v11.0: UI Sync for Auto-Drift (Check if instruments changed externally)
            # This allows the background audio engine to add/remove instruments and reflected on UI
            try:
                if config.ETAT["mode_auto"] and config.ETAT["collection"] == "instruments":
                     # Simple check: we could store a hash, but list length comparison + first item check is 'good enough' for now
                     # Or just call a lightweight update?
                     # Ideally we need a flag "ui_needs_update" in config
                     if config.ETAT.get("ui_needs_update", False):
                         update_ui()
                         config.ETAT["ui_needs_update"] = False
            except: pass


    # --- LOGIQUE UI ---

    def update_ui():
        lbl_vitesse.value = f"{int(config.ETAT['vitesse'])}%"
        lbl_intensite.value = f"{int(config.ETAT['intensite'])}%"
        lbl_gravite.value = f"{int(config.ETAT['gravite'])}"
        lbl_gravite.value = f"{int(config.ETAT['gravite'])}"
        lbl_chaos.value = f"{int(config.ETAT['chaos'])}%"
        lbl_bpm.value = f"{int(config.ETAT.get('bpm', 120))} BPM" # v11.0: Auto-Drift Sync
        
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
        
        # v10.5 & v11.0: Refresh Instrument Grid to show/hide excluded instruments
        if config.ETAT["collection"] == "instruments":
             # OPTIMIZED REFRESH: Don't rebuild, just update styles
             # We assume container_presets.content is the main Column
             try:
                 main_col = container_presets.content
                 if not main_col or not isinstance(main_col, ft.Column): return
                 
                 actifs = config.ETAT.get("instruments_actifs", [])
                 
                 # Recursive helper to find and update instrument buttons
                 def update_recursive(controls):
                     for c in controls:
                         # Check if it's an instrument button (Container with data=code)
                         if isinstance(c, ft.Container) and isinstance(c.data, str) and c.data in instruments_mapping:
                             inst_code = c.data
                             is_active = inst_code in actifs
                             
                             # Update Style
                             c.bgcolor = ft.Colors.with_opacity(0.2, "#FFD700") if is_active else ft.Colors.TRANSPARENT
                             c.border = ft.Border.all(1, "#FFD700") if is_active else ft.Border.all(1, ft.Colors.with_opacity(0.5, "#FFFFFF"))
                             c.shadow.color = "#FF9800" if is_active else ft.Colors.TRANSPARENT
                             # Update Icon Color (nested in Column -> Image)
                             try:
                                 # Content structure: Column -> [Image, Text]
                                 if isinstance(c.content, ft.Column):
                                     img = c.content.controls[0]
                                     if isinstance(img, ft.Image):
                                         img.color = "#FFD700" if is_active else "#FFFFFF"
                             except: pass
                             
                             # c.update() # OPTIMIZATION: Don't update individual controls, let page.update() handle it at the end
                             
                         # Recurse if control has controls (Row, Column, etc)
                         elif hasattr(c, "controls") and c.controls:
                             update_recursive(c.controls)
                         # Recurse if control is Container with content being a Row/Column
                         elif isinstance(c, ft.Container) and hasattr(c.content, "controls"):
                             update_recursive(c.content.controls)
                 
                 # Need a reference list of valid instruments to check data against
                 # We can reconstruct it or import it. For now, let's hardcode the keys or assume any short string data is one?
                 # Better: re-use the mapping keys from get_asset logic if possible, or just checking if data is not None
                 # Let's simple check if data is not None and matches our known keys
                 instruments_mapping = [
                     "violon", "violoncelle", "contrebasse", "guitare", "basse", "harpe",
                     "flute", "clarinette", "hautbois", "trompette", "cor", "cuivres",
                     "piano", "orgue", "timbales", "batterie",
                     "choir", "voice", "celesta", "bells", "pizzicato"
                 ]
                 
                 update_recursive(main_col.controls)
                 
             except Exception as e: 
                 # print(f"UI Update Error: {e}")
                 pass
             
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
        if config.ETAT["mode_auto"]:
            # v11.0: Initialize Auto-Drift State for Intro Mode
            config.ETAT["auto_start_time"] = time.time()
            config.ETAT["last_inst_update"] = time.time()
            
            # Ensure at least one instrument is active to start with (Piano default)
            if not config.ETAT.get("instruments_actifs"):
                config.ETAT["instruments_actifs"] = ["piano"]
                
        update_ui()
        
    def toggle_play(e):
        config.ETAT["actif"] = not config.ETAT["actif"]
        update_ui()
    
    btn_play_container.on_click = toggle_play

    # --- NAVIGATION ---

    # ZEN TIMER LOGIC (v12.0)
    def lancer_zen_timer(minutes):
        if minutes <= 0: return
        
        def timer_thread():
            print(f"⏳ Zen Timer Started: {minutes} minutes")
            time.sleep(minutes * 60)
            
            # Stop playback
            if config.ETAT["actif"]:
                config.ETAT["actif"] = False
                config.ETAT["timer_minutes"] = 0 # Reset
                
                # UI Update Trigger
                try:
                    btn_play_content.value = "▶  PLAY"
                    btn_play_container.gradient.colors = ["#56ab2f", "#a8e063"]
                    page.update()
                    
                    page.snack_bar = ft.SnackBar(ft.Text(f"🧘 Zen Session Finished ({minutes} min)", color="white"), bgcolor="#4caf50")
                    page.snack_bar.open = True
                    page.update()
                except: pass
                
        threading.Thread(target=timer_thread, daemon=True).start()

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

        # v13.3 Header Controls
        def pause_click(e):
            is_paused = global_audio.toggle_pause()
            # Update Icon
            btn = e.control.content
            if isinstance(btn, ft.Container): btn = btn.content # Handle nesting if any
            if isinstance(btn, ft.Image):
                 # We need to swap the source base64
                 # But get_ui_icon returns a new Image. Better to update the container content.
                 new_icon = get_ui_icon(assets.SVG_PLAY if is_paused else assets.SVG_PAUSE, size=20)
                 e.control.content = new_icon
                 e.control.update()

        def mute_click(e):
            is_muted = global_audio.toggle_mute()
            # Update Icon
            # e.control is the Container
            new_icon = get_ui_icon(assets.SVG_MUTE if is_muted else assets.SVG_VOLUME, 
                                  color="#ff4444" if is_muted else "white", size=20)
            e.control.content = new_icon
            e.control.update()

        def volume_change(e):
            global_audio.set_volume(e.control.value)

        # Controls
        ctrl_bar = ft.Row([
            ft.Container(
                content=get_ui_icon(assets.SVG_PAUSE, size=20), 
                on_click=pause_click,
                tooltip="Pause Ambience",
                padding=5,
                border_radius=50,
                ink=True
            ),
            ft.Slider(
                min=0, max=100, value=40, 
                width=80, 
                active_color="white", inactive_color="#44ffffff",
                on_change=volume_change,
                tooltip="Ambience Volume"
            ),
            ft.Container(
                content=get_ui_icon(assets.SVG_VOLUME, size=20),
                on_click=mute_click,
                tooltip="Mute/Unmute",
                padding=5,
                border_radius=50,
                ink=True
            )
        ], spacing=0, alignment="center")

        header_nav = ft.Container(
            content=ft.Row([
                bouton_retour,
                ft.Container(expand=True),
                ft.Row([
                    ft.Text("LIQUID SOUL", size=18, weight="bold", color="white", font_family="Verdana"),
                    ft.Text("v13.3", size=10, color="#88ffffff", italic=True)
                ], spacing=5),
                ft.Container(expand=True),
                # We replace the top_bar (navigation) with audio controls here? 
                # Wait, top_bar was for navigating Collections (Elements, Seasons...)
                # The user asked for Audio Controls in the Header.
                # Let's keep top_bar but maybe put Audio Controls ABOVE or NEXT to title?
                # Actually, the user said "barre de contrôle dans la barre des menus".
                # Current header has: Back | Title | TopBar (Nav).
                # Adding Audio Controls might crowd it.
                # Let's replace the Title with the Controls, or put controls on the right and move Nav below?
                # Decision: Put Audio Controls to the RIGHT (replacing TopBar? No, TopBar is needed).
                # Let's put Audio Controls in the CENTER instead of Title, and keep Nav on Right.
                # Or better: Back | Audio Controls | Nav.
                
                ctrl_bar,
                
                ft.Container(width=10),
                top_bar,
                
            ], alignment="center"),
            bgcolor=ft.Colors.with_opacity(0.4, "black"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
            border_radius=20,
            padding=5,
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


    def changer_preset(e):
        val = e.control.data
        config.ETAT["preset"] = val
        print(f"🎛️ Logic: Preset changed to {val}")
        
        # Trigger Audio
        try:
            global_audio.play_ambience(val)
        except Exception as err:
            print(f"❌ Error triggering audio: {err}")


    def btn_preset(icon_key, nom, code, c1, c2):
        # Resolve SVG
        mapping = {
            "earth": assets.SVG_EARTH, "water": assets.SVG_WATER, "fire": assets.SVG_FIRE,
            "air": assets.SVG_AIR, "space": assets.SVG_SPACE,
            "winter": assets.SVG_WINTER, "spring": assets.SVG_SPRING, "summer": assets.SVG_SUMMER,
            "autumn": assets.SVG_AUTUMN, "void": assets.SVG_VOID,
            "zen": assets.SVG_ZEN, "cyber": assets.SVG_CYBER, "lofi": assets.SVG_LOFI,
            "jungle": assets.SVG_JUNGLE, "indus": assets.SVG_INDUS
        }
        svg_content = mapping.get(icon_key, assets.SVG_NOTE)
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Image(src=f"data:image/svg+xml;base64,{b64}", 
                                   width=42, height=42, 
                                   color="white",
                                   fit="contain"),
                    alignment=ft.Alignment(0,0),
                    height=45
                ),
                ft.Text(nom, size=10, color="white", weight="bold", 
                       style=ft.TextStyle(shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.with_opacity(1.0, "black"), offset=ft.Offset(1, 1))))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            data=code, 
            on_click=lambda e: [changer_preset(e), update_central_icon_for_preset(code)],
            width=70, height=80,
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
            ink=True,
            tooltip=nom
        )

    def creer_boutons_elements():
        return ft.Column([
            ft.Row([
                btn_preset("earth", "Earth", "terre", "#4caf50", "#2e7d32"), 
                btn_preset("water", "Water", "eau", "#00bcd4", "#0288d1"), 
                btn_preset("fire", "Fire", "feu", "#ff5722", "#ffeb3b")
            ], alignment="center"),
            ft.Container(height=5),
            ft.Row([
                btn_preset("air", "Air", "air", "#b0bec5", "#ffffff"), 
                btn_preset("space", "Space", "espace", "#311b92", "#673ab7")
            ], alignment="center")
        ])

    def creer_boutons_saisons():
        return ft.Column([
            ft.Row([
                btn_preset("winter", "Winter", "hiver", "#81d4fa", "#ffffff"), 
                btn_preset("spring", "Spring", "printemps", "#f48fb1", "#c5e1a5"), 
                btn_preset("summer", "Summer", "ete", "#ff9800", "#ffeb3b")
            ], alignment="center"),
            ft.Container(height=5),
            ft.Row([
                btn_preset("autumn", "Autumn", "automne", "#a1887f", "#ff7043"), 
                btn_preset("void", "Void", "vide", "#000000", "#4a148c")
            ], alignment="center")
        ])
    
    def creer_boutons_atmos():
        return ft.Column([
            ft.Row([
                btn_preset("zen", "Zen", "zen", "#81c784", "#c8e6c9"), 
                btn_preset("cyber", "Cyber", "cyber", "#00e676", "#2979ff"), 
                btn_preset("lofi", "LoFi", "lofi", "#d7ccc8", "#795548")
            ], alignment="center"),
            ft.Container(height=5),
            ft.Row([
                btn_preset("jungle", "Thunder", "jungle", "#455a64", "#90a4ae"), # Changed colors to Stormy Grey/Blue
                btn_preset("indus", "Traffic", "indus", "#546e7a", "#cfd8dc")   # Changed colors to Urban Grey
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
                "timbales": assets.SVG_DRUM, "batterie": assets.SVG_DRUM,
                # v10.6 ETHEREAL & VOICES
                "choir": assets.SVG_CHOIR, "voice": assets.SVG_VOICE, "celesta": assets.SVG_CELESTA,
                "bells": assets.SVG_BELLS, "pizzicato": assets.SVG_PIZZICATO
            }
            return mapping.get(code, assets.SVG_NOTE)

        def btn_inst(nom, code):
            est_actif = code in config.ETAT.get("instruments_actifs", [])
            
            # v10.4: Check exclusion based on current emotion
            current_emo = config.ETAT.get("emotion", "aleatoire")
            if current_emo == "aleatoire": 
                target = config.ETAT.get("target_emotion", "joyeux")
            else:
                target = current_emo
                
            emo_data = config.EMOTIONS.get(target, {})
            est_exclu = code in emo_data.get("excluded", [])
            
            svg_content = get_asset(code)
            b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            
            # Colors & Tooltip
            if est_exclu:
                icon_color = "#555555"
                border_color = "#333333"
                bg_color = ft.Colors.with_opacity(0.1, "#000000")
                opacity = 0.3
                tooltip = f"{nom} (Unavailable in {target} mode)"
                on_click_action = None
            else:
                icon_color = "#FFD700" if est_actif else "#FFFFFF"
                border_color = ft.Colors.with_opacity(0.5, icon_color)
                bg_color = ft.Colors.with_opacity(0.2, "#FFD700") if est_actif else ft.Colors.TRANSPARENT
                opacity = 1.0
                tooltip = nom
                on_click_action = toggle_inst

            return ft.Container(
                content=ft.Column([
                    ft.Image(src=f"data:image/svg+xml;base64,{b64}", width=40, height=40, color=icon_color, fit="contain"),
                    ft.Text(nom, size=10, color="white" if not est_exclu else "#555555", weight="bold", text_align="center", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                data=code,
                on_click=on_click_action,
                padding=5,
                border=ft.Border.all(1, border_color),
                border_radius=10,
                bgcolor=bg_color,
                shadow=ft.BoxShadow(blur_radius=10, color="#FF9800" if est_actif else ft.Colors.TRANSPARENT) if not est_exclu else None,
                ink=not est_exclu,
                opacity=opacity,
                tooltip=tooltip,
                animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT) if est_actif else None,
                width=80, height=80 
            )

        def section(titre, instruments_list):
            return ft.Column([
                ft.Text(titre, size=12, weight="bold", color="#88ffffff"),
                ft.Row([btn_inst(n, c) for n, c in instruments_list], alignment="center", wrap=True, spacing=10)
            ], horizontal_alignment="center", spacing=5)

        # v10.9: Emotion Color Mapping
        EMOTION_COLORS = {
            "aleatoire": "#CCCCCC",
            "creatif": "#E91E63", # Pink
            "joyeux": "#FFD700", # Gold
            "melancolique": "#2196F3", # Blue
            "action": "#FF5722", # Deep Orange
            "suspense": "#9C27B0", # Purple
            "epique": "#F44336", # Red
        }

        # Handlers for Emotion Buttons
        def update_emotion_buttons():
            current = config.ETAT.get("emotion", "aleatoire")
            for btn in row_emotions.controls:
                val = btn.data
                is_active = (current == val)
                
                # Determine Color
                if val.startswith("profile_"):
                    base_color = "#00BCD4" # Cyan for profiles
                else:
                    base_color = EMOTION_COLORS.get(val, "white")
                
                # Apply Styles
                # Apply Styles
                try:
                    btn.bgcolor = ft.Colors.with_opacity(0.2, base_color) if is_active else ft.Colors.with_opacity(0.05, "white")
                    btn.border = ft.Border.all(2, base_color) if is_active else ft.Border.all(1, ft.Colors.with_opacity(0.1, "white"))
                    # Update Content (Image)
                    if isinstance(btn.content, ft.Image):
                        btn.content.color = base_color if is_active else "#88ffffff"
                    
                    btn.scale = 1.1 if is_active else 1.0
                    btn.update()
                except RuntimeError:
                    pass

        def change_emotion(e):
            val = e.control.data
            print(f"🖱️ UI: Change Emotion -> {val}")
            
            # Load Profile Data
            if val.startswith("profile_"):
                p_name = val.replace("profile_", "")
                p_data = config.ETAT["custom_profiles"].get(p_name)
                if p_data:
                    config.ETAT["bpm"] = p_data.get("bpm", 120)
                    config.ETAT["instruments_actifs"] = list(p_data.get("actifs", []))
                    config.ETAT["chaos"] = p_data.get("chaos", 100)
                    config.ETAT["gravite"] = p_data.get("gravite", 0)
                    print(f"📂 Loaded Profile: {p_name}")
                    # Update active instruments visual
                    update_ui()
            
            config.ETAT["emotion"] = val
            config.ETAT["target_emotion"] = val 
            if val == "aleatoire":
                 config.ETAT["last_emotion_switch"] = 0 
            
            update_emotion_buttons()
            
            if val == "creatif":
                 update_ui()

        def get_emotion_asset(code):
            mapping = {
               "aleatoire": assets.SVG_DICE,
               "creatif": assets.SVG_PALETTE,
               "joyeux": assets.SVG_SUN,
               "melancolique": assets.SVG_RAIN,
               "action": assets.SVG_SWORD,
               "suspense": assets.SVG_SUSPENSE,
               "epique": assets.SVG_EPIC
            }
            if code.startswith("profile_"): return assets.SVG_USER
            return mapping.get(code, assets.SVG_NOTE)

        def emotion_btn(icon_key, val, tooltip):
             # Initial State Calculation
             is_active = config.ETAT.get("emotion") == val
             
             # Determine Color
             if val.startswith("profile_"):
                 base_color = "#00BCD4" # Cyan
             else:
                 base_color = EMOTION_COLORS.get(val, "white")
             
             # Prepare SVG
             svg_content = get_emotion_asset(val)
             b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
             
             return ft.Container(
                content=ft.Image(src=f"data:image/svg+xml;base64,{b64}", 
                                width=22, height=22, 
                                color=base_color if is_active else "#88ffffff",
                                fit="contain"),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.2, base_color) if is_active else ft.Colors.with_opacity(0.05, "white"),
                border_radius=10,
                border=ft.Border.all(2, base_color) if is_active else ft.Border.all(1, ft.Colors.with_opacity(0.1, "white")),
                on_click=change_emotion,
                tooltip=tooltip,
                ink=True,
                data=val,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                scale=1.1 if is_active else 1.0,
                animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
            )

        row_emotions = ft.Row([
            emotion_btn("dice", "aleatoire", "Random Flow"),
            emotion_btn("palette", "creatif", "Creative Mode"),
            emotion_btn("sun", "joyeux", "Joy"),
            emotion_btn("rain", "melancolique", "Melancholy"),
            emotion_btn("sword", "action", "Action"),
            emotion_btn("suspense", "suspense", "Suspense"),
            emotion_btn("castle", "epique", "Epic"),
        ], alignment="center", spacing=10)
        
        # Container for Custom Profiles Buttons
        row_custom_profiles = ft.Row(alignment="center", spacing=10, wrap=True)

        def refresh_profiles_row():
            items = []
            for name in config.ETAT.get("custom_profiles", {}):
                # Use profile name as tooltip, special icon handling inside emotion_btn driven by "profile_" prefix
                items.append(emotion_btn("user", f"profile_{name}", f"Load {name}"))
            row_custom_profiles.controls = items
            try:
                if row_custom_profiles.page: row_custom_profiles.update()
            except RuntimeError:
                pass

        # Initial Load
        refresh_profiles_row()
        
        # --- PROFILE MANAGEMENT (Restored v10.9) ---
        def show_dialog(title, content, actions):
            def close_dialog(e):
                main_layout_stack.controls.pop()
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
                alignment=ft.Alignment(0, 0)
            )
            
            overlay = ft.Container(
                content=dialog_container,
                bgcolor=ft.Colors.with_opacity(0.8, "black"),
                alignment=ft.Alignment(0, 0),
                expand=True,
                ink=False
            )
            
            main_layout_stack.controls.append(overlay)
            page.update()

        def save_profile_click(e):
            txt_name = ft.TextField(label="Profile Name", value=f"Profile {len(config.ETAT.get('custom_profiles', {})) + 1}", border_color="white", color="white")
            
            def confirm_save(e):
                name = txt_name.value.strip()
                if not name: return
                
                # Save Logic
                profile_data = {
                    "bpm": config.ETAT.get("bpm", 120),
                    "actifs": list(config.ETAT.get("instruments_actifs", [])),
                    "chaos": config.ETAT.get("chaos", 100),
                    "gravite": config.ETAT.get("gravite", 0),
                    # Store current 'emotion' mode if needed, or just treat as 'custom'
                }
                
                if "custom_profiles" not in config.ETAT: config.ETAT["custom_profiles"] = {}
                config.ETAT["custom_profiles"][name] = profile_data
                
                # PERSIST TO DISK (v11.1)
                config.save_profiles_to_disk()
                
                print(f"💾 Profil sauvegardé : {name}")
                
                # REFRESH UI
                refresh_profiles_row()
                
                main_layout_stack.controls.pop()
                page.update()
                
                # Feedback
                btn_save.content.value = "✅ SAVED"
                btn_save.content.color = "#4caf50"
                btn_save.update()
                import time
                def reset_btn():
                    import time
                    time.sleep(2)
                    try:
                        if not btn_save.page: return # Safety check
                        btn_save.content.value = "💾 SAVE PROFILE"
                        btn_save.content.color = "#88ffffff"
                        btn_save.update()
                    except RuntimeError:
                        pass
                threading.Thread(target=reset_btn, daemon=True).start()

            show_dialog("Save Profile", txt_name, [
                ft.Container(content=ft.Text("SAVE", color="#4caf50", weight="bold"), on_click=confirm_save, padding=10, ink=True)
            ])

        btn_save = ft.Container(
            content=ft.Text("💾 SAVE PROFILE", color="#88ffffff", size=10, weight="bold"), 
            on_click=save_profile_click, 
            padding=10, 
            border_radius=15, 
            ink=True, 
            border=ft.Border.all(1, "#22ffffff"),
            bgcolor=ft.Colors.with_opacity(0.05, "white")
        )

        return ft.Column([
            ft.Text("ORCHESTRA", size=18, weight="bold", color="white"),
            # ft.Row([txt_emotion], alignment="center"), # Removed as requested
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
            
            ft.Divider(color="#22ffffff"),
            
            # v10.6 ETHEREAL & VOICES SECTION
            section("ETHEREAL & VOICES", [
                ("Choir", "choir"), 
                ("Voice", "voice"), 
                ("Celesta", "celesta"), 
                ("Bells", "bells"), 
                ("Pizzicato", "pizzicato")
            ]),

            ft.Container(height=10),
            ft.Divider(color="#22ffffff"),
            ft.Text("MOOD", size=12, weight="bold", color="#88ffffff"),
            row_emotions,
            
            ft.Container(height=10),
            row_custom_profiles, # Added Profiles Row
            ft.Container(height=10),
            
            # ft.Container(height=20), # Spacer before Save
            btn_save,
            ft.Container(height=10),
            
        ], horizontal_alignment="center", spacing=15)

    def creer_panneau_sliders():
        switch_auto.tooltip = "Enable Auto-Drifting"
        switch_auto.on_change = toggle_auto
        


        # v13.2: Re-implemented Value Changer with Audio Volume Link
        def changer_valeur(e, key):
            val = e.control.value
            config.ETAT[key] = val
            
            # Update Audio Volume if Intensity changes
            if key == "intensite":
                 global_audio.set_volume(val)
            
            # Update Labels
            if key == "vitesse": lbl_vitesse.value = f"{int(val)}%"
            elif key == "intensite": lbl_intensite.value = f"{int(val)}%"
            elif key == "chaos": lbl_chaos.value = f"{int(val)}%"
            elif key == "gravite": lbl_gravite.value = f"{int(val)}"
            
            try:
                page.update()
            except: pass

        # BPM Control Logic
        def change_bpm(delta):
            current = config.ETAT.get("bpm", 120)
            new_bpm = max(40, min(200, current + delta))
            config.ETAT["bpm"] = new_bpm
            lbl_bpm.value = f"{new_bpm} BPM"
            lbl_bpm.update()
            
            lbl_bpm.value = f"{new_bpm} BPM"
            lbl_bpm.update()
            
        # lbl_bpm was here, now global
        
        # --- BLOCS DE CONTROLE ---
        def creer_bloc(titre, svg_icon, controls, color="#22ffffff"):
             return ft.Container(
                 content=ft.Column([
                     ft.Row([get_ui_icon(svg_icon), ft.Text(titre, size=12, weight="bold", color="#ddffffff")], spacing=10),
                     ft.Container(height=5),
                     ft.Column(controls, spacing=10)
                 ]),
                 padding=15,
                 bgcolor=color,
                 border_radius=15,
                 border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white"))
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

        def slider_row(label, key, svg_icon, display, tooltip_text=""):
            return ft.Column([
                ft.Row([
                    get_ui_icon(svg_icon, size=16, color="#88ffffff"),
                    ft.Text(label, size=12, tooltip=tooltip_text), # Tooltip on label
                    ft.Container(expand=True),
                    display
                ]),
                ft.Slider(min=0 if key!="gravite" else -2, max=100 if key!="gravite" else 2, 
                          divisions=100 if key!="gravite" else 4, 
                          value=config.ETAT[key], on_change=lambda e: changer_valeur(e, key),
                          active_color="white", inactive_color="#33ffffff", thumb_color="white",
                          tooltip=tooltip_text) # Tooltip on slider
            ], spacing=0)

        # 2. AUTO MODE BLOCK
        txt_auto = ft.Text("The AI will gently drift parameters over time.", size=10, color="#88ffffff", italic=True)
        
        # Zen Timer Dropdown
        def on_timer_change(e):
             val = e.control.value
             mins = 0
             if val == "15 min": mins = 15
             elif val == "30 min": mins = 30
             elif val == "60 min": mins = 60
             
             if mins > 0:
                 lancer_zen_timer(mins)
                 page.snack_bar = ft.SnackBar(ft.Text(f"⏳ Zen Timer set for {mins} minutes", color="white"), bgcolor="#2196f3")
                 page.snack_bar.open = True
                 page.update()

        dd_timer = ft.Dropdown(
            options=[
                ft.dropdown.Option("Off"),
                ft.dropdown.Option("15 min"),
                ft.dropdown.Option("30 min"),
                ft.dropdown.Option("60 min"),
            ],
            width=100,
            text_size=12,
            height=35,
            content_padding=5,
            border_color="#44ffffff",
            color="white",
            value="Off",
        )
        dd_timer.on_change = on_timer_change

        return ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([get_ui_icon(assets.SVG_TUNE, color="white"), ft.Text("Advanced Controls", size=14, color="white")], alignment="center"),
                controls=[
                    ft.Container(height=10),
                    
                    # ZEN & AUTO MODE
                    creer_bloc("ZEN MODE & AUTO", assets.SVG_AUTO, [
                        ft.Row([
                            ft.Column([
                                ft.Text("Auto-Drift", size=11, color="#ddffffff"),
                                switch_auto
                            ]),
                            ft.Container(width=20),
                            ft.Column([
                                ft.Text("Sleep Timer", size=11, color="#ddffffff"),
                                dd_timer
                            ])
                        ], alignment="center"),
                        txt_auto
                    ], color="#22ffffff"),
                    
                    ft.Container(height=10),

                    # RHYTHM & CHAOS
                    creer_bloc("RHYTHM & FLOW", assets.SVG_WAVES, [
                        row_bpm,
                        slider_row("Chaos", "chaos", assets.SVG_SHUFFLE, lbl_chaos, "Probability of random variations")
                    ], color="#224caf50"), 
                    
                    ft.Container(height=10),
                    
                    # PHYSICS
                    creer_bloc("ENVIRONMENT", assets.SVG_EARTH, [
                         slider_row("Intensity", "intensite", assets.SVG_FLASH, lbl_intensite, "Generic density and volume of the soundscape"),
                         slider_row("Gravity", "gravite", assets.SVG_ARROW_DOWN, lbl_gravite, "Pitch bias: High (Aer) vs Low (Earth)"),
                    ], color="#22ff9800"), 

                ],
                collapsed_text_color="#88ffffff",
                text_color="white",
                icon_color="white",
                maintain_state=True
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
    print("Lancement v10.0 Final Polish...")
    thread_son = threading.Thread(target=moteur_audio.main, daemon=True)
    thread_son.start()
    ft.app(target=main)