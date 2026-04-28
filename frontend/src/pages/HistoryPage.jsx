import { useEffect, useState } from "react";

import { listSessions } from "../api/client";
import { Header } from "../components/Header";

function formatReceiptText(session) {
  const items = Array.isArray(session.receipt_items)
    ? session.receipt_items
    : [];
  const lines = [
    "ACOS RECEIPT",
    `Session: ${session.id}`,
    `Status: ${session.status}`,
    `Created: ${new Date(session.created_at).toLocaleString()}`,
  ];

  if (session.confirmed_at) {
    lines.push(`Confirmed: ${new Date(session.confirmed_at).toLocaleString()}`);
  }

  lines.push("", "Items:");

  items.forEach((item) => {
    lines.push(
      `- ${item.label.replace(/_/g, " ")} x${item.qty} | ${Number(item.unit_price).toFixed(3)} TND | ${Number(item.subtotal).toFixed(3)} TND`,
    );
  });

  lines.push("", `Total: ${Number(session.total || 0).toFixed(3)} TND`);

  if (session.error) {
    lines.push("", `Error: ${session.error}`);
  }

  return lines.join("\n");
}

function buildReceiptHtml(session) {
  const items = Array.isArray(session.receipt_items)
    ? session.receipt_items
    : [];
  const rows = items
    .map(
      (item) => `
        <tr>
          <td>${item.label.replace(/_/g, " ")}</td>
          <td>${item.qty}</td>
          <td>${Number(item.unit_price).toFixed(3)} TND</td>
          <td>${Number(item.subtotal).toFixed(3)} TND</td>
        </tr>`,
    )
    .join("");

  return `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8" />
      <title>Receipt ${session.id}</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 24px; color: #111; }
        h1 { margin: 0 0 8px; font-size: 20px; }
        .meta { color: #555; font-size: 12px; margin-bottom: 18px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid #ddd; }
        th { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #666; }
        tfoot td { font-weight: 700; border-top: 2px solid #111; border-bottom: 0; }
        .total { text-align: right; font-size: 18px; font-weight: 700; margin-top: 14px; }
        @media print { body { padding: 0; } }
      </style>
    </head>
    <body>
      <h1>ACOS Receipt</h1>
      <div class="meta">
        <div><strong>Session:</strong> ${session.id}</div>
        <div><strong>Status:</strong> ${session.status}</div>
        <div><strong>Created:</strong> ${new Date(session.created_at).toLocaleString()}</div>
        ${session.confirmed_at ? `<div><strong>Confirmed:</strong> ${new Date(session.confirmed_at).toLocaleString()}</div>` : ""}
      </div>
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Qty</th>
            <th>Unit</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          ${rows || "<tr><td colspan='4'>No receipt items available.</td></tr>"}
        </tbody>
      </table>
      <div class="total">Total: ${Number(session.total || 0).toFixed(3)} TND</div>
    </body>
  </html>`;
}

function downloadReceipt(session) {
  const blob = new Blob([formatReceiptText(session)], {
    type: "text/plain;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `receipt-${session.id}.txt`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function printReceipt(session) {
  const win = window.open("", "_blank", "width=420,height=700");
  if (!win) return;

  win.document.open();
  win.document.write(buildReceiptHtml(session));
  win.document.close();
  win.focus();
  setTimeout(() => {
    win.focus();
    win.print();
  }, 250);
}

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

  const confidenceItems = sessions
    .flatMap((session) => {
      const rawItems = session.receipt_raw?.items || [];
      const diagnostics = session.receipt_raw?.diagnostics || [];
      const diagnosticByLabel = new Map(
        diagnostics.map((entry) => [entry.label, entry]),
      );

      return rawItems.map((item) => {
        const diagnostic = diagnosticByLabel.get(item.label);
        const confidence =
          typeof item.confidence === "number"
            ? item.confidence
            : typeof diagnostic?.avg_confidence === "number"
              ? diagnostic.avg_confidence
              : null;

        return {
          label: item.label,
          confidence,
        };
      });
    })
    .filter((item) => typeof item.confidence === "number");

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
          <>
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
                      RECEIPT
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {sessions.map((s, idx) => (
                    <tr
                      key={s.id}
                      style={{
                        borderBottom: "1px solid var(--border)",
                        background:
                          idx % 2 ? "var(--bg-row-alt)" : "transparent",
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
                      <td
                        style={{
                          padding: "10px 12px",
                          textAlign: "right",
                        }}
                      >
                        <div
                          style={{
                            display: "inline-flex",
                            gap: 8,
                            justifyContent: "flex-end",
                          }}
                        >
                          <button
                            type="button"
                            className="btn btn-ghost"
                            disabled={!s.receipt_items?.length}
                            onClick={() => printReceipt(s)}
                            style={{ padding: "5px 10px", fontSize: 11 }}
                          >
                            Print
                          </button>
                          <button
                            type="button"
                            className="btn btn-primary"
                            disabled={!s.receipt_items?.length}
                            onClick={() => downloadReceipt(s)}
                            style={{ padding: "5px 10px", fontSize: 11 }}
                          >
                            Download
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {confidenceItems.length ? (
              <div className="surface-card" style={{ marginTop: 14 }}>
                <div
                  className="history-title"
                  style={{ padding: "14px 14px 0" }}
                >
                  CONFIDENCE ANALYTICS
                </div>
                <div style={{ padding: "0 14px 14px" }}>
                  <ul style={{ listStyle: "none", display: "grid", gap: 6 }}>
                    {confidenceItems.slice(0, 12).map((item, index) => (
                      <li
                        key={`${item.label}-${index}`}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 12,
                          padding: "8px 10px",
                          border: "1px solid var(--border)",
                          borderRadius: "var(--r8)",
                          background: "var(--bg-input)",
                          fontFamily: "var(--font-data)",
                        }}
                      >
                        <span>{item.label.replace(/_/g, " ")}</span>
                        <strong>{(item.confidence * 100).toFixed(1)}%</strong>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : null}
          </>
        ) : null}
      </div>
    </div>
  );
}
