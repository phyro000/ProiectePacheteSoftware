import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, roc_auc_score, roc_curve)
from utils import verifica_date, COLOANE_INTARZIERE, TINTA

st.set_page_config(page_title="Clasificare & Segmentare", page_icon="🤖", layout="wide")
st.title("🤖 Clasificare & Segmentare")
st.caption("Regresie logistica si clusterizare K-Means cu scikit-learn.")

date = verifica_date()

tab1, tab2 = st.tabs(["Regresie logistica", "Clusterizare K-Means"])

with tab1:
    st.subheader("Predictia probabilitatii de neplata")
    st.markdown("""
    Antrenam un model de **regresie logistica** care prezice daca un client va intra in
    default luna urmatoare, pe baza caracteristicilor financiare si demografice.
    """)

    predictori = ["LIMIT_BAL", "AGE", "total_facturat", "total_platit"] + COLOANE_INTARZIERE
    proportie_test = st.slider("Proportia setului de test", 0.1, 0.5, 0.3, 0.05)
    echilibrare = st.checkbox("Echilibreaza clasele (class_weight='balanced')", value=True)

    X = date[predictori]
    y = date[TINTA]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=proportie_test,
                                                        random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000,
                               class_weight="balanced" if echilibrare else None)
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]

    st.markdown("**Metrici de performanta**")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Acuratete", f"{accuracy_score(y_test, y_pred)*100:.1f}%")
    col2.metric("Precizie", f"{precision_score(y_test, y_pred)*100:.1f}%")
    col3.metric("Recall", f"{recall_score(y_test, y_pred)*100:.1f}%")
    col4.metric("Scor F1", f"{f1_score(y_test, y_pred)*100:.1f}%")
    col5.metric("AUC", f"{roc_auc_score(y_test, y_prob):.3f}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Matricea de confuzie**")
        cm = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(["Fara default", "Default"])
        ax.set_yticklabels(["Fara default", "Default"])
        ax.set_xlabel("Prezis"); ax.set_ylabel("Real")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="white" if cm[i, j] > cm.max()/2 else "black")
        st.pyplot(fig)
    with col2:
        st.markdown("**Curba ROC**")
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.plot(fpr, tpr, color="#4f9dff", label=f"AUC = {roc_auc_score(y_test, y_prob):.3f}")
        ax2.plot([0, 1], [0, 1], "--", color="gray")
        ax2.set_xlabel("Rata fals pozitiv"); ax2.set_ylabel("Rata adevarat pozitiv")
        ax2.legend()
        st.pyplot(fig2)

    st.markdown("**Importanta predictorilor (coeficienti)**")
    coeficienti = pd.DataFrame({
        "Predictor": predictori,
        "Coeficient": model.coef_[0]
    }).sort_values("Coeficient", key=abs, ascending=False)
    fig3 = px.bar(coeficienti, x="Coeficient", y="Predictor", orientation="h",
                  title="Coeficientii regresiei logistice")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Segmentarea clientilor prin K-Means")
    st.markdown("""
    Grupam clientii in segmente cu profil financiar similar, folosind variabile scalate.
    Numarul de segmente este ales interactiv.
    """)

    nr_clustere = st.slider("Numar de segmente (k)", 2, 6, 3)
    variabile_cluster = ["LIMIT_BAL", "AGE", "total_facturat", "total_platit"]
    X_cluster = StandardScaler().fit_transform(date[variabile_cluster])
    km = KMeans(n_clusters=nr_clustere, random_state=42, n_init=10)
    etichete = km.fit_predict(X_cluster)

    date_cluster = date.copy()
    date_cluster["segment"] = etichete

    profil = date_cluster.groupby("segment").agg(
        nr_clienti=("segment", "size"),
        limita_medie=("LIMIT_BAL", "mean"),
        varsta_medie=("AGE", "mean"),
        facturat_mediu=("total_facturat", "mean"),
        platit_mediu=("total_platit", "mean"),
        rata_default=(TINTA, "mean")
    ).round(2).reset_index()
    profil["rata_default"] = (profil["rata_default"] * 100).round(2)
    st.dataframe(profil, use_container_width=True, hide_index=True)

    esantion = date_cluster.sample(min(3000, len(date_cluster)), random_state=42)
    fig4 = px.scatter(esantion, x="LIMIT_BAL", y="total_facturat", color=esantion["segment"].astype(str),
                      labels={"color": "Segment", "LIMIT_BAL": "Limita de credit (NT$)",
                              "total_facturat": "Total facturat (NT$)"},
                      title=f"Segmentarea clientilor in {nr_clustere} grupuri", opacity=0.6)
    st.plotly_chart(fig4, use_container_width=True)

st.info("Continua cu pagina 6: Regresie Multipla")
