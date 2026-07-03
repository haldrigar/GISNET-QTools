import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QRadioButton

from ..tools.Config import plugin_config

# Funkcja uic.loadUiType dynamiczne sparsowuje plik .ui i przygotowuje klasę bazową interfejsu
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'settings.ui'))

class SettingsDialog(QDialog, FORM_CLASS):

    # ===============================================================================================================================================
    def __init__(self, parent=None):
        """Konstruktor okna ładowanego z Qt Designera."""

        super().__init__(parent) # Wywołuje konstruktor klasy bazowej QDialog

        self.setupUi(self) # Inicjalizuje interfejs użytkownika z pliku .ui
      
        # -------------------------------------------------------------------------------------------------------------------------------------------
        self.comboBoxObliView.clear()
        self.comboBoxObliView.addItems(sorted(plugin_config.obliview_urls_list.keys()))

        obliview_selected_city = plugin_config.data.get("obliview_selected_city") # Pobiera z konfiguracji wybrane miasto dla ObliView

        self.comboBoxObliView.setCurrentText(obliview_selected_city) # Ustawia w comboBoxie aktualnie wybrane miasto na podstawie konfiguracji
        
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # Ustawia zaznaczony radioButton na podstawie konfiguracji
        obliview_type = plugin_config.data.get("obliview_type")
        
        for radio_button in self.groupBoxObliViewType.findChildren(QRadioButton):
            if radio_button.objectName() == obliview_type:
                radio_button.setChecked(True)
                break

        # -------------------------------------------------------------------------------------------------------------------------------------------
        self.buttonBox.accepted.connect(self.save_settings) # Zapisuje ustawienia po kliknięciu "OK"
        self.buttonBox.rejected.connect(self.reject) # Zamyka okno dialogowe po kliknięciu "Anuluj"

    # ===============================================================================================================================================
    def save_settings(self):
        """Zapisuje zmienione w oknie wartości z powrotem do konfiguracji."""

        plugin_config.data["obliview_selected_city"] = self.comboBoxObliView.currentText() # Pobiera aktualnie wybrane miasto z comboBoxa
        
        # -------------------------------------------------------------------------------------------------------------------------------------------
        # pobierz aktualnie zaznaczony radioButton z groupBoxObliViewType
        for radio_button in self.groupBoxObliViewType.findChildren(QRadioButton):
            if radio_button.isChecked():
                plugin_config.data["obliview_type"] = radio_button.objectName() # Zapisuje nazwę zaznaczonego radioButtona do konfiguracji
                break
        # -------------------------------------------------------------------------------------------------------------------------------------------

        plugin_config.save_config()

        plugin_config.read_config() # Wczytuje ponownie konfigurację, aby zaktualizować pełny URL do portalu ObliView

        self.accept() # Zamyka okno dialogowe z wynikiem QDialog.Accepted
