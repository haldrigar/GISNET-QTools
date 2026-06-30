import webbrowser

from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt.QtWidgets import QMessageBox

from .Config import plugin_config

class Obliview(QgsMapToolEmitPoint):
    """Narzędzie mapowe otwierające ObliView dla klikniętego punktu."""

    TARGET_CRS = "EPSG:3857"

    # ===============================================================================================================================================
    def __init__(self, canvas, iface):
        """Inicjalizuje narzędzie mapowe dla portalu ObliView."""
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface

    # ===============================================================================================================================================
    def canvasReleaseEvent(self, event):
        """Obsługuje kliknięcie użytkownika na mapie."""
        try:
            clicked_point = self.toMapCoordinates(event.pos())
            point_3857 = self._transform_point_to_target_crs(clicked_point)
            url = self._build_obliview_url(point_3857.x(), point_3857.y())
            webbrowser.open(url)
        except Exception as exc:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "GISNET QTools",
                f"Nie udało się otworzyć ObliView: {exc}",
            )
        finally:
            self.iface.actionPan().trigger()

    # ===============================================================================================================================================
    def _transform_point_to_target_crs(self, point):
        """Transformuje punkt z CRS projektu do EPSG:3857 (Web Mercator)."""

        source_crs = QgsProject.instance().crs()
        target_crs = QgsCoordinateReferenceSystem(self.TARGET_CRS)
        transform = QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance())
        return transform.transform(point)

    # ===============================================================================================================================================
    @staticmethod
    def _build_obliview_url(x_coord, y_coord):
        """Buduje adres URL do portalu ObliView."""

        selected_city = plugin_config.data.get("obliview_selected_city")

        url = plugin_config.obliview_urls_list[selected_city]["url"]
        lvl_oblique = plugin_config.obliview_urls_list[selected_city]["lvl_oblique"]

        return f"{url}/?d=0&l=-1&r={lvl_oblique}&z=21&x={x_coord}&y={y_coord}"
