import os
import json

from qgis.core import Qgis, QgsMessageLog

class QToolsConfig:

    # ===============================================================================================================================================
    def __init__(self):
        """Inicjalizuje konfigurację wtyczki GISNET QTools."""

        self.plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Ścieżka do katalogu wtyczki
        self.config_file_name = os.path.join(self.plugin_dir, 'config.json') # Pełna ścieżka do pliku konfiguracyjnego config.json

        self.data = {} # Słownik, w którym będą przechowywane bieżące parametry w pamięci

        self.obliview_urls_list = {} # Słownik przechowujący pary miasto:URL dla portalu ObliView

        # Domyślne wartości gdyby plik konfiguracyjny nie istniał lub był uszkodzony
        self.default_settings = {
            "obliview_selected_city": "Gdańsk",
            "obreb":"226101_1.0001",
            "obliview_type": "radioButtonOblique",
            "clipboard_monitoring_enabled": False,
            "clipboard_zoom_enabled": False,
            "clipboard_zoom_scale": 500,
            "gdansk_filter_enabled": False
        }

        self.read_config() # Wczytaj dane od razu przy inicjalizacji modułu

    # ===============================================================================================================================================
    def read_config(self):
        """Odczytuje konfigurację z pliku JSON na dysku."""

        # 1. najpierw zainicjalizuj domyślne ustawienia
        self.data = self.default_settings.copy()

        # -------------------------------------------------------------------------------------------------------------------------------------------
        # 2. zawsze wczytaj listę miast z Obliview.cfg

        obliview_config_file_name = os.path.join(self.plugin_dir, 'tools', 'Obliview.cfg') # Pełna ścieżka do pliku konfiguracyjnego Obliview.cfg
        self.obliview_urls_list = {}

        # Wczytaj konfigurację dla portalu ObliView z pliku Obliview.cfg
        try:
            with open(obliview_config_file_name, 'r', encoding='utf-8') as f:
                for linia in f:
                    linia = linia.strip()
                    if not linia or linia.startswith('#'):
                        continue

                    parts = linia.split(';')
                    if len(parts) < 5:
                        continue

                    miasto = parts[0].strip()
                    url = parts[1].strip()
                    lvl_orto = parts[2].strip()
                    lvl_oblique = parts[3].strip()
                    lvl_3d = parts[4].strip()

                    self.obliview_urls_list[miasto] = {
                        "url": url,
                        "lvl_orto": lvl_orto,
                        "lvl_oblique": lvl_oblique,
                        "lvl_3d": lvl_3d
                    }
        except Exception as e:
            QgsMessageLog.logMessage(f"Błąd wczytania konfiguracji ObliView: {e}", "GISNET QTools", level=Qgis.MessageLevel.Warning)

        # 3. jeśli config.json istnieje, nadpisz ustawienia użytkownika
        if os.path.exists(self.config_file_name):
            try:
                with open(self.config_file_name, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    if isinstance(saved_data, dict):
                        self.data.update(saved_data)
            except Exception:
                self.data = self.default_settings.copy()

        # 4. uzupełnij brakujące klucze
        for key, value in self.default_settings.items():
            self.data.setdefault(key, value)

    # ===============================================================================================================================================
    def save_config(self):
        """Zapisuje bieżący stan słownika data do pliku JSON."""

        try:
            with open(self.config_file_name, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            QgsMessageLog.logMessage(f"Błąd zapisu konfiguracji GISNET QTools: {e}", "GISNET QTools", level=Qgis.MessageLevel.Critical)
            return False

 # ==================================================================================================================================================
# Tworzymy jedną instancję, którą będą importować inne pliki
plugin_config = QToolsConfig()
