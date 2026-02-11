import flet as ft
from flet import canvas as cv
import threading
import time
from audio_engine import QuoniamAudioEngine
import config
import random
import base64
import assets_library as assets
import os # v13.0 fix
import math # v13.3 fix for visualizer

def main(page: ft.Page):
    # --- CONFIGURATION ---
    page.title = "QUONIAM v1.20"

    # Lock to serialize all Flet .update() calls (prevents concurrent diff crash)
    _ui_lock = threading.Lock()

    def safe_update(*controls):
        """Thread-safe update: acquires lock before any Flet .update() call."""
        with _ui_lock:
            for c in controls:
                try:
                    c.update()
                except Exception:
                    pass

    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1200
    page.window.height = 800
    page.window.resizable = True
    page.window.frameless = True  # Frameless for modern look
    page.window.bgcolor = "#00000000"
    page.bgcolor = "#00000000"

    # --- SETTINGS (v1.20) ---
    config.load_settings_from_storage(page)
    if config.SETTINGS["fullscreen"]:
        page.window.full_screen = True

    # --- INITIALISATION AUDIO (Séquentielle) ---
    print("Lancement v1.20 Kaleidoscope & Particles...")
    # PALETTES DE COULEURS (v1.20 — deep, desaturated backgrounds for kaleidoscope contrast)
    COLORS_ACCUEIL  = ["#08060f", "#1a1535", "#12101e"]
    COLORS_ELEMENTS = ["#1a0505", "#2a0a0a", "#1f0808"]   # Deep ember
    COLORS_SAISONS  = ["#051208", "#0a1f0e", "#081a0b"]   # Deep forest
    COLORS_ATMOS    = ["#0d0520", "#160a30", "#110825"]   # Deep amethyst

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
                shadow=ft.BoxShadow(blur_radius=10*scale, color=color_start, offset=ft.Offset(0,0), blur_style=ft.BlurStyle.OUTER)
            )
        elif kind == "leaf": # Nature
            return ft.Container(
                width=size, height=size,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0,1), end=ft.Alignment(0,-1),
                    colors=[color_start, color_end]
                ),
                border_radius=ft.BorderRadius.only(top_left=size, bottom_right=size, top_right=0, bottom_left=0),
                shadow=ft.BoxShadow(blur_radius=10*scale, color=color_start, offset=ft.Offset(0,0), blur_style=ft.BlurStyle.OUTER)
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
                shadow=ft.BoxShadow(blur_radius=15*scale, color=color_start, offset=ft.Offset(0,0), blur_style=ft.BlurStyle.OUTER)
            )
        elif kind == "orb": # Abstract
            return ft.Container(
                width=size, height=size,
                gradient=ft.RadialGradient(
                    colors=[color_end, color_start],
                ),
                border_radius=size,
                border=ft.Border.all(2*scale, ft.Colors.with_opacity(0.5, "white")),
                shadow=ft.BoxShadow(blur_radius=15*scale, color=color_start, offset=ft.Offset(0,0), blur_style=ft.BlurStyle.OUTER)
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

    # Counter-rotation for inner icon (stays upright while outer spins)
    icon_counter_rotate = ft.Rotate(0, alignment=ft.Alignment(0, 0))
    icon_display_wrapper = ft.Container(
        content=icon_display,
        alignment=ft.Alignment(0, 0),
        rotate=icon_counter_rotate,
        animate_rotation=ft.Animation(1000, ft.AnimationCurve.LINEAR),
    )
    
    # L'AURA (GLOW)
    glow_shadow = ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        color=ft.Colors.with_opacity(0.5, "cyan"),
        offset=ft.Offset(0, 0),
        blur_style=ft.BlurStyle.OUTER 
    )

    icone_rotate = ft.Rotate(0, alignment=ft.Alignment(0, 0))

    container_icone = ft.Container(
        content=icon_display_wrapper,
        alignment=ft.Alignment(0, 0),
        scale=1.0,
        rotate=icone_rotate,
        shadow=glow_shadow,
        border_radius=100, 
        width=100,
        height=100,
        animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        animate_rotation=ft.Animation(1000, ft.AnimationCurve.LINEAR),
    )

    # --- KALEIDOSCOPE VISUALIZER v1.20 ---
    # Unified color palettes (6 colors per preset for layered blending)
    KALEIDOSCOPE_COLORS = {
        "home": ["#4dd0e1", "#00bcd4", "#0097a7", "#ffffff", "#b0bec5", "#cfd8dc"],
        "elements": {
            "feu":    ["#ff5722", "#ff9800", "#ffeb3b", "#ff6d00", "#e64a19", "#ffcc80"],
            "eau":    ["#00bcd4", "#0288d1", "#4dd0e1", "#80deea", "#006064", "#b2ebf2"],
            "terre":  ["#4caf50", "#2e7d32", "#81c784", "#a5d6a7", "#1b5e20", "#c8e6c9"],
            "air":    ["#b0bec5", "#cfd8dc", "#eceff1", "#ffffff", "#78909c", "#e0e0e0"],
            "espace": ["#311b92", "#673ab7", "#9575cd", "#b39ddb", "#4527a0", "#7e57c2"],
        },
        "saisons": {
            "hiver":     ["#81d4fa", "#b3e5fc", "#e1f5fe", "#ffffff", "#4fc3f7", "#039be5"],
            "printemps": ["#f48fb1", "#c5e1a5", "#e8f5e9", "#fce4ec", "#ce93d8", "#aed581"],
            "ete":       ["#ff9800", "#ffeb3b", "#fff9c4", "#ffe0b2", "#ffca28", "#f57f17"],
            "automne":   ["#a1887f", "#ff7043", "#d7ccc8", "#ffab91", "#795548", "#bcaaa4"],
            "vide":      ["#4a148c", "#7b1fa2", "#ce93d8", "#1a1a1a", "#ea80fc", "#6a1b9a"],
        },
        "atmos": {
            "zen":    ["#81c784", "#c8e6c9", "#a5d6a7", "#e8f5e9", "#4caf50", "#66bb6a"],
            "cyber":  ["#00e676", "#2979ff", "#00e5ff", "#76ff03", "#00c853", "#1de9b6"],
            "lofi":   ["#d7ccc8", "#795548", "#a1887f", "#bcaaa4", "#8d6e63", "#efebe9"],
            "jungle": ["#1b5e20", "#4caf50", "#388e3c", "#66bb6a", "#2e7d32", "#a5d6a7"],
            "indus":  ["#607d8b", "#ff5722", "#ff8a65", "#90a4ae", "#455a64", "#ffab91"],
        },
        "instruments": ["#FFD700", "#FFC107", "#FFE082", "#ffffff", "#FF9800", "#ffca28"],
    }

    # Theme config: (symmetry_arms, shape_types, normal_layers, focus_layers, rotation_speed, shape_scale)
    KALEIDOSCOPE_THEMES = {
        "feu":       (3,  ["teardrop", "arc"],          3, 6, 0.008, 1.2),
        "eau":       (6,  ["circle", "crescent"],       3, 7, 0.005, 1.0),
        "terre":     (4,  ["petal", "diamond"],          3, 6, 0.003, 1.1),
        "air":       (8,  ["circle", "arc"],             4, 8, 0.010, 0.9),
        "espace":    (5,  ["circle", "teardrop", "arc"], 4, 8, 0.012, 1.0),
        "hiver":     (6,  ["diamond", "circle"],         3, 7, 0.004, 1.0),
        "printemps": (5,  ["petal", "circle"],           4, 7, 0.006, 1.0),
        "ete":       (4,  ["circle", "arc"],             3, 6, 0.007, 1.1),
        "automne":   (4,  ["petal", "teardrop"],         3, 6, 0.005, 1.0),
        "vide":      (7,  ["arc", "circle", "diamond"],  4, 8, 0.015, 0.8),
        "zen":       (12, ["petal", "circle"],           4, 8, 0.002, 1.0),
        "cyber":     (8,  ["diamond", "arc"],            4, 8, 0.020, 0.9),
        "lofi":      (6,  ["circle", "petal"],           3, 6, 0.003, 1.0),
        "jungle":    (5,  ["petal", "teardrop"],         3, 7, 0.004, 1.1),
        "indus":     (8,  ["diamond", "arc"],            4, 8, 0.018, 0.9),
        "_default":  (8,  ["circle", "petal"],           3, 6, 0.005, 1.0),
    }

    class KaleidoscopeEngine:
        """Generates cv.Canvas shapes for a radially-symmetric kaleidoscope visualizer."""

        def __init__(self):
            self.width = 1200
            self.height = 800
            self.cx = 600.0
            self.cy = 400.0
            self.global_angle = 0.0
            self.layers = []
            self._last_theme = None
            self._last_preset = None
            self._symmetry = 8
            self._shape_types = ["circle", "petal"]
            self._palette = KALEIDOSCOPE_COLORS["home"]
            self._normal_layers = 3
            self._focus_layers = 6
            self._rotation_speed = 0.005
            self._shape_scale = 1.0

        def resize(self, width, height):
            self.width = max(width, 100)
            self.height = max(height, 100)
            self.cx = self.width / 2.0
            self.cy = self.height / 2.0
            self._rebuild_layers()

        def _resolve_config(self):
            coll = config.ETAT.get("collection")
            preset = config.ETAT.get("preset")
            theme = coll if coll in ("elements", "saisons", "atmos", "instruments") else "home"

            if theme == self._last_theme and preset == self._last_preset:
                return
            self._last_theme = theme
            self._last_preset = preset

            entry = KALEIDOSCOPE_COLORS.get(theme, KALEIDOSCOPE_COLORS["home"])
            if isinstance(entry, dict):
                self._palette = entry.get(preset, list(entry.values())[0] if entry else KALEIDOSCOPE_COLORS["home"])
            else:
                self._palette = entry

            key = preset if preset in KALEIDOSCOPE_THEMES else "_default"
            params = KALEIDOSCOPE_THEMES[key]
            self._symmetry = params[0]
            self._shape_types = params[1]
            self._normal_layers = params[2]
            self._focus_layers = params[3]
            self._rotation_speed = params[4]
            self._shape_scale = params[5]
            self._rebuild_layers()

        def _rebuild_layers(self):
            max_layers = self._focus_layers
            self.layers = []
            max_radius = min(self.width, self.height) * 0.42
            for i in range(max_layers):
                t = i / max(max_layers - 1, 1)
                self.layers.append({
                    "radius": 30 + t * (max_radius - 30),
                    "angle_offset": i * (math.pi / max_layers) * 0.3,
                    "shape_type": self._shape_types[i % len(self._shape_types)],
                    "color_idx": i % len(self._palette),
                    "rotation_dir": 1 if i % 2 == 0 else -1,
                    "phase_offset": i * 0.4,
                })

        def _make_paint(self, color, opacity, style=None, stroke_width=None):
            if style is None:
                style = ft.PaintingStyle.FILL
            p = ft.Paint(
                color=ft.Colors.with_opacity(min(1.0, max(0.02, opacity)), color),
                style=style,
                anti_alias=True,
            )
            if stroke_width is not None:
                p.stroke_width = stroke_width
            return p

        # --- Shape generators ---
        def _shape_circle(self, cx, cy, r, color, opacity):
            return cv.Circle(cx, cy, max(1, r), paint=self._make_paint(color, opacity))

        def _shape_petal(self, cx, cy, size, angle, color, opacity):
            s = max(size, 2)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            tip_x = cx + cos_a * s * 2
            tip_y = cy + sin_a * s * 2
            perp_cos = math.cos(angle + math.pi / 2)
            perp_sin = math.sin(angle + math.pi / 2)
            cp_dist = s * 0.8
            mid_dist = s * 1.0
            return cv.Path(
                elements=[
                    cv.Path.MoveTo(cx, cy),
                    cv.Path.CubicTo(
                        cx + cos_a * mid_dist + perp_cos * cp_dist,
                        cy + sin_a * mid_dist + perp_sin * cp_dist,
                        tip_x + perp_cos * cp_dist * 0.3,
                        tip_y + perp_sin * cp_dist * 0.3,
                        tip_x, tip_y
                    ),
                    cv.Path.CubicTo(
                        tip_x - perp_cos * cp_dist * 0.3,
                        tip_y - perp_sin * cp_dist * 0.3,
                        cx + cos_a * mid_dist - perp_cos * cp_dist,
                        cy + sin_a * mid_dist - perp_sin * cp_dist,
                        cx, cy
                    ),
                    cv.Path.Close(),
                ],
                paint=self._make_paint(color, opacity)
            )

        def _shape_teardrop(self, cx, cy, size, angle, color, opacity):
            s = max(size, 2)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            tip_x = cx + cos_a * s * 2.5
            tip_y = cy + sin_a * s * 2.5
            perp_cos = math.cos(angle + math.pi / 2)
            perp_sin = math.sin(angle + math.pi / 2)
            bulge = s * 0.6
            base_x = cx - cos_a * s * 0.3
            base_y = cy - sin_a * s * 0.3
            return cv.Path(
                elements=[
                    cv.Path.MoveTo(tip_x, tip_y),
                    cv.Path.QuadraticTo(
                        cx + perp_cos * bulge, cy + perp_sin * bulge,
                        base_x, base_y, 1.0
                    ),
                    cv.Path.QuadraticTo(
                        cx - perp_cos * bulge, cy - perp_sin * bulge,
                        tip_x, tip_y, 1.0
                    ),
                    cv.Path.Close(),
                ],
                paint=self._make_paint(color, opacity)
            )

        def _shape_diamond(self, cx, cy, size, angle, color, opacity):
            s = max(size, 2)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            perp_cos = math.cos(angle + math.pi / 2)
            perp_sin = math.sin(angle + math.pi / 2)
            return cv.Path(
                elements=[
                    cv.Path.MoveTo(cx + cos_a * s * 1.5, cy + sin_a * s * 1.5),
                    cv.Path.LineTo(cx + perp_cos * s * 0.6, cy + perp_sin * s * 0.6),
                    cv.Path.LineTo(cx - cos_a * s * 1.5, cy - sin_a * s * 1.5),
                    cv.Path.LineTo(cx - perp_cos * s * 0.6, cy - perp_sin * s * 0.6),
                    cv.Path.Close(),
                ],
                paint=self._make_paint(color, opacity)
            )

        def _shape_arc(self, cx, cy, size, angle, color, opacity):
            s = max(size * 1.5, 3)
            return cv.Arc(
                cx - s, cy - s, s * 2, s * 2,
                start_angle=angle,
                sweep_angle=math.pi / max(self._symmetry, 1),
                use_center=False,
                paint=self._make_paint(color, opacity, ft.PaintingStyle.STROKE,
                                       stroke_width=max(1, size * 0.15))
            )

        def _shape_crescent(self, cx, cy, size, angle, color, opacity):
            s = max(size, 2)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            offset_d = s * 0.3
            return cv.Path(
                elements=[
                    cv.Path.MoveTo(cx, cy - s),
                    cv.Path.ArcTo(cx, cy + s, s, 0, True, True),
                    cv.Path.ArcTo(cx + cos_a * offset_d, cy - s + sin_a * offset_d,
                                  s * 0.7, 0, False, False),
                    cv.Path.Close(),
                ],
                paint=self._make_paint(color, opacity)
            )

        def _make_shape(self, shape_type, cx, cy, radius, angle, color, opacity, scale):
            size = radius * 0.18 * scale
            # Low quality: replace complex path shapes with simple circles
            quality = config.SETTINGS.get("visual_quality", "high")
            if quality == "low" and shape_type not in ("circle", "diamond"):
                shape_type = "circle"
            if shape_type == "circle":
                return self._shape_circle(cx, cy, size, color, opacity)
            elif shape_type == "petal":
                return self._shape_petal(cx, cy, size, angle, color, opacity)
            elif shape_type == "teardrop":
                return self._shape_teardrop(cx, cy, size, angle, color, opacity)
            elif shape_type == "diamond":
                return self._shape_diamond(cx, cy, size, angle, color, opacity)
            elif shape_type == "arc":
                return self._shape_arc(cx, cy, size, angle, color, opacity)
            elif shape_type == "crescent":
                return self._shape_crescent(cx, cy, size, angle, color, opacity)
            return None

        def generate_frame(self, is_focus):
            self._resolve_config()
            if not self.layers:
                return []

            t = time.time()
            bpm = config.ETAT.get("bpm", 120)
            intensity = config.ETAT.get("intensite", 30)
            vitesse = config.ETAT.get("vitesse", 50)
            quality = config.SETTINGS.get("visual_quality", "high")

            bpm_factor = bpm / 60.0
            breath = math.sin(t * bpm_factor * math.pi)
            intensity_mult = 0.5 + (intensity / 100.0)
            speed_mult = 0.3 + (vitesse / 100.0) * 1.7

            self.global_angle += self._rotation_speed * speed_mult

            visible_count = self._focus_layers if is_focus else self._normal_layers
            # Quality: low reduces layers, high keeps all
            if quality == "low":
                visible_count = max(2, visible_count // 2)
            base_opacity = 0.22 if is_focus else 0.10
            max_opacity = 0.42 if is_focus else 0.22

            shapes = []
            arm_angle = 2 * math.pi / max(self._symmetry, 1)

            for li, layer in enumerate(self.layers):
                if li >= visible_count:
                    break

                layer_speed = (0.3 + li * 0.15) * speed_mult
                layer_angle = (self.global_angle * layer["rotation_dir"] * layer_speed
                               + layer["angle_offset"])

                pulse_factor = 0.06 + (li / max(len(self.layers), 1)) * 0.10
                scale = (1.0 + abs(breath) * pulse_factor * intensity_mult) * self._shape_scale

                radius = layer["radius"] * scale
                color = self._palette[layer["color_idx"] % len(self._palette)]

                layer_t = li / max(visible_count - 1, 1)
                opacity = base_opacity + layer_t * (max_opacity - base_opacity)
                opacity += abs(breath) * 0.08
                opacity = min(1.0, max(0.02, opacity))

                for arm in range(self._symmetry):
                    angle = layer_angle + arm * arm_angle
                    sx = self.cx + math.cos(angle) * radius * 0.5
                    sy = self.cy + math.sin(angle) * radius * 0.5

                    shape = self._make_shape(
                        layer["shape_type"], sx, sy, radius, angle,
                        color, opacity, scale
                    )
                    if shape:
                        shapes.append(shape)

            return shapes

    # ═══════════════════════════════════════════════════════════
    #  PARTICLE SYSTEM v1.20
    # ═══════════════════════════════════════════════════════════

    class ParticleSystem:
        """
        Ambient particle system synced with KaleidoscopeEngine.
        Particles drift upward with sinusoidal wobble, fade in/out,
        and use the current kaleidoscope palette colors.
        """

        def __init__(self, engine: KaleidoscopeEngine):
            self.engine = engine
            self.particles: list[dict] = []
            self.max_particles = 22
            self.spawn_rate = 0.35  # seconds between spawns
            self._last_spawn = 0.0
            self._shapes = ["circle", "diamond", "star", "dot"]

        def _spawn_particle(self, t: float) -> dict:
            """Create a new particle with randomized properties."""
            palette = self.engine._palette
            color = random.choice(palette) if palette else "#ffffff"
            # Low quality: only simple shapes; high: all shapes
            quality = config.SETTINGS.get("visual_quality", "high")
            if quality == "low":
                shape = random.choice(["circle", "dot"])
            else:
                shape = random.choice(self._shapes)
            size = random.uniform(2.0, 6.0)
            lifespan = random.uniform(3.0, 5.5)

            # Spawn zone: bottom 40% of canvas, spread horizontally
            w, h = self.engine.width, self.engine.height
            x = random.uniform(w * 0.1, w * 0.9)
            y = random.uniform(h * 0.55, h * 0.95)

            return {
                "x": x, "y": y,
                "vx": random.uniform(-8, 8),       # horizontal drift speed
                "vy": random.uniform(-25, -12),     # upward speed (negative = up)
                "size": size,
                "color": color,
                "shape": shape,
                "born": t,
                "lifespan": lifespan,
                "wobble_freq": random.uniform(1.5, 3.5),   # Hz
                "wobble_amp": random.uniform(8, 25),        # px
                "phase": random.uniform(0, 2 * math.pi),
                "rotation": random.uniform(0, 2 * math.pi),
                "rot_speed": random.uniform(-0.8, 0.8),
            }

        def _particle_opacity(self, age: float, lifespan: float) -> float:
            """Fade in (15%) → full → fade out (25%)."""
            if age < 0:
                return 0.0
            ratio = age / lifespan
            if ratio < 0.15:
                return ratio / 0.15  # Fade in
            elif ratio > 0.75:
                return max(0.0, (1.0 - ratio) / 0.25)  # Fade out
            return 1.0

        def _render_circle(self, x, y, size, color, opacity):
            paint = ft.Paint(
                color=ft.Colors.with_opacity(min(0.7, opacity * 0.6), color),
                style=ft.PaintingStyle.FILL,
                anti_alias=True,
            )
            return cv.Circle(x, y, max(1, size), paint=paint)

        def _render_diamond(self, x, y, size, angle, color, opacity):
            s = max(size, 1.5)
            ca, sa = math.cos(angle), math.sin(angle)
            pa, pb = math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)
            paint = ft.Paint(
                color=ft.Colors.with_opacity(min(0.65, opacity * 0.55), color),
                style=ft.PaintingStyle.FILL,
                anti_alias=True,
            )
            return cv.Path(
                elements=[
                    cv.Path.MoveTo(x + ca * s * 1.8, y + sa * s * 1.8),
                    cv.Path.LineTo(x + pa * s * 0.7, y + pb * s * 0.7),
                    cv.Path.LineTo(x - ca * s * 1.8, y - sa * s * 1.8),
                    cv.Path.LineTo(x - pa * s * 0.7, y - pb * s * 0.7),
                    cv.Path.Close(),
                ],
                paint=paint,
            )

        def _render_star(self, x, y, size, angle, color, opacity):
            """4-pointed star."""
            s = max(size, 1.5)
            paint = ft.Paint(
                color=ft.Colors.with_opacity(min(0.6, opacity * 0.5), color),
                style=ft.PaintingStyle.FILL,
                anti_alias=True,
            )
            points = []
            for i in range(8):
                a = angle + i * (math.pi / 4)
                r = s * 1.6 if i % 2 == 0 else s * 0.5
                points.append((x + math.cos(a) * r, y + math.sin(a) * r))
            elements = [cv.Path.MoveTo(points[0][0], points[0][1])]
            for px, py in points[1:]:
                elements.append(cv.Path.LineTo(px, py))
            elements.append(cv.Path.Close())
            return cv.Path(elements=elements, paint=paint)

        def _render_dot(self, x, y, size, color, opacity):
            """Tiny bright dot — like a distant sparkle."""
            paint = ft.Paint(
                color=ft.Colors.with_opacity(min(0.85, opacity * 0.75), color),
                style=ft.PaintingStyle.FILL,
                anti_alias=True,
            )
            return cv.Circle(x, y, max(0.8, size * 0.4), paint=paint)

        def generate_particles(self) -> list:
            """Update particles and return cv shapes."""
            t = time.time()
            intensity = config.ETAT.get("intensite", 30)
            bpm = config.ETAT.get("bpm", 120)
            quality = config.SETTINGS.get("visual_quality", "high")

            # Adaptive max particles: more when intensity is high
            base_particles = int(15 + (intensity / 100.0) * 12)
            if quality == "low":
                self.max_particles = base_particles // 2
            elif quality == "high":
                self.max_particles = int(base_particles * 1.3)
            else:
                self.max_particles = base_particles

            # Spawn new particles
            if t - self._last_spawn > self.spawn_rate and len(self.particles) < self.max_particles:
                self.particles.append(self._spawn_particle(t))
                self._last_spawn = t
                # Occasionally spawn 2 at once for variety
                if random.random() < 0.3 and len(self.particles) < self.max_particles:
                    self.particles.append(self._spawn_particle(t))

            # BPM-synced pulse: particles subtly breathe
            bpm_pulse = 0.5 + 0.5 * math.sin(t * (bpm / 60.0) * math.pi)

            # Update and render
            shapes = []
            alive = []
            for p in self.particles:
                age = t - p["born"]
                if age > p["lifespan"]:
                    continue  # Dead particle

                alive.append(p)
                opacity = self._particle_opacity(age, p["lifespan"])
                if opacity <= 0.02:
                    continue

                # Position update: drift + sinusoidal wobble
                dt = age
                wobble_x = math.sin(dt * p["wobble_freq"] + p["phase"]) * p["wobble_amp"]
                x = p["x"] + p["vx"] * dt + wobble_x
                y = p["y"] + p["vy"] * dt

                # Size pulsation synced with BPM
                size = p["size"] * (0.85 + bpm_pulse * 0.3)

                angle = p["rotation"] + p["rot_speed"] * dt

                # Render based on shape
                shape_type = p["shape"]
                if shape_type == "circle":
                    shapes.append(self._render_circle(x, y, size, p["color"], opacity))
                elif shape_type == "diamond":
                    shapes.append(self._render_diamond(x, y, size, angle, p["color"], opacity))
                elif shape_type == "star":
                    shapes.append(self._render_star(x, y, size, angle, p["color"], opacity))
                elif shape_type == "dot":
                    shapes.append(self._render_dot(x, y, size, p["color"], opacity))

            self.particles = alive
            return shapes

    # --- KALEIDOSCOPE CANVAS ---
    kaleidoscope_engine = KaleidoscopeEngine()
    particle_system = ParticleSystem(kaleidoscope_engine)

    def on_canvas_resize(e: cv.CanvasResizeEvent):
        kaleidoscope_engine.resize(e.width, e.height)

    kaleidoscope_canvas = cv.Canvas(
        shapes=[],
        expand=True,
        on_resize=on_canvas_resize,
    )

    def animer_fond():
        while True:
            try:
                shapes = kaleidoscope_engine.generate_frame(focus_mode)
                # Overlay particles on top of kaleidoscope
                particles = particle_system.generate_particles()
                kaleidoscope_canvas.shapes = shapes + particles
                safe_update(kaleidoscope_canvas)
            except Exception:
                pass
            fps = config.SETTINGS.get("target_fps", 30)
            time.sleep(1.0 / max(fps, 1) if fps > 0 else 0.004)




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

    # --- UI COMPONENTS ---
    # ...
    
    lbl_vitesse = ft.Text("50%", size=12)
    lbl_intensite = ft.Text("30%", size=12)
    lbl_gravite = ft.Text("0", size=12)
    lbl_gravite = ft.Text("0", size=12)
    lbl_chaos = ft.Text("20%", size=12)
    lbl_bpm = ft.Text("120 BPM", size=14, weight=ft.FontWeight.BOLD) # v11.0: Global for Auto-Drift Sync
    switch_auto = ft.Switch(value=False, active_color="#00E5FF")
    
    btn_play_content = ft.Row(
        [get_ui_icon(assets.SVG_PLAY, color="white", size=18), ft.Text(config.T("play"), color="white", weight=ft.FontWeight.BOLD)],
        spacing=8, alignment=ft.MainAxisAlignment.CENTER
    )
    btn_play_container = ft.Container(
        content=btn_play_content, padding=15, border_radius=30,
        alignment=ft.Alignment(0, 0), width=200, ink=True,
        # Liquid Glass Style
        bgcolor=ft.Colors.with_opacity(0.15, "white"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
        blur=ft.Blur(15, 15),
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=-5, color=ft.Colors.with_opacity(0.3, "#56ab2f")),
    )

    # v1.20: Recording controls
    recording_active = [False]  # mutable for closure access
    btn_record_content = get_ui_icon(assets.SVG_RECORD, color="#ff4444", size=16)
    btn_record_container = ft.Container(
        content=btn_record_content, width=50, height=50, border_radius=25,
        alignment=ft.Alignment(0, 0), ink=True, tooltip=config.T("record"),
        bgcolor=ft.Colors.with_opacity(0.15, "white"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
        blur=ft.Blur(10, 10),
    )
    recording_timer_text = ft.Text("00:00", size=11, color="#ff4444", visible=False, weight=ft.FontWeight.BOLD)
    recording_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor="#ff4444", visible=False)

    container_presets = ft.Container()
    
    # WRAPPER PRINCIPAL (STACK)
    # Layer 0: Gradient Background
    bg_grad = ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=COLORS_ACCUEIL)
    bg_gradient = ft.Container(
        gradient=bg_grad,
        expand=True,
        animate=ft.Animation(2000, ft.AnimationCurve.EASE_OUT_CUBIC)
    )
    
    # Layer 1: Kaleidoscope Canvas (kaleidoscope_canvas)
    # Layer 2: Main Content (content_layer)
    
    # TITLE BAR REMOVED PER USER REQUEST
    # The application will remain frameless but without custom controls for now.

    content_layer = ft.Container(
        expand=True,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
    )

    # --- FOCUS MODE (v1.20 — Kaleidoscope & Particles) ---
    focus_mode = False

    def toggle_focus(e):
        nonlocal focus_mode
        focus_mode = not focus_mode
        if focus_mode:
            content_layer.opacity = 0
            focus_exit_hint.visible = True
            focus_exit_hint.opacity = 1
        else:
            content_layer.opacity = 1
            focus_exit_hint.opacity = 0
            focus_exit_hint.visible = False
        safe_update(page)

    focus_exit_hint = ft.Container(
        content=ft.Row([
            get_ui_icon(assets.SVG_EYE, color="#88ffffff", size=14),
            ft.Text(config.T("exit_focus"), size=10, weight=ft.FontWeight.BOLD,
                     color="#88ffffff")
        ], spacing=5),
        on_click=toggle_focus,
        bottom=20, right=20,
        padding=ft.Padding(left=12, top=8, right=12, bottom=8),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.3, "black"),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
        visible=False,
        opacity=0,
        animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        ink=True,
    )

    main_layout_stack = ft.Stack(
        [
            bg_gradient,
            kaleidoscope_canvas,   # v1.20 Canvas kaleidoscope + particles
            content_layer,
            focus_exit_hint,
        ],
        expand=True
    )

    # HELPER NEON
    def creer_separateur_neon(couleur="#00E5FF"):
        return ft.Container(
            width=120, height=2, bgcolor="#e0ffffff", border_radius=10,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=couleur, blur_style=ft.BlurStyle.OUTER),
            margin=ft.Margin(left=0, top=15, right=0, bottom=15)
        )

    # --- HEADER ---
    def creer_header():
        return ft.Column([
            ft.Text(config.T("quoniam_header"), size=30, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Text(config.T("fluid_dynamics"), size=10, weight=ft.FontWeight.W_300, color="#88ffffff"),
                margin=ft.Margin(left=0, top=5, right=0, bottom=0)
            ),
            creer_separateur_neon("#00E5FF")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

    # --- BOUCLE D'ANIMATION ---
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
                    bpm = config.ETAT.get("bpm", 60)
                    intensite = config.ETAT.get("intensite", 50)
                    
                    # Unified Breathing Logic (Sine Wave)
                    # Smooth, continuous expansion/contraction linked to BPM
                    t = time.time()
                    cycle = math.sin(t * (bpm / 60.0) * math.pi) # -1 to 1
                    
                    # Convert sine to 0-1 scale range
                    # Base scale 1.0, max scale depends on intensity
                    max_growth = 0.2 + (intensite / 200.0) # 0.2 to 0.7 extra
                    current_scale = 1.0 + (max_growth * abs(cycle))
                    
                    container_icone.scale = current_scale

                    # Aura Pulse (Sync with cycle) — disabled on low quality
                    quality = config.SETTINGS.get("visual_quality", "high")
                    if quality == "low":
                        glow_shadow.spread_radius = 0
                        glow_shadow.color = ft.Colors.with_opacity(0, "white")
                    else:
                        glow_shadow.spread_radius = 5 + (intensite/5) * abs(cycle)
                        glow_shadow.color = ft.Colors.with_opacity(0.3 + (abs(cycle)*0.3), "white")

                    # Spin for Space Themes (with counter-rotation for inner icon)
                    if config.ETAT.get("preset") in ["espace", "vide", "cyber", "indus"]:
                        angle += 1.0
                        icone_rotate.angle = angle
                        icon_counter_rotate.angle = -angle  # Counter-rotate inner icon
                    else:
                        # Reset rotation when leaving space themes
                        if angle != 0:
                            angle = 0
                            icone_rotate.angle = 0
                            icon_counter_rotate.angle = 0

                    safe_update(container_icone)

                    fps = config.SETTINGS.get("target_fps", 30)
                    time.sleep(1.0 / max(fps, 1) if fps > 0 else 0.004)
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
            btn_play_content.controls = [
                get_ui_icon(assets.SVG_PAUSE, color="white", size=18),
                ft.Text(config.T("pause"), color="white", weight=ft.FontWeight.BOLD)
            ]
            btn_play_container.shadow = ft.BoxShadow(blur_radius=20, spread_radius=-5, color=ft.Colors.with_opacity(0.4, "#ff416c"))
        else:
            btn_play_content.controls = [
                get_ui_icon(assets.SVG_PLAY, color="white", size=18),
                ft.Text(config.T("play"), color="white", weight=ft.FontWeight.BOLD)
            ]
            btn_play_container.shadow = ft.BoxShadow(blur_radius=20, spread_radius=-5, color=ft.Colors.with_opacity(0.3, "#56ab2f"))
            
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
                             c.shadow = ft.BoxShadow(blur_radius=10, color="#FF9800" if is_active else ft.Colors.TRANSPARENT)
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
                         elif isinstance(c, (ft.Row, ft.Column)):
                             update_recursive(c.controls)
                         # Recurse if control is Container with content being a Row/Column
                         elif isinstance(c, ft.Container) and isinstance(c.content, (ft.Row, ft.Column)):
                             update_recursive(c.content.controls)
                 
                 # Need a reference list of valid instruments to check data against
                 # We can reconstruct it or import it. For now, let's hardcode the keys or assume any short string data is one?
                 # Better: re-use the mapping keys from get_asset logic if possible, or just checking if data is not None
                 # Let's simple check if data is not None and matches our known keys
                 instruments_mapping = [
                     "violon", "alto", "violoncelle", "contrebasse", "guitare", "basse", "harpe", "pizzicato",
                     "flute", "piccolo", "clarinette", "hautbois", "basson", "trompette", "cor", "cuivres",
                     "piano", "orgue", "clavecin", "accordeon",
                     "timbales", "batterie", "xylophone", "glockenspiel",
                     "choir", "voice", "celesta", "bells"
                 ]
                 
                 update_recursive(main_col.controls)
                 
             except Exception as e:
                 # print(f"UI Update Error: {e}")
                 pass

        safe_update(page)

    def changer_valeur(e, cle):
        config.ETAT[cle] = e.control.value
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

    # --- i18n HOT-RELOAD SYSTEM (v1.20) ---
    _i18n_refs: list[tuple[ft.Text, str]] = []

    def tr(key, **kwargs):
        """Create a ft.Text with translated value and register for hot-reload."""
        txt = ft.Text(config.T(key), **kwargs)
        _i18n_refs.append((txt, key))
        return txt

    def update_language_ui():
        """Hot-reload: update all registered text controls + rebuild current view."""
        # 1. Update registered i18n refs (settings dialog texts)
        stale = []
        for i, (txt, key) in enumerate(_i18n_refs):
            try:
                txt.value = config.T(key)
            except Exception:
                stale.append(i)
        for i in reversed(stale):
            _i18n_refs.pop(i)

        # 2. Update persistent widgets (focus hint, record tooltip)
        try:
            focus_exit_hint.content.controls[1].value = config.T("exit_focus")
            btn_record_container.tooltip = config.T("stop_recording") if recording_active[0] else config.T("record")
        except Exception:
            pass

        # 3. Rebuild the current view so all config.T() calls pick up new language
        try:
            coll = config.ETAT.get("collection")
            if coll is None:
                content_layer.content = creer_contenu_accueil()
            else:
                # Rebuild preset buttons for current collection
                if coll == "elements":
                    container_presets.content = creer_boutons_elements()
                elif coll == "saisons":
                    container_presets.content = creer_boutons_saisons()
                elif coll == "instruments":
                    container_presets.content = creer_boutons_instruments()
                else:
                    container_presets.content = creer_boutons_atmos()
                content_layer.content = creer_contenu_controle()
        except Exception:
            pass

        # 4. Update play/pause button text
        update_ui()

        try:
            safe_update(page)
        except Exception:
            pass

    # v1.20: Recording toggle
    def toggle_recording(e):
        if not recording_active[0]:
            # Start recording
            global_audio.start_recording()
            recording_active[0] = True
            btn_record_container.content = get_ui_icon(assets.SVG_STOP, color="white", size=16)
            btn_record_container.bgcolor = "#ff4444"
            btn_record_container.border = ft.Border.all(2, "#ff4444")
            btn_record_container.tooltip = config.T("stop_recording")
            recording_timer_text.visible = True
            recording_dot.visible = True
            safe_update(btn_record_container, recording_timer_text, recording_dot)

            def update_timer():
                while recording_active[0]:
                    elapsed = global_audio.get_recording_duration()
                    mins = int(elapsed // 60)
                    secs = int(elapsed % 60)
                    recording_timer_text.value = f"{mins:02d}:{secs:02d}"
                    recording_timer_text.color = "#ff4444" if int(elapsed) % 2 == 0 else "#ff8888"
                    try:
                        safe_update(recording_timer_text)
                    except Exception:
                        pass
                    time.sleep(0.5)

            threading.Thread(target=update_timer, daemon=True).start()
        else:
            # Stop recording
            export_dir = config.SETTINGS.get("export_folder", "./recordings")
            saved_path = global_audio.stop_recording(output_dir=export_dir)
            recording_active[0] = False

            btn_record_container.content = get_ui_icon(assets.SVG_RECORD, color="#ff4444", size=16)
            btn_record_container.bgcolor = ft.Colors.with_opacity(0.15, "white")
            btn_record_container.border = ft.Border.all(1, ft.Colors.with_opacity(0.3, "white"))
            btn_record_container.tooltip = config.T("record")
            recording_timer_text.visible = False
            recording_timer_text.value = "00:00"
            recording_dot.visible = False
            safe_update(btn_record_container, recording_timer_text, recording_dot)

            if saved_path:
                snack = ft.SnackBar(
                    ft.Text(f"{config.T('recording_saved')}: {saved_path}", color="white"),
                    bgcolor="#4caf50", open=True
                )
                page.overlay.append(snack)
                safe_update(page)

    btn_record_container.on_click = toggle_recording

    # v1.20: Premium Settings Modal
    def open_settings_dialog(e):
        accent = config.SETTINGS.get("accent_color", "#00E5FF")

        def on_setting_change(key, value, callback=None):
            config.save_setting(page, key, value)
            if callback:
                callback(value)

        def apply_fullscreen(value):
            page.window.full_screen = value
            page.update()

        def apply_language(value):
            config.save_setting(page, "language", value)
            update_language_ui()

        def apply_accent(color):
            config.save_setting(page, "accent_color", color)
            nonlocal accent
            accent = color

        def apply_fps(fps_val):
            config.save_setting(page, "target_fps", int(fps_val))

        def confirm_reset():
            config.reset_all_settings(page)
            main_layout_stack.controls.pop()
            safe_update(page)
            snack = ft.SnackBar(ft.Text(config.T("settings_reset"), color="white"), bgcolor="#ff9800", open=True)
            page.overlay.append(snack)
            safe_update(page)

        def close_settings(e):
            main_layout_stack.controls.pop()
            safe_update(page)

        # --- Helper: section card ---
        def section_card(icon_svg, icon_color, title_key, gradient_colors, controls_list):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        get_ui_icon(icon_svg, color=icon_color, size=22),
                        ft.Text(config.T(title_key), size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ], spacing=10),
                    ft.Container(height=8),
                    ft.Column(controls_list, spacing=12),
                ]),
                padding=20,
                border_radius=20,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                    colors=gradient_colors,
                ),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
                blur=ft.Blur(15, 15),
            )

        def setting_row(label_key, control):
            return ft.Row([
                ft.Text(config.T(label_key), size=13, color="#ddffffff", expand=True),
                control,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # ========= VISUALS SECTION =========
        sw_fullscreen = ft.Switch(
            value=config.SETTINGS["fullscreen"], active_color=accent,
            on_change=lambda e: on_setting_change("fullscreen", e.control.value, apply_fullscreen)
        )
        sw_zen = ft.Switch(
            value=config.SETTINGS["zen_intro"], active_color=accent,
            on_change=lambda e: on_setting_change("zen_intro", e.control.value)
        )

        # Visual Quality as radio-style pills
        quality_val = [config.SETTINGS["visual_quality"]]
        def make_quality_pill(label_key, val, color):
            is_active = quality_val[0] == val
            c = ft.Container(
                content=ft.Text(config.T(label_key), size=11, color="white" if is_active else "#88ffffff",
                                weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL),
                padding=ft.Padding(left=14, top=6, right=14, bottom=6),
                border_radius=20,
                bgcolor=color if is_active else ft.Colors.with_opacity(0.1, "white"),
                border=ft.Border.all(1, color if is_active else "#33ffffff"),
                ink=True,
            )
            def on_pick(e, v=val):
                quality_val[0] = v
                on_setting_change("visual_quality", v)
                # Rebuild overlay
                main_layout_stack.controls.pop()
                safe_update(page)
                open_settings_dialog(None)
            c.on_click = on_pick
            return c

        quality_row = ft.Row([
            make_quality_pill("low", "low", "#ff9800"),
            make_quality_pill("medium", "medium", "#4caf50"),
            make_quality_pill("high", "high", "#2196f3"),
        ], spacing=8)

        # FPS Slider
        fps_map = {0: 30, 1: 60, 2: 120, 3: 0}
        fps_labels = {30: "30", 60: "60", 120: "120", 0: config.T("unlimited")}
        current_fps = config.SETTINGS.get("target_fps", 30)
        fps_idx = {30: 0, 60: 1, 120: 2, 0: 3}.get(current_fps, 0)
        fps_display = ft.Text(fps_labels.get(current_fps, "30"), size=13, color=accent, weight=ft.FontWeight.BOLD)

        def on_fps_change(e):
            idx = int(e.control.value)
            fps = fps_map.get(idx, 30)
            fps_display.value = fps_labels.get(fps, "30")
            apply_fps(fps)
            safe_update(fps_display)

        fps_slider = ft.Slider(
            min=0, max=3, divisions=3, value=fps_idx,
            active_color=accent, inactive_color="#33ffffff", thumb_color="white",
            on_change=on_fps_change, width=180,
        )

        visual_card = section_card(
            assets.SVG_EYE, "#64B5F6", "sec_visuals",
            [ft.Colors.with_opacity(0.15, "#1565C0"), ft.Colors.with_opacity(0.05, "#0D47A1")],
            [
                setting_row("fullscreen", sw_fullscreen),
                setting_row("zen_intro", sw_zen),
                ft.Row([ft.Text(config.T("visual_quality"), size=13, color="#ddffffff"), ft.Container(expand=True), quality_row]),
                ft.Row([ft.Text(config.T("target_fps"), size=13, color="#ddffffff"), ft.Container(expand=True), fps_display]),
                fps_slider,
            ]
        )

        # ========= APP & LOCALIZATION SECTION =========
        dd_language = ft.Dropdown(
            value=config.SETTINGS["language"],
            options=[
                ft.dropdown.Option("EN"),
                ft.dropdown.Option("FR"),
                ft.dropdown.Option("ES"),
                ft.dropdown.Option("AR"),
            ],
            width=100, height=42, text_size=13, color="white", border_color="#44ffffff",
            bgcolor=ft.Colors.with_opacity(0.2, "black"), border_radius=12,
        )
        def on_lang_select(e):
            apply_language(e.control.value)
            # Rebuild the dialog with new language
            main_layout_stack.controls.pop()
            safe_update(page)
            open_settings_dialog(None)
        dd_language.on_select = on_lang_select

        # Accent color picker
        accent_colors = ["#00E5FF", "#FF9800", "#E040FB", "#69F0AE", "#FF5252", "#FFD740"]
        def make_accent_dot(color):
            is_selected = config.SETTINGS.get("accent_color", "#00E5FF") == color
            return ft.Container(
                width=32, height=32, border_radius=16,
                bgcolor=color,
                border=ft.Border.all(3, "white" if is_selected else "transparent"),
                shadow=ft.BoxShadow(blur_radius=8, color=color) if is_selected else None,
                ink=True,
                on_click=lambda e, c=color: _pick_accent(c),
            )
        def _pick_accent(color):
            apply_accent(color)
            main_layout_stack.controls.pop()
            safe_update(page)
            open_settings_dialog(None)

        accent_row = ft.Row([make_accent_dot(c) for c in accent_colors], spacing=8)

        app_card = section_card(
            assets.SVG_TUNE, "#CE93D8", "sec_app",
            [ft.Colors.with_opacity(0.15, "#6A1B9A"), ft.Colors.with_opacity(0.05, "#4A148C")],
            [
                setting_row("language", dd_language),
                ft.Text(config.T("accent_color"), size=13, color="#ddffffff"),
                accent_row,
            ]
        )

        # ========= DATA SECTION =========
        txt_export = ft.Text(config.SETTINGS["export_folder"], size=12, color="#aaffffff", italic=True)
        btn_reset = ft.Container(
            content=ft.Row([
                ft.Text(config.T("reset_all"), size=12, color="#ff6b6b", weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            on_click=lambda e: confirm_reset(),
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=15,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "#ff6b6b")),
            bgcolor=ft.Colors.with_opacity(0.1, "#ff6b6b"),
            ink=True, width=200,
        )

        data_card = section_card(
            assets.SVG_ARROW_DOWN, "#A5D6A7", "sec_data",
            [ft.Colors.with_opacity(0.15, "#1B5E20"), ft.Colors.with_opacity(0.05, "#0D3B0F")],
            [
                setting_row("export_folder", txt_export),
                ft.Container(height=5),
                ft.Row([btn_reset], alignment=ft.MainAxisAlignment.CENTER),
            ]
        )

        # ========= FULL MODAL LAYOUT =========
        settings_body = ft.Column([
            ft.Row([
                # Left column: Visuals
                ft.Column([visual_card], expand=True),
                ft.Container(width=15),
                # Right column: App + Data
                ft.Column([app_card, ft.Container(height=15), data_card], expand=True),
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START),
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        # Header bar
        header_row = ft.Row([
            get_ui_icon(assets.SVG_SETTINGS, color="white", size=24),
            ft.Container(width=8),
            ft.Text(config.T("settings"), size=22, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Text(config.T("close"), size=13, color="#aaffffff", weight=ft.FontWeight.BOLD),
                on_click=close_settings,
                padding=ft.Padding(left=20, top=8, right=20, bottom=8),
                border_radius=20,
                bgcolor=ft.Colors.with_opacity(0.15, "white"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
                ink=True,
            ),
        ], alignment=ft.MainAxisAlignment.START)

        dialog_container = ft.Container(
            content=ft.Column([
                header_row,
                ft.Container(height=15),
                settings_body,
            ], expand=True),
            width=900,
            height=600,
            bgcolor=ft.Colors.with_opacity(0.85, "#111118"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.25, "white")),
            border_radius=25,
            padding=30,
            blur=ft.Blur(20, 20),
            shadow=ft.BoxShadow(blur_radius=40, spread_radius=-5, color=ft.Colors.with_opacity(0.5, "black")),
        )

        overlay = ft.Container(
            content=dialog_container,
            bgcolor=ft.Colors.with_opacity(0.7, "black"),
            alignment=ft.Alignment(0, 0),
            expand=True,
            on_click=close_settings,
        )

        main_layout_stack.controls.append(overlay)
        safe_update(page)

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
                    btn_play_container.gradient = ft.LinearGradient(colors=["#56ab2f", "#a8e063"])
                    safe_update(page)

                    snack = ft.SnackBar(ft.Text(f"{config.T('zen_finished')} ({minutes} min)", color="white"), bgcolor="#4caf50", open=True)
                    page.overlay.append(snack)
                    safe_update(page)
                except: pass
                
        threading.Thread(target=timer_thread, daemon=True).start()

    def update_central_icon_for_preset(preset_code):
        if preset_code not in PRESET_THEMES: return
        kind, c1, c2 = PRESET_THEMES[preset_code]
        container_icone.content = LiquidIcon(kind, c1, c2, scale=1.0)
        # Also update particles color if needed (optional, handled by update_ui loop mostly)
        safe_update(container_icone)

    def charger_interface_controle(nom_collection):
        config.ETAT["collection"] = nom_collection
        
        if nom_collection == "elements":
            config.ETAT["preset"] = "feu" # Changed to Fire as default for Red theme
            presets_controls = creer_boutons_elements()
            bg_grad.colors = COLORS_ELEMENTS
            glow_shadow.color = ft.Colors.with_opacity(0.5, "red") 
            container_icone.content = LiquidIcon("droplet", "#b71c1c", "#f44336", scale=1.0) # Reset to Fire/Droplet
            
        elif nom_collection == "saisons":
            config.ETAT["preset"] = "terre" # Changed to Earth as default for Green theme
            presets_controls = creer_boutons_saisons()
            bg_grad.colors = COLORS_SAISONS
            glow_shadow.color = ft.Colors.with_opacity(0.5, "green") 
            container_icone.content = LiquidIcon("leaf", "#1b5e20", "#4caf50", scale=1.0) # Reset to Leaf
            
        elif nom_collection == "instruments":
            config.ETAT["mode_orchestre"] = True
            config.ETAT["preset"] = None # No single preset
            if "instruments_actifs" not in config.ETAT: config.ETAT["instruments_actifs"] = []
            
            presets_controls = creer_boutons_instruments()
            bg_grad.colors = ["#120d08", "#1f1610", "#1a130d"]  # Deep bronze
            glow_shadow.color = ft.Colors.with_opacity(0.5, "orange") 
            container_icone.content = LiquidIcon("note", "#ff9800", "#ffca28", scale=1.0) # New Note Icon
            
        else:
            config.ETAT["preset"] = "zen"
            presets_controls = creer_boutons_atmos()
            bg_grad.colors = COLORS_ATMOS
            glow_shadow.color = ft.Colors.with_opacity(0.5, "purple") 
            container_icone.content = LiquidIcon("orb", "#4a148c", "#9c27b0", scale=1.0) # Reset to Orb 
            
        container_presets.content = presets_controls

        content_layer.content = creer_contenu_controle()
        safe_update(page)
        
        config.ETAT["actif"] = True 
        update_ui()

    def retour_accueil(e):
        config.ETAT["collection"] = None
        config.ETAT["actif"] = False
        config.ETAT["mode_orchestre"] = False # Disable Orchestra mode

        bg_grad.colors = COLORS_ACCUEIL
        content_layer.content = creer_contenu_accueil()
        safe_update(page)



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
                    ft.Text(titre, weight=ft.FontWeight.BOLD, size=16, color="white", text_align=ft.TextAlign.CENTER),
                    ft.Text(sous_titre, size=11, color=ft.Colors.with_opacity(0.7, "white"), text_align=ft.TextAlign.CENTER)
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
        
        # v13.4: Hero Card for Orchestra
        hero_carte = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=LiquidIcon("note", "#FF9800", "#FFD700", scale=1.8), # Extra Large Icon
                    padding=10
                ),
                ft.Column([
                    ft.Text(config.T("orchestra"), weight=ft.FontWeight.BOLD, size=24, color="white"), # Larger Title
                    ft.Text(config.T("orchestra_sub"), size=12, color=ft.Colors.with_opacity(0.8, "white")) # Slightly smaller text to fit
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5), # Better spacing
                ft.Container(expand=True),
                get_ui_icon(assets.SVG_ARROW_RIGHT, color="white", size=18),
                ft.Container(width=5)
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER), # Added vertical alignment
            width=360, height=140, # increased width (340->360)
            border_radius=20,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=[ft.Colors.with_opacity(0.8, "#3e2723"), ft.Colors.with_opacity(0.8, "#5d4037")]
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.4, "#FFD700")), # Gold Border
            shadow=ft.BoxShadow(blur_radius=20, color="#FF9800", offset=ft.Offset(0, 5)),
            padding=15,
            ink=True,
            on_click=lambda _: charger_interface_controle("instruments")
        )

        # Liste explicite pour éviter tout élément fantôme
        liste_cartes_ambiance: list[ft.Control] = [
            carte("droplet", config.T("elements"), config.T("elements_sub"), "elements", "cyan", "blue", "cyan"),
            carte("leaf", config.T("seasons"), config.T("seasons_sub"), "saisons", "green", "green", "yellow"),
            carte("orb", config.T("atmos"), config.T("atmos_sub"), "atmos", "purple", "purple", "pink"),
        ]
        def quitter_app(e):
            """Cleanly shut down audio engine and close the app."""
            try:
                config.ETAT["actif"] = False
                audio_engine.stop()
            except Exception:
                pass
            page.window.close()
            os._exit(0)

        btn_quit = ft.Container(
            content=ft.Row([
                get_ui_icon(assets.SVG_POWER, color="#ff6b6b", size=16),
                ft.Text(config.T("quit"), size=12, weight=ft.FontWeight.BOLD, color="#ff6b6b")
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=25,
            bgcolor=ft.Colors.with_opacity(0.1, "white"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, "#ff6b6b")),
            blur=ft.Blur(10, 10),
            ink=True,
            on_click=quitter_app,
            tooltip=config.T("quit_tip")
        )

        btn_settings_home = ft.Container(
            content=ft.Row([
                get_ui_icon(assets.SVG_SETTINGS, color="#aaffffff", size=16),
                ft.Text(config.T("settings"), size=12, weight=ft.FontWeight.BOLD, color="#aaffffff")
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
            border_radius=25,
            bgcolor=ft.Colors.with_opacity(0.1, "white"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, "white")),
            blur=ft.Blur(10, 10),
            ink=True,
            on_click=open_settings_dialog,
            tooltip=config.T("settings")
        )

        return ft.Column([
            ft.Container(height=40),
            creer_header(),
            ft.Container(height=40),

            # ORCHESTRA SECTION
            ft.Text(config.T("main_stage"), size=12, weight=ft.FontWeight.BOLD, color="#88ffffff"),
            hero_carte,

            ft.Container(height=30),

            # AMBIENCE SECTION
            ft.Text(config.T("atmospheres"), size=12, weight=ft.FontWeight.BOLD, color="#88ffffff"),
            ft.Row(controls=liste_cartes_ambiance, alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=10),

            ft.Container(expand=True),
            ft.Row([
                ft.Text(config.T("version_label"), size=10, color="#44ffffff"),
                ft.Container(width=15),
                btn_settings_home,
                btn_quit,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            ft.Container(height=15),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, expand=True)

    def creer_presets_pills():
        """Compact pill-style preset row for current collection."""
        coll = config.ETAT.get("collection")
        SVG_MAP = {
            "earth": assets.SVG_EARTH, "water": assets.SVG_WATER, "fire": assets.SVG_FIRE,
            "air": assets.SVG_AIR, "space": assets.SVG_SPACE,
            "winter": assets.SVG_WINTER, "spring": assets.SVG_SPRING, "summer": assets.SVG_SUMMER,
            "autumn": assets.SVG_AUTUMN, "void": assets.SVG_VOID,
            "zen": assets.SVG_ZEN, "cyber": assets.SVG_CYBER, "lofi": assets.SVG_LOFI,
            "jungle": assets.SVG_JUNGLE, "indus": assets.SVG_INDUS,
        }

        def pill(icon_key, label, code, c1):
            svg = SVG_MAP.get(icon_key, assets.SVG_NOTE)
            b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
            is_active = config.ETAT.get("preset") == code
            return ft.Container(
                content=ft.Row([
                    ft.Image(src=f"data:image/svg+xml;base64,{b64}",
                             width=18, height=18, color=c1, fit=ft.BoxFit.CONTAIN),
                    ft.Text(label, size=9, weight=ft.FontWeight.BOLD,
                            color="white" if is_active else "#aaffffff"),
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                data=code,
                on_click=lambda e, c=code: [changer_preset(e), update_central_icon_for_preset(c)],
                height=34, padding=ft.Padding(left=10, top=4, right=10, bottom=4),
                border_radius=17,
                bgcolor=ft.Colors.with_opacity(0.35, c1) if is_active
                        else ft.Colors.with_opacity(0.12, "white"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.4 if is_active else 0.15, "white")),
                ink=True, tooltip=label,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

        if coll == "elements":
            pills: list = [
                pill("earth", "Earth", "terre", "#4caf50"),
                pill("water", "Water", "eau", "#00bcd4"),
                pill("fire", "Fire", "feu", "#ff5722"),
                pill("air", "Air", "air", "#b0bec5"),
                pill("space", "Space", "espace", "#673ab7"),
            ]
        elif coll == "saisons":
            pills = [
                pill("winter", "Winter", "hiver", "#81d4fa"),
                pill("spring", "Spring", "printemps", "#f48fb1"),
                pill("summer", "Summer", "ete", "#ff9800"),
                pill("autumn", "Autumn", "automne", "#a1887f"),
                pill("void", "Void", "vide", "#7b1fa2"),
            ]
        elif coll == "instruments":
            return ft.Container(height=0)
        else:  # atmos
            pills = [
                pill("zen", "Zen", "zen", "#81c784"),
                pill("cyber", "Cyber", "cyber", "#00e676"),
                pill("lofi", "LoFi", "lofi", "#d7ccc8"),
                pill("jungle", "Thunder", "jungle", "#455a64"),
                pill("indus", "Traffic", "indus", "#546e7a"),
            ]

        return ft.Container(
            content=ft.Row(pills, alignment=ft.MainAxisAlignment.CENTER,
                           spacing=6, wrap=True),
            bgcolor=ft.Colors.with_opacity(0.3, "black"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, "white")),
            border_radius=16, padding=8,
            blur=ft.Blur(10, 10),
            margin=ft.Margin(left=10, top=5, right=10, bottom=0),
        )

    def creer_contenu_controle():
        bouton_retour = ft.Container(
            content=ft.Row([
                get_ui_icon(assets.SVG_ARROW_LEFT, color="white", size=16),
                ft.Text(config.T("back"), size=12, weight=ft.FontWeight.BOLD, color="white")
            ], spacing=5),
            padding=10, border_radius=10, ink=True, on_click=retour_accueil
        )

        # TOP ACTION BAR
        def top_btn(text, code):
            is_active = config.ETAT["collection"] == code
            return ft.Container(
                content=ft.Text(text, size=10, weight=ft.FontWeight.BOLD, color="white" if is_active else "#88ffffff"),
                padding=ft.Padding(left=10, top=5, right=10, bottom=5),
                border_radius=20,
                bgcolor="#33ffffff" if is_active else ft.Colors.TRANSPARENT,
                ink=True,
                on_click=lambda _: charger_interface_controle(code),
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            )

        top_bar = ft.Row([
            top_btn(config.T("elements"), "elements"),
            top_btn(config.T("seasons"), "saisons"),
            top_btn(config.T("atmos"), "atmos"),
            top_btn(config.T("orchestra"), "instruments")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5)

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
                 safe_update(e.control)

        def mute_click(e):
            is_muted = global_audio.toggle_mute()
            # Update Icon
            # e.control is the Container
            new_icon = get_ui_icon(assets.SVG_MUTE if is_muted else assets.SVG_VOLUME,
                                  color="#ff4444" if is_muted else "white", size=20)
            e.control.content = new_icon
            safe_update(e.control)

        def volume_change(e):
            global_audio.set_volume(e.control.value)

        # Controls
        ctrl_bar = ft.Row([
            ft.Container(
                content=get_ui_icon(assets.SVG_PAUSE, size=20), 
                on_click=pause_click,
                tooltip=config.T("pause_ambience"),
                padding=5,
                border_radius=50,
                ink=True
            ),
            ft.Slider(
                min=0, max=100, value=40, 
                width=80, 
                active_color="white", inactive_color="#44ffffff",
                on_change=volume_change,
                tooltip=config.T("ambience_vol")
            ),
            ft.Container(
                content=get_ui_icon(assets.SVG_VOLUME, size=20),
                on_click=mute_click,
                tooltip=config.T("mute"),
                padding=5,
                border_radius=50,
                ink=True
            )
        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)

        header_nav = ft.Container(
            content=ft.Row([
                bouton_retour,
                ft.Container(expand=True),
                ft.Row([
                    ft.Text(config.T("liquid_soul"), size=18, weight=ft.FontWeight.BOLD, color="white", font_family="Verdana"),
                    ft.Text(config.T("version_tag"), size=10, color="#88ffffff", italic=True)
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

                ft.Container(width=5),
                ft.Container(
                    content=get_ui_icon(assets.SVG_EYE, color="white", size=18),
                    on_click=toggle_focus,
                    tooltip=config.T("focus_mode"),
                    padding=5,
                    border_radius=50,
                    ink=True,
                ),
                ft.Container(width=5),
                ft.Container(
                    content=get_ui_icon(assets.SVG_SETTINGS, color="white", size=18),
                    on_click=open_settings_dialog,
                    tooltip=config.T("settings"),
                    padding=5,
                    border_radius=50,
                    ink=True,
                ),
                recording_dot,
                ft.Container(width=5),
                top_bar,
                
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.4, "black"),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
            border_radius=20,
            padding=5,
            blur=ft.Blur(10, 10),
            margin=ft.Margin(left=10, top=0, right=10, bottom=0)
        )

        # Orchestra mode: show instrument rack in glassmorphism container
        if config.ETAT.get("collection") == "instruments":
            centre = ft.Container(
                content=container_presets,
                bgcolor=ft.Colors.with_opacity(0.4, "black"),
                border=ft.Border.all(1, ft.Colors.with_opacity(0.3, "white")),
                border_radius=20,
                padding=15,
                blur=ft.Blur(10, 10),
                margin=ft.Margin(left=10, top=5, right=10, bottom=0),
                expand=True,
            )
        else:
            centre = ft.Container(expand=True)

        return ft.Column([
            header_nav,
            creer_presets_pills(),
            centre,
            ft.Container(height=10),
            ft.Row([
                btn_record_container,
                btn_play_container,
                recording_timer_text,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=5),
            creer_panneau_sliders(),
            ft.Container(height=10),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, expand=True)


    def changer_preset(e):
        val = e.control.data
        config.ETAT["mode_auto"] = False
        config.ETAT["preset"] = val
        print(f"🎛️ Logic: Preset changed to {val}")

        # Trigger Audio
        try:
            global_audio.play_ambience(val)
        except Exception as err:
            print(f"❌ Error triggering audio: {err}")

        update_ui()


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

        # v1.20 Liquid Glass preset button
        icon_with_glow = ft.Container(
            content=ft.Image(src=f"data:image/svg+xml;base64,{b64}",
                             width=32, height=32,
                             color=c1,
                             fit=ft.BoxFit.CONTAIN),
            alignment=ft.Alignment(0, 0),
            width=42, height=42,
            border_radius=50,
            gradient=ft.RadialGradient(
                colors=[ft.Colors.with_opacity(0.25, c1),
                        ft.Colors.with_opacity(0.0, c1)],
            ),
        )

        return ft.Container(
            content=ft.Column([
                icon_with_glow,
                ft.Text(nom, size=9, color="#ccffffff", weight=ft.FontWeight.BOLD,
                       style=ft.TextStyle(shadow=ft.BoxShadow(blur_radius=4, color="black", offset=ft.Offset(0, 1))))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            data=code,
            on_click=lambda e: [changer_preset(e), update_central_icon_for_preset(code)],
            width=75, height=85,
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-0.5, -1.0),
                end=ft.Alignment(0.5, 1.0),
                colors=[
                    ft.Colors.with_opacity(0.18, "white"),
                    ft.Colors.with_opacity(0.06, "white"),
                    ft.Colors.with_opacity(0.02, "white"),
                ],
            ),
            border=ft.Border(
                top=ft.BorderSide(1.5, ft.Colors.with_opacity(0.35, "white")),
                left=ft.BorderSide(1, ft.Colors.with_opacity(0.15, "white")),
                right=ft.BorderSide(1, ft.Colors.with_opacity(0.08, "white")),
                bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.05, "white")),
            ),
            shadow=ft.BoxShadow(
                blur_radius=18, spread_radius=-2,
                color=ft.Colors.with_opacity(0.5, c1),
                offset=ft.Offset(0, 6),
                blur_style=ft.BlurStyle.OUTER,
            ),
            blur=ft.Blur(8, 8),
            padding=5,
            ink=True,
            tooltip=nom,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    def creer_boutons_elements():
        return ft.Column([
            ft.Row([
                btn_preset("earth", config.T("earth"), "terre", "#4caf50", "#2e7d32"),
                btn_preset("water", config.T("water"), "eau", "#00bcd4", "#0288d1"),
                btn_preset("fire", config.T("fire"), "feu", "#ff5722", "#ffeb3b")
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=5),
            ft.Row([
                btn_preset("air", config.T("air"), "air", "#b0bec5", "#ffffff"),
                btn_preset("space", config.T("space"), "espace", "#311b92", "#673ab7")
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

    def creer_boutons_saisons():
        return ft.Column([
            ft.Row([
                btn_preset("winter", config.T("winter"), "hiver", "#81d4fa", "#ffffff"),
                btn_preset("spring", config.T("spring"), "printemps", "#f48fb1", "#c5e1a5"),
                btn_preset("summer", config.T("summer"), "ete", "#ff9800", "#ffeb3b")
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=5),
            ft.Row([
                btn_preset("autumn", config.T("autumn"), "automne", "#a1887f", "#ff7043"),
                btn_preset("void", config.T("void"), "vide", "#000000", "#4a148c")
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])
    
    def creer_boutons_atmos():
        return ft.Column([
            ft.Row([
                btn_preset("zen", config.T("zen"), "zen", "#81c784", "#c8e6c9"),
                btn_preset("cyber", config.T("cyber"), "cyber", "#00e676", "#2979ff"),
                btn_preset("lofi", config.T("lofi"), "lofi", "#d7ccc8", "#795548")
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=5),
            ft.Row([
                btn_preset("jungle", config.T("thunder"), "jungle", "#455a64", "#90a4ae"),
                btn_preset("indus", config.T("traffic"), "indus", "#546e7a", "#cfd8dc")
            ], alignment=ft.MainAxisAlignment.CENTER)
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
            safe_update(e.control)

        def get_asset(code):
            mapping = {
                # STRINGS
                "violon": assets.SVG_VIOLIN, "alto": assets.SVG_VIOLA, "violoncelle": assets.SVG_CELLO,
                "contrebasse": assets.SVG_CONTRABASS, "guitare": assets.SVG_GUITAR, "basse": assets.SVG_BASS,
                "harpe": assets.SVG_HARP, "pizzicato": assets.SVG_PIZZICATO,
                # WINDS & BRASS
                "flute": assets.SVG_FLUTE, "piccolo": assets.SVG_PICCOLO, "clarinette": assets.SVG_CLARINET,
                "hautbois": assets.SVG_OBOE, "basson": assets.SVG_BASSOON,
                "trompette": assets.SVG_TRUMPET, "cor": assets.SVG_HORN, "cuivres": assets.SVG_TRUMPET,
                # KEYS
                "piano": assets.SVG_PIANO, "orgue": assets.SVG_ORGAN,
                "clavecin": assets.SVG_HARPSICHORD, "accordeon": assets.SVG_ACCORDION,
                # PERCUSSION
                "timbales": assets.SVG_DRUM, "batterie": assets.SVG_DRUM,
                "xylophone": assets.SVG_XYLOPHONE, "glockenspiel": assets.SVG_GLOCKENSPIEL,
                # ETHEREAL & VOICES
                "choir": assets.SVG_CHOIR, "voice": assets.SVG_VOICE, "celesta": assets.SVG_CELESTA,
                "bells": assets.SVG_BELLS,
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
                tooltip = f"{nom} ({config.T('unavailable_in')} {target} {config.T('mode_suffix')})"
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
                    ft.Image(src=f"data:image/svg+xml;base64,{b64}", width=40, height=40, color=icon_color, fit=ft.BoxFit.CONTAIN),
                    ft.Text(nom, size=10, color="white" if not est_exclu else "#555555", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
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
                ft.Text(titre, size=12, weight=ft.FontWeight.BOLD, color="#88ffffff"),
                ft.Row([btn_inst(n, c) for n, c in instruments_list], alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

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
                if not isinstance(btn, ft.Container):
                    continue
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
                    safe_update(btn)
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

             # v1.20 Liquid Glass emotion button
             icon_glow = ft.Container(
                 content=ft.Image(src=f"data:image/svg+xml;base64,{b64}",
                                  width=20, height=20,
                                  color=base_color if is_active else "#aaffffff",
                                  fit=ft.BoxFit.CONTAIN),
                 alignment=ft.Alignment(0, 0),
                 width=30, height=30,
                 border_radius=50,
                 gradient=ft.RadialGradient(
                     colors=[ft.Colors.with_opacity(0.3 if is_active else 0.0, base_color),
                             ft.Colors.with_opacity(0.0, base_color)],
                 ),
             )

             return ft.Container(
                content=icon_glow,
                padding=6,
                border_radius=16,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-0.5, -1.0),
                    end=ft.Alignment(0.5, 1.0),
                    colors=[
                        ft.Colors.with_opacity(0.20 if is_active else 0.10, "white"),
                        ft.Colors.with_opacity(0.05, "white"),
                    ],
                ),
                border=ft.Border(
                    top=ft.BorderSide(1.5 if is_active else 1, ft.Colors.with_opacity(0.4 if is_active else 0.2, base_color if is_active else "white")),
                    left=ft.BorderSide(1, ft.Colors.with_opacity(0.15, "white")),
                    right=ft.BorderSide(1, ft.Colors.with_opacity(0.08, "white")),
                    bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.05, "white")),
                ),
                shadow=ft.BoxShadow(
                    blur_radius=12 if is_active else 0,
                    color=ft.Colors.with_opacity(0.4, base_color),
                    blur_style=ft.BlurStyle.OUTER,
                ),
                blur=ft.Blur(6, 6),
                on_click=change_emotion,
                tooltip=tooltip,
                ink=True,
                data=val,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                scale=1.1 if is_active else 1.0,
                animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
            )

        row_emotions = ft.Row([
            emotion_btn("dice", "aleatoire", config.T("random_flow")),
            emotion_btn("palette", "creatif", config.T("creative")),
            emotion_btn("sun", "joyeux", config.T("joy")),
            emotion_btn("rain", "melancolique", config.T("melancholy")),
            emotion_btn("sword", "action", config.T("action")),
            emotion_btn("suspense", "suspense", config.T("suspense")),
            emotion_btn("castle", "epique", config.T("epic")),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        # Container for Custom Profiles Buttons
        row_custom_profiles = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10, wrap=True)

        def refresh_profiles_row():
            items = []
            for name in config.ETAT.get("custom_profiles", {}):
                # Use profile name as tooltip, special icon handling inside emotion_btn driven by "profile_" prefix
                items.append(emotion_btn("user", f"profile_{name}", f"{config.T('load')} {name}"))
            row_custom_profiles.controls = items
            try:
                if row_custom_profiles.page: safe_update(row_custom_profiles)
            except RuntimeError:
                pass

        # Initial Load
        refresh_profiles_row()
        
        # --- PROFILE MANAGEMENT (Restored v10.9) ---
        def show_dialog(title, content, actions):
            def close_dialog(e):
                main_layout_stack.controls.pop()
                safe_update(page)

            dialog_container = ft.Container(
                content=ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Container(height=10),
                    content,
                    ft.Container(height=20),
                    ft.Row(actions + [
                        ft.Container(content=ft.Text(config.T("cancel"), color="#88ffffff"), on_click=close_dialog, padding=10, ink=True)
                    ], alignment=ft.MainAxisAlignment.END)
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
            safe_update(page)

        def save_profile_click(e):
            txt_name = ft.TextField(label=config.T("profile_name"), value=f"Profile {len(config.ETAT.get('custom_profiles', {})) + 1}", border_color="white", color="white")
            
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
                safe_update(page)

                # Feedback
                btn_save_text.value = f"✅ {config.T('saved')}"
                btn_save_text.color = "#4caf50"
                safe_update(btn_save)
                import time
                def reset_btn():
                    import time
                    time.sleep(2)
                    try:
                        if not btn_save.page: return # Safety check
                        btn_save_text.value = f"💾 {config.T('save_profile')}"
                        btn_save_text.color = "#88ffffff"
                        safe_update(btn_save)
                    except RuntimeError:
                        pass
                threading.Thread(target=reset_btn, daemon=True).start()

            show_dialog(config.T("save_profile"), txt_name, [
                ft.Container(content=ft.Text(config.T("save"), color="#4caf50", weight=ft.FontWeight.BOLD), on_click=confirm_save, padding=10, ink=True)
            ])

        btn_save_text = ft.Text(config.T("save_profile"), color="#88ffffff", size=10, weight=ft.FontWeight.BOLD)
        btn_save = ft.Container(
            content=btn_save_text, 
            on_click=save_profile_click, 
            padding=10, 
            border_radius=15, 
            ink=True, 
            border=ft.Border.all(1, "#22ffffff"),
            bgcolor=ft.Colors.with_opacity(0.05, "white")
        )

        return ft.Column([
            ft.Text(config.T("orchestra"), size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=5),

            # STRINGS
            section(config.T("strings"), [
                (config.T("violin"), "violon"), (config.T("viola"), "alto"), (config.T("cello"), "violoncelle"),
                (config.T("contrabass"), "contrebasse"), (config.T("harp"), "harpe"), (config.T("guitar"), "guitare"),
                (config.T("pizzicato"), "pizzicato"),
            ]),
            ft.Divider(color="#22ffffff"),

            # WINDS & BRASS
            section(config.T("winds_brass"), [
                (config.T("flute"), "flute"), (config.T("piccolo"), "piccolo"), (config.T("clarinet"), "clarinette"),
                (config.T("oboe"), "hautbois"), (config.T("bassoon"), "basson"),
                (config.T("trumpet"), "trompette"), (config.T("horn"), "cor"), (config.T("brass"), "cuivres"),
            ]),
            ft.Divider(color="#22ffffff"),

            # KEYS
            section(config.T("keys"), [
                (config.T("piano"), "piano"), (config.T("organ"), "orgue"),
                (config.T("harpsichord"), "clavecin"), (config.T("accordion"), "accordeon"),
            ]),
            ft.Divider(color="#22ffffff"),

            # PERCUSSION
            section(config.T("percussion"), [
                (config.T("timpani"), "timbales"), (config.T("drums"), "batterie"),
                (config.T("xylophone"), "xylophone"), (config.T("glockenspiel"), "glockenspiel"),
            ]),
            ft.Divider(color="#22ffffff"),

            # ETHEREAL & VOICES
            section(config.T("ethereal"), [
                (config.T("choir"), "choir"), (config.T("voice"), "voice"),
                (config.T("celesta"), "celesta"), (config.T("bells"), "bells"),
            ]),

            ft.Container(height=10),
            ft.Divider(color="#22ffffff"),
            ft.Text(config.T("mood"), size=12, weight=ft.FontWeight.BOLD, color="#88ffffff"),
            row_emotions,
            
            ft.Container(height=10),
            row_custom_profiles, # Added Profiles Row
            ft.Container(height=10),
            
            # ft.Container(height=20), # Spacer before Save
            btn_save,
            ft.Container(height=10),
            
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

    def creer_panneau_sliders():
        switch_auto.tooltip = config.T("enable_auto")
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
                safe_update(page)
            except: pass

        # BPM Control Logic
        def change_bpm(delta):
            current = config.ETAT.get("bpm", 120)
            new_bpm = max(40, min(200, current + delta))
            config.ETAT["bpm"] = new_bpm
            lbl_bpm.value = f"{new_bpm} BPM"
            safe_update(lbl_bpm)
            
        # lbl_bpm was here, now global
        
        # --- BLOCS DE CONTROLE ---
        def creer_bloc(titre, svg_icon, controls, color="#22ffffff"):
             return ft.Container(
                 content=ft.Column([
                     ft.Row([get_ui_icon(svg_icon), ft.Text(titre, size=12, weight=ft.FontWeight.BOLD, color="#ddffffff")], spacing=10),
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
            ft.Text(config.T("tempo"), size=12),
            ft.Container(expand=True),
            ft.Container(content=ft.Text("-", color="white", size=20), on_click=lambda e: change_bpm(-5), padding=5, border_radius=15, ink=True, bgcolor="#33000000"),
            ft.Container(width=10),
            lbl_bpm,
            ft.Container(width=10),
            ft.Container(content=ft.Text("+", color="white", size=20), on_click=lambda e: change_bpm(5), padding=5, border_radius=15, ink=True, bgcolor="#33000000"),
        ], alignment=ft.MainAxisAlignment.CENTER)

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
        txt_auto = ft.Text(config.T("auto_desc"), size=10, color="#88ffffff", italic=True)
        
        # Zen Timer Dropdown
        def on_timer_change(e):
             val = e.control.value
             mins = 0
             if val == "15 min": mins = 15
             elif val == "30 min": mins = 30
             elif val == "60 min": mins = 60
             
             if mins > 0:
                 lancer_zen_timer(mins)
                 snack = ft.SnackBar(ft.Text(f"{config.T('zen_set')} {mins} {config.T('minutes')}", color="white"), bgcolor="#2196f3", open=True)
                 page.overlay.append(snack)
                 safe_update(page)

        dd_timer = ft.Dropdown(
            options=[
                ft.dropdown.Option(config.T("off")),
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
            value=config.T("off"),
        )
        dd_timer.on_select = on_timer_change

        return ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row([get_ui_icon(assets.SVG_TUNE, color="white"), ft.Text(config.T("advanced_controls"), size=14, color="white")], alignment=ft.MainAxisAlignment.CENTER),
                controls=[
                    ft.Container(height=10),

                    # ZEN & AUTO MODE
                    creer_bloc(config.T("zen_auto"), assets.SVG_AUTO, [
                        ft.Row([
                            ft.Column([
                                ft.Text(config.T("auto_drift"), size=11, color="#ddffffff"),
                                switch_auto
                            ]),
                            ft.Container(width=20),
                            ft.Column([
                                ft.Text(config.T("sleep_timer"), size=11, color="#ddffffff"),
                                dd_timer
                            ])
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        txt_auto
                    ], color="#22ffffff"),

                    ft.Container(height=10),

                    # RHYTHM & CHAOS
                    creer_bloc(config.T("rhythm_flow"), assets.SVG_WAVES, [
                        row_bpm,
                        slider_row(config.T("chaos"), "chaos", assets.SVG_SHUFFLE, lbl_chaos, config.T("chaos_tip"))
                    ], color="#224caf50"),

                    ft.Container(height=10),

                    # PHYSICS
                    creer_bloc(config.T("environment"), assets.SVG_EARTH, [
                         slider_row(config.T("intensity"), "intensite", assets.SVG_FLASH, lbl_intensite, config.T("intensity_tip")),
                         slider_row(config.T("gravity"), "gravite", assets.SVG_ARROW_DOWN, lbl_gravite, config.T("gravity_tip")),
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
    content_layer.content = creer_contenu_accueil()
    page.add(main_layout_stack)
    
    # Threading correction: Start animation loop AFTER adding content to page
    thread_anim = threading.Thread(target=animer_coeur, daemon=True)
    thread_anim.start()

    # v14.0: Start Background Animation
    thread_fond = threading.Thread(target=animer_fond, daemon=True)
    thread_fond.start()

if __name__ == "__main__":
    print("Lancement v1.20 Kaleidoscope...")

    # Initialiser et démarrer le moteur audio
    audio_engine = QuoniamAudioEngine()
    audio_engine.start()

    ft.app(main, view=ft.AppView.WEB_BROWSER)