import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QInputDialog, QMessageBox, QToolBar

from .tools.Obliview import Obliview
from .tools.FilterProject import set_project_filter
from .tools.ClipboardZoom import ClipboardZoom
from .tools.Config import plugin_config

from .ui.settings import SettingsDialog

class GisnetQTools:

    # ===============================================================================================================================================
    def __init__(self, iface):
        """Klasa reprezentująca wtyczkę GISNET dla QGIS."""

        self.iface = iface # Zapisuje referencję do interfejsu QGIS, aby wtyczka mogła korzystać z funkcji QGIS

        self.plugin_dir = os.path.dirname(__file__) # Ścieżka do katalogu wtyczki

        self.toolbar = None # QToolBar
        self.toolbar_created_by_plugin = False # Flaga informująca, czy pasek narzędzi został utworzony przez wtyczkę
        self.actions = [] # Lista akcji dodanych do paska narzędzi

        self.obliviewTool = None # Narzędzie mapowe do otwierania ObliView dla klikniętego punktu

        self.filter_button_action = None # Przycisk filtrowania warstw projektu po KOD_OBREBU, który może być dodany lub usunięty w zależności od ustawień wtyczki

        # --- Inicjalizacja modułu schowka ---
        self.clipboard_zoom_handler = ClipboardZoom(self.iface)

    # ===============================================================================================================================================
    def initGui(self):
        """ Metoda initGui jest wywoływana podczas inicjalizacji wtyczki i służy do tworzenia paska narzędzi oraz dodawania przycisków do tego paska. """

        self.toolbar = QToolBar("GISNET", self.iface.mainWindow()) # Tworzymy nowy pasek narzędzi o nazwie "GISNET" i przypisujemy go do głównego okna QGIS

        toolbar_area = Qt.ToolBarArea.TopToolBarArea # Określamy, że pasek narzędzi ma być umieszczony w górnej części okna QGIS

        self.iface.mainWindow().addToolBar(toolbar_area, self.toolbar) # Dodajemy pasek narzędzi do głównego okna QGIS w określonym obszarze (górnym)

        self.toolbar_created_by_plugin = True # Flaga informująca, że pasek narzędzi został utworzony przez wtyczkę

        # Dodaj przycisk do paska narzędzi, który uruchamia narzędzie ObliView
        self.add_button_to_toolbar(
            ikona_nazwa="obliview.png",
            tekst="ObliView",
            metoda_callback=self.toolbar_obliview_click,
            status_tip="Uruchom portal ObliView we wskazanym miejscu",
        )

        # Dodaj przycisk do paska narzędzi, który uruchamia filtrację warstw projektu po KOD_OBREBU, jeśli opcja jest włączona w ustawieniach
        if plugin_config.data.get("gdansk_filter_enabled"):
            self.filter_button_action = self.add_button_to_toolbar(
                ikona_nazwa="filter.png",
                tekst="Filtruj obręb",
                metoda_callback=self.toolbar_set_project_filter_click,
                status_tip="Filtruje warstwy projektu po KOD_OBREBU",
            )

        # Dodaj przycisk ustawień wtyczki
        self.add_button_to_toolbar(
            ikona_nazwa="settings.png",
            tekst="Ustawienia",
            metoda_callback=self.toolbar_settings_click,
            status_tip="Otwiera okno ustawień wtyczki",
        )

    # ===============================================================================================================================================
    def add_button_to_toolbar(self, ikona_nazwa, tekst, metoda_callback, status_tip=""):
        """Dodaje przycisk do paska narzędzi wtyczki."""

        sciezka_ikony = os.path.join(self.plugin_dir, "icons", ikona_nazwa)
        icon = QIcon(sciezka_ikony) if os.path.exists(sciezka_ikony) else QIcon()

        akcja = QAction(icon, tekst, self.iface.mainWindow())
        akcja.setStatusTip(status_tip)
        akcja.triggered.connect(metoda_callback)

        self.toolbar.addAction(akcja)
        self.actions.append(akcja)

        return akcja

    # ===============================================================================================================================================
    def toolbar_obliview_click(self):
        """Uruchamia dedykowane narzędzie wyboru punktu na mapie."""

        # Jeśli narzędzie ObliView nie zostało jeszcze utworzone, tworzymy je
        if self.obliviewTool is None:
            self.obliviewTool = Obliview(self.iface.mapCanvas(), self.iface)

        self.iface.mapCanvas().setMapTool(self.obliviewTool) # Ustawiamy narzędzie mapy na ObliView, aby użytkownik mógł wybrać punkt na mapie

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

        if dialog.exec(): # Zamyka okno dialogowe z wynikiem QDialog.Accepted
            self.update_filter_button_visibility()  # Aktualizuj widoczność przycisku

            self.iface.messageBar().pushMessage("GISNET QTools", "Pomyślnie zaktualizowano konfigurację.", duration=3)

    # ===============================================================================================================================================
    def update_filter_button_visibility(self):
        """Aktualizuje widoczność przycisku filtrowania na podstawie ustawień."""

        is_enabled = plugin_config.data.get("gdansk_filter_enabled", False) # Pobiera wartość z konfiguracji wtyczki, która określa, czy filtracja Gdańsk jest włączona

        if is_enabled and self.filter_button_action is None:
            # Dodaj przycisk do paska narzędzi, jeśli jest włączony w ustawieniach i nie został jeszcze dodany
            self.filter_button_action = self.add_button_to_toolbar(
                ikona_nazwa="filter.png",
                tekst="Filtruj obręb",
                metoda_callback=self.toolbar_set_project_filter_click,
                status_tip="Filtruje warstwy projektu po KOD_OBREBU",
            )
        elif not is_enabled and self.filter_button_action is not None:
            # Ukryj przycisk - usuń go z paska narzędzi
            self.toolbar.removeAction(self.filter_button_action)
            self.actions.remove(self.filter_button_action)
            self.filter_button_action.deleteLater() # Usuń akcję z pamięci
            self.filter_button_action = None

    # ===============================================================================================================================================
    def unload(self):
        """Czyści akcje i pasek narzędzi podczas wyłączania wtyczki."""

        # 1. Czyszczenie modułu schowka
        if hasattr(self, "clipboard_zoom_handler") and self.clipboard_zoom_handler:
            self.clipboard_zoom_handler.cleanup()
            self.clipboard_zoom_handler = None

        # 2. Czyszczenie narzędzia ObliView
        if self.obliviewTool:
            if self.iface.mapCanvas().mapTool() == self.obliviewTool:
                self.iface.mapCanvas().unsetMapTool(self.obliviewTool)

            self.obliviewTool.deleteLater()
            self.obliviewTool = None

        # 3. Czyszczenie paska i akcji
        if self.toolbar:
            for action in self.actions:
                self.toolbar.removeAction(action)
                action.deleteLater()  # Zwolnienie pamięci C++

            if self.toolbar_created_by_plugin:
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.deleteLater()

        self.actions.clear()
        self.toolbar = None
        self.filter_button_action = None
