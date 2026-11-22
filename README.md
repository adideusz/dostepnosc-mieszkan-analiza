# Dostępność mieszkań w największych miastach Polski

Projekt z przedmiotu **Metody analizy, przetwarzania i wizualizacji danych**.

**Autorzy:** Adrian Tusiński, Aleksander Klank  
**Prowadząca:** mgr Paulina Kuśmierz

**Temat:** analiza dostępności cenowej mieszkań w 15 największych miastach Polski w relacji do lokalnych wynagrodzeń i kosztów życia.

Najważniejsze wyniki:

- Mieszkanie 50 m² kosztuje od **~81 pensji netto** (Radom, Częstochowa) do **~142 pensji** (Warszawa).
- Najwyższa rentowność najmu jest w Radomiu, Częstochowie i Katowicach (**7,3–7,5%**), a najniższa w Krakowie (5,1%) i Warszawie (5,6%).
- Miasta o najwyższych zarobkach są **względnie najmniej dostępne**, bo ceny rosną szybciej niż płace. Wyjątkiem są Wrocław i Poznań.
- Drzewo decyzyjne wycenia m² z dokładnością **R² = 0,78** (średni błąd 11,8%).
- K-means dzieli miasta na 4 grupy dostępności, a oferty na 4 segmenty rynku.

## Dane

| Zbiór | Źródło | Pliki |
|---|---|---|
| Apartment Prices in Poland | Kaggle (oferty sprzedaży i najmu 2023–2024, dane OpenStreetMap) | `data/raw/apartments_prices/*.csv` |
| Poland cost of living vs salary per city | Kaggle (GUS/BDL, Numbeo) | `data/raw/cost_of_living/*.csv` |

## Struktura projektu

```
notebooks/                              analiza krok po kroku (uruchomione, z wynikami)
  01_temat_i_zrodla_danych.ipynb        etap 1 — temat, cel, źródła, rodzaje danych
  02_struktura_i_statystyka.ipynb       etap 2 — klasyfikacja atrybutów, relacje, statystyki, imputacja
  03_czyszczenie_i_przygotowanie.ipynb  etap 3 — duplikaty, błędy, braki, dyskretyzacja, Min-Max, integracja
  04_korelacje_i_redukcja_wymiarowosci  etap 4 — Pearson/Spearman/Kendall, PCA, LDA
  05_uczenie_maszynowe.ipynb            etap 5 — drzewo decyzyjne: regresja i klasyfikacja
  06_grupowanie.ipynb                   etap 6 — K-means, grupowanie hierarchiczne, silhouette
  07_wizualizacja_i_prezentacja.ipynb   etap 7 — odpowiedzi na pytania, zestawienie wyników, eksport do KNIME
data/raw/          dane surowe (bez zmian)
data/processed/    dane oczyszczone i wyniki (CSV)
figures/           wszystkie wykresy (PNG)
knime/             workflow KNIME (.knwf + folder), dane wejściowe (CSV + Excel) i opis
raport/            sprawozdanie (Markdown + Word)
src/utils.py       wspólne funkcje (wczytywanie, normalizacja nazw miast, styl wykresów)
```

## Uruchomienie

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/jupyter lab notebooks/
```

Notebooki uruchamiaj po kolei (01 → 07). Etap 3 zapisuje dane do `data/processed/`, a kolejne etapy z nich korzystają. Sprawozdanie w formacie Word generuje polecenie `.venv/bin/python src/make_report_docx.py`.

## Etapy w historii repozytorium

Każdy etap ma tag git (`etap-1` … `etap-7`). Stan projektu po kolejnych zajęciach oznaczają tagi `zajecia-1` … `zajecia-4`:

| Zajęcia | Materiały | Etapy | Tag |
|---|---|---|---|
| 1 | Temat projektu, źródła danych | 1 | `zajecia-1` |
| 2 | Struktura zbiorów, przygotowanie danych | 2–3 | `zajecia-2` |
| 3 | Korelacje, redukcja wymiarowości, uczenie maszynowe | 4–5 | `zajecia-3` |
| 4 | Grupowanie, wizualizacja i prezentacja wyników | 6–7 + raport | `zajecia-4` |
