import { useEffect, useState } from "react";
import { getStats, getFeedbackStats } from "../utils/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell,
  CartesianGrid, Legend
} from "recharts";
import AdminLogin from "../components/AdminLogin";

const COLORS = ["#10b981","#3b82f6","#f59e0b","#ef4444","#8b5cf6","#14b8a6","#6366f1"];

export default function AdminPage() {
  const [stats, setStats] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [err, setErr] = useState("");
  const [logged, setLogged] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [s, f] = await Promise.all([getStats(), getFeedbackStats()]);
        setStats(s); setFeedback(f);
      } catch (e) { setErr(e.message || "Erreur stats"); }
    })();
  }, []);

  if (!logged) return <AdminLogin onSuccess={() => setLogged(true)} />;

  if (err) return <div className="p-6 text-red-600">{err}</div>;

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-6xl mx-auto space-y-10">
        <h1 className="text-3xl font-bold">Dashboard Admin</h1>

        {/* --- Section prédictions --- */}
        {stats && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">📊 Statistiques des prédictions</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <Card title="Total prédictions" value={stats.total} />
              <Card title="Taux d’approbation" value={`${Math.round(stats.approved_rate*100)}%`} />
              <Card title="Proba moyenne" value={`${(stats.avg_prob*100).toFixed(1)}%`} />
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <ChartWrapper title="Approbations par zone">
                <BarChart width={520} height={260}
                  data={Object.entries(stats.by_property_area).map(([k,v])=>({area:k, approved:v}))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="area" /><YAxis /><Tooltip /><Legend />
                  <Bar dataKey="approved" fill="#3b82f6" />
                </BarChart>
              </ChartWrapper>

              <ChartWrapper title="Répartition classes">
                <PieChart width={520} height={260}>
                  <Pie data={[
                      {name:"Approvals", value: stats.class_counts.approved},
                      {name:"Refus", value: stats.class_counts.rejected},
                    ]}
                    dataKey="value" cx="50%" cy="50%" outerRadius={90}>
                    {[0,1].map(i => <Cell key={i} fill={COLORS[i]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ChartWrapper>
            </div>
          </div>
        )}
        <hr className="my-10 border-t-2 border-slate-200" />
        {/* --- Section feedback --- */}
        {feedback && feedback.total > 0 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">🗣️ Feedback utilisateurs</h2>
            <div className="flex justify-center gap-6">
              <div className="flex-1 max-w-xs">
                <Card title="Total feedbacks" value={feedback.total} />
              </div>
              <div className="flex-1 max-w-xs">
                <Card title="Apport moyen" value={`${Math.round(feedback.avgContribution)} €`} />
              </div>  
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <ChartWrapper title="Situation professionnelle">
                <PieChart width={520} height={260}>
                  <Pie data={Object.entries(feedback.jobSituation).map(([k,v])=>({name:k, value:v}))}
                       dataKey="value" cx="50%" cy="50%" outerRadius={90}>
                    {Object.keys(feedback.jobSituation).map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ChartWrapper>

              <ChartWrapper title="Objectif du prêt">
                <BarChart width={520} height={260}
                  data={Object.entries(feedback.loanObjective).map(([k,v])=>({name:k, value:v}))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" /><YAxis /><Tooltip />
                  <Bar dataKey="value" fill="#8b5cf6" />
                </BarChart>
              </ChartWrapper>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <ChartWrapper title="Délai d’achat prévu">
                <BarChart width={520} height={260}
                  data={Object.entries(feedback.purchaseDelay).map(([k,v])=>({name:k, value:v}))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" /><YAxis /><Tooltip />
                  <Bar dataKey="value" fill="#f59e0b" />
                </BarChart>
              </ChartWrapper>

              <ChartWrapper title="Comment ont-ils connu le simulateur ?">
                <PieChart width={520} height={260}>
                  <Pie data={Object.entries(feedback.discovery).map(([k,v])=>({name:k, value:v}))}
                       dataKey="value" cx="50%" cy="50%" outerRadius={90}>
                    {Object.keys(feedback.discovery).map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ChartWrapper>

            </div>
          </div>
        )}
      </div>
    </main>
  );
}

function Card({ title, value }) {
  return (
    <div className="bg-white rounded-xl p-4 shadow text-center">
      <div className="text-slate-500 text-sm">{title}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}

function ChartWrapper({ title, children }) {
  return (
    <div className="bg-white p-4 rounded-2xl shadow">
      <h3 className="font-semibold mb-2">{title}</h3>
      {children}
    </div>
  );
}
