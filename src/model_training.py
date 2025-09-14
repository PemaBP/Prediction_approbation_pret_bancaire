import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib

# 1. Charger les données
print("Current working directory:", os.getcwd())
loan_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Loan_clean.csv"))
print("Loan CSV path:", loan_csv_path)
loan_df = pd.read_csv(loan_csv_path)

X = loan_df.drop("Loan_Status", axis=1)
y = loan_df["Loan_Status"]

# 2. Définir les features
num_features = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount_log", "InterestRate"]
cat_features = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"]

# 3. Préprocesseur
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_features)
    ]
)

# 4. Définir les modèles
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

# 5. Cross-validation + SMOTE
results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, model in models.items():
    # pipeline = SMOTE + preprocessor + model
    clf = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("model", model)
    ])
    
    scores = cross_val_score(clf, X, y, cv=cv, scoring="f1")
    results[name] = {
        "CV F1 mean": np.mean(scores),
        "CV F1 std": np.std(scores)
    }

results_df = pd.DataFrame(results).T

# 6. Sélection du meilleur modèle
best_model_name = results_df["CV F1 mean"].idxmax()
print(f"\n✅ Meilleur modèle sélectionné : {best_model_name}")

best_model = ImbPipeline(steps=[
    ("preprocessor", preprocessor),
    ("smote", SMOTE(random_state=42)),
    ("model", models[best_model_name])
])

best_model.fit(X, y)

# 7. Sauvegarde du pipeline complet
models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
os.makedirs(models_dir, exist_ok=True)
joblib.dump(best_model, os.path.join(models_dir, "best_model.pkl"))
