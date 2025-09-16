import { useState, useMemo } from "react";
import Jauge from "../components/Jauge";
import { predictOne, predictBatchFile, getTemplateCsv } from "../utils/api";

const selects = {
  Gender: ["Male","Female"],
  Married: ["Yes","No"],
  Dependents: ["0","1","2","3+"],
  Education: ["Graduate","Not Graduate"],
  Self_Employed: ["Yes","No"],
  Property_Area: ["Urban","Semiurban","Rural"],
};

export default function BankPage() {
  // --- Saisie d'un client (manuel) ---
  const [one, setOne] = useState({
    Gender:"Male", Married:"Yes", Dependents:"0", Education:"Graduate",
    Self_Employed:"No", Property_Area:"Urban",
    ApplicantIncome:5000, CoapplicantIncome:2000, LoanAmount:200000
  });
  const [resOne, setResOne] = useState(null);

  // --- Batch ---
  const [file, setFile] = useState(null);
  const [batch, setBatch] = useState([]);          // résultats
  const [idx, setIdx] = useState(0);               // index courant dans les résultats

  // --- Etats / erreurs ---
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  function updOne(k, v) { setOne(o => ({ ...o, [k]: v })); }

  async function onPredictOne(e) {
    e.preventDefault();
    setErr(""); setResOne(null); setBusy(true);
    try { setResOne(await predictOne(one)); }
    catch(e){ setErr(normalizeErr(e)); }
    finally{ setBusy(false); }
  }

  function onFileChange(e) {
    const f = e.target.files?.[0] || null;
    setFile(f);
    setBatch([]);
    setIdx(0);
    setErr("");
  }

  async function onPredictFile() {
    if (!file) return;
    setErr(""); setBatch([]); setIdx(0); setBusy(true);
    try {
      const data = await predictBatchFile(file);
      setBatch(data || []);
      setIdx(0);
    } catch (e) {
      setErr(normalizeErr(e));
    } finally {
      setBusy(false);
    }
  }

  async function downloadTemplate(){
    try {
      const blob = await getTemplateCsv();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a"); a.href = url; a.download = "loan_template.csv"; a.click();
      URL.revokeObjectURL(url);
    } catch(e){ setErr(normalizeErr(e)); }
  }

  const current = batch[idx] || null;
  const summary = useMemo(() => {
    if (!batch.length) return null;
    const approved = batch.filter(b => Number(b.prediction) === 1).length;
    const avgProb = batch.reduce((s,b)=>s+Number(b.probability||0),0) / batch.length;
    return { total: batch.length, approved, rejected: batch.length - approved, avgProb };
  }, [batch]);

  return (
    <main className="space-y-8">
      <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Espace Banque</h1>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* --- Carte: Saisie individuelle --- */}
        <div className="bg-white p-6 rounded-2xl shadow space-y-4">
          <h2 className="text-xl font-semibold">Saisie d&apos;informations client</h2>
          <form onSubmit={onPredictOne} className="grid md:grid-cols-2 gap-4">
            {Object.entries(selects).map(([k, values]) => (
              <label key={k} className="flex flex-col">
                <span className="text-sm font-medium text-slate-700 mb-1">{k}</span>
                <select
                  className="border rounded-xl p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                  value={one[k]}
                  onChange={(e)=>updOne(k,e.target.value)}
                >
                  {values.map(v => <option key={v} value={v}>{v}</option>)}
                </select>
              </label>
            ))}
            <Field label="ApplicantIncome (€)">
              <input type="number" min={0} className="border rounded-xl p-2 w-full focus:ring-2 focus:ring-blue-500 outline-none"
                     value={one.ApplicantIncome} onChange={e=>updOne("ApplicantIncome", +e.target.value)} />
            </Field>
            <Field label="CoapplicantIncome (€)">
              <input type="number" min={0} className="border rounded-xl p-2 w-full focus:ring-2 focus:ring-blue-500 outline-none"
                     value={one.CoapplicantIncome} onChange={e=>updOne("CoapplicantIncome", +e.target.value)} />
            </Field>
            <Field label="LoanAmount (€)">
              <input type="number" min={1000} step={1000} className="border rounded-xl p-2 w-full focus:ring-2 focus:ring-blue-500 outline-none"
                     value={one.LoanAmount} onChange={e=>updOne("LoanAmount", +e.target.value)} />
            </Field>

            <div className="md:col-span-2">
              <button disabled={busy}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-5 py-2 rounded-xl transition">
                {busy ? "Prédiction…" : "Prédire"}
              </button>
            </div>
          </form>

          {resOne && (
            <div className="mt-2 flex items-center gap-6">
              <Jauge value={resOne.probability} />
              <div>
                <h3 className="text-lg font-semibold mb-1">Résultat</h3>
                {resOne.prediction === 1 ? (
                  <p className="text-emerald-600 font-semibold">✅ Prêt APPROUVÉ</p>
                ) : (
                  <p className="text-rose-600 font-semibold">❌ Prêt REFUSÉ</p>
                )}
                <p className="text-slate-600 mt-2 text-sm">Probabilité : {(resOne.probability*100).toFixed(2)}%</p>
              </div>
            </div>
          )}
        </div>

        {/* --- Carte: Batch --- */}
        <div className="bg-white p-6 rounded-2xl shadow space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Fichier (CSV/XLSX)</h2>
            <button onClick={downloadTemplate} className="text-blue-600 hover:underline">
              Télécharger le template
            </button>
          </div>

          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={onFileChange}
            className="block w-full border rounded-xl p-2"
          />

          <div className="flex items-center gap-3">
            <button
              onClick={onPredictFile}
              disabled={!file || busy}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-xl transition disabled:opacity-50"
            >
              {busy ? "Analyse en cours…" : "Prédire le fichier"}
            </button>
          </div>

          {err && <p className="text-rose-600 text-sm">{err}</p>}

          {/* Résumé batch */}
          {summary && (
            <div className="grid md:grid-cols-3 gap-3 mt-2">
              <Stat title="Total dossiers" value={summary.total} />
              <Stat title="Approbations" value={summary.approved} positive />
              <Stat title="Proba moyenne" value={`${(summary.avgProb*100).toFixed(1)}%`} />
            </div>
          )}

          {/* Viewer par dossier (sans tableau) */}
          {current && (
            <div className="mt-4 p-4 border rounded-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Dossier {idx+1} / {batch.length}</h3>
                <div className="flex gap-2">
                  <button
                    className="px-3 py-1 rounded-lg border hover:bg-slate-50"
                    onClick={()=>setIdx(i => Math.max(0, i-1))}
                    disabled={idx === 0}
                  >
                    ← Précédent
                  </button>
                  <button
                    className="px-3 py-1 rounded-lg border hover:bg-slate-50"
                    onClick={()=>setIdx(i => Math.min(batch.length-1, i+1))}
                    disabled={idx === batch.length-1}
                  >
                    Suivant →
                  </button>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-6">
                <Jauge value={Number(current.probability || 0)} />
                <div>
                  {Number(current.prediction) === 1 ? (
                    <p className="text-emerald-600 font-semibold text-lg">✅ Prêt APPROUVÉ</p>
                  ) : (
                    <p className="text-rose-600 font-semibold text-lg">❌ Prêt REFUSÉ</p>
                  )}
                  <p className="text-slate-600 mt-2 text-sm">
                    Probabilité : {((Number(current.probability||0))*100).toFixed(2)}%
                  </p>
                </div>
              </div>

              <details className="mt-4">
                <summary className="cursor-pointer text-sm text-slate-700">Voir les informations du client</summary>
                <div className="grid md:grid-cols-3 gap-3 text-sm mt-3">
                  {[
                    "Gender","Married","Dependents","Education","Self_Employed","Property_Area",
                    "ApplicantIncome","CoapplicantIncome","LoanAmount"
                  ].map(k => (
                    <div key={k} className="p-2 rounded-lg bg-slate-50">
                      <div className="text-slate-500">{k}</div>
                      <div className="font-medium">{String(current[k])}</div>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

function Field({ label, children }) {
  return (
    <label className="flex flex-col">
      <span className="text-sm font-medium text-slate-700 mb-1">{label}</span>
      {children}
    </label>
  );
}

function Stat({ title, value, positive }) {
  return (
    <div className="bg-slate-50 rounded-xl p-4">
      <div className="text-slate-500 text-xs">{title}</div>
      <div className={`text-xl font-bold ${positive ? "text-emerald-600" : "text-slate-900"}`}>{value}</div>
    </div>
  );
}

function normalizeErr(e) {
  // essaie d'extraire un JSON renvoyé par l'API FastAPI; sinon retourne le message brut
  try {
    const j = JSON.parse(e.message);
    if (typeof j === "string") return j;
    return j.detail?.message || j.detail || j.message || e.message || "Erreur";
  } catch {
    return e.message || "Erreur";
  }
}
