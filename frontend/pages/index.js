import Link from "next/link";
import Image from "next/image";
import heroImg from "../../images/coup-moyen-couple-flou-a-l-interieur.jpg";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative h-[500px] w-full overflow-hidden">
        <Image
          src={heroImg}
          alt="Couple planifiant un projet immobilier"
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center text-center px-4">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white max-w-3xl">
            Estimez vos chances d&apos;approbation pour un prêt immobilier
          </h1>
          <p className="mt-4 text-lg text-slate-200 max-w-2xl">
            Un simulateur intelligent, rapide et gratuit pour particuliers et banques.
          </p>
          <div className="mt-6 flex gap-4">
            <Link
              href="/user"
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold transition"
            >
              Tester maintenant
            </Link>
            <Link
              href="/bank"
              className="px-6 py-3 rounded-xl bg-white/90 hover:bg-white text-slate-800 font-semibold transition"
            >
              Espace Banque
            </Link>
          </div>
        </div>
      </section>

      {/* 3 étapes */}
      <section className="py-16 max-w-6xl mx-auto px-4 text-center space-y-12">
        <h2 className="text-2xl font-bold text-slate-800">Comment ça marche ?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Step
            number="1"
            title="Remplissez vos informations"
            desc="Saisissez vos revenus, situation familiale et montant du prêt."
          />
          <Step
            number="2"
            title="L’IA calcule vos chances"
            desc="Notre modèle prédictif estime en quelques secondes votre éligibilité."
          />
          <Step
            number="3"
            title="Passez à l’action"
            desc="Contactez une banque pour concrétiser votre projet immobilier."
          />
        </div>
      </section>

      {/* Cartes accès */}
      <section className="py-16 bg-slate-100">
        <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-6">
          <Card
            title="👤 Utilisateur"
            desc="Simulez vos chances et explorez différents scénarios."
            href="/user"
          />
          <Card
            title="🏦 Banque"
            desc="Analysez des dossiers individuellement ou par lot (CSV/XLSX)."
            href="/bank"
          />
          <Card
            title="📊 Admin"
            desc="Visualisez les statistiques globales et les feedbacks."
            href="/admin"
          />
        </div>
      </section>
    </main>
  );
}

function Step({ number, title, desc }) {
  return (
    <div className="flex flex-col items-center">
      <div className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-600 text-white text-xl font-bold">
        {number}
      </div>
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      <p className="text-slate-600 mt-2">{desc}</p>
    </div>
  );
}

function Card({ title, desc, href }) {
  return (
    <Link href={href} className="group">
      <div className="h-full bg-white rounded-2xl shadow hover:shadow-lg transition p-6">
        <h3 className="text-lg font-semibold text-slate-900 group-hover:text-blue-600 transition">
          {title}
        </h3>
        <p className="text-sm text-slate-600 mt-2">{desc}</p>
        <span className="inline-block mt-4 text-blue-600 text-sm font-medium">
          Ouvrir →
        </span>
      </div>
    </Link>
  );
}
