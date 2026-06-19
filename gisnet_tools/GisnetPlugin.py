import os

from qgis.PyQt.QtCore import Qt, QSettings # type: ignore
from qgis.PyQt.QtGui import QIcon # type: ignore
from qgis.PyQt.QtWidgets import QAction, QInputDialog, QMessageBox, QToolBar # type: ignore

from .OtworzObliviewTool import OtworzObliviewTool
from .FiltrObrebTool import uruchom_filtr_obrebu


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

        self.dodaj_przycisk_do_paska(
            ikona_nazwa="filtr_obrebu.png",
            tekst="Filtruj obręb",
            metoda_callback=self.filtruj_obreb,
            status_tip="Filtruje warstwy projektu po KOD_OBREBU",
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

    def filtruj_obreb(self):
        """Pyta o kod obrębu, zapamiętuje go i uruchamia filtrację warstw."""
        settings = QSettings()
        last_obreb = settings.value("GISNET_QTools/last_obreb", "", type=str)

        kod_obrebu, ok = QInputDialog.getText(
            self.iface.mainWindow(),
            "Filtracja po obrębie",
            "Podaj kod obrębu (KOD_OBREBU):",
            text=last_obreb,
        )

        if not ok:
            return

        kod_obrebu = kod_obrebu.strip()
        if not kod_obrebu:
            QMessageBox.warning(self.iface.mainWindow(), "Brak danych", "Wpisz kod obrębu.")
            return

        settings.setValue("GISNET_QTools/last_obreb", kod_obrebu)

        try:
            uruchom_filtr_obrebu(kod_obrebu, self.iface)
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), "Błąd filtrowania", str(e))
