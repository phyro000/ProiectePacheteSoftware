import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import plotly.express as px
from utils import verifica_date

st.set_page_config(page_title="Regresie Multipla", page_icon="📐", layout="wide")
st.title("📐 Regresie Multipla")
st.caption("Model de regresie multipla cu statsmodels pentru explicarea sumei facturate.")

date = verifica_date()

st.markdown("""
Construim un model de **regresie liniara multipla** care explica suma totala facturata
(`total_facturat`) in functie de limita de credit, varsta si variabilele demografice codificate.
Modelul este estimat cu `statsmodels` (metoda celor mai mici patrate, OLS).
""")

st.subheader("1. Alegerea predictorilor")
predictori_numerici = st.multiselect(
    "Predictori numerici",
    ["LIMIT_BAL", "AGE", "total_platit"],
    default=["LIMIT_BAL", "AGE", "total_platit"]
)
include_categoriale = st.checkbox("Include variabile categoriale (sex, educatie, stare civila)", value=True)

if len(predictori_numerici) == 0:
    st.warning("Selecteaza cel putin un predictor numeric.")
    st.stop()

termeni = list(predictori_numerici)
if include_categoriale:
    termeni += ["C(sex_label)", "C(educatie_label)", "C(stare_civila_label)"]
formula = "total_facturat ~ " + " + ".join(termeni)

st.code(f'model = smf.ols("{formula}", data=date).fit()', language="python")

model = smf.ols(formula, data=date).fit()

st.subheader("2. Indicatori ai modelului")
col1, col2, col3, col4 = st.columns(4)
col1.metric("R-patrat", f"{model.rsquared:.3f}")
col2.metric("R-patrat ajustat", f"{model.rsquared_adj:.3f}")
col3.metric("Statistica F", f"{model.fvalue:.1f}")
col4.metric("Nr. observatii", f"{int(model.nobs):,}")

st.subheader("3. Coeficientii modelului")
rezumat = pd.DataFrame({
    "Coeficient": model.params,
    "Eroare std.": model.bse,
    "Statistica t": model.tvalues,
    "p-value": model.pvalues
}).round(4)
rezumat["Semnificativ (p<0.05)"] = np.where(rezumat["p-value"] < 0.05, "Da", "Nu")
st.dataframe(rezumat, use_container_width=True)

st.subheader("4. Sumarul complet statsmodels")
with st.expander("Vezi sumarul complet al modelului"):
    st.text(model.summary().as_text())

st.subheader("5. Valori prezise vs. valori reale")
date_grafic = date.copy()
date_grafic["prezis"] = model.fittedvalues
esantion = date_grafic.sample(min(3000, len(date_grafic)), random_state=42)
fig = px.scatter(esantion, x="total_facturat", y="prezis", opacity=0.5,
                 labels={"total_facturat": "Suma facturata reala (NT$)", "prezis": "Suma facturata prezisa (NT$)"},
                 title="Valori prezise vs. valori reale")
minim = min(esantion["total_facturat"].min(), esantion["prezis"].min())
maxim = max(esantion["total_facturat"].max(), esantion["prezis"].max())
fig.add_shape(type="line", x0=minim, y0=minim, x1=maxim, y1=maxim,
              line=dict(color="red", dash="dash"))
st.plotly_chart(fig, use_container_width=True)

st.success("Aceasta este ultima pagina a aplicatiei. Toate facilitatile cerute au fost demonstrate.")
