import re

from qgis.PyQt.QtCore import QObject, QTimer
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QApplication

from qgis.gui import QgsVertexMarker

from qgis.core import (Qgis, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY, QgsProject)

from .Config import plugin_config

class ClipboardZoom(QObject):
    """Klasa odpowiedzialna za monitorowanie schowka, parsowanie współrzędnych i zoomowanie mapy."""

    # ===============================================================================================================================================
    def __init__(self, iface, parent=None):
        """Inicjalizuje klasę ClipboardZoom, podłączając sygnał zmiany schowka do metody obsługi."""

        super().__init__(parent)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.clipboard = QApplication.clipboard()

        self._temp_marker = None # Obiekt tymczasowego markera, który jest wyświetlany na mapie po wklejeniu współrzędnych

        # Podłączenie sygnału schowka
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)

    # ===============================================================================================================================================
    def on_clipboard_changed(self):
        """Obsługuje zdarzenie zmiany zawartości schowka."""

        if not plugin_config.data.get("clipboard_monitoring_enabled", True): # Sprawdza, czy monitorowanie schowka jest włączone w konfiguracji
            return

        text = self.clipboard.text()

        # jeżeli tekst jest pusty lub nie zawiera współrzędnych, to nic nie robimy
        if not text:
            return

        point = self._parse_coordinates(text)
        if point is None:
            return

        # Wycentrowanie i ewentualny zoom
        self.canvas.setCenter(point)

        if plugin_config.data.get("clipboard_zoom_enabled", True): # Sprawdza, czy zoomowanie po wklejeniu współrzędnych jest włączone w konfiguracji
            try:
                zoom_scale = int(plugin_config.data.get("clipboard_zoom_scale"))
                self.canvas.zoomScale(zoom_scale)
            except (ValueError, TypeError):
                pass

        self.canvas.refresh()

        # Pokazanie tymczasowego markera punktowego
        self.show_temporary_marker(point, timeout_ms=2500)

    # ===============================================================================================================================================
    def _parse_coordinates(self, text):
        """Parsuje tekst ze schowka i transformuje współrzędne do CRS projektu."""

        text = text.strip() # Usunięcie białych znaków z początku i końca tekstu
        if not text:
            return None

        # Wyszukiwanie liczb (z kropką lub przecinkiem)
        numbers = re.findall(r"[-+]?\d+(?:[.,]\d+)?", text)

        if len(numbers) != 2: # Jeżeli nie znaleziono dokładnie dwóch liczb, to zwracamy None
            return None

        try: # Konwersja znalezionych liczb na float, zamieniając przecinki na kropki
            val1 = float(numbers[0].replace(",", "."))
            val2 = float(numbers[1].replace(",", "."))
        except ValueError:
            return None

        x, y = val1, val2

        return self._transform_to_project_crs(y, x) # Zamiana miejscami, bo w QGIS współrzędne są w formacie (y, x) w przeciwieństwie do standardowego (x, y) geodezyjnego zapisu.

    # ===============================================================================================================================================
    def _transform_to_project_crs(self, x, y):
        """Transformuje współrzędne (WGS84, PL-1992, PL-2000) do CRS aktywnego projektu."""

        source_crs = None
        point = QgsPointXY(y, x)

        # 1. WGS84 (EPSG:4326)
        if abs(x) <= 180 and abs(y) <= 90:
            source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            point = QgsPointXY(x, y)

        # 2. Układ PL-1992 (EPSG:2180)
        elif 100000 <= x <= 900000 and 100000 <= y <= 900000:
            source_crs = QgsCoordinateReferenceSystem("EPSG:2180")
            point = QgsPointXY(x, y)

        # 3. Układ PL-2000 (Strefy 5, 6, 7, 8 -> EPSG:2176, 2177, 2178, 2179)
        else:
            zone_digit = int(x // 1000000) # badamy po x, bo qgis ma współrzędne zamienione w stosunku do geodezyjnego zapisu
            zone_epsg_map = {
                5: "EPSG:2176",  # Strefa 5 (15°E)
                6: "EPSG:2177",  # Strefa 6 (18°E)
                7: "EPSG:2178",  # Strefa 7 (21°E)
                8: "EPSG:2179",  # Strefa 8 (24°E)
            }

            if zone_digit in zone_epsg_map:
                source_crs = QgsCoordinateReferenceSystem(zone_epsg_map[zone_digit])
                point = QgsPointXY(x, y)

        # Jeśli układ nie został rozpoznany, przyjmujemy domyślnie CRS projektu
        if source_crs is None:

            self.iface.messageBar().pushMessage(
                "GISNET QTools",
                "Nie rozpoznano układu współrzędnych (WGS84 / PL-1992 / PL-2000). Próba przybliżenia bez transformacji.",
                level=Qgis.MessageLevel.Warning,
                duration=3)

            return QgsPointXY(x, y)

        project_crs = QgsProject.instance().crs()

        if source_crs != project_crs:
            transform = QgsCoordinateTransform(source_crs, project_crs, QgsProject.instance())
            point = transform.transform(point)

        return point

    # ===============================================================================================================================================
    def show_temporary_marker(self, point, timeout_ms=2500):
        """Tworzy czerwony marker na płótnie mapy i usuwa go po czasie."""

        self.clear_marker()

        marker = QgsVertexMarker(self.canvas) # Tworzenie markera na płótnie mapy
        marker.setCenter(point)
        marker.setIconType(QgsVertexMarker.IconType.ICON_CROSS)
        marker.setIconSize(16)
        marker.setPenWidth(3)
        marker.setColor(QColor(255, 0, 0))
        marker.setFillColor(QColor(255, 0, 0, 80))

        self._temp_marker = marker

        # Timer Qt6 do czyszczenia
        QTimer.singleShot(timeout_ms, self.clear_marker)

    # ===============================================================================================================================================
    def clear_marker(self):
        """Usuwa marker z mapy."""

        if self._temp_marker is not None:
            self.canvas.scene().removeItem(self._temp_marker)
            self._temp_marker = None
            self.canvas.refresh()

    # ===============================================================================================================================================
    def cleanup(self):
        """Odłącza sygnały i czyści obiekty podczas wyłączania wtyczki."""

        try:
            self.clipboard.dataChanged.disconnect(self.on_clipboard_changed)
        except (TypeError, RuntimeError):
            pass

        self.clear_marker()
