import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function confidenceColor(confidence) {
  if (confidence >= 0.7) return "var(--green-vivid)";
  if (confidence >= 0.4) return "var(--amber)";
  return "var(--red)";
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;

  const d = payload[0].payload;

  return (
    <div
      style={{
        background: "var(--bg-elevated)",
        border: "1px solid var(--border-mid)",
        borderRadius: "var(--r8)",
        padding: "7px 11px",
        fontFamily: "var(--font-data)",
        fontSize: 11,
      }}
    >
      <div style={{ color: "var(--text-secondary)", marginBottom: 3 }}>
        {d.label.replace(/_/g, " ")}
      </div>
      <div style={{ color: confidenceColor(d.confidence), fontWeight: 600 }}>
        {(d.confidence * 100).toFixed(1)}%
      </div>
    </div>
  );
}

export function ConfidenceChart({ items = [] }) {
  const sorted = [...items]
    .map((item) => ({
      ...item,
      confidence:
        typeof item.confidence === "number"
          ? item.confidence
          : item.unit_price > 0
            ? 0.85
            : 0.6,
    }))
    .sort((a, b) => b.confidence - a.confidence);

  if (!sorted.length) return null;

  return (
    <div style={{ padding: "14px 0 8px" }}>
      <div
        style={{
          fontFamily: "var(--font-data)",
          fontSize: 10,
          color: "var(--text-muted)",
          letterSpacing: "0.06em",
          padding: "0 14px 10px",
        }}
      >
        DETECTION CONFIDENCE
      </div>

      <ResponsiveContainer width="100%" height={sorted.length * 30 + 32}>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 0, right: 44, left: 14, bottom: 0 }}
        >
          <XAxis
            type="number"
            domain={[0, 1]}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            tick={{
              fontFamily: "var(--font-data)",
              fontSize: 10,
              fill: "var(--text-muted)",
            }}
            axisLine={{ stroke: "var(--border)" }}
            tickLine={false}
          />

          <YAxis
            type="category"
            dataKey="label"
            width={126}
            tickFormatter={(v) => v.replace(/_/g, " ").slice(0, 18)}
            tick={{
              fontFamily: "var(--font-body)",
              fontSize: 11,
              fill: "var(--text-secondary)",
            }}
            axisLine={false}
            tickLine={false}
          />

          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: "var(--bg-row-alt)" }}
          />

          <Bar dataKey="confidence" radius={[0, 2, 2, 0]} barSize={12}>
            {sorted.map((entry, i) => (
              <Cell key={i} fill={confidenceColor(entry.confidence)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
