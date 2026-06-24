from qgis.core import QgsProject # type: ignore


def aplikuj_i_odswiez(nazwa_warstwy, kolumna_id, kod_obrebu):
    
    layers = QgsProject.instance().mapLayersByName(nazwa_warstwy) # Pobierz warstwę o podanej nazwie z projektu QGIS
    
    if layers:
        lyr = layers[0] # Pobierz pierwszą warstwę z listy (jeśli istnieje)

        # Ustaw filtr na warstwę, aby wyświetlała tylko obiekty pasujące do podanego kodu obrębu
        lyr.setSubsetString(f'"{kolumna_id}" LIKE \'%{kod_obrebu}%\'')
    else:
        print(f"Ominięto: {nazwa_warstwy} (brak warstwy w projekcie)")

# Funkcja uruchamiająca filtr obrębu
def uruchom_filtr_obrebu(kod_obrebu, iface):
    
    # 1. Pobierz aktualne metadane projektu
    metadata = QgsProject.instance().metadata()

    # 2. Ustaw nowy tytuł projektu
    nowy_tytul = f"Obręb: {kod_obrebu}"
    metadata.setTitle(nowy_tytul)

    # 3. Zapisz zmodyfikowane metadane z powrotem do projektu
    QgsProject.instance().setMetadata(metadata)

    # AKTUALIZACJA WARSTW
    aplikuj_i_odswiez('EGB_Budynek', 'idBudynku', kod_obrebu)
    aplikuj_i_odswiez('EGB_DzialkaEwidencyjna', 'idDzialki', kod_obrebu)
    aplikuj_i_odswiez('EGB_ObrebEwidencyjny', 'idObrebu', kod_obrebu)
    aplikuj_i_odswiez('EGB_KonturUzytkuGruntowego', 'idUzytku', kod_obrebu)
    aplikuj_i_odswiez('EGB_KonturKlasyfikacyjny', 'idKonturu', kod_obrebu)
    aplikuj_i_odswiez('EGB_PunktGraniczny', 'idPunktu', kod_obrebu)

    aplikuj_i_odswiez('EGB_opisyKARTO', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_BlokBudynku_1', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_BlokBudynku_2', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_ObiektTrwaleZwiazanyZBudynkiem_0', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_ObiektTrwaleZwiazanyZBudynkiem_1', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_ObiektTrwaleZwiazanyZBudynkiem_2', 'teryt', kod_obrebu)

    aplikuj_i_odswiez('EGB_PrezentacjaGraficzna', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_odnosnik', 'teryt', kod_obrebu)
    aplikuj_i_odswiez('EGB_poliliniaKierunkowa', 'teryt', kod_obrebu)

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

        print(f"Projekt wczytano dla obrębu {kod_obrebu}!")

    else:
        # Zabezpieczenie na wypadek, gdyby projekt był zupełnie nowy i nienazwany
        print("BŁĄD: Projekt nie jest jeszcze zapisany na dysku (jest bez nazwy).")
        print("Zapisz go ręcznie chociaż raz (Projekt -> Zapisz jako...), aby skrypt znał jego ścieżkę.")
