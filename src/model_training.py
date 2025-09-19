import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


print("Current working directory:", os.getcwd())
loan_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Loan_clean.csv"))
print("Loan CSV path:", loan_csv_path)
loan_df = pd.read_csv(loan_csv_path)

X = loan_df.drop("Loan_Status", axis=1)
y = loan_df["Loan_Status"]


num_features = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount_log", "InterestRate"]
cat_features = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_features)
    ]
)

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
    "LDA": LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")
}

#train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

#cross-validation
results = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, model in models.items():
    clf = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("model", model)
    ])
    
    scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="f1")
    results[name] = {
        "CV F1 mean": np.mean(scores),
        "CV F1 std": np.std(scores)
    }

results_df = pd.DataFrame(results).T
print("cross validation sur train:")
print(results_df.sort_values("CV F1 mean", ascending=False))


best_model_name = results_df["CV F1 mean"].idxmax()
print(f" Modèle sélectionné : {best_model_name}")

best_model = ImbPipeline(steps=[
    ("preprocessor", preprocessor),
    ("smote", SMOTE(random_state=42)),
    ("model", models[best_model_name])
])


best_model.fit(X_train, y_train)
y_pred = best_model.predict(X_test)

print("\n Évaluation sur TEST :")
print("Accuracy :", accuracy_score(y_test, y_pred))
print("F1 Score :", f1_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("ROC AUC  :", roc_auc_score(y_test, y_pred))


best_model.fit(X, y)

# Sauvegarde du modèle
models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
os.makedirs(models_dir, exist_ok=True)
joblib.dump(best_model, os.path.join(models_dir, "best_model.pkl"))

#### Visualisations ####

# Matrice de confusion
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.xlabel("Prédit")
plt.ylabel("Réel")
plt.title("Matrice de confusion sur TEST")
plt.show()

# Comparaison des modèles selon plusieurs métriques 
metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
metrics_results = {}

for name, model in models.items():
    clf = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("model", model)
    ])
    scores = {}
    for metric in metrics:
        if metric == "roc_auc":
            try:
                score = cross_val_score(clf, X_train, y_train, cv=cv, scoring=metric)
            except ValueError:
                score = np.array([np.nan]*cv.get_n_splits())
        else:
            score = cross_val_score(clf, X_train, y_train, cv=cv, scoring=metric)
        scores[metric] = np.mean(score)
    metrics_results[name] = scores
metrics_df = pd.DataFrame(metrics_results).T

# Comparaison des modèles selon plusieurs métriques (graphique)
metrics_df_plot = metrics_df.sort_values("f1", ascending=False)
ax = metrics_df_plot.plot(kind="bar", figsize=(10,6))
plt.ylabel("Score (CV moyenne)")
plt.xlabel("Modèle")
plt.title("Comparaison des modèles selon plusieurs métriques (cross-validation)")
plt.ylim(0, 1)
plt.legend(title="Métrique")
plt.tight_layout()
plt.show()


# Affichage d'un graphique en barre pour comparer les modèles selon le F1 score 
f1_scores = results_df["CV F1 mean"].sort_values(ascending=False)

plt.figure(figsize=(8, 5))
ax = f1_scores.plot(kind="bar", color="cornflowerblue")
plt.ylabel("F1 Score (CV moyenne)")
plt.xlabel("Modèle")
plt.title("Comparaison des modèles selon le F1 score (cross-validation)")
plt.ylim(0, 1)
plt.tight_layout()
for i, v in enumerate(f1_scores):
    ax.text(i, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=10)

plt.show()

# Sélection des modèles proches en F1-score et ROC-AUC
candidats = metrics_df[["f1", "roc_auc"]].copy()
candidats.columns = ["F1", "ROC-AUC"]

plt.figure(figsize=(8, 4))
plt.scatter(candidats["F1"], candidats["ROC-AUC"], color="orange", s=100)
for idx in candidats.index:
    plt.text(candidats.loc[idx, "F1"], candidats.loc[idx, "ROC-AUC"], idx, fontsize=12)
plt.xlabel("F1-score")
plt.ylabel("ROC-AUC")
plt.title("Sélection des modèles proches en F1-score et ROC-AUC")
plt.grid(True)
plt.tight_layout()
plt.show()
