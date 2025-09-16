import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";

const NAV = [
  { href: "/", label: "Accueil" },
  { href: "/user", label: "Client" },
  { href: "/bank", label: "Banque" },
  { href: "/admin", label: "Admin" },
];

export default function NavBar() {
  const { pathname } = useRouter();
  const [open, setOpen] = useState(false);

  const base =
    "px-3 py-2 rounded-lg text-sm font-medium transition hover:text-blue-600";
  const active =
    "text-blue-700 bg-blue-50 ring-1 ring-blue-100 hover:text-blue-700";

  return (
    <header className="sticky top-0 z-20 bg-white/80 backdrop-blur border-b">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-extrabold tracking-tight text-slate-900">
          Loan<span className="text-blue-600">Approval</span>
        </Link>

        {/* Desktop */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className={`${base} ${
                pathname === n.href ? active : "text-slate-700"
              }`}
              aria-current={pathname === n.href ? "page" : undefined}
            >
              {n.label}
            </Link>
          ))}
        </nav>

        {/* Mobile */}
        <button
          className="md:hidden inline-flex items-center justify-center w-9 h-9 rounded-lg border text-slate-700"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" />
          </svg>
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t bg-white">
          <nav className="max-w-6xl mx-auto px-4 py-2 grid gap-1">
            {NAV.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                onClick={() => setOpen(false)}
                className={`px-3 py-2 rounded-lg text-sm ${
                  pathname === n.href ? active : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                {n.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
