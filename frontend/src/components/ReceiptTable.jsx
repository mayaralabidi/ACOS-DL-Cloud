function Pill({ variant, label }) {
  const map = {
    green: { bg: "var(--green-dim)", color: "var(--green-text)" },
    amber: { bg: "var(--amber-dim)", color: "var(--amber)" },
  };
  const s = map[variant];

  return (
    <span
      style={{
        padding: "3px 9px",
        borderRadius: "var(--r4)",
        background: s.bg,
        border: "1px solid var(--border)",
        color: s.color,
        fontFamily: "var(--font-data)",
        fontSize: 10,
        letterSpacing: "0.04em",
      }}
    >
      {label}
    </span>
  );
}

export function ReceiptTable({ items = [], total = 0, confirmedAt }) {
  const hasManualAdjustments = items.some((item) => item.is_override);

  return (
    <div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 44px 84px 84px",
          padding: "7px 14px",
          background: "var(--bg-input)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        {[
          ["Product", "left"],
          ["Qty", "right"],
          ["Unit", "right"],
          ["Total", "right"],
        ].map(([header, align]) => (
          <span
            key={header}
            style={{
              fontFamily: "var(--font-data)",
              fontSize: 10,
              color: "var(--text-muted)",
              letterSpacing: "0.06em",
              textAlign: align,
            }}
          >
            {header.toUpperCase()}
          </span>
        ))}
      </div>

      {items.map((item, i) => (
        <div
          key={`${item.label}-${i}`}
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 44px 84px 84px",
            padding: "7px 14px",
            borderBottom:
              i < items.length - 1 ? "1px solid var(--border)" : "none",
            background: i % 2 ? "var(--bg-row-alt)" : "transparent",
          }}
        >
          <span style={{ fontSize: 12, color: "var(--text-primary)" }}>
            {item.label.replace(/_/g, " ")}
          </span>

          <span
            style={{
              fontFamily: "var(--font-data)",
              fontSize: 12,
              color: "var(--text-secondary)",
              textAlign: "right",
            }}
          >
            {item.qty}
          </span>

          <span
            style={{
              fontFamily: "var(--font-data)",
              fontSize: 12,
              color: "var(--text-secondary)",
              textAlign: "right",
            }}
          >
            {Number(item.unit_price).toFixed(3)}
          </span>

          <span
            style={{
              fontFamily: "var(--font-data)",
              fontSize: 12,
              color: "var(--text-primary)",
              textAlign: "right",
            }}
          >
            {Number(item.subtotal).toFixed(3)}
          </span>
        </div>
      ))}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 44px 84px 84px",
          padding: "10px 14px",
          background: "var(--green-dim)",
          borderTop: "1px solid var(--border-mid)",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-data)",
            fontSize: 11,
            fontWeight: 600,
            color: "var(--green-text)",
            letterSpacing: "0.06em",
            alignSelf: "center",
          }}
        >
          TOTAL
        </span>
        <span />
        <span />
        <span
          style={{
            fontFamily: "var(--font-data)",
            fontSize: 20,
            fontWeight: 700,
            color: "var(--green-vivid)",
            textAlign: "right",
          }}
        >
          {Number(total).toFixed(3)}
        </span>
      </div>

      {(hasManualAdjustments || confirmedAt) && (
        <div
          style={{
            padding: "7px 14px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            gap: 7,
            flexWrap: "wrap",
          }}
        >
          {hasManualAdjustments ? (
            <Pill variant="amber" label="Manually adjusted" />
          ) : null}
          {confirmedAt ? (
            <Pill
              variant="green"
              label={`Confirmed ${new Date(confirmedAt).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}`}
            />
          ) : null}
        </div>
      )}
    </div>
  );
}
