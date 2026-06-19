# import os; from qgis.core import QgsProject; f = open(os.path.join(QgsProject.instance().homePath(), 'filtr.py'), encoding='utf-8'); exec(f.read(), globals()); f.close()

from qgis.core import QgsProject # type: ignore
from qgis.utils import iface # type: ignore

# ==========================================
# TUNING: TUTAJ WPISZ SWÓJ KOD OBRĘBU
# ==========================================
KOD_OBREBU = '226101_1.0303'
# ==========================================

# FUNKCJA
def aplikuj_i_odswiez(nazwa_warstwy, kolumna_id):
    layers = QgsProject.instance().mapLayersByName(nazwa_warstwy)
    if layers:
        lyr = layers[0]
        lyr.setSubsetString(f'"{kolumna_id}" LIKE \'%{KOD_OBREBU}%\'')
    else:
        print(f"Ominięto: {nazwa_warstwy} (brak warstwy w projekcie)")
        
# 1. Pobierz aktualne metadane projektu
metadata = QgsProject.instance().metadata()

# 2. Ustaw nowy tytuł projektu
NOWY_TYTUL = f"Obręb: {KOD_OBREBU}"
metadata.setTitle(NOWY_TYTUL)

# 3. Zapisz zmodyfikowane metadane z powrotem do projektu
QgsProject.instance().setMetadata(metadata)
        
# AKTUALIZACJA WARSTW
aplikuj_i_odswiez('EGB_Budynek', 'idBudynku')
aplikuj_i_odswiez('EGB_DzialkaEwidencyjna', 'idDzialki')
aplikuj_i_odswiez('EGB_ObrebEwidencyjny', 'idObrebu')
aplikuj_i_odswiez('EGB_KonturUzytkuGruntowego', 'idUzytku')
aplikuj_i_odswiez('EGB_KonturKlasyfikacyjny', 'idKonturu')
aplikuj_i_odswiez('EGB_PunktGraniczny', 'idPunktu')

aplikuj_i_odswiez('EGB_opisyKARTO', 'teryt')
aplikuj_i_odswiez('EGB_BlokBudynku_1', 'teryt')
aplikuj_i_odswiez('EGB_BlokBudynku_2', 'teryt')
aplikuj_i_odswiez('EGB_ObiektTrwaleZwiazanyZBudynkiem_0', 'teryt')
aplikuj_i_odswiez('EGB_ObiektTrwaleZwiazanyZBudynkiem_1', 'teryt')
aplikuj_i_odswiez('EGB_ObiektTrwaleZwiazanyZBudynkiem_2', 'teryt')

aplikuj_i_odswiez('EGB_PrezentacjaGraficzna', 'teryt')
aplikuj_i_odswiez('EGB_odnosnik', 'teryt')
aplikuj_i_odswiez('EGB_poliliniaKierunkowa', 'teryt')
      
# 1. Pobierz ścieżkę do aktualnego pliku projektu
sciezka_pliku = QgsProject.instance().fileName()

if sciezka_pliku:
    # 2. ZAPISZ projekt na dysku
    print("Zapis projektu na dysk...")
    QgsProject.instance().write()
        
    # 3. ODCZYTAJ projekt ponownie z dysku
    print("Wczytywanie projektu...")
    QgsProject.instance().read(sciezka_pliku)
    
    # 4. ZOOM DO NOWYCH DZIAŁEK (Zanim odświeżymy widok!)
    dzialki_layers = QgsProject.instance().mapLayersByName('EGB_DzialkaEwidencyjna')
    if dzialki_layers:
        lyr_dzialka = dzialki_layers[0]
        zasieg = lyr_dzialka.extent()
        
        if not zasieg.isEmpty():
            iface.mapCanvas().setExtent(zasieg)
    
    # 5. Wyczyść cache płótna i odśwież widok
    print("Odświeżanie widoku...")
    iface.mapCanvas().clearCache()
    iface.mapCanvas().refreshAllLayers()
        
    print(f"Projekt wczytano dla obrębu {KOD_OBREBU}!")
   
else:
    # Zabezpieczenie na wypadek, gdyby projekt był zupełnie nowy i nienazwany
    print("BŁĄD: Projekt nie jest jeszcze zapisany na dysku (jest bez nazwy).")
    print("Zapisz go ręcznie chociaż raz (Projekt -> Zapisz jako...), aby skrypt znał jego ścieżkę.")