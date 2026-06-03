import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from utils import verifica_date

st.set_page_config(page_title="Pregatirea Datelor", page_icon="⚙️", layout="wide")
st.title("⚙️ Pregatirea Datelor")
st.caption("Codificarea variabilelor categoriale si scalarea variabilelor numerice.")

date = verifica_date()

st.subheader("1. Codificarea variabilelor categoriale")
st.markdown("""
Variabilele categoriale trebuie transformate in valori numerice inainte de modelare.
Demonstram doua metode: **Label Encoding** (un cod intreg per categorie) si
**One-Hot Encoding** (cate o coloana binara per categorie).
""")

metoda = st.radio("Metoda de codificare:", ["One-Hot Encoding", "Label Encoding"], horizontal=True)
coloane_categoriale = ["sex_label", "educatie_label", "stare_civila_label"]

if metoda == "One-Hot Encoding":
    st.code('codificat = pd.get_dummies(date[["sex_label", "educatie_label", "stare_civila_label"]])', language="python")
    codificat = pd.get_dummies(date[coloane_categoriale]).astype(int)
else:
    st.code("""
from sklearn.preprocessing import LabelEncoder
for coloana in coloane_categoriale:
    date[coloana + "_cod"] = LabelEncoder().fit_transform(date[coloana])
""", language="python")
    from sklearn.preprocessing import LabelEncoder
    codificat = pd.DataFrame()
    for coloana in coloane_categoriale:
        codificat[coloana + "_cod"] = LabelEncoder().fit_transform(date[coloana])

st.dataframe(codificat.head(10), use_container_width=True)
st.caption(f"Rezultat: {codificat.shape[1]} coloane numerice generate.")

st.subheader("2. Scalarea variabilelor numerice")
st.markdown("""
Variabilele numerice au scari foarte diferite (limita de credit ajunge la sute de mii NT\\$,
varsta la zeci de ani). Scalarea le aduce la o scara comparabila, esential pentru
regresia logistica si clusterizare.
""")

coloane_numerice = ["LIMIT_BAL", "AGE", "total_facturat", "total_platit"]
tip_scalare = st.selectbox("Metoda de scalare:", ["StandardScaler (medie 0, abatere 1)", "MinMaxScaler (interval 0-1)"])

if tip_scalare.startswith("Standard"):
    scaler = StandardScaler()
    st.code("""
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
date_scalate = scaler.fit_transform(date[coloane_numerice])
""", language="python")
else:
    scaler = MinMaxScaler()
    st.code("""
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
date_scalate = scaler.fit_transform(date[coloane_numerice])
""", language="python")

scalate = pd.DataFrame(scaler.fit_transform(date[coloane_numerice]), columns=coloane_numerice)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Inainte de scalare (statistici)**")
    st.dataframe(date[coloane_numerice].describe().round(1), use_container_width=True)
with col2:
    st.markdown("**Dupa scalare (statistici)**")
    st.dataframe(scalate.describe().round(3), use_container_width=True)

st.markdown("**Primele randuri dupa scalare**")
st.dataframe(scalate.head(10), use_container_width=True)

st.info("Continua cu pagina 5: Clasificare & Segmentare")
