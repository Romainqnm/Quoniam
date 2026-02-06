import flet as ft
from main import ETAT, main as lancer_moteur_sonore
import threading

def main(page: ft.Page):
    page.title = "QUONIAM Lab v1.4"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 750
    page.padding = 30
    page.bgcolor = "#1a1a2e"

    def mise_a_jour_labels():
        v = slider_vitesse.value
        if v < 20: txt = "Lent (Zen)"
        elif v < 60: txt = "Modéré (Flow)"
        else: txt = "Rapide (Transe)"
        lbl_vitesse.value = f"Vitesse : {int(v)}% - {txt}"
        lbl_intensite.value = f"Intensité : {int(slider_intensite.value)}%"
        page.update()

    def changer_preset(e):
        code = e.control.data
        ETAT["preset"] = code
        
        if code == "eau":
            txt_icone.value = "💧"
            txt_ambiance.value = "RIVIÈRE (Marimba)"
            page.bgcolor = "#1a1a2e"
            slider_vitesse.value = 50
            slider_intensite.value = 30
        elif code == "air":
            txt_icone.value = "☁️"
            txt_ambiance.value = "CÉLESTE (Piano Élec.)"
            page.bgcolor = "#455A64"
            slider_vitesse.value = 25
            slider_intensite.value = 60
        elif code == "feu":
            txt_icone.value = "🔥"
            txt_ambiance.value = "URBAIN (Guitare)"
            page.bgcolor = "#3E2723"
            slider_vitesse.value = 70
            slider_intensite.value = 50

        ETAT["vitesse"] = slider_vitesse.value
        ETAT["intensite"] = slider_intensite.value
        mise_a_jour_labels()

    def on_slider_change(e):
        ETAT["vitesse"] = slider_vitesse.value
        ETAT["intensite"] = slider_intensite.value
        mise_a_jour_labels()

    def toggle_play(e):
        ETAT["actif"] = not ETAT["actif"]
        btn_play.text = "⏸ PAUSE" if ETAT["actif"] else "▶ REPRENDRE"
        btn_play.bgcolor = "#B71C1C" if ETAT["actif"] else "#2E7D32"
        page.update()

    # UI
    titre = ft.Text("QUONIAM", size=40, font_family="Roboto Mono", weight="w100")
    sous_titre = ft.Text("v1.4 Multiverse", color="#9E9E9E")
    txt_icone = ft.Text("💧", size=80, text_align="center")
    txt_ambiance = ft.Text("RIVIÈRE (Marimba)", size=16, weight="bold", color="#64B5F6")

    def btn_preset(icon, nom, code, color):
        return ft.Container(
            content=ft.Column([ft.Text(icon, size=24), ft.Text(nom, size=10)], alignment="center", spacing=2),
            data=code, on_click=changer_preset, padding=10, width=80, height=80,
            bgcolor=color, border_radius=15, ink=True
        )

    row_presets = ft.Row([
        btn_preset("💧", "Eau", "eau", "#0D47A1"),
        btn_preset("☁️", "Air", "air", "#546E7A"),
        btn_preset("🔥", "Feu", "feu", "#BF360C")
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    lbl_vitesse = ft.Text("Vitesse : ...")
    slider_vitesse = ft.Slider(min=0, max=100, divisions=100, value=50, on_change=on_slider_change)
    lbl_intensite = ft.Text("Intensité : ...")
    slider_intensite = ft.Slider(min=0, max=100, divisions=100, value=30, on_change=on_slider_change)

    container = ft.Container(
        content=ft.Column([lbl_vitesse, slider_vitesse, ft.Divider(height=10, color="transparent"), lbl_intensite, slider_intensite]),
        padding=20, bgcolor="#00000033", border_radius=15
    )

    btn_play = ft.ElevatedButton("⏸ PAUSE", on_click=toggle_play, bgcolor="#B71C1C", color="white", width=300)

    mise_a_jour_labels()

    page.add(ft.Column([
        ft.Container(height=10), titre, sous_titre, ft.Divider(height=20, color="transparent"),
        txt_icone, txt_ambiance, ft.Divider(height=20, color="transparent"),
        row_presets, ft.Divider(height=20, color="transparent"),
        container, ft.Divider(height=30, color="transparent"), btn_play
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))

if __name__ == "__main__":
    # On lance l'interface d'abord !
    print("Lancement de l'interface...")
    
    # Le thread audio démarrera en parallèle sans bloquer l'import
    thread_son = threading.Thread(target=lancer_moteur_sonore, daemon=True)
    thread_son.start()
    
    ft.app(target=main)