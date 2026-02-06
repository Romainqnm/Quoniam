import flet
import sys

print("--- DIAGNOSTIC FLET ---")
print(f"Version Python : {sys.version}")
print(f"Fichier Flet chargé depuis : {flet.__file__}")
print("Contenu du module flet :")
print(dir(flet))