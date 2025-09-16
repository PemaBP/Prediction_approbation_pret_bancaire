import { useState } from "react";

export default function AdminLogin({ onSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  function handleLogin(e) {
    e.preventDefault();
    if (username === "pemabp" && password === "1234") {
      onSuccess();
    } else {
    setErr(<span style={{ color: "red" }}>Identifiants invalides</span>);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-2xl shadow w-full max-w-sm space-y-6"
      >
        <h1 className="text-2xl font-bold text-center">Connexion Admin</h1>

        <div>
          <label className="block text-sm font-medium text-slate-700">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 w-full border rounded-xl p-2 focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full border rounded-xl p-2 focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        {err && <p className="text-red-600 text-sm">{err}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-xl transition"
        >
          Se connecter
        </button>
      </form>
    </div>
  );
}
