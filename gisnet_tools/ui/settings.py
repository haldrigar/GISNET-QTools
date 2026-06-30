import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QCheckBox
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QButtonGroup

from ..tools.Config import plugin_config

# Funkcja uic.loadUiType dynamiczne sparsowuje plik .ui i przygotowuje klasę bazową interfejsu
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'settings.ui'))

class SettingsDialog(QDialog, FORM_CLASS):

    # ===============================================================================================================================================
    def __init__(self, parent=None):
        """Konstruktor okna ładowanego z Qt Designera."""

        super().__init__(parent) # Wywołuje konstruktor klasy bazowej QDialog

        self.setupUi(self) # Inicjalizuje interfejs użytkownika z pliku .ui

        self.obliview_urls_list = {} # Słownik przechowujący pary miasto:URL dla portalu ObliView

        self.read_obliview_urls() # Wczytuje plik Obliview.cfg i parsuje go do słownika self.obliview_urls_list
        
        self.comboBoxObliView.addItems(self.obliview_urls_list.keys()) # Dodaje miasta do comboBoxa w oknie ustawień

        self.obliview_selected = plugin_config.data.get("obliview_selected") # Pobiera z konfiguracji wybrane miasto dla ObliView

        self.comboBoxObliView.setCurrentText(self.obliview_selected) # Ustawia w comboBoxie aktualnie wybrane miasto na podstawie konfiguracji
        self.set_obliview_url_ui(self.comboBoxObliView.currentText()) # Ustawia pole URL na podstawie aktualnie wybranego miasta w comboBoxie
        
        self.comboBoxObliView.currentTextChanged.connect(self.set_obliview_url_ui) # Po zmianie wyboru w comboBoxie, aktualizuje pole URL na podstawie nowego wyboru

        self.buttonBox.accepted.connect(self.save_settings) # Zapisuje ustawienia po kliknięciu "OK"
        self.buttonBox.rejected.connect(self.reject) # Zamyka okno dialogowe po kliknięciu "Anuluj"

    # ===============================================================================================================================================
    def read_obliview_urls(self):
        """Wczytuje plik Obliview.cfg i parsuje go do słownika."""

        self.plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Ścieżka do katalogu wtyczki

        sciezka_pliku = os.path.join(self.plugin_dir, 'tools', 'Obliview.cfg') # Pełna ścieżka do pliku konfiguracyjnego Obliview.cfg


        # Używamy encoding='utf-8', aby prawidłowo obsłużyć polskie znaki (ń, ś)
        with open(sciezka_pliku, 'r', encoding='utf-8') as f:

            for linia in f:
                linia = linia.strip() # Usuwamy białe znaki z początku i końca linii

                if linia and ';' in linia:
                    # split(';', 1) dzieli linię tylko na 2 części (w razie gdyby w URL był średnik)
                    miasto, url = linia.split(';', 1)
                    self.obliview_urls_list[miasto.strip()] = url.strip()

    # ===============================================================================================================================================
    def set_obliview_url_ui(self, wybrane_miasto):
        """Wyciąga URL ze słownika na podstawie wybranego miasta i wpisuje do lineEditUrl."""

        # Pobieramy wartość ze słownika. Jeśli miasta nie ma, zwraca pusty tekst ""
        url = self.obliview_urls_list.get(wybrane_miasto)
        self.lineEditObliViewUrl.setText(url)

    # ===============================================================================================================================================
    def save_settings(self):
        """Zapisuje zmienione w oknie wartości z powrotem do konfiguracji."""

        plugin_config.data["obliview_selected"] = self.comboBoxObliView.currentText()
        plugin_config.data["obliview_selected_url"] = self.lineEditObliViewUrl.text()

        plugin_config.zapisz()

        self.accept() # Zamyka okno dialogowe z wynikiem QDialog.Accepted
