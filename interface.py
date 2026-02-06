import flet as ft
from main import ETAT, lancer_ecoute_clavier, main as lancer_moteur_sonore
import threading

def main(page: ft.Page):
    # --- 1. CONFIGURATION DE LA FENÊTRE ---
    page.title = "QUONIAM Controller"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 600
    page.window_resizable = False
    page.padding = 30
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#1a1a2e" # Bleu nuit profond

    # --- 2. FONCTIONS DE MISE À JOUR ---
    def changer_mode(e):
        nouveau_mode = e.control.data
        ETAT["mode"] = nouveau_mode
        
        if nouveau_mode == "nuit":
            # On remplace l'icône par un Emoji
            txt_icone.value = "🌙"
            txt_status.value = "MODE NUIT ACTIF"
            page.bgcolor = "#1a1a2e" 
        else:
            txt_icone.value = "☀️"
            txt_status.value = "MODE JOUR ACTIF"
            page.bgcolor = "#2c3e50" 
            
        page.update()

    def toggle_play(e):
        ETAT["actif"] = not ETAT["actif"]
        if ETAT["actif"]:
            btn_play.text = "⏸ PAUSE"
            btn_play.bgcolor = "#B71C1C" # Rouge
        else:
            btn_play.text = "▶ REPRENDRE"
            btn_play.bgcolor = "#2E7D32" # Vert
        page.update()

    # --- 3. CRÉATION DES ÉLÉMENTS VISUELS ---
    
    titre = ft.Text("QUONIAM", size=40, weight=ft.FontWeight.W_100, font_family="Roboto Mono")
    sous_titre = ft.Text("Générateur d'Ambiance", size=12, color="#9E9E9E")

    # LE FIX EST ICI : Un texte géant au lieu d'une icône buggée
    txt_icone = ft.Text("🌙", size=80)
    txt_status = ft.Text("MODE NUIT ACTIF", size=16, weight=ft.FontWeight.BOLD)

    # Bouton NUIT (Simplifié)
    btn_nuit = ft.Container(
        content=ft.Row([
            ft.Text("🛌", size=20), # Emoji Lit
            ft.Text("Relaxation (Nuit)", size=16)
        ], alignment=ft.MainAxisAlignment.CENTER),
        data="nuit",
        on_click=changer_mode,
        padding=15,
        bgcolor=ft.Colors.WHITE10,
        border_radius=10,
        ink=True
    )

    # Bouton JOUR (Simplifié)
    btn_jour = ft.Container(
        content=ft.Row([
            ft.Text("⚡", size=20), # Emoji Eclair
            ft.Text("Focus (Jour)", size=16)
        ], alignment=ft.MainAxisAlignment.CENTER),
        data="jour",
        on_click=changer_mode,
        padding=15,
        bgcolor=ft.Colors.WHITE10,
        border_radius=10,
        ink=True
    )

    btn_play = ft.ElevatedButton(
        "⏸ PAUSE", 
        on_click=toggle_play,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=20,
            bgcolor="#B71C1C",
            color="#FFFFFF"
        ),
        width=200
    )

    # --- 4. ASSEMBLAGE ---
    page.add(
        ft.Column(
            [
                titre,
                sous_titre,
                ft.Divider(height=40, color="transparent"),
                txt_icone, # On ajoute notre emoji géant
                txt_status,
                ft.Divider(height=40, color="transparent"),
                btn_nuit,
                ft.Divider(height=10, color="transparent"),
                btn_jour,
                ft.Divider(height=40, color="transparent"),
                btn_play
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    thread_son = threading.Thread(target=lancer_moteur_sonore, daemon=True)
    thread_son.start()
    
    print("Lancement de l'interface graphique...")
    ft.app(target=main)