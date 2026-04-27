import { useEffect, useState } from "react";

import { listSessions } from "../api/client";
import { Header } from "../components/Header";

export function HistoryPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isHealthy, setIsHealthy] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await listSessions();
        if (mounted) setSessions(data);
      } catch (e) {
        if (mounted) setError(e.response?.data?.detail || e.message);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    const baseUrl =
      import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";
    (async () => {
      try {
        const response = await fetch(`${baseUrl}/health`);
        if (mounted) setIsHealthy(response.ok);
      } catch {
        if (mounted) setIsHealthy(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="page-shell">
      <Header
        sessionId={null}
        runningTotal={null}
        env={import.meta.env.MODE || "dev"}
        isHealthy={isHealthy}
      />

      <div className="history-wrap">
        <div className="history-title">SESSION HISTORY</div>

        {loading ? <p className="history-state">Loading sessions...</p> : null}
        {error ? <p className="history-state error">{error}</p> : null}

        {!loading && !error ? (
          <div className="surface-card" style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr
                  style={{
                    borderBottom: "1px solid var(--border)",
                    textAlign: "left",
                  }}
                >
                  <th
                    style={{
                      padding: "10px 12px",
                      color: "var(--text-muted)",
                      fontFamily: "var(--font-data)",
                      fontSize: 10,
                      letterSpacing: "0.06em",
                    }}
                  >
                    ID
                  </th>
                  <th
                    style={{
                      padding: "10px 12px",
                      color: "var(--text-muted)",
                      fontFamily: "var(--font-data)",
                      fontSize: 10,
                      letterSpacing: "0.06em",
                    }}
                  >
                    STATUS
                  </th>
                  <th
                    style={{
                      padding: "10px 12px",
                      color: "var(--text-muted)",
                      fontFamily: "var(--font-data)",
                      fontSize: 10,
                      letterSpacing: "0.06em",
                      textAlign: "right",
                    }}
                  >
                    TOTAL
                  </th>
                  <th
                    style={{
                      padding: "10px 12px",
                      color: "var(--text-muted)",
                      fontFamily: "var(--font-data)",
                      fontSize: 10,
                      letterSpacing: "0.06em",
                    }}
                  >
                    CREATED
                  </th>
                </tr>
              </thead>

              <tbody>
                {sessions.map((s, idx) => (
                  <tr
                    key={s.id}
                    style={{
                      borderBottom: "1px solid var(--border)",
                      background: idx % 2 ? "var(--bg-row-alt)" : "transparent",
                    }}
                  >
                    <td
                      style={{
                        padding: "10px 12px",
                        fontFamily: "var(--font-data)",
                        fontSize: 11,
                        color: "var(--text-secondary)",
                      }}
                    >
                      {s.id}
                    </td>
                    <td
                      style={{
                        padding: "10px 12px",
                        color: "var(--text-primary)",
                        fontSize: 12,
                      }}
                    >
                      {s.status}
                    </td>
                    <td
                      style={{
                        padding: "10px 12px",
                        textAlign: "right",
                        fontFamily: "var(--font-data)",
                        color: "var(--green-vivid)",
                        fontWeight: 600,
                      }}
                    >
                      {Number(s.total || 0).toFixed(3)} TND
                    </td>
                    <td
                      style={{
                        padding: "10px 12px",
                        color: "var(--text-secondary)",
                        fontSize: 12,
                      }}
                    >
                      {new Date(s.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </div>
  );
}
