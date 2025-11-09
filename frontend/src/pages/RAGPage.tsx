import React, { useState } from "react";

export default function RagPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setError(null);
    setAnswer(null);

    const q = question.trim();
    if (!q) {
      setError("Please enter a question");
      return;
    }

    setLoading(true);
    try {
      // Кодируем вопрос в URL
      const url = `/rag_search?question=${encodeURIComponent(q)}`;
      const resp = await fetch(url, {
        method: "GET",
        headers: {
          "Accept": "application/json",
        },
      });

      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`Server error: ${resp.status} ${txt}`);
      }

      const data = await resp.json(); // ожидаем { answer: "..." }
      if (!data || typeof data.answer !== "string") {
        throw new Error("Invalid response from server");
      }

      setAnswer(data.answer);
    } catch (err: any) {
      setError(err.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 className="text-2xl font-bold mb-4">RAG Assistant — Ask a question</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">Question</label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={5}
          placeholder="Type a medical question related to the stored articles..."
          className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          disabled={loading}
        />

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-primary-600 text-white rounded-md disabled:opacity-50"
          >
            {loading ? "Generating..." : "Get Answer"}
          </button>

          <button
            type="button"
            onClick={() => {
              setQuestion("");
              setAnswer(null);
              setError(null);
            }}
            className="px-4 py-2 border rounded-md"
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {answer && (
        <div className="mt-6 bg-white border rounded-lg p-4 shadow-sm">
          <h3 className="text-lg font-semibold mb-2">Answer</h3>
          <p className="whitespace-pre-wrap text-gray-800">{answer}</p>
        </div>
      )}
    </div>
  );
}
