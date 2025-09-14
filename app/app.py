import streamlit as st
import pandas as pd
import numpy as np
import joblib

# --- Config Streamlit ---
st.set_page_config(page_title="Loan Approval Prediction", page_icon="💰", layout="wide")

# --- Charger modèle ---
model = joblib.load("models/best_model.pkl")

# Charger taux 2025
df_rates = pd.read_csv("data/interest_rates.csv")
taux_2025 = df_rates.loc[df_rates["year"] == 2025, "obs_value"].values[0]

# --- Header ---
st.title("💳 Loan Approval Predictor")
st.markdown("### Entrez les informations ci-dessous pour savoir si votre prêt peut être approuvé.")

# --- Formulaire en colonnes ---
with st.form("loan_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox("👤 Gender", ["Male", "Female"])
        married = st.selectbox("💍 Married", ["Yes", "No"])
        dependents = st.selectbox("👶 Dependents", ["0", "1", "2", "3+"])

    with col2:
        education = st.selectbox("🎓 Education", ["Graduate", "Not Graduate"])
        self_employed = st.selectbox("🏢 Self Employed", ["Yes", "No"])
        property_area = st.selectbox("🏠 Property Area", ["Urban", "Semiurban", "Rural"])

    with col3:
        applicant_income = st.number_input("💵 Applicant Income (€)", min_value=0, value=5000, step=500)
        coapplicant_income = st.number_input("🤝 Coapplicant Income (€)", min_value=0, value=2000, step=500)
        loan_amount = st.number_input("🏦 Loan Amount (€)", min_value=1000, value=200000, step=1000)

    submitted = st.form_submit_button("🚀 Prédire le prêt")

# --- Prédiction ---
if submitted:
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

    # Prédiction directe avec le modèle (pipeline)
    prediction = model.predict(X_new)[0]
    prob = model.predict_proba(X_new)[0][1]

    # --- Résultat stylé ---
    st.markdown("## 📊 Résultat de la prédiction")
    if prediction == 1:
        st.success(f"### ✅ Prêt **APPROUVÉ** 🎉\nProbabilité d'approbation : **{prob:.2%}**")
    else:
        st.error(f"### ❌ Prêt **REFUSÉ** 💔\nProbabilité d'approbation : **{prob:.2%}**")

    # --- Détails ---
    with st.expander("🔎 Voir les détails de la simulation"):
        st.json(new_client)
