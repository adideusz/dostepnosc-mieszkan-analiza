# Wizualizacja w KNIME Analytics Platform — instrukcja budowy workflow

Etap 7 projektu: *import danych z minimum dwóch różnych źródeł, zestawienie wyników algorytmów uczenia maszynowego i grupowania, wizualizacja wyników w formie wykresów* na wybranej platformie — **KNIME Analytics Platform** (darmowa, działa na macOS/Windows/Linux, wersja 5.x).

Dane wejściowe są gotowe w `knime/data/` (generuje je notebook `07_wizualizacja_i_prezentacja.ipynb`).

| Plik | Źródło | Format | Opis |
|---|---|---|---|
| `oferty_segmenty.csv` | zbiór 1 — oferty mieszkań (Kaggle) + wyniki ML | **CSV** | 20 tys. ofert: cena, cechy, `segment_rynku` (K-means), `PC1`, `PC2` |
| `koszty_zycia_miasta.xlsx` | zbiór 2 — koszty życia i płace (GUS/Numbeo) | **Excel** | arkusz `koszty_2024` (15 miast), arkusz `szereg_2010_2024` |
| `miasta_wskazniki.csv` | połączenie zbiorów 1 + 2 | CSV | wskaźniki dostępności + `grupa_miast` (K-means) |
| `ceny_miesieczne.csv` | zbiór 1 | CSV | mediana ceny za m² per miasto i miesiąc |
| `predykcje_test.csv` | drzewo decyzyjne (etap 5) | CSV | cena rzeczywista vs przewidywana |
| `zestawienie_wynikow.csv` | etapy 5–6 | CSV | metryki modeli (R², MAE, accuracy, F1) i grupowania (silhouette, ARI) |

---

## 0. Przygotowanie

1. Zainstaluj KNIME ze strony knime.com (Download → KNIME Analytics Platform).
2. Utwórz nowy workflow: *File → New… → New KNIME Workflow*, nazwa `dostepnosc_mieszkan`.
3. Wszystkie węzły znajdziesz w panelu **Node Repository** (wyszukiwarka po nazwie). Węzły łączysz, przeciągając wyjście (trójkąt) na wejście kolejnego węzła. Konfiguracja: dwuklik na węźle. Uruchomienie: *F7* (Execute) albo *Shift+F7* (Execute All).

> Wskazówka: ścieżki do plików ustaw jako względne do workflow, albo wybierz pliki przyciskiem *Browse…* z katalogu `knime/data`.

---

## 1. Import danych z dwóch źródeł

| # | Węzeł | Konfiguracja |
|---|---|---|
| 1 | **CSV Reader** | plik `oferty_segmenty.csv`; separator `,`; *Has column header* ✔ |
| 2 | **Excel Reader** | plik `koszty_zycia_miasta.xlsx`; arkusz `koszty_2024`; *Table contains column names in row 1* ✔ |
| 3 | **CSV Reader** | plik `miasta_wskazniki.csv` |
| 4 | **CSV Reader** | plik `ceny_miesieczne.csv` |
| 5 | **CSV Reader** | plik `zestawienie_wynikow.csv` |
| 6 | **CSV Reader** | plik `predykcje_test.csv` |

Opisz węzły (dwuklik na podpisie pod węzłem), np. „Źródło 1: oferty (CSV)”, „Źródło 2: koszty życia (Excel)”.

## 2. ETL — standaryzacja klucza i połączenie źródeł

Klucz łączenia to nazwa miasta. W ofertach jest zapisana jako `krakow`, w Excelu jako `Kraków`.

| # | Węzeł | Wejście | Konfiguracja |
|---|---|---|---|
| 7 | **String Manipulation** | Excel Reader (2) | wyrażenie: `replace(removeDiacritic(lowerCase($city$)), "ł", "l")`; *Append column* → `city_key` |
| 8 | **Joiner** | górne wejście: CSV Reader (1), dolne: String Manipulation (7) | *Joiner settings*: `city` (top) = `city_key` (bottom); *Include in output*: matching rows (inner join); w zakładce *Column selection* z dolnej tabeli zostaw `median_salary_net_pln`, `cost_of_living_index`, `est_monthly_cost_single_pln`, `voivodeship` |
| 9 | **Math Formula** | Joiner (8) | wyrażenie: `$price$ / $median_salary_net_pln$`; nowa kolumna `liczba_pensji_oferta` (ile pensji netto kosztuje ta oferta) |
| 10 | **GroupBy** | Math Formula (9) | *Groups*: `city_label`; *Manual aggregation*: `price_per_m2` → Median, `liczba_pensji_oferta` → Median, `id` → Count, `median_salary_net_pln` → First |

Wynik węzła 10 to tabela miast powstała z **połączenia obu źródeł bezpośrednio w KNIME**. Możesz ją porównać z `miasta_wskazniki.csv` (powinny się zgadzać co do kolejności miast).

## 3. Kolory grup i segmentów

| # | Węzeł | Wejście | Konfiguracja |
|---|---|---|---|
| 11 | **Color Manager** | CSV Reader (3) — miasta | kolumna `grupa_miast`, paleta np. *Set2* |
| 12 | **Color Manager** | Joiner (8) — oferty | kolumna `segment_rynku` |

## 4. Wykresy (węzły z kategorii *Views*)

