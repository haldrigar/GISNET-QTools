from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsMapLayerType
from qgis.PyQt.QtWidgets import QMessageBox

# ===================================================================================================================================================
# Funkcja uruchamiająca filtr obrębu
def set_project_filter(kod_obrebu, iface):
    """Ustawia filtr obrębu na wszystkie warstwy projektu QGIS i zapisuje projekt na dysku."""

    # ------------------------------------------- sprawdzanie, czy którakolwiek warstwa jest w trybie edycji ----------------------------------------

    all_layers = QgsProject.instance().mapLayers().values()

    active_edits_layers = [] # Lista nazw warstw, które są w trybie edycji

    for warstwa in all_layers:
        if warstwa.type() == QgsMapLayerType.VectorLayer: # Sprawdzamy tylko warstwy wektorowe, ponieważ tylko one mogą być w trybie edycji
            if warstwa.isEditable(): # Sprawdzamy, czy warstwa jest w trybie edycji
                active_edits_layers.append(warstwa.name())

    # Jeżeli którakolwiek warstwa jest w trybie edycji, to wyświetlamy komunikat ostrzegawczy i przerywamy działanie funkcji
    if active_edits_layers:
        lista_nazw = "\n- ".join(active_edits_layers)

        QMessageBox.warning(
            None,
            "Wykryto otwartą edycję",
            f"Operacja została przerwana! Następujące warstwy są w trybie edycji:\n\n- {lista_nazw}\n\n"
            f"Zapisz zmiany lub wyłącz edycję dla tych warstw przed przeładowaniem projektu."
        )

        return # Przerywamy działanie funkcji, aby uniknąć utraty danych lub konfliktów podczas filtrowania warstw projektu QGIS

    # -------------------------------------------- filtorwanie warstw projektu QGIS po KOD_OBREBU ---------------------------------------------------

    # Pobierz ścieżkę do aktualnego pliku projektu
    project_file_name = QgsProject.instance().fileName()

    # Pobierz aktualne metadane projektu
    metadata = QgsProject.instance().metadata()

    # Ustaw nowy tytuł projektu
    nowy_tytul = f"Obręb: {kod_obrebu}"
    metadata.setTitle(nowy_tytul)

    # Zapisz zmodyfikowane metadane z powrotem do projektu
    QgsProject.instance().setMetadata(metadata)

    # AKTUALIZACJA WARSTW
    set_layer_filter('EGB_Budynek', 'idBudynku', kod_obrebu)
    set_layer_filter('EGB_DzialkaEwidencyjna', 'idDzialki', kod_obrebu)
    set_layer_filter('EGB_ObrebEwidencyjny', 'idObrebu', kod_obrebu)
    set_layer_filter('EGB_KonturUzytkuGruntowego', 'idUzytku', kod_obrebu)
    set_layer_filter('EGB_KonturKlasyfikacyjny', 'idKonturu', kod_obrebu)
    set_layer_filter('EGB_PunktGraniczny', 'idPunktu', kod_obrebu)

    set_layer_filter('EGB_opisyKARTO', 'teryt', kod_obrebu)
    set_layer_filter('EGB_AdresNieruchomosci', 'teryt', kod_obrebu)
    set_layer_filter('EGB_BlokBudynku_1', 'teryt', kod_obrebu)
    set_layer_filter('EGB_BlokBudynku_2', 'teryt', kod_obrebu)
    set_layer_filter('EGB_ObiektTrwaleZwiazanyZBudynkiem_0', 'teryt', kod_obrebu)
    set_layer_filter('EGB_ObiektTrwaleZwiazanyZBudynkiem_1', 'teryt', kod_obrebu)
    set_layer_filter('EGB_ObiektTrwaleZwiazanyZBudynkiem_2', 'teryt', kod_obrebu)

    set_layer_filter('EGB_PrezentacjaGraficzna', 'teryt', kod_obrebu)
    set_layer_filter('EGB_odnosnik', 'teryt', kod_obrebu)
    set_layer_filter('EGB_poliliniaKierunkowa', 'teryt', kod_obrebu)

    set_layer_filter('OT_BudynekNiewykazanyWEGIB', 'teryt', kod_obrebu)

    # ZAPISZ projekt na dysku
    QgsMessageLog.logMessage("Zapis projektu na dysk...", "GISNET QTools", level=Qgis.MessageLevel.Info)
    QgsProject.instance().write()

    # ODCZYTAJ projekt ponownie z dysku
    QgsMessageLog.logMessage("Wczytywanie projektu...", "GISNET QTools", level=Qgis.MessageLevel.Info)
    QgsProject.instance().read(project_file_name)

    # ZOOM DO NOWYCH DZIAŁEK (Zanim odświeżymy widok!)
    dzialki_layers = QgsProject.instance().mapLayersByName('EGB_DzialkaEwidencyjna')

    if dzialki_layers:
        lyr_dzialka = dzialki_layers[0]
        zasieg = lyr_dzialka.extent()

        if not zasieg.isEmpty():
            iface.mapCanvas().setExtent(zasieg)

    # Wyświetl komunikat w logu i na pasku komunikatów QGIS, że projekt został wczytany dla danego obrębu
    QgsMessageLog.logMessage(f"Wczytano projekt dla obrębu {kod_obrebu}!", "GISNET QTools", level=Qgis.MessageLevel.Info)

    iface.messageBar().pushMessage("Info", f"Wczytano projekt dla obrębu {kod_obrebu}!", level=Qgis.MessageLevel.Info, duration=3)



# ===================================================================================================================================================
def set_layer_filter(nazwa_warstwy, kolumna_id, kod_obrebu):
    """Ustawia filtr na warstwę projektu QGIS, aby wyświetlała tylko obiekty pasujące do podanego kodu obrębu."""

    layers = QgsProject.instance().mapLayersByName(nazwa_warstwy) # Pobierz warstwę o podanej nazwie z projektu QGIS

    if layers:
        lyr = layers[0] # Pobierz pierwszą warstwę z listy (jeśli istnieje)

        # Ustaw filtr na warstwę, aby wyświetlała tylko obiekty pasujące do podanego kodu obrębu
        lyr.setSubsetString(f'"{kolumna_id}" LIKE \'%{kod_obrebu}%\'')
    else:
        QgsMessageLog.logMessage(f"Ominięto: {nazwa_warstwy} (brak warstwy w projekcie)", "GISNET QTools", level=Qgis.MessageLevel.Warning)
