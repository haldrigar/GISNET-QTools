# -*- coding: utf-8 -*-
import os
import json

class QToolsConfig:
    def __init__(self):
        """Inicjalizuje konfigurację wtyczki GISNET QTools."""
        
        self.plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.sciezka_pliku = os.path.join(self.plugin_dir, 'config.json')
        
        # Słownik, w którym będą przechowywane bieżące parametry w pamięci RAM
        self.data = {}
        
        # Domyślne wartości
        self.domyslne_ustawienia = {
            "obliview_url": "https://obliview.brg.gda.pl"
        }
        
        # Wczytaj dane od razu przy inicjalizacji modułu
        self.wczytaj()

    def wczytaj(self):
        """Odczytuje konfigurację z pliku JSON na dysku."""

        if not os.path.exists(self.sciezka_pliku):
            self.data = self.domyslne_ustawienia.copy()
            self.zapisz()
            return

        try:
            with open(self.sciezka_pliku, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception:
            self.data = self.domyslne_ustawienia.copy()

    def zapisz(self):
        """Zapisuje bieżący stan słownika data do pliku JSON."""
        
        try:
            with open(self.sciezka_pliku, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Błąd zapisu konfiguracji GISNET QTools: {e}")
            return False

# KLUCZOWY MOMENT: Tworzymy jedną instancję, którą będą importować inne pliki
plugin_config = QToolsConfig()