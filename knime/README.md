# Wizualizacja w KNIME Analytics Platform

Etap 7 projektu: *import danych z minimum dwóch różnych źródeł, zestawienie wyników algorytmów uczenia maszynowego i grupowania, wizualizacja wyników w formie wykresów* — platforma **KNIME Analytics Platform 5.12**.

## Gotowy workflow

| Plik | Opis |
|---|---|
| `dostepnosc_mieszkan.knwf` | wyeksportowany workflow (z danymi i wykonanymi węzłami) — do oddania / importu |
| `dostepnosc_mieszkan/` | ten sam workflow jako folder |
| `data/` | dane wejściowe (generuje je notebook `07_wizualizacja_i_prezentacja.ipynb`) |

**Otwarcie:** w KNIME *File → Import KNIME Workflow…* → wybierz `dostepnosc_mieszkan.knwf` (albo przeciągnij plik do okna KNIME). Workflow jest już wykonany — widok każdego wykresu otwiera się przez kliknięcie węzła (*Open view* / F10). Dane są w folderze danych workflow, więc działa na każdym komputerze bez zmiany ścieżek.

## Struktura workflow (14 węzłów, wszystkie wykonane)

```
[CSV Reader: oferty (źródło 1)]──┬───────────────[Joiner city = miasto_klucz]──[Math Formula]──[Bar Chart P1]
                                 └─[Scatter Plot: segmenty K-means w rzucie PCA]      ▲
[Excel Reader: koszty życia (źródło 2)]──[String Manipulation: klucz miasta]─────────┘

[CSV Reader: wskaźniki miast]──┬─[Bar Chart: pensje na 50 m²]          (P1)
                               ├─[Bar Chart: rentowność najmu]         (P2)
                               ├─[Bar Chart: lata na wkład 20%]        (P4)
                               └─[Scatter Plot: pensja vs dostępność, kolor = grupa K-means] (P5)

[CSV Reader: wyniki ML i grupowania]──[Table View: zestawienie wyników]
```

| Węzeł | Rola |
|---|---|
| **CSV Reader** — `oferty_segmenty.csv` | źródło 1: 20 tys. ofert z ceną, cechami, segmentem K-means i składowymi PCA |
| **Excel Reader** — `koszty_zycia_miasta.xlsx`, arkusz `koszty_2024` | źródło 2: płace i koszty życia (GUS/Numbeo) |
| **String Manipulation** | standaryzacja klucza: `replace(removeDiacritic(lowerCase($city$)), "ł", "l")` → `Kraków` → `krakow` |
| **Joiner** | połączenie źródeł: `city` (oferty) = `miasto_klucz` (koszty życia), inner join |
| **Math Formula** | `$price$ / $median_salary_net_pln$` → `liczba_pensji_oferta` (ile pensji netto kosztuje oferta) |
| **Bar Chart** (×4) | P1 — średnia liczba pensji na ofertę (z połączonych źródeł) i pensje na 50 m²; P2 — rentowność najmu; P4 — lata zbierania na wkład |
| **Scatter Plot** (×2) | segmenty rynku K-means w rzucie PCA; pensja vs dostępność z kolorem grupy miast K-means |
| **Table View** | zestawienie metryk: drzewo decyzyjne (R², MAE, accuracy, F1), K-means/Ward (silhouette, ARI) |

## Jak powstał

Workflow został wygenerowany i wykonany automatycznie (bez klikania) przez publiczne API KNIME: węzły utworzono programowo, ustawienia uzupełniono w plikach `settings.xml`, a całość wykonano w trybie bez interfejsu graficznego. Można go dowolnie edytować w KNIME jak każdy inny workflow.

## Ewentualne rozszerzenia w KNIME

- **Dashboard:** zaznacz węzły wykresów → prawy przycisk → *Create Component…* → w komponencie *Layout Editor* ułóż wykresy w siatce.
- **Odtworzenie algorytmów:** Normalizer → k-Means (k = 4) → Silhouette Coefficient na `miasta_wskazniki.csv`; Table Partitioner → Decision Tree Learner/Predictor → Scorer na połączonych ofertach.
