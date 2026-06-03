import os
import pandas as pd
import numpy as np
import streamlit as st

CALE_DATE = os.path.join(os.path.dirname(__file__), "date", "credit_card_default.csv")

ETICHETE_SEX = {1: "Barbat", 2: "Femeie"}
ETICHETE_EDUCATIE = {1: "Studii postuniversitare", 2: "Studii universitare",
                     3: "Liceu", 4: "Altele"}
ETICHETE_STARE_CIVILA = {1: "Casatorit", 2: "Necasatorit", 3: "Altele"}
COLOANE_FACTURI = ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]
COLOANE_PLATI = ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]
COLOANE_INTARZIERE = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
LUNI = ["Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie"]
TINTA = "default.payment.next.month"


@st.cache_data
def incarca_date(cale=None):
    if cale is None:
        cale = CALE_DATE
    date = pd.read_csv(cale)
    return date


def curata_date(date):
    rezultat = date.copy()

    rezultat["EDUCATION"] = rezultat["EDUCATION"].replace({0: np.nan, 5: np.nan, 6: np.nan})
    rezultat["MARRIAGE"] = rezultat["MARRIAGE"].replace({0: np.nan})

    mod_educatie = rezultat["EDUCATION"].mode()[0]
    mod_stare = rezultat["MARRIAGE"].mode()[0]
    rezultat["EDUCATION"] = rezultat["EDUCATION"].fillna(mod_educatie)
    rezultat["MARRIAGE"] = rezultat["MARRIAGE"].fillna(mod_stare)

    rezultat["EDUCATION"] = rezultat["EDUCATION"].astype(int)
    rezultat["MARRIAGE"] = rezultat["MARRIAGE"].astype(int)

    rezultat["sex_label"] = rezultat["SEX"].map(ETICHETE_SEX)
    rezultat["educatie_label"] = rezultat["EDUCATION"].map(ETICHETE_EDUCATIE)
    rezultat["stare_civila_label"] = rezultat["MARRIAGE"].map(ETICHETE_STARE_CIVILA)
    rezultat["default_label"] = rezultat[TINTA].map({0: "Fara default", 1: "Default"})

    rezultat["total_facturat"] = rezultat[COLOANE_FACTURI].sum(axis=1)
    rezultat["total_platit"] = rezultat[COLOANE_PLATI].sum(axis=1)
    rezultat["grupa_varsta"] = pd.cut(
        rezultat["AGE"],
        bins=[20, 30, 40, 50, 60, 80],
        labels=["21-30", "31-40", "41-50", "51-60", "61+"]
    )
    return rezultat


def obtine_date():
    if "date_brute" not in st.session_state:
        st.session_state["date_brute"] = incarca_date()
    if "date_curate" not in st.session_state:
        st.session_state["date_curate"] = curata_date(st.session_state["date_brute"])
    return st.session_state["date_curate"]


def verifica_date():
    if "date_curate" not in st.session_state:
        st.warning("Nu exista date incarcate. Mergi la pagina principala (Home) si incarca fisierul CSV.")
        st.stop()
    return st.session_state["date_curate"]
