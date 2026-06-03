import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from utils import verifica_date, COLOANE_FACTURI, COLOANE_PLATI, LUNI, TINTA

st.set_page_config(page_title="Vizualizari", page_icon="📈", layout="wide")
st.title("📈 Vizualizari")
st.caption("Grafice dinamice cu matplotlib, seaborn si plotly.")

date = verifica_date()
sns.set_style("darkgrid")

tab1, tab2, tab3 = st.tabs(["Matplotlib & Seaborn", "Plotly interactiv", "Serie de timp"])

with tab1:
    st.subheader("Distributia limitei de credit")
    nr_intervale = st.slider("Numar de intervale (histograma)", 10, 80, 40)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(date["LIMIT_BAL"], bins=nr_intervale, color="#4f9dff", edgecolor="white")
    ax.set_xlabel("Limita de credit (NT$)")
    ax.set_ylabel("Numar clienti")
    ax.set_title("Distributia limitei de credit")
    st.pyplot(fig)

    st.subheader("Rata de default pe nivel de educatie (seaborn)")
    rata_educatie = date.groupby("educatie_label", observed=True)[TINTA].mean().mul(100).reset_index()
    rata_educatie.columns = ["Educatie", "Rata default"]
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.barplot(data=rata_educatie, x="Educatie", y="Rata default", ax=ax2, palette="Blues_d")
    ax2.set_ylabel("Rata de default (%)")
    ax2.set_title("Rata de default pe nivel de educatie")
    st.pyplot(fig2)

    st.subheader("Corelatii intre variabilele financiare")
    coloane_corelatie = ["LIMIT_BAL", "AGE", "total_facturat", "total_platit", TINTA]
    matrice = date[coloane_corelatie].corr()
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrice, annot=True, cmap="coolwarm", fmt=".2f", ax=ax3)
    ax3.set_title("Matricea de corelatie")
    st.pyplot(fig3)

with tab2:
    st.subheader("Limita de credit vs. suma facturata")
    dimensiune_culoare = st.selectbox("Coloreaza punctele dupa:", ["default_label", "sex_label", "educatie_label"])
    esantion = date.sample(min(3000, len(date)), random_state=42)
    fig4 = px.scatter(esantion, x="LIMIT_BAL", y="total_facturat", color=dimensiune_culoare,
                      labels={"LIMIT_BAL": "Limita de credit (NT$)", "total_facturat": "Total facturat (NT$)"},
                      title="Relatia limita - sume facturate", opacity=0.6)
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Numar de clienti pe grupa de varsta si stare de plata")
    pivot = date.groupby(["grupa_varsta", "default_label"], observed=True).size().reset_index(name="nr")
    fig5 = px.bar(pivot, x="grupa_varsta", y="nr", color="default_label", barmode="group",
                  labels={"grupa_varsta": "Grupa de varsta", "nr": "Numar clienti", "default_label": "Stare"},
                  title="Distributia clientilor pe grupe de varsta")
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.subheader("Evolutia sumelor facturate si platite (Aprilie - Septembrie 2005)")
    st.markdown("""
    Setul de date contine sase capturi lunare consecutive. Coloanele `BILL_AMT6 ... BILL_AMT1`
    corespund lunilor Aprilie ... Septembrie, iar `PAY_AMT6 ... PAY_AMT1` reprezinta platile aferente.
    """)
    facturi_pe_luna = [date[c].mean() for c in reversed(COLOANE_FACTURI)]
    plati_pe_luna = [date[c].mean() for c in reversed(COLOANE_PLATI)]
    serie = pd.DataFrame({"Luna": LUNI, "Suma facturata medie": facturi_pe_luna, "Suma platita medie": plati_pe_luna})

    grupare = st.radio("Vezi seria defalcata dupa:", ["Total", "Stare de plata"], horizontal=True)
    if grupare == "Total":
        fig6 = px.line(serie, x="Luna", y=["Suma facturata medie", "Suma platita medie"], markers=True,
                       labels={"value": "Suma medie (NT$)", "variable": "Indicator"},
                       title="Evolutia lunara a facturilor si platilor")
        st.plotly_chart(fig6, use_container_width=True)
    else:
        randuri = []
        for stare, grup in date.groupby("default_label"):
            for luna, col in zip(LUNI, reversed(COLOANE_FACTURI)):
                randuri.append({"Luna": luna, "Stare": stare, "Suma facturata medie": grup[col].mean()})
        serie_grup = pd.DataFrame(randuri)
        fig7 = px.line(serie_grup, x="Luna", y="Suma facturata medie", color="Stare", markers=True,
                       title="Evolutia facturilor pe stare de plata")
        st.plotly_chart(fig7, use_container_width=True)

st.info("Continua cu pagina 4: Pregatirea Datelor")
