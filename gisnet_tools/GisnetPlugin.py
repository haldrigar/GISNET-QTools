import os

from qgis.PyQt.QtCore import Qt # type: ignore
from qgis.PyQt.QtGui import QIcon # type: ignore
from qgis.PyQt.QtWidgets import QAction, QToolBar # type: ignore

from .OtworzObliviewTool import OtworzObliviewTool


class GisnetPlugin:
    """Główna klasa wtyczki GISNET QTools."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.toolbar = None
        self.toolbar_created_by_plugin = False
        self.actions = []
        self.this_tool = None

    def initGui(self):
        """Metoda wywoływana podczas uruchamiania wtyczki w QGIS."""
        self.toolbar = self.iface.mainWindow().findChild(QToolBar, "GISNETToolbar")

        if not self.toolbar:
            self.toolbar = QToolBar("GISNET", self.iface.mainWindow())
            self.toolbar.setObjectName("GISNETToolbar")
            self.iface.mainWindow().addToolBar(Qt.TopToolBarArea, self.toolbar)
            self.toolbar_created_by_plugin = True

        self.dodaj_przycisk_do_paska(
            ikona_nazwa="obliview.png",
            tekst="ObliView Gdańsk",
            metoda_callback=self.obliview_gdansk,
            status_tip="Uruchom portal ObliView Gdańska we wskazanym miejscu",
        )

    def dodaj_przycisk_do_paska(self, ikona_nazwa, tekst, metoda_callback, status_tip=""):
        """Dodaje przycisk do paska narzędzi wtyczki."""
        sciezka_ikony = os.path.join(self.plugin_dir, "ikony", ikona_nazwa)
        icon = QIcon(sciezka_ikony) if os.path.exists(sciezka_ikony) else QIcon()

        akcja = QAction(icon, tekst, self.iface.mainWindow())
        akcja.setStatusTip(status_tip)
        akcja.triggered.connect(metoda_callback)

        self.toolbar.addAction(akcja)
        self.actions.append(akcja)

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

    def obliview_gdansk(self):
        """Uruchamia dedykowane narzędzie wyboru punktu na mapie."""
        self.this_tool = OtworzObliviewTool(self.iface.mapCanvas(), self.iface)
        self.iface.mapCanvas().setMapTool(self.this_tool)
