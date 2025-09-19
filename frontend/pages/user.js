import { useState } from "react";
import Jauge from "../components/Jauge";
import Image from "next/image";
import bannerImg from "../../images/lay-plat-du-concept-immobilier.jpg";
import { predictOne, sendFeedback } from "../utils/api";

const selects = {
  Gender: ["Male","Female"],
  Married: ["Yes","No"],
  Dependents: ["0","1","2","3+"],
  Education: ["Graduate","Not Graduate"],
  Self_Employed: ["Yes","No"],
  Property_Area: ["Urban","Semiurban","Rural"],
};

export default function UserPage() {
  // --- Formulaire prédiction ---
  const [form, setForm] = useState({
    Gender:"Male", Married:"Yes", Dependents:"0", Education:"Graduate",
    Self_Employed:"No", Property_Area:"Urban",
    ApplicantIncome:5000, CoapplicantIncome:2000, LoanAmount:200000,
  });
  const [loading, setLoading] = useState(false);
  const [resu, setResu] = useState(null);
  const [err, setErr] = useState("");

  // --- Formulaire feedback ---
  const [feedback, setFeedback] = useState({
    jobSituation: "",
    personalContribution: "",
    loanObjective: "",
    purchaseDelay: "",
    discovery: "",
  });
  const [saved, setSaved] = useState(false);

  function upd(name, value) { setForm(f => ({ ...f, [name]: value })); }
  async function onSubmit(e){
    e.preventDefault(); setErr(""); setResu(null); setLoading(true);
    try { setResu(await predictOne(form)); } catch(e){ setErr(e.message || "Erreur"); }
    finally { setLoading(false); }
  }

  function updFeedback(name, value) { setFeedback(f => ({ ...f, [name]: value })); }
  async function onSubmitFeedback(e){
   e.preventDefault();
   try {
    await sendFeedback(feedback);
    setSaved(true);
    setFeedback({
       jobSituation: "",
       personalContribution: "",
       loanObjective: "",
       purchaseDelay: "",
       discovery: "",
     });
     setTimeout(() => setSaved(false), 3000);
   } catch (err) {
     console.error("Erreur feedback:", err);
    }
  }

  return (
    <section className="space-y-10">
      {/* Image + intro */}
      <div className="relative w-full h-72 md:h-96 rounded-2xl overflow-hidden shadow">
        <Image src={bannerImg} alt="Concept immobilier" fill className="object-cover" priority />
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
          <h1 className="text-3xl md:text-5xl font-extrabold text-white text-center max-w-3xl">
            Simulateur de prêt immobilier
          </h1>
        </div>
      </div>

      <div className="text-center max-w-3xl mx-auto space-y-3">
        <p className="text-lg text-slate-700">
          Découvrez vos chances d&apos;approbation de votre prêt immobilier grâce à notre modèle d&apos;intelligence artificielle.
          Remplissez le formulaire ci-dessous pour obtenir une estimation personnalisée.
        </p>
      <div className="text-center max-w-3xl mx-auto">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mt-4">
          <p className="text-slate-600 text-sm">
            Cette estimation est fournie à titre indicatif.  
            Pour une étude personnalisée et des conseils adaptés à votre situation,  
            rapprochez-vous de votre banque locale ou d’un conseiller immobilier.
          </p>
        </div>
      </div>
      </div>

      {/* Formulaire principal prédiction */}
      <form onSubmit={onSubmit} className="bg-white p-8 rounded-2xl shadow space-y-6">
        <h2 className="text-2xl font-semibold">Vos informations</h2>

        <div className="grid md:grid-cols-3 gap-6">
          {Object.entries(selects).map(([k, values]) => (
            <label key={k} className="flex flex-col">
              <span className="text-sm font-medium text-slate-700 mb-1">{k}</span>
              <select
                className="border rounded-xl p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                value={form[k]} onChange={(e)=>upd(k,e.target.value)}
              >
                {values.map(v => <option key={v} value={v}>{v}</option>)}
              </select>
            </label>
          ))}

          <Field label="ApplicantIncome (€)">
            <input type="number" min={0} className="border rounded-xl p-2 w-full focus:ring-2 focus:ring-blue-500 outline-none"
                   value={form.ApplicantIncome} onChange={e=>upd("ApplicantIncome", +e.target.value)} />
          </Field>
          <Field label="CoapplicantIncome (€)">
            <input type="number" min={0} className="border rounded-xl p-2 w-full focus:ring-2 focus:ring-blue-500 outline-none"
                   value={form.CoapplicantIncome} onChange={e=>upd("CoapplicantIncome", +e.target.value)} />
          </Field>
          <Field label="LoanAmount (€)">
            <input type="number" min={1000} step={1000} className="border rounded-xl p-2 w-full focus:ring-2 focus:ring-blue-500 outline-none"
                   value={form.LoanAmount} onChange={e=>upd("LoanAmount", +e.target.value)} />
          </Field>
        </div>

        <button
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-3 rounded-xl transition"
        >
          {loading ? "Prédiction…" : "Estimer mes chances"}
        </button>
        {err && <p className="text-red-600 text-sm">{err}</p>}
      </form>

      {/* Résultat prédiction */}
      {resu && (
        <div className="bg-white p-8 rounded-2xl shadow flex flex-col items-center text-center">
          <Jauge value={resu.probability} />
          <h2 className="text-xl font-semibold mt-4">Résultat</h2>
          {resu.prediction === 1 ? (
            <p className="text-emerald-600 font-semibold">Votre prêt a de fortes chances d&apos;être approuvé</p>
          ) : (
            <p className="text-rose-600 font-semibold">Votre prêt a peu de chances d&apos;être approuvé</p>
          )}
          <p className="text-slate-600 mt-2 text-sm">
            Probabilité estimée : {(resu.probability*100).toFixed(2)}%
          </p>
        </div>
      )}

      {/* Formulaire feedback facultatif */}
      <form onSubmit={onSubmitFeedback} className="bg-white p-8 rounded-2xl shadow space-y-6">
        <h2 className="text-2xl font-semibold">Partagez plus d&apos;informations (facultatif)</h2>
        <p className="text-slate-600 text-sm">
          Ces informations ne sont pas utilisées dans la prédiction mais nous aident à améliorer le service.
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <Field label="Votre situation professionnelle">
            <select className="border rounded-xl p-2" value={feedback.jobSituation}
                    onChange={e=>updFeedback("jobSituation", e.target.value)}>
              <option value="">-- Sélectionner --</option>
              <option value="CDI">CDI</option>
              <option value="CDD">CDD</option>
              <option value="Indépendant">Indépendant</option>
              <option value="Sans emploi">Sans emploi</option>
            </select>
          </Field>

          <Field label="Apport personnel prévu (€)">
            <input type="number" className="border rounded-xl p-2"
                   value={feedback.personalContribution}
                   onChange={e=>updFeedback("personalContribution", e.target.value)} />
          </Field>

          <Field label="Objectif du prêt">
            <select className="border rounded-xl p-2" value={feedback.loanObjective}
                    onChange={e=>updFeedback("loanObjective", e.target.value)}>
              <option value="">-- Sélectionner --</option>
              <option value="Résidence principale">Résidence principale</option>
              <option value="Résidence secondaire">Résidence secondaire</option>
              <option value="Investissement locatif">Investissement locatif</option>
            </select>
          </Field>

          <Field label="Délai prévu pour l&apos;achat">
            <select className="border rounded-xl p-2" value={feedback.purchaseDelay}
                    onChange={e=>updFeedback("purchaseDelay", e.target.value)}>
              <option value="">-- Sélectionner --</option>
              <option value="Moins de 3 mois">Moins de 3 mois</option>
              <option value="3 à 6 mois">3 à 6 mois</option>
              <option value="6 à 12 mois">6 à 12 mois</option>
              <option value="Plus de 12 mois">Plus de 12 mois</option>
            </select>
          </Field>

          <Field label="Comment avez-vous connu ce simulateur ?">
            <input type="text" className="border rounded-xl p-2"
                   value={feedback.discovery}
                   onChange={e=>updFeedback("discovery", e.target.value)} />
          </Field>
        </div>

        <button className="bg-slate-700 hover:bg-slate-800 text-white px-5 py-3 rounded-xl font-semibold">
          Envoyer le feedback
        </button>

        {saved && <p className="text-emerald-600 text-sm">✅ Merci pour votre retour !</p>}
      </form>
    </section>
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
