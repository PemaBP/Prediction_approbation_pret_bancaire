from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, List
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import io
from datetime import datetime

# -----------------------------
# Config & chemins
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # racine du projet
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

MODEL_PATH = MODELS_DIR / "best_model.pkl"
RATES_PATH = DATA_DIR / "interest_rates.csv"
PRED_LOG_PATH = DATA_DIR / "predictions_log.csv"   # log simple des prédictions
FEEDBACK_LOG = DATA_DIR / "feedback_log.csv"

# -----------------------------
# App FastAPI
# -----------------------------
app = FastAPI(title="Loan Approval API", version="1.0.0")

# CORS (frontend Next.js en local + ouvert par défaut)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # resserre plus tard: ["http://localhost:3000", "https://ton-domaine"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Chargement modèle & taux
# -----------------------------
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Impossible de charger le modèle: {MODEL_PATH}\n{e}")

def load_interest_rate(year: int = 2025) -> float:
    df_rates = pd.read_csv(RATES_PATH)
    if "year" not in df_rates or "obs_value" not in df_rates:
        raise RuntimeError("Fichier 'interest_rates.csv' invalide: colonnes attendues: year, obs_value")
    # Tente d'abord l'année demandée, sinon prend la dernière valeur connue
    row = df_rates.loc[df_rates["year"] == year, "obs_value"]
    if not row.empty:
        return float(row.values[0])
    return float(df_rates.sort_values("year").iloc[-1]["obs_value"])

TAUX_2025 = load_interest_rate(2025)

# -----------------------------
# Schéma Pydantic (un client)
# -----------------------------
class LoanApplication(BaseModel):
    Gender:       Literal["Male", "Female"]
    Married:      Literal["Yes", "No"]
    Dependents:   Literal["0", "1", "2", "3+"]
    Education:    Literal["Graduate", "Not Graduate"]
    Self_Employed: Literal["Yes", "No"]
    Property_Area: Literal["Urban", "Semiurban", "Rural"]
    ApplicantIncome: float = Field(ge=0)
    CoapplicantIncome: float = Field(ge=0)
    LoanAmount: float = Field(gt=0)

# Colonnes minimales attendues côté banque (CSV)
REQUIRED_COLUMNS = [
    "Gender","Married","Dependents","Education","Self_Employed",
    "Property_Area","ApplicantIncome","CoapplicantIncome","LoanAmount"
]

# -----------------------------
# Feature engineering
# -----------------------------
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    # Calculs comme dans ton Streamlit / notebook
    df = df.copy()
    df["LoanAmount_log"] = df["LoanAmount"].apply(lambda x: np.log(x) if x > 0 else 0)
    df["InterestRate"] = TAUX_2025
    return df

def ensure_required_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Colonnes manquantes: {missing}. "
                                                    f"Colonnes requises: {REQUIRED_COLUMNS}")

# -----------------------------
# Utils logging (simple CSV)
# -----------------------------
def log_predictions(df_input: pd.DataFrame, preds: np.ndarray, probs: np.ndarray):
    out = df_input.copy()
    out["prediction"] = preds
    out["probability"] = probs
    # append
    header = not PRED_LOG_PATH.exists()
    out.to_csv(PRED_LOG_PATH, mode="a", index=False, header=header)

# -----------------------------
# Colonnes numériques attendues
NUMERIC_COLUMNS = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount"]

CATEGORICAL_COLUMNS = [
    "Gender","Married","Dependents","Education","Self_Employed","Property_Area"
]

def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip()
    return df

def _coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        # supprime tout sauf chiffres, signe et point -> gère € , espaces, , ; etc.
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[^\d\.\-]", "", regex=True)
            .replace({"": np.nan, ".": np.nan, "-": np.nan})
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def _force_categorical(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        df[col] = df[col].astype(str).str.strip()
        # normalise quelques valeurs fréquentes
        df[col] = df[col].replace({"nan": "", "NaN": "", "None": ""})
        # valeurs vides -> "Unknown" (si ton pipeline n’impute pas les cat.)
        df[col] = df[col].replace({"": "Unknown"})
    return df

def ensure_required_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Colonnes manquantes: {missing}. Requis: {REQUIRED_COLUMNS}"
        )

