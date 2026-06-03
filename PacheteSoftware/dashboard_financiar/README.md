# Dashboard Financiar - Analiza Riscului de Credit

Aplicatie Streamlit multi-pagina pentru analiza portofoliului de carduri de credit al unui
emitent din Taiwan (30.000 de clienti, 2005). Componenta Python a proiectului de la seminarul
**Pachete Software** (CSIE, anul III).

## Organizatia analizata

Setul de date provine de la un emitent de carduri de credit din Taiwan si contine, pentru
fiecare client, informatii demografice, limita de credit, istoricul lunar al facturilor si
platilor (Aprilie - Septembrie 2005), precum si daca a intrat in default luna urmatoare.

Sursa: UCI Machine Learning Repository, "Default of Credit Card Clients" (Yeh, I., 2009),
licenta CC BY 4.0, DOI 10.24432/C55S3H.

## Rulare

```bash
pip install -r requirements.txt
python -m streamlit run Home.py
```

Aplicatia se deschide la `http://localhost:8501`. Fisierul de date este inclus in folderul
`date/` si se incarca automat; alternativ, poate fi incarcat manual din pagina Home.

## Structura

```
dashboard_financiar/
├── Home.py                            pagina principala, import date, indicatori
├── utils.py                           functii comune: incarcare, curatare, etichete
├── requirements.txt
├── date/
│   └── credit_card_default.csv        30.000 randuri x 25 coloane
└── pages/
    ├── 1_Date_si_Statistici.py        import CSV, valori lipsa, describe
    ├── 2_Filtrare_si_Explorare.py     widget-uri, loc/iloc, groupby/agg
    ├── 3_Vizualizari.py               matplotlib, seaborn, plotly, serie de timp
    ├── 4_Pregatire_Date.py            codificare categoriale + scalare
    ├── 5_Clasificare_si_Segmentare.py regresie logistica + K-Means (scikit-learn)
    └── 6_Regresie_Multipla.py         regresie multipla (statsmodels)
```

## Acoperirea celor 11 facilitati cerute

| # | Facilitate | Unde |
|---|-----------|------|
| 1 | Structura multi-pagina | Home.py + folderul pages/ |
| 2 | Widget-uri pentru filtrare interactiva | pagina 2 (sidebar), pagina 3 (slider/select), paginile 4-6 |
| 3 | Import CSV in pandas | Home.py (st.file_uploader + pd.read_csv) |
| 4 | Tratarea valorilor lipsa | pagina 1 (replace + fillna pe coduri nedocumentate) |
| 5 | Scalarea / codificarea variabilelor categoriale | pagina 4 (StandardScaler, MinMaxScaler, get_dummies, LabelEncoder) |
| 6 | Prelucrari statistice, grupare si agregare | pagina 2 (groupby + agg), pagina 1 (describe) |
| 7 | Accesarea datelor cu loc si iloc | pagina 2 |
| 8 | Grafice dinamice (matplotlib / seaborn / plotly) | pagina 3 |
| 9 | scikit-learn (clusterizare, regresie logistica) | pagina 5 |
| 10 | statsmodels (regresie multipla) | pagina 6 |
| 11 | Afisarea metricilor specifice | Home + paginile 1, 2, 5, 6 (st.metric, metrici de clasificare) |

Sunt acoperite toate cele 11 facilitati (cerinta minima: 7).
