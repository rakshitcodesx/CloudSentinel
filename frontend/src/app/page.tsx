"use client";

import { useState } from "react";

export default function Dashboard() {
  const [filePath, setFilePath] = useState("examples/vulnerable.json");
  const [findings, setFindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runScan = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: filePath }),
      });
      if (!res.ok) throw new Error("API Request Failed");
      const data = await res.json();
      setFindings(data.data.findings || []);
    } catch (err: any) {
      setError("Failed to reach FastAPI backend. Is it running on port 8000?");
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <header className="border-b border-gray-800 pb-4">
          <h1 className="text-3xl font-bold text-emerald-400">CloudSentinel</h1>
          <p className="text-gray-400">DevSecOps IaC Guardrail</p>
        </header>

        <section className="bg-gray-900 p-6 rounded-lg border border-gray-800 flex gap-4">
          <input
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            className="flex-1 bg-gray-950 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-emerald-500"
            placeholder="Path to IaC file..."
          />
          <button
            onClick={runScan}
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded font-medium disabled:opacity-50 transition-colors"
          >
            {loading ? "Scanning..." : "Run Scan"}
          </button>
        </section>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded">
            {error}
          </div>
        )}

        {findings.length > 0 && (
          <section className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-950 text-gray-400">
                <tr>
                  <th className="p-4 font-medium">Rule ID</th>
                  <th className="p-4 font-medium">Severity</th>
                  <th className="p-4 font-medium">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {findings.map((f, i) => (
                  <tr key={i} className="hover:bg-gray-800/50">
                    <td className="p-4 font-mono text-emerald-400">{f.rule}</td>
                    <td className="p-4">
                      <span className="bg-red-500/10 text-red-400 px-2 py-1 rounded text-xs">
                        {f.severity || "HIGH"}
                      </span>
                    </td>
                    <td className="p-4 text-gray-300">{f.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </div>
    </main>
  );
}
