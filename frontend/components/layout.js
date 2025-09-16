import NavBar from "./navbar";

export default function Layout({ children }) {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <NavBar />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-10 w-full">{children}</main>
      <footer className="border-t py-6 text-center text-sm text-slate-500">
        {new Date().getFullYear()} LoanApproval Project — Péma Belise-Perreard — ECE — B3
      </footer>
    </div>
  );
}

