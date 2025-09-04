import pandas as pd
import numpy as np
import joblib

# Charger modèle et pipeline
model = joblib.load("models/best_model.pkl")
encoder = joblib.load("models/encoder.pkl")
scaler = joblib.load("models/scaler.pkl")

# Charger les taux
df_rates = pd.read_csv("data/interest_rates.csv")
taux_2025 = df_rates.loc[df_rates["year"] == 2025, "obs_value"].values[0]

# Exemple d'un nouveau client (sans InterestRate, ni log déjà calculé)
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

# Convertir en DataFrame (1 seule ligne)
import pandas as pd
X_new = pd.DataFrame([new_client])

# Séparer num / cat features
num_features = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount_log", "InterestRate"]
cat_features = ["Gender", "Married", "Dependents","Education", "Self_Employed", "Property_Area"]

# Encoder + scaler
X_num = scaler.transform(X_new[num_features])
X_cat = encoder.transform(X_new[cat_features])
import numpy as np
from scipy.sparse import hstack
X_final = hstack([X_num, X_cat])

# Prédiction
prediction = model.predict(X_final)
print("Résultat prédiction :", "Approved" if prediction[0]==1 else "Rejected")
