"""Wspólne funkcje pomocnicze dla notebooków projektu.

Projekt: Analiza dostępności cenowej mieszkań w największych miastach Polski
w relacji do lokalnych wynagrodzeń i kosztów życia.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# --------------------------------------------------------------------------
# Ścieżki
# --------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
APARTMENTS_DIR = RAW_DIR / "apartments_prices"
COST_DIR = RAW_DIR / "cost_of_living"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURES_DIR = PROJECT_DIR / "figures"
KNIME_DIR = PROJECT_DIR / "knime"

COST_2024_FILE = COST_DIR / "poland_cost_of_living_vs_salary_2024.csv"
COST_LONG_FILE = COST_DIR / "poland_col_salary_longitudinal_2010_2024.csv"

RANDOM_STATE = 42

# Ładne nazwy miast do wykresów (klucz = znormalizowana nazwa)
CITY_LABELS = {
    "warszawa": "Warszawa", "krakow": "Kraków", "wroclaw": "Wrocław",
    "gdansk": "Gdańsk", "lodz": "Łódź", "bydgoszcz": "Bydgoszcz",
    "gdynia": "Gdynia", "poznan": "Poznań", "szczecin": "Szczecin",
    "lublin": "Lublin", "katowice": "Katowice", "radom": "Radom",
    "czestochowa": "Częstochowa", "bialystok": "Białystok", "rzeszow": "Rzeszów",
}


# --------------------------------------------------------------------------
# Wczytywanie danych
# --------------------------------------------------------------------------
def load_apartments(kind: str = "sale") -> pd.DataFrame:
    """Wczytuje i łączy miesięczne pliki ofert.

    kind: "sale" (sprzedaż, cena w PLN) albo "rent" (najem, cena w PLN/miesiąc).
    Dodaje kolumny `source_file` oraz `period` (rok-miesiąc z nazwy pliku).
    """
    pattern = "apartments_pl_*.csv" if kind == "sale" else "apartments_rent_pl_*.csv"
    files = sorted(APARTMENTS_DIR.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Brak plików {pattern} w {APARTMENTS_DIR}")
    frames = []
    for path in files:
        df = pd.read_csv(path)
        df["source_file"] = path.name
        year, month = path.stem.split("_")[-2:]
        df["period"] = pd.Period(f"{year}-{month}", freq="M")
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_cost_2024() -> pd.DataFrame:
    return pd.read_csv(COST_2024_FILE)


def load_cost_longitudinal() -> pd.DataFrame:
    return pd.read_csv(COST_LONG_FILE)


# --------------------------------------------------------------------------
# Czyszczenie / integracja
# --------------------------------------------------------------------------
def normalize_city(name: str) -> str:
    """Standaryzacja nazwy miasta: małe litery, bez polskich znaków i spacji na brzegach.

    'Kraków' -> 'krakow', 'Łódź' -> 'lodz', ' Bielsko-Biała ' -> 'bielsko-biala'
    """
    if pd.isna(name):
        return name
    text = str(name).strip().lower().replace("ł", "l")
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def city_label(key: str) -> str:
    return CITY_LABELS.get(key, str(key).title())


# --------------------------------------------------------------------------
# Wykresy
# --------------------------------------------------------------------------
def set_plot_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook", palette="deep")
    plt.rcParams.update({
        "figure.figsize": (10, 5.5),
        "figure.dpi": 100,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_fig(fig, name: str) -> Path:
    """Zapisuje wykres do katalogu figures/ (PNG)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path)
    return path


def thousands(x, _pos=None) -> str:
    """Formatter osi: 1234567 -> '1 234 567'."""
    return f"{x:,.0f}".replace(",", " ")