| # | Węzeł | Wejście | Konfiguracja | Pytanie analityczne |
|---|---|---|---|---|
| 13 | **Bar Chart** | Color Manager (11) | *Category column*: `miasto`; *Aggregation*: Sum; *Frequency column*: `miesiace_pensji_50m2`; orientacja pozioma; tytuł „Ile pensji netto kosztuje 50 m²?” | P1 |
| 14 | **Bar Chart** | CSV Reader (3) | kategoria `miasto`; wartości: `lata_wklad20_30proc_pensji`, `lata_wklad20_50proc_dysp` (dwie serie); tytuł „Lata oszczędzania na wkład 20%” | P4 |
| 15 | **Bar Chart** | CSV Reader (3) | kategoria `miasto`; wartość `rentownosc_brutto_proc`; tytuł „Rentowność najmu brutto [%]” | P2 |
| 16 | **Scatter Plot** | Color Manager (11) | X: `median_salary_net_pln`; Y: `miesiace_pensji_50m2`; kolor wg grupy; etykiety: `miasto`; tytuł „Pensja vs dostępność — grupy miast (K-means)” | P5 + grupowanie |
| 17 | **Box Plot** | Color Manager (12) | kolumna kategorii `segment_rynku`, wartość `price_index_city`; tytuł „Cena względem mediany miasta w segmentach rynku” | grupowanie |
| 18 | **Scatter Plot** | Color Manager (12) | X: `PC1`, Y: `PC2`; kolor wg `segment_rynku`; tytuł „Segmenty ofert w rzucie PCA” | PCA + grupowanie |
| 19 | **Box Plot** | Joiner (8) | kategoria `strefa` (centrum/pośrednia/peryferia), wartość `price_index_city` | P3 |
| 20 | **Pivot** → **Line Plot** | CSV Reader (4) | Pivot: *Groups* `period`, *Pivots* `city_label`, agregacja `mediana_cena_m2` → First; Line Plot: oś X `period`, serie — kolumny miast | dynamika cen |
| 21 | **Scatter Plot** | CSV Reader (6) | X: `price_per_m2`, Y: `pred_price_per_m2`; tytuł „Drzewo decyzyjne: cena rzeczywista vs przewidywana” | wynik ML |
| 22 | **Table View** | CSV Reader (5) | tytuł „Zestawienie wyników ML i grupowania” | zestawienie |
| 23 | **Bar Chart** | CSV Reader (2) — Excel | kategoria `city`, wartości `median_salary_net_pln` i `est_monthly_cost_single_pln` | dane źródłowe zbioru 2 |

## 5. Dashboard (komponent)

1. Zaznacz węzły widoków (13–23) → prawy przycisk → **Create Component…** → nazwa `Dashboard dostępności mieszkań`.
2. Wejdź do komponentu (*Ctrl/Cmd + dwuklik*) i otwórz **Layout Editor** (ikona siatki na pasku) — ułóż wykresy w siatce, np.:
   - wiersz 1: P1 (13) | P5 grupy miast (16)
   - wiersz 2: P2 rentowność (15) | P4 wkład własny (14)
   - wiersz 3: segmenty (17) | PCA (18)
   - wiersz 4: dynamika cen (20) | predykcje (21)
   - wiersz 5: tabela wyników (22)
3. Opcjonalnie dodaj **Text View** z tytułem i najważniejszymi wnioskami.
4. Uruchom komponent i otwórz widok (prawy przycisk → *Open view*). Z widoku możesz zapisać obrazy wykresów.

## 6. (Opcjonalnie) Odtworzenie algorytmów w KNIME

Aby pokazać, że wyniki z Pythona da się odtworzyć na platformie:

- **Grupowanie:** CSV Reader (3) → **Normalizer** (Z-score, kolumny wskaźników) → **k-Means** (k = 4) → **Silhouette Coefficient** → porównaj z `grupa_miast`.
  Grupowanie hierarchiczne: **Hierarchical Clustering (DistMatrix)** + **Distance Matrix Calculate** → widok dendrogramu.
- **Drzewo decyzyjne:** Joiner (8) → **Partitioning** (80/20, stratified by `city`) → **Simple Regression Tree Learner** (cel `price_per_m2`) → **Simple Regression Tree Predictor** → **Numeric Scorer** (R², MAE).
  Klasyfikacja: **Decision Tree Learner** (cel `segment_cenowy`) → **Decision Tree Predictor** → **Scorer** (macierz pomyłek, accuracy).

## 7. Eksport do oddania

- *File → Export KNIME Workflow…* → zaznacz `dostepnosc_mieszkan` → zapisz jako `knime/dostepnosc_mieszkan.knwf` (plik do wrzucenia na platformę / do repozytorium).
- Zrzuty ekranu workflow i dashboardu zapisz w `knime/screenshots/`.

## Schemat workflow

```
[CSV Reader: oferty]──────────────┐
                                  ├─[Joiner city=city_key]─[Math Formula]─[GroupBy city]
[Excel Reader: koszty]─[String M.]┘          │
                                             ├─[Color Manager: segment]─┬─[Box Plot segmenty]
                                             │                          └─[Scatter PC1/PC2]
                                             └─[Box Plot strefy]
[CSV Reader: miasta]─[Color Manager: grupa]─┬─[Bar Chart P1]
                                            ├─[Scatter P5 grupy]
                                            ├─[Bar Chart P2]  [Bar Chart P4]
[CSV Reader: ceny_mies.]─[Pivot]─[Line Plot]
[CSV Reader: predykcje]─[Scatter rzecz. vs przew.]
[CSV Reader: wyniki]─[Table View]
            └──────────── wszystkie widoki → Component „Dashboard” ───────────┘
```
