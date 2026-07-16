import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QInputDialog, QMessageBox, QToolBar

from .tools.Obliview import Obliview
from .tools.FilterProject import set_project_filter
from .tools.Config import plugin_config
from .ui.settings import SettingsDialog

class GisnetQTools:

    # ===============================================================================================================================================
    def __init__(self, iface): 
        """Klasa reprezentująca wtyczkę GISNET dla QGIS."""

        # save reference to the QGIS interface
        self.iface = iface

        self.plugin_dir = os.path.dirname(__file__) # Ścieżka do katalogu wtyczki

        self.toolbar = None # QToolBar
        self.toolbar_created_by_plugin = False # Flaga informująca, czy pasek narzędzi został utworzony przez wtyczkę
        self.actions = [] # Lista akcji dodanych do paska narzędzi
        
        self.this_tool = None # Narzędzie mapy (QgsMapTool) używane przez wtyczkę

    # ===============================================================================================================================================
    def initGui(self): 
        """ Metoda initGui jest wywoływana podczas inicjalizacji wtyczki i służy do tworzenia paska narzędzi oraz dodawania przycisków do tego paska. """
        
        self.toolbar = QToolBar("GISNET", self.iface.mainWindow()) # Tworzymy nowy pasek narzędzi o nazwie "GISNET" i przypisujemy go do głównego okna QGIS

        #self.iface.mainWindow().addToolBar(Qt.TopToolBarArea, self.toolbar) # Dodajemy pasek narzędzi do głównego okna QGIS w górnej części interfejsu (Qt.TopToolBarArea)

        # Kompatybilność Qt5/Qt6 (QGIS 3/4):
        # - Qt6: Qt.ToolBarArea.TopToolBarArea
        # - Qt5: Qt.TopToolBarArea
        try:
            toolbar_area = Qt.ToolBarArea.TopToolBarArea
        except AttributeError:
            toolbar_area = Qt.TopToolBarArea

        self.iface.mainWindow().addToolBar(toolbar_area, self.toolbar)

        self.toolbar_created_by_plugin = True # Flaga informująca, że pasek narzędzi został utworzony przez wtyczkę

        # Dodajemy przyciski do paska narzędzi
        self.add_button_to_toolbar(
            ikona_nazwa="obliview.png",
            tekst="ObliView",
            metoda_callback=self.toolbar_obliview_click,
            status_tip="Uruchom portal ObliView we wskazanym miejscu",
        )

        self.add_button_to_toolbar(
            ikona_nazwa="filter.png",
            tekst="Filtruj obręb",
            metoda_callback=self.toolbar_set_project_filter_click,
            status_tip="Filtruje warstwy projektu po KOD_OBREBU",
        )

        self.add_button_to_toolbar(
            ikona_nazwa="settings.png",
            tekst="Ustawienia",
            metoda_callback=self.toolbar_settings_click,
            status_tip="Otwiera okno ustawień wtyczki",
        )

    # ===============================================================================================================================================
    def toolbar_obliview_click(self):
        """Uruchamia dedykowane narzędzie wyboru punktu na mapie."""

        self.this_tool = Obliview(self.iface.mapCanvas(), self.iface)
        self.iface.mapCanvas().setMapTool(self.this_tool)

    # ===============================================================================================================================================
    def toolbar_set_project_filter_click(self):
        """Pyta o kod obrębu, zapamiętuje go i uruchamia filtrację warstw."""

        last_obreb = plugin_config.data.get("obreb") # Pobiera ostatnio używany kod obrębu z konfiguracji wtyczki

        # Wyświetla okno dialogowe z polem tekstowym, w którym użytkownik może wpisać kod obrębu. Wartość domyślna to ostatnio używany kod obrębu.
        kod_obrebu, ok = QInputDialog.getText(self.iface.mainWindow(), "Filtruj po obrębie", "Podaj kod obrębu (KOD_OBREBU):", text=last_obreb) 

        if not ok: # Użytkownik anulował wprowadzanie danych, więc kończymy działanie funkcji
            return

        kod_obrebu = kod_obrebu.strip() # Usuwamy białe znaki z początku i końca wprowadzonego tekstu

        if not kod_obrebu:
            QMessageBox.warning(self.iface.mainWindow(), "Brak danych", "Wpisz kod obrębu.")
            return

        # Zapamiętuje w konfiguracji wtyczki ostatnio używany kod obrębu, aby przy następnym uruchomieniu funkcji był on podpowiadany jako wartość domyślna.
        plugin_config.data["obreb"] = kod_obrebu # Zapisuje kod obrębu w konfiguracji wtyczki
        plugin_config.save_config()

        try:
            set_project_filter(kod_obrebu, self.iface)
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), "Błąd filtrowania", str(e))

    # ===============================================================================================================================================
    def toolbar_settings_click(self):
        """Otwiera okno ustawień wtyczki."""

        dialog = SettingsDialog(self.iface.mainWindow())

        # W Qt6 / PyQt6 usunięto podkreślenie na końcu nazwy metody - używamy exec() zamiast exec_()
        if dialog.exec(): # Zamyka okno dialogowe z wynikiem QDialog.Accepted
            self.iface.messageBar().pushMessage("GISNET QTools", "Pomyślnie zaktualizowano konfigurację.", duration=3)

    # ===============================================================================================================================================
    def add_button_to_toolbar(self, ikona_nazwa, tekst, metoda_callback, status_tip=""):
        """Dodaje przycisk do paska narzędzi wtyczki."""

        sciezka_ikony = os.path.join(self.plugin_dir, "icons", ikona_nazwa)
        icon = QIcon(sciezka_ikony) if os.path.exists(sciezka_ikony) else QIcon()

        akcja = QAction(icon, tekst, self.iface.mainWindow())
        akcja.setStatusTip(status_tip)
        akcja.triggered.connect(metoda_callback)

        self.toolbar.addAction(akcja) # Dodajemy akcję do paska narzędzi
        self.actions.append(akcja) # Dodajemy akcję do listy akcji wtyczki, aby móc je później usunąć podczas wyłączania wtyczki

    # ===============================================================================================================================================
    def unload(self):
        """Czyści akcje i pasek narzędzi podczas wyłączania wtyczki."""

        if self.toolbar:
            for action in self.actions:
                self.toolbar.removeAction(action)

            if self.toolbar_created_by_plugin:
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.deleteLater()

        self.actions.clear()
        self.toolbar = None
        self.toolbar_created_by_plugin = False
        self.this_tool = None