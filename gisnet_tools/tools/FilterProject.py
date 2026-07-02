from qgis.core import QgsProject, QgsMapLayerType
from qgis.PyQt.QtWidgets import QMessageBox

# ===================================================================================================================================================
# Funkcja uruchamiająca filtr obrębu
def set_project_filter(kod_obrebu, iface):
    """Ustawia filtr obrębu na wszystkie warstwy projektu QGIS i zapisuje projekt na dysku."""

    # ------------------------------------------- sprawdzanie, czy którakolwiek warstwa jest w trybie edycji ----------------------------------------
    # Pobierz wszystkie warstwy aktualnie załadowane do projektu QGIS
    all_layers = QgsProject.instance().mapLayers().values()

    # Lista, do której zbierzemy nazwy warstw z włączoną edycją
    active_edits_layers = []

    for warstwa in all_layers:
        # Tylko warstwy wektorowe mogą być edytowane (rastry pomijamy)
        if warstwa.type() == QgsMapLayerType.VectorLayer:
            # Sprawdzamy, czy warstwa jest w trybie edycji
            if warstwa.isEditable():
                active_edits_layers.append(warstwa.name())

    if active_edits_layers:
        # Tworzymy czytelną listę warstw oddzielonych przecinkami
        lista_nazw = "\n- ".join(active_edits_layers)
        
        QMessageBox.warning(
            None,
            "Wykryto otwartą edycję",
            f"Operacja została przerwana! Następujące warstwy są w trybie edycji:\n\n- {lista_nazw}\n\n"
            f"Zapisz zmiany lub wyłącz edycję dla tych warstw przed przeładowaniem projektu."
        )
        
        return  # Słowo kluczowe 'return' natychmiast przerywa i wychodzi z funkcji!

    # -------------------------------------------- filtorwanie warstw projektu QGIS po KOD_OBREBU ---------------------------------------------------

    # 1. Pobierz ścieżkę do aktualnego pliku projektu
    project_file_name = QgsProject.instance().fileName()

    if project_file_name:

        # 1. Pobierz aktualne metadane projektu
        metadata = QgsProject.instance().metadata()

        # 2. Ustaw nowy tytuł projektu
        nowy_tytul = f"Obręb: {kod_obrebu}"
        metadata.setTitle(nowy_tytul)

        # 3. Zapisz zmodyfikowane metadane z powrotem do projektu
        QgsProject.instance().setMetadata(metadata)

        # AKTUALIZACJA WARSTW
        set_layer_filter('EGB_Budynek', 'idBudynku', kod_obrebu)
        set_layer_filter('EGB_DzialkaEwidencyjna', 'idDzialki', kod_obrebu)
        set_layer_filter('EGB_ObrebEwidencyjny', 'idObrebu', kod_obrebu)
        set_layer_filter('EGB_KonturUzytkuGruntowego', 'idUzytku', kod_obrebu)
        set_layer_filter('EGB_KonturKlasyfikacyjny', 'idKonturu', kod_obrebu)
        set_layer_filter('EGB_PunktGraniczny', 'idPunktu', kod_obrebu)

        set_layer_filter('EGB_opisyKARTO', 'teryt', kod_obrebu)
        set_layer_filter('EGB_BlokBudynku_1', 'teryt', kod_obrebu)
        set_layer_filter('EGB_BlokBudynku_2', 'teryt', kod_obrebu)
        set_layer_filter('EGB_ObiektTrwaleZwiazanyZBudynkiem_0', 'teryt', kod_obrebu)
        set_layer_filter('EGB_ObiektTrwaleZwiazanyZBudynkiem_1', 'teryt', kod_obrebu)
        set_layer_filter('EGB_ObiektTrwaleZwiazanyZBudynkiem_2', 'teryt', kod_obrebu)

        set_layer_filter('EGB_PrezentacjaGraficzna', 'teryt', kod_obrebu)
        set_layer_filter('EGB_odnosnik', 'teryt', kod_obrebu)
        set_layer_filter('EGB_poliliniaKierunkowa', 'teryt', kod_obrebu)

        # 4. ZAPISZ projekt na dysku
        print("Zapis projektu na dysk...")
        QgsProject.instance().write()

        # 5. ODCZYTAJ projekt ponownie z dysku
        print("Wczytywanie projektu...")
        QgsProject.instance().read(project_file_name)

        # 6. ZOOM DO NOWYCH DZIAŁEK (Zanim odświeżymy widok!)
        dzialki_layers = QgsProject.instance().mapLayersByName('EGB_DzialkaEwidencyjna')

        if dzialki_layers:
            lyr_dzialka = dzialki_layers[0]
            zasieg = lyr_dzialka.extent()

            if not zasieg.isEmpty():
                iface.mapCanvas().setExtent(zasieg)

        print(f"Wczytano projekt dla obrębu {kod_obrebu}!")

    else:
        # Zabezpieczenie na wypadek, gdyby projekt był zupełnie nowy i nienazwany
        print("BŁĄD: Projekt nie jest jeszcze zapisany na dysku (jest bez nazwy).")
        print("Zapisz go ręcznie chociaż raz (Projekt -> Zapisz jako...), aby skrypt znał jego ścieżkę.")

# ===================================================================================================================================================
def set_layer_filter(nazwa_warstwy, kolumna_id, kod_obrebu):
    """Ustawia filtr na warstwę projektu QGIS, aby wyświetlała tylko obiekty pasujące do podanego kodu obrębu."""
    
    layers = QgsProject.instance().mapLayersByName(nazwa_warstwy) # Pobierz warstwę o podanej nazwie z projektu QGIS
    
    if layers:
        lyr = layers[0] # Pobierz pierwszą warstwę z listy (jeśli istnieje)

        # Ustaw filtr na warstwę, aby wyświetlała tylko obiekty pasujące do podanego kodu obrębu
        lyr.setSubsetString(f'"{kolumna_id}" LIKE \'%{kod_obrebu}%\'')
    else:
        print(f"Ominięto: {nazwa_warstwy} (brak warstwy w projekcie)")