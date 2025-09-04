import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE  
import joblib

# 1. Charger les données
print("Current working directory:", os.getcwd())
loan_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Loan_clean.csv"))
print("Loan CSV path:", loan_csv_path)
loan_df = pd.read_csv(loan_csv_path)

X = loan_df.drop("Loan_Status", axis=1)
y = loan_df["Loan_Status"]

train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 2. Preprocessing
num_features = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount_log", "InterestRate"]
cat_features = ["Gender", "Married","Dependents", "Education", "Self_Employed", "Property_Area"]

encoder = OneHotEncoder(drop='first', handle_unknown='ignore')
scaler = StandardScaler()

X_train_cat = encoder.fit_transform(X_train[cat_features])
X_test_cat = encoder.transform(X_test[cat_features])

X_train_num = scaler.fit_transform(X_train[num_features])
X_test_num = scaler.transform(X_test[num_features])

X_train_final = np.hstack((X_train_num, X_train_cat.toarray()))
X_test_final = np.hstack((X_test_num, X_test_cat.toarray()))

# 2bis. Rééquilibrage avec SMOTE uniquement sur le train
print("Avant SMOTE:", np.bincount(y_train))
smote = SMOTE(random_state=42)
X_train_final, y_train = smote.fit_resample(X_train_final, y_train)
print("Après SMOTE:", np.bincount(y_train))

# 3. Modèles à tester
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "AdaBoost": AdaBoostClassifier(n_estimators=300, random_state=42),
    "XGBoost": XGBClassifier(
        n_estimators=500, max_depth=4, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
        n_jobs=-1, objective="binary:logistic", eval_metric="logloss"
    ),
    "LDA": LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"),
    "Dummy": DummyClassifier(strategy="most_frequent", random_state=42)
}

# 4. Entraînement et comparaison
results = {}
for name, model in models.items():
    model.fit(X_train_final, y_train)
    y_pred = model.predict(X_test_final)
    y_proba = model.predict_proba(X_test_final)[:,1] if hasattr(model, "predict_proba") else None

    results[name] = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred, zero_division=0),
        "Recall": recall_score(y_test, y_pred, zero_division=0),
        "F1": f1_score(y_test, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan
    }

results_df = pd.DataFrame(results).T
print(results_df)

# 5. Sélection du meilleur modèle (basé sur F1 puis ROC-AUC)
sorted_df = results_df.sort_values("F1", ascending=False)
best_model_name = sorted_df.index[0]
best_model = models[best_model_name]

print(f" Meilleur modèle sélectionné : {best_model_name}")

# 6. Sauvegarde
models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
os.makedirs(models_dir, exist_ok=True)
joblib.dump(best_model, os.path.join(models_dir, "best_model.pkl"))
joblib.dump(encoder, os.path.join(models_dir, "encoder.pkl"))
joblib.dump(scaler, os.path.join(models_dir, "scaler.pkl"))
