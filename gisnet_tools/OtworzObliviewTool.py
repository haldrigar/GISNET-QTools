import webbrowser
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.utils import iface

class OtworzObliviewTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        
    def canvasReleaseEvent(self, e):
        # 1. Pobierz punkt kliknięcia w układzie współrzędnych mapy
        punkt_klikniety = self.toMapCoordinates(e.pos())
        
        # 2. Zdefiniuj układy współrzędnych
        uklad_zrodlowy = QgsProject.instance().crs()
        uklad_docelowy = QgsCoordinateReferenceSystem("EPSG:3857") # WGS84 Web Mercator
        
        # 3. Przelicz współrzędne (transformacja)
        transformacja = QgsCoordinateTransform(uklad_zrodlowy, uklad_docelowy, QgsProject.instance())
        punkt_3857 = transformacja.transform(punkt_klikniety)
        
        # 4. Wyciągnij X i Y dla EPSG:3857
        x_3857 = punkt_3857.x()
        y_3857 = punkt_3857.y()
        
        # 5. Zbuduj adres URL do Obliview
        url = f"https://obliview.brg.gda.pl/?r=15&z=20&x={x_3857}&y={y_3857}"
        
        # 6. Otwórz w domyślnej przeglądarce internetowej
        webbrowser.open(url)
        
        # 7. Po kliknięciu przywracamy zwykłą rączkę/przesuwanie mapy
        iface.actionPan().trigger()