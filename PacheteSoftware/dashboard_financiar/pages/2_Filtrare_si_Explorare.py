import streamlit as st
import pandas as pd
from utils import verifica_date, TINTA

st.set_page_config(page_title="Filtrare & Explorare", page_icon="🔎", layout="wide")
st.title("🔎 Filtrare & Explorare")
st.caption("Filtrare interactiva, accesarea datelor cu loc si iloc, grupare si agregare.")

date = verifica_date()

st.sidebar.header("Filtre")
sexe = st.sidebar.multiselect("Sex", options=sorted(date["sex_label"].unique()),
                              default=sorted(date["sex_label"].unique()))
educatii = st.sidebar.multiselect("Educatie", options=sorted(date["educatie_label"].unique()),
                                  default=sorted(date["educatie_label"].unique()))
stari = st.sidebar.multiselect("Stare civila", options=sorted(date["stare_civila_label"].unique()),
                               default=sorted(date["stare_civila_label"].unique()))
varsta_min, varsta_max = st.sidebar.slider("Interval varsta", int(date["AGE"].min()),
                                           int(date["AGE"].max()),
                                           (int(date["AGE"].min()), int(date["AGE"].max())))
limita_min, limita_max = st.sidebar.slider("Interval limita de credit (NT$)",
                                           int(date["LIMIT_BAL"].min()), int(date["LIMIT_BAL"].max()),
                                           (int(date["LIMIT_BAL"].min()), int(date["LIMIT_BAL"].max())),
                                           step=10000)
doar_default = st.sidebar.checkbox("Doar clientii cu default", value=False)

filtru = (
    date["sex_label"].isin(sexe)
    & date["educatie_label"].isin(educatii)
    & date["stare_civila_label"].isin(stari)
    & date["AGE"].between(varsta_min, varsta_max)
    & date["LIMIT_BAL"].between(limita_min, limita_max)
)
if doar_default:
    filtru = filtru & (date[TINTA] == 1)

date_filtrate = date.loc[filtru]

col1, col2, col3 = st.columns(3)
col1.metric("Clienti selectati", f"{len(date_filtrate):,}")
col2.metric("Rata default (selectie)", f"{date_filtrate[TINTA].mean()*100:.2f}%" if len(date_filtrate) else "-")
col3.metric("Limita medie (selectie)", f"{date_filtrate['LIMIT_BAL'].mean():,.0f} NT$" if len(date_filtrate) else "-")

st.subheader("1. Selectie cu loc (pe etichete de coloane)")
st.markdown("`.loc[]` selecteaza randuri dupa conditie si coloane dupa nume.")
st.code('date.loc[filtru, ["LIMIT_BAL", "AGE", "educatie_label", "default_label"]]', language="python")
coloane_afisate = ["LIMIT_BAL", "AGE", "sex_label", "educatie_label", "stare_civila_label", "default_label"]
st.dataframe(date_filtrate.loc[:, coloane_afisate].head(20), use_container_width=True)

st.subheader("2. Selectie cu iloc (pe pozitii)")
st.markdown("`.iloc[]` selecteaza randuri si coloane dupa pozitia lor numerica.")
nr = st.number_input("Cati clienti din selectie sa afisam (cu iloc)?", min_value=5, max_value=100, value=10, step=5)
if len(date_filtrate) > 0:
    st.code(f"date_filtrate.iloc[0:{nr}, 0:6]", language="python")
    st.dataframe(date_filtrate.iloc[0:nr, 0:6], use_container_width=True)
else:
    st.warning("Selectia curenta nu contine niciun client. Modifica filtrele.")

st.subheader("3. Grupare si agregare")
st.markdown("Folosim `groupby()` impreuna cu `agg()` pentru a calcula indicatori pe grupuri.")
dimensiune = st.selectbox("Grupeaza dupa:", ["educatie_label", "sex_label", "stare_civila_label", "grupa_varsta"])

if len(date_filtrate) > 0:
    agregat = date_filtrate.groupby(dimensiune, observed=True).agg(
        nr_clienti=(TINTA, "size"),
        rata_default=(TINTA, "mean"),
        limita_medie=("LIMIT_BAL", "mean"),
        suma_facturata_medie=("total_facturat", "mean")
    ).reset_index()
    agregat["rata_default"] = (agregat["rata_default"] * 100).round(2)
    agregat["limita_medie"] = agregat["limita_medie"].round(0)
    agregat["suma_facturata_medie"] = agregat["suma_facturata_medie"].round(0)
    agregat.columns = [dimensiune, "Nr. clienti", "Rata default (%)", "Limita medie (NT$)", "Suma facturata medie (NT$)"]
    st.dataframe(agregat, use_container_width=True, hide_index=True)
    st.bar_chart(agregat.set_index(dimensiune)["Rata default (%)"])
else:
    st.warning("Modifica filtrele pentru a vedea agregari.")

st.info("Continua cu pagina 3: Vizualizari")
