# -*- coding: utf-8 -*-
import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QCheckBox 
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QButtonGroup 

from ..tools.Config import plugin_config

# Funkcja uic.loadUiType dynamicznesparsowuje plik .ui i przygotowuje klasę bazową interfejsu
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'settings.ui'))

class OknoUstawien(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Konstruktor okna ładowanego z Qt Designera."""

        super().__init__(parent)
        
        # Kluczowa linijka: buduje interfejs narysowany w Qt Designerze
        self.setupUi(self)
        
        # Standardowe przyciski Qt Designera (QDialogButtonBox) automatycznie obsługują akcje
        # Szukamy domyślnego elementu buttonBox z Designera i łączymy sygnały:
        self.buttonBox.accepted.connect(self.akcja_zapisz)
        self.buttonBox.rejected.connect(self.reject)

    def akcja_zapisz(self):
        """Zapisuje zmienione w oknie wartości z powrotem do konfiguracji."""

        if self.radioButtonOGdansk.isChecked():
            plugin_config.data["obliview_selected"] = "gdansk"
            plugin_config.data["obliview_url"] = self.lineEditGdansk.text()
            print("Gdańsk")

        if self.radioButtonOGdynia.isChecked():
            plugin_config.data["obliview_selected"] = "gdynia"
            plugin_config.data["obliview_url"] = self.lineEditGdynia.text()
            print("Gdynia")

        plugin_config.zapisz()
        self.accept() # Zamyka okno dialogowe z wynikiem QDialog.Accepted
