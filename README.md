# GISNET-QTools

Wtyczka QGIS firmy GISNET do uruchamiania narzędzi pomocniczych bezpośrednio z poziomu mapy.

## Aktualne funkcje

- przycisk **ObliView Gdańsk** na pasku narzędzi QGIS,
- wybór punktu na mapie,
- przeliczenie współrzędnych do układu **EPSG:3857**,
- otwarcie portalu ObliView w przeglądarce dla wskazanej lokalizacji.

## Wymagania

- QGIS 3.x,
- Python dostarczany z QGIS,
- dostęp do internetu w celu otwarcia zewnętrznego portalu.

## Instalacja

1. Sklonuj repozytorium lub pobierz je jako ZIP.
2. Skopiuj katalog `gisnet_tools` do katalogu wtyczek QGIS.
3. Uruchom QGIS.
4. Włącz wtyczkę **GISNET QTools** w menedżerze wtyczek.

## Użycie

1. Kliknij przycisk **ObliView Gdańsk** na pasku narzędzi GISNET.
2. Kliknij wybrany punkt na mapie.
3. Wtyczka przeliczy współrzędne i otworzy lokalizację w ObliView.
4. Po zakończeniu narzędzie automatycznie wróci do trybu przesuwania mapy.

## Struktura projektu

- `gisnet_tools/GisnetPlugin.py` – inicjalizacja wtyczki i paska narzędzi,
- `gisnet_tools/OtworzObliviewTool.py` – narzędzie mapowe obsługujące kliknięcie i otwieranie ObliView,
- `gisnet_tools/metadata.txt` – metadane wtyczki.

## Sugestie dalszego rozwoju

- dodanie kolejnych narzędzi GISNET,
- konfiguracja parametrów URL z poziomu ustawień wtyczki,
- dodanie testów dla logiki budowania adresów URL,
- internacjonalizacja komunikatów użytkownika.
