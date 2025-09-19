import joblib
import pandas as pd
import numpy as np

# Charger modèle, encoder, scaler
model = joblib.load("models/best_model.pkl")

# Taux d’intérêt par défaut (2025)
DEFAULT_INTEREST_RATE = 3.5

# Profils de test
test_clients = [
    {
        "name": "Très faible revenu - énorme prêt",
        "Gender": "Male",
        "Married": "No",
        "Dependents": "0",
        "Education": "Not Graduate",
        "Self_Employed": "No",
        "Property_Area": "Rural",
        "ApplicantIncome": 0,
        "CoapplicantIncome": 0,
        "LoanAmount": 200000
    },
    {
        "name": "Revenu moyen - prêt modeste",
        "Gender": "Female",
        "Married": "Yes",
        "Dependents": "1",
        "Education": "Graduate",
        "Self_Employed": "No",
        "Property_Area": "Urban",
        "ApplicantIncome": 4000,
        "CoapplicantIncome": 1500,
        "LoanAmount": 120000
    },
    {
        "name": "Haut revenu - petit prêt",
        "Gender": "Male",
        "Married": "Yes",
        "Dependents": "0",
        "Education": "Graduate",
        "Self_Employed": "Yes",
        "Property_Area": "Semiurban",
        "ApplicantIncome": 15000,
        "CoapplicantIncome": 5000,
        "LoanAmount": 100
    },
    {
        "name": "Chômage - revenu nul",
        "Gender": "Male",
        "Married": "No",
        "Dependents": "0",
        "Education": "Not Graduate",
        "Self_Employed": "No",
        "Property_Area": "Rural",
        "ApplicantIncome": 0,
        "CoapplicantIncome": 0,
        "LoanAmount": 50
    }
]

def preprocess_client(client):
    """Prépare un client pour la prédiction (ajout log + taux d'intérêt 2025)."""
    df = pd.DataFrame([client])
    
    # Ajouter InterestRate fixe 2025
    df["InterestRate"] = DEFAULT_INTEREST_RATE
    
    # Transformer LoanAmount en LoanAmount_log
    df["LoanAmount_log"] = df["LoanAmount"].apply(lambda x: np.log(x) if x > 0 else 0)
    
    return df

# Fonction de prédiction
def predict_client(client):
    df = preprocess_client(client)    
    # Prédire
    pred = model.predict(df)[0]
    return "Approved" if pred == 1 else "Rejected"

# Test sur les profils
for client in test_clients:
    result = predict_client(client)
    print(f"{client['name']}: {result}")
