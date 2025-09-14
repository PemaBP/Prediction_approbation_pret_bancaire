import pandas as pd
import numpy as np
import joblib

# Charger pipeline complet
model = joblib.load("models/best_model.pkl")

# Charger les taux
df_rates = pd.read_csv("data/interest_rates.csv")
taux_2025 = df_rates.loc[df_rates["year"] == 2025, "obs_value"].values[0]

# Exemple d'un nouveau client 
new_client = {
    "Gender": "Male",
    "Married": "No",
    "Dependents": "2",
    "Education": "Not Graduate",
    "Self_Employed": "No",
    "Property_Area": "Rural",
    "ApplicantIncome": 0,
    "CoapplicantIncome": 0,
    "LoanAmount": 1
}

# ---- Transformations automatiques ----
# Ajouter LoanAmount_log
new_client["LoanAmount_log"] = np.log(new_client["LoanAmount"]) if new_client["LoanAmount"] > 0 else 0

# Ajouter InterestRate = valeur 2025
new_client["InterestRate"] = taux_2025

# Convertir en DataFrame
X_new = pd.DataFrame([new_client])

# Prédiction
prediction = model.predict(X_new)
print("Résultat prédiction :", "Approved" if prediction[0] == 1 else "Rejected")