def clean_and_validate_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les types et valide avant features/pred."""
    ensure_required_columns(df)
    df = _strip_strings(df)
    df = _force_categorical(df, CATEGORICAL_COLUMNS)
    df = _coerce_numeric(df, NUMERIC_COLUMNS)

    # Lignes non numériques restantes
    bad = {col: (df[col].isna()).to_numpy().nonzero()[0] for col in NUMERIC_COLUMNS}
    bad = {k: [int(i)+1 for i in v] for k, v in bad.items() if len(v) > 0}
    if bad:
        raise HTTPException(
            status_code=400,
            detail={"message": "Valeurs numériques invalides", "rows_by_column": bad}
        )

    # Règles simples
    if (df["LoanAmount"] <= 0).any():
        rows = (df["LoanAmount"] <= 0).to_numpy().nonzero()[0]
        raise HTTPException(status_code=400,
            detail={"message": "LoanAmount doit être > 0", "rows": [int(i)+1 for i in rows]}
        )
    for col in ["ApplicantIncome","CoapplicantIncome"]:
        if (df[col] < 0).any():
            rows = (df[col] < 0).to_numpy().nonzero()[0]
            raise HTTPException(status_code=400,
                detail={"message": f"{col} ne peut pas être négatif", "rows": [int(i)+1 for i in rows]}
            )
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["LoanAmount_log"] = df["LoanAmount"].apply(lambda x: np.log(x) if x > 0 else 0.0)
    df["InterestRate"] = TAUX_2025
    return df

def ensure_model_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Force les dtypes finaux que ton pipeline attend (évite isnan sur object)."""
    df = df.copy()
    num_final = ["ApplicantIncome","CoapplicantIncome","LoanAmount","LoanAmount_log","InterestRate"]
    for col in num_final:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].astype("object")
    return df

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "Loan Approval API running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/columns")
def columns():
    """Colonnes obligatoires attendues pour le CSV."""
    return {"required_columns": REQUIRED_COLUMNS}

@app.get("/csv-template")
def csv_template():
    """Renvoie un template CSV téléchargeable pour la banque."""
    sample = pd.DataFrame([{
        "Gender":"Male",
        "Married":"Yes",
        "Dependents":"0",
        "Education":"Graduate",
        "Self_Employed":"No",
        "Property_Area":"Urban",
        "ApplicantIncome":5000,
        "CoapplicantIncome":2000,
        "LoanAmount":200000
    }], columns=REQUIRED_COLUMNS)
    buf = io.StringIO()
    sample.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]),
                             media_type="text/csv",
                             headers={"Content-Disposition":"attachment; filename=loan_template.csv"})

