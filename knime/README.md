# Wizualizacja w KNIME Analytics Platform

Etap 7 projektu: *import danych z minimum dwóch różnych źródeł, zestawienie wyników algorytmów uczenia maszynowego i grupowania, wizualizacja wyników w formie wykresów* — platforma **KNIME Analytics Platform 5.12**.

**Autorzy:** Adrian Tusiński, Aleksander Klank

## Gotowy workflow

| Plik | Opis |
|---|---|
| `dostepnosc_mieszkan.knwf` | wyeksportowany workflow (z danymi i wykonanymi węzłami) — do oddania / importu |
| `dostepnosc_mieszkan/` | ten sam workflow jako folder |
| `data/` | dane wejściowe (generuje je notebook `07_wizualizacja_i_prezentacja.ipynb`) |

**Otwarcie:** w KNIME *File → Import KNIME Workflow…* → wybierz `dostepnosc_mieszkan.knwf` (albo przeciągnij plik do okna KNIME). Workflow jest już wykonany — widok każdego wykresu otwiera się po zaznaczeniu węzła w panelu pod canvasem, a w większym oknie przyciskiem *Open in new window*. Dane są w folderze danych workflow, więc działa na każdym komputerze bez zmiany ścieżek.

## Struktura workflow (18 węzłów, wszystkie wykonane)

```
                     [Color Palette Designer]─┐
[CSV Reader: oferty (źródło 1)]──┬─[Color Designer (Apply): segment_rynku]──[Scatter Plot: segmenty K-means w rzucie PCA]
                                 └───────────────[Joiner city = miasto_klucz]──[Math Formula]──[Bar Chart P1: pensje na ofertę]
[Excel Reader: koszty życia (źródło 2)]──[String Manipulation: klucz miasta]──┘

[CSV Reader: wskaźniki miast]──┬─[Bar Chart: pensje na 50 m²]          (P1)
                               ├─[Bar Chart: rentowność najmu]         (P2)
                               ├─[Bar Chart: lata na wkład 20%]        (P4)
                               └─[Color Designer (Apply): grupa_miast]──[Scatter Plot: pensja vs dostępność] (P5)
                                   [Color Palette Designer]─┘

[CSV Reader: wyniki ML i grupowania]──[Table View: zestawienie wyników]
```

| Węzeł | Rola |
|---|---|
| **CSV Reader** — `oferty_segmenty.csv` | źródło 1: 20 tys. ofert z ceną, cechami, segmentem K-means i składowymi PCA |
| **Excel Reader** — `koszty_zycia_miasta.xlsx`, arkusz `koszty_2024` | źródło 2: płace i koszty życia (GUS/Numbeo) |
| **String Manipulation** | standaryzacja klucza: `replace(removeDiacritic(lowerCase($city$)), "ł", "l")` → `Kraków` → `krakow` |
| **Joiner** | połączenie źródeł: `city` (oferty) = `miasto_klucz` (koszty życia), inner join |
| **Math Formula** | `$price$ / $median_salary_net_pln$` → `liczba_pensji_oferta` (ile pensji netto kosztuje oferta) |
| **Color Palette Designer** (×2) + **Color Designer (Apply)** (×2) | przypisanie kolorów (paleta Brewer Set 1) do `segment_rynku` i `grupa_miast` — bez tego Scatter Plot nie może kolorować punktów według grup |
| **Bar Chart** (×4) | P1 — średnia liczba pensji na ofertę w mieście (z połączonych źródeł, agregacja *Average*) i pensje na 50 m²; P2 — rentowność najmu; P4 — lata zbierania na wkład |
| **Scatter Plot** (×2) | segmenty rynku K-means w rzucie PCA; pensja vs dostępność z kolorem grupy miast K-means |
| **Table View** | zestawienie metryk: drzewo decyzyjne (R², MAE, accuracy, F1), K-means/Ward (silhouette, ARI) |

## Zrzuty ekranu (KNIME 5.12, test 22.11.2026)

Workflow otwarty z *Local space* w KNIME Analytics Platform 5.12 — wszystkie 18 węzłów wykonanych (zielone światła).

![Workflow — 18 węzłów](screenshots/workflow.jpg)

**Bar Chart — P1: średnia liczba pensji netto na ofertę (oferty ⋈ koszty życia)**

![Bar Chart P1 — pensje na ofertę](screenshots/bar_chart_p1_pensje_na_oferte.jpg)

**Bar Chart — P1: ile pensji netto kosztuje mieszkanie 50 m²**

![Bar Chart P1 — pensje na 50 m²](screenshots/bar_chart_p1_pensje_50m2.jpg)

**Bar Chart — P2: rentowność najmu brutto [%]**

![Bar Chart P2](screenshots/bar_chart_p2_rentownosc_najmu.jpg)

**Bar Chart — P4: lata oszczędzania na wkład 20%**

![Bar Chart P4](screenshots/bar_chart_p4_lata_na_wklad.jpg)

**Scatter Plot — segmenty ofert K-means w rzucie PCA (PC1 × PC2)**

![Scatter Plot segmenty](screenshots/scatter_segmenty_kmeans_pca.jpg)

**Scatter Plot — P5: pensja netto vs liczba pensji na 50 m², kolor = grupa miast K-means**

![Scatter Plot P5](screenshots/scatter_p5_pensja_vs_dostepnosc.jpg)

**Table View — zestawienie wyników uczenia maszynowego i grupowania**

![Table View](screenshots/table_view_zestawienie_wynikow.jpg)

### Poprawki po teście (22.11.2026)

- **Bar Chart „P1: pensje na ofertę (KNIME)”** — zapisane ustawienie `aggregationMethod = AVERAGE` było nieprawidłowe dla KNIME 5.12 (poprawne: `AVG`), więc węzeł wracał do ustawień domyślnych. Ustawiono ponownie: *Category* = `city_label`, *Aggregation* = *Average*, *Frequency* = `liczba_pensji_oferta`.
- **Scatter Ploty** — kolumny koloru (`segment_rynku`, `grupa_miast`) nie miały przypisanych kolorów, więc wykresy były jednokolorowe. Przed każdym Scatter Plotem dodano parę **Color Palette Designer → Color Designer (Apply)** (w KNIME 5.12 zastępuje dawny Color Manager).

## Jak powstał

Workflow został wygenerowany i wykonany automatycznie (bez klikania) przez publiczne API KNIME: węzły utworzono programowo, ustawienia uzupełniono w plikach `settings.xml`, a całość wykonano w trybie bez interfejsu graficznego. Można go dowolnie edytować w KNIME jak każdy inny workflow. Poprawki po teście (Bar Chart P1 i węzły kolorów przed Scatter Plotami) wprowadzono ręcznie w KNIME 5.12.

## Ewentualne rozszerzenia w KNIME

- **Dashboard:** zaznacz węzły wykresów → prawy przycisk → *Create Component…* → w komponencie *Layout Editor* ułóż wykresy w siatce.
- **Odtworzenie algorytmów:** Normalizer → k-Means (k = 4) → Silhouette Coefficient na `miasta_wskazniki.csv`; Table Partitioner → Decision Tree Learner/Predictor → Scorer na połączonych ofertach.
