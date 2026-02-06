import flet as ft
import inspect

print("--- INTERROGATOIRE DE FLET ---")
try:
    # On demande la signature (la liste des arguments acceptés)
    signature = inspect.signature(ft.Icon.__init__)
    print(f"L'objet Icon accepte ces arguments :\n{signature}")
except Exception as e:
    print(f"Impossible de lire la signature : {e}")

print("-" * 30)