@app.post("/predict-one")
def predict_one(client: LoanApplication):
    df = pd.DataFrame([client.dict()])
    df_fe = add_features(df)
    try:
        pred = model.predict(df_fe)[0]
        prob = float(model.predict_proba(df_fe)[0][1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {e}")

    # log
    try:
        log_predictions(df_fe, np.array([pred]), np.array([prob]))
    except Exception:
        pass  # logging best-effort

    return {"prediction": int(pred), "probability": prob}
@app.post("/predict-batch-json")
def predict_batch_json(clients: List[LoanApplication]):
    if not clients:
        raise HTTPException(status_code=400, detail="Liste vide.")
    df = pd.DataFrame([c.dict() for c in clients])
    df = clean_and_validate_batch(df)
    df_fe = add_features(df)
    df_fe = ensure_model_dtypes(df_fe)
    try:
        preds = model.predict(df_fe)
        probs = model.predict_proba(df_fe)[:, 1]
    except Exception as e:
        # renvoie dtypes pour debug rapide
        raise HTTPException(status_code=500, detail=f"Erreur prédiction batch: {e}; dtypes={df_fe.dtypes.to_dict()}")

    try:
        log_predictions(df_fe, preds, probs)
    except Exception:
        pass

    out = df.copy()
    out["prediction"] = preds
    out["probability"] = probs
    return JSONResponse(out.to_dict(orient="records"))

@app.post("/predict-batch-file")
async def predict_batch_file(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    try:
        if filename.endswith(".csv"):
            # auto-détection du séparateur (utile pour CSV français)
            df = pd.read_csv(file.file, sep=None, engine="python")
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(status_code=400, detail="Format non supporté. Utilisez .csv ou .xlsx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible de lire le fichier: {e}")

    df = clean_and_validate_batch(df)
    df_fe = add_features(df)
    df_fe = ensure_model_dtypes(df_fe)

    try:
        preds = model.predict(df_fe)
        probs = model.predict_proba(df_fe)[:, 1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction batch: {e}; dtypes={df_fe.dtypes.to_dict()}")

    try:
        log_predictions(df_fe, preds, probs)
    except Exception:
        pass

    out = df.copy()
    out["prediction"] = preds
    out["probability"] = probs
    return JSONResponse(out.to_dict(orient="records"))

@app.post("/feedback")
def save_feedback(feedback: dict):
    """Enregistre un feedback facultatif envoyé par un utilisateur."""
    try:
        df = pd.DataFrame([feedback])
        df["timestamp"] = datetime.utcnow().isoformat()

        header = not FEEDBACK_LOG.exists()
        df.to_csv(FEEDBACK_LOG, mode="a", index=False, header=header)

        return {"status": "ok", "message": "Feedback enregistré"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible d'enregistrer le feedback: {e}")
    
@app.get("/stats")
def stats():
    # Renvoie des stats simples pour la page admin
    try:
        if not PRED_LOG_PATH.exists():
            return {
                "total": 0,
                "approved_rate": 0.0,
                "avg_prob": 0.0,
                "class_counts": {"approved": 0, "rejected": 0},
                "by_property_area": {},
                "prob_hist": [],
            }
        df = pd.read_csv(PRED_LOG_PATH)
        total = len(df)
        approved = int((df["prediction"] == 1).sum())
        rejected = total - approved
        approved_rate = approved / total if total else 0.0
        avg_prob = float(df["probability"].mean()) if total else 0.0

        # group by Property_Area si dispo
        if "Property_Area" in df.columns:
            g = (df[df["prediction"]==1]
                 .groupby("Property_Area")["prediction"].count()
                 .sort_index())
            by_area = {k: int(v) for k, v in g.to_dict().items()}
        else:
            by_area = {}

        # histogramme des probabilités (bins 0.0..1.0 step 0.05)
        bins = np.linspace(0, 1, 21)
        hist, edges = np.histogram(df["probability"], bins=bins)
        prob_hist = [{"bin": f"{edges[i]:.2f}-{edges[i+1]:.2f}", "count": int(hist[i])}
                     for i in range(len(hist))]

        return {
            "total": int(total),
            "approved_rate": float(approved_rate),
            "avg_prob": float(avg_prob),
            "class_counts": {"approved": int(approved), "rejected": int(rejected)},
            "by_property_area": by_area,
            "prob_hist": prob_hist,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats: {e}")

@app.get("/feedback-stats")
def feedback_stats():
    try:
        if not FEEDBACK_LOG.exists():
            return {
                "total": 0,
                "jobSituation": {},
                "loanObjective": {},
                "purchaseDelay": {},
                "avgContribution": 0,
                "discovery": {},
                "discovery_texts": [],
            }

        df = pd.read_csv(FEEDBACK_LOG).fillna("")

        def safe_counts(col):
            return df[col].value_counts().to_dict() if col in df.columns else {}

        return {
            "total": int(len(df)),
            "jobSituation": safe_counts("jobSituation"),
            "loanObjective": safe_counts("loanObjective"),
            "purchaseDelay": safe_counts("purchaseDelay"),
            "avgContribution": float(
                pd.to_numeric(df.get("personalContribution", pd.Series(dtype=float)), errors="coerce").mean() or 0
            ),
            "discovery": safe_counts("discovery"),
            "discovery_texts": df["discovery"].dropna().astype(str).tolist() if "discovery" in df.columns else [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats feedback: {e}")
