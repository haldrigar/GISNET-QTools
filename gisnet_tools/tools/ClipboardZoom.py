import re

from qgis.PyQt.QtCore import QObject, QTimer, Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QApplication
from qgis.gui import QgsVertexMarker
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject
)

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

        # Zakładamy domyślnie x=val1, y=val2 lub odwrotnie w zależności od zakresu
        x, y = val2, val1

        return self._transform_to_project_crs(x, y)

    # ===============================================================================================================================================
    def _transform_to_project_crs(self, x, y):
        """Transformuje współrzędne do układu odniesienia aktywnego projektu."""

        # Sprawdzenie, czy współrzędne mieszczą się w zakresie typowych układów odniesienia
        if abs(x) <= 180 and abs(y) <= 90: # Współrzędne w układzie geograficznym (EPSG:4326)
            source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            point = QgsPointXY(x, y)
        elif abs(y) <= 180 and abs(x) <= 90: # Współrzędne w układzie geograficznym (EPSG:4326) w odwrotnej kolejności
            source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            point = QgsPointXY(y, x)
        elif 100000 <= x <= 900000 and 100000 <= y <= 900000: # Współrzędne w układzie lokalnym (EPSG:2180)
            source_crs = QgsCoordinateReferenceSystem("EPSG:2180")
            point = QgsPointXY(x, y)
        else:
            # Jeżeli współrzędne nie mieszczą się w żadnym z powyższych zakresów, to zwracamy je bez transformacji
            return QgsPointXY(x, y)

        project_crs = QgsProject.instance().crs() # Pobranie układu odniesienia aktywnego projektu

        if source_crs != project_crs:
            transform = QgsCoordinateTransform(source_crs, project_crs, QgsProject.instance()) # Tworzenie transformacji współrzędnych z układu źródłowego do układu projektu
            point = transform.transform(point)

        return point

    # ===============================================================================================================================================
    def show_temporary_marker(self, point, timeout_ms=2500):
        """Tworzy czerwony marker na płótnie mapy i usuwa go po czasie."""

        self.clear_marker()

        marker = QgsVertexMarker(self.canvas) # Tworzenie markera na płótnie mapy
        marker.setCenter(point)
        marker.setIconType(QgsVertexMarker.ICON_CROSS)
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
