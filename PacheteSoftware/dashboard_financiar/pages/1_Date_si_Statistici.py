import streamlit as st
import pandas as pd
import numpy as np
from utils import verifica_date, incarca_date, TINTA

st.set_page_config(page_title="Date & Statistici", page_icon="📊", layout="wide")
st.title("📊 Date & Statistici")
st.caption("Importul datelor, tratarea valorilor lipsa si statistici descriptive.")

date = verifica_date()
date_brute = st.session_state["date_brute"]

st.subheader("1. Previzualizarea datelor")
st.markdown("Datele sunt importate din fisierul CSV cu `pd.read_csv()` si afisate cu `st.dataframe()`.")
nr_randuri = st.slider("Cate randuri sa afisam?", min_value=5, max_value=50, value=10, step=5)
st.dataframe(date.head(nr_randuri), use_container_width=True)

st.subheader("2. Indicatori principali")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Numar clienti", f"{len(date):,}")
col2.metric("Numar variabile", f"{date_brute.shape[1]}")
col3.metric("Clienti cu default", f"{int(date[TINTA].sum()):,}")
col4.metric("Rata de default", f"{date[TINTA].mean()*100:.2f}%")

st.subheader("3. Statistici descriptive")
st.markdown("`.describe()` calculeaza pentru fiecare coloana numerica: numar valori, medie, abatere standard, minim, maxim si cuartile.")
coloane_numerice = ["LIMIT_BAL", "AGE", "total_facturat", "total_platit"]
st.dataframe(date[coloane_numerice].describe().round(2), use_container_width=True)

st.subheader("4. Tratarea valorilor lipsa")
st.markdown("""
Setul de date contine **categorii nedocumentate** care sunt tratate ca valori lipsa:
codurile `0`, `5`, `6` pentru educatie si codul `0` pentru starea civila. Acestea sunt
inlocuite cu valoarea cea mai frecventa (modul), conform metodei prezentate la seminar.
""")

educatie_problematice = date_brute["EDUCATION"].isin([0, 5, 6]).sum()
stare_problematice = (date_brute["MARRIAGE"] == 0).sum()

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Inainte de curatare**")
    inainte = pd.DataFrame({
        "Variabila": ["EDUCATION", "MARRIAGE"],
        "Valori problematice": [int(educatie_problematice), int(stare_problematice)]
    })
    st.dataframe(inainte, use_container_width=True, hide_index=True)
    st.code("""
date["EDUCATION"] = date["EDUCATION"].replace({0: np.nan, 5: np.nan, 6: np.nan})
date["MARRIAGE"] = date["MARRIAGE"].replace({0: np.nan})

mod_educatie = date["EDUCATION"].mode()[0]
date["EDUCATION"] = date["EDUCATION"].fillna(mod_educatie)
date["MARRIAGE"] = date["MARRIAGE"].fillna(date["MARRIAGE"].mode()[0])
""", language="python")

with col2:
    st.markdown("**Dupa curatare**")
    dupa = pd.DataFrame({
        "Variabila": ["EDUCATION", "MARRIAGE"],
        "Valori lipsa ramase": [int(date["EDUCATION"].isna().sum()), int(date["MARRIAGE"].isna().sum())]
    })
    st.dataframe(dupa, use_container_width=True, hide_index=True)
    st.success("Toate valorile problematice au fost inlocuite cu modul fiecarei variabile.")

st.subheader("5. Structura datelor")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Coloane si tipuri de date**")
    info = pd.DataFrame({
        "Coloana": date_brute.columns,
        "Tip": date_brute.dtypes.values.astype(str),
        "Valori lipsa": date_brute.isnull().sum().values
    })
    st.dataframe(info, use_container_width=True, hide_index=True)
with col2:
    st.markdown("**Distributia pe nivel de educatie**")
    distributie = date["educatie_label"].value_counts().reset_index()
    distributie.columns = ["Educatie", "Nr. clienti"]
    st.dataframe(distributie, use_container_width=True, hide_index=True)

st.info("Continua cu pagina 2: Filtrare & Explorare")
