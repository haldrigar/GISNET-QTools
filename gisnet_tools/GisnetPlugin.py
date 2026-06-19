import os
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QMessageBox

# IMPORT TWOJEGO WŁASNEGO NARZĘDZIA Z ZEWNĘTRZNEGO PLIKU
from .OtworzObliviewTool import OtworzObliviewTool

class GisnetPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Przechowujemy referencje do paska i akcji, aby móc je posprzątać przy wyłączaniu
        self.toolbar = None
        self.actions = []

        # Deklaracja zmiennej przechowującej instancję naszego narzędzia klikania
        self.this_tool = None

    def initGui(self):
        """Metoda wywoływana podczas uruchamiania wtyczki w QGIS."""
        
        # 1. TWORZENIE WŁASNEGO TOOLBARU
        # Sprawdzamy najpierw, czy taki pasek już nie istnieje w oknie głównym QGIS
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, "GISNETToolbar")
        
        if not self.toolbar:
            self.toolbar = QToolBar("GISNET", self.iface.mainWindow())
            self.toolbar.setObjectName("GISNETToolbar")
            # Dodajemy pasek do obszaru pasków narzędziowych QGIS
            self.iface.mainWindow().addToolBar(Qt.TopToolBarArea, self.toolbar)

        # 2. DODAWANIE KOLEJNYCH PRZYCISKÓW (AKCJI) DO PASKA
        
        # ObliView Gdańsk
        self.dodaj_przycisk_do_paska(
            ikona_nazwa="obliview.png",
            tekst="ObliView Gdańsk",
            metoda_callback=self.obliview_gdansk,
            status_tip="Uruchom portal ObliView Gdańska we wskazanym miejscu"
        )

    def dodaj_przycisk_do_paska(self, ikona_nazwa, tekst, metoda_callback, status_tip=""):
        # Ścieżka do ikony w folderze wtyczki
        sciezka_ikony = os.path.join(self.plugin_dir, 'ikony', ikona_nazwa)
        
        # Jeśli plik ikony nie istnieje, QGIS użyje domyślnego wyglądu przycisku tekstowego
        icon = QIcon(sciezka_ikony) if os.path.exists(sciezka_ikony) else QIcon()
        
        # Tworzenie akcji
        akcja = QAction(icon, tekst, self.iface.mainWindow())
        akcja.setStatusTip(status_tip)
        akcja.triggered.connect(metoda_callback)
        
        # Dodanie akcji do naszego paska narzędzi
        self.toolbar.addAction(akcja)
        
        # Zapisujemy referencję do listy, żeby móc ją usunąć w unload()
        self.actions.append(akcja)

    def unload(self):
        # 1. Usuwamy wszystkie przyciski z paska
        if self.toolbar:
            for action in self.actions:
                self.toolbar.removeAction(action)
            
            # 2. Usuwamy sam pasek narzędzi z interfejsu QGIS
            self.iface.mainWindow().removeToolBar(self.toolbar)
            self.toolbar.deleteLater()
            
        self.actions.clear()

    # --- MIEJSCE NA TWOJE FUNKCJONALNOŚCI (CALLBACKI) ---

    def obliview_gdansk(self):
        """Uruchamia dedykowane narzędzie wyboru punktu na mapie."""
        # Tworzymy instancję narzędzia podając aktualne płótno mapy
        self.this_tool = OtworzObliviewTool(self.iface.mapCanvas())
        # Ustawiamy narzędzie jako aktywne w QGIS (kursor zmieni się, czekając na kliknięcie)
        self.iface.mapCanvas().setMapTool(self.this_tool)