import streamlit as st
import pandas as pd
import numpy as np
import joblib
from scipy.sparse import hstack

# --- Charger modèle et objets ---
model = joblib.load("models/best_model.pkl")
encoder = joblib.load("models/encoder.pkl")
scaler = joblib.load("models/scaler.pkl")

# Charger taux 2025
df_rates = pd.read_csv("data/interest_rates.csv")
taux_2025 = df_rates.loc[df_rates["year"] == 2025, "obs_value"].values[0]

# --- Streamlit UI ---
st.title("📊 Prédiction d’approbation de prêt")

st.sidebar.header("Infos client")
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
married = st.sidebar.selectbox("Married", ["Yes", "No"])
dependents = st.sidebar.selectbox("Dependents", ["0", "1", "2", "3+"])
education = st.sidebar.selectbox("Education", ["Graduate", "Not Graduate"])
self_employed = st.sidebar.selectbox("Self_employed", ["Yes", "No"])
property_area = st.sidebar.selectbox("Property_Area", ["Urban", "Semiurban", "Rural"])

applicant_income = st.sidebar.number_input("ApplicantIncome (€)", min_value=0, value=5000)
coapplicant_income = st.sidebar.number_input("CoapplicantIncome (€)", min_value=0, value=2000)
loan_amount = st.sidebar.number_input("LoanAmount (€)", min_value=1000, value=200000, step=1000)

# --- Construire l’input ---
if st.button("Prédire"):
    new_client = {
        "Gender": gender,
        "Married": married,
        "Dependents": dependents,
        "Education": education,
        "Self_Employed": self_employed,
        "Property_Area": property_area,
        "ApplicantIncome": applicant_income,
        "CoapplicantIncome": coapplicant_income,
        "LoanAmount": loan_amount
    }

    # Ajout des features calculées
    new_client["LoanAmount_log"] = np.log(new_client["LoanAmount"]) if new_client["LoanAmount"] > 0 else 0
    new_client["InterestRate"] = taux_2025

    X_new = pd.DataFrame([new_client])

    # Colonnes attendues
    num_features = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount_log", "InterestRate"]
    cat_features = ["Gender", "Married", "Dependents","Education", "Self_Employed", "Property_Area"]

    # Transformation
    X_cat = encoder.transform(X_new[cat_features])
    X_num = scaler.transform(X_new[num_features])
    X_final = hstack([X_num, X_cat])

    # Prédiction
    prediction = model.predict(X_final)[0]
    prob = model.predict_proba(X_final)[0][1]

    st.subheader("Résultat de la prédiction")
    if prediction == 1:
        st.success(f"✅ Prêt APPROUVÉ avec probabilité {prob:.2f}")
    else:
        st.error(f"❌ Prêt REFUSÉ avec probabilité {prob:.2f}")
