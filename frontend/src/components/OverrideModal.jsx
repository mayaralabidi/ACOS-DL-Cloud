import { useState } from "react";

export function OverrideModal({ open, onClose, onSubmit, disabled }) {
  const [label, setLabel] = useState("");
  const [qty, setQty] = useState(1);
  const [action, setAction] = useState("add");

  if (!open) return null;

  function handleSubmit(e) {
    e.preventDefault();
    if (!label.trim()) return;
    onSubmit(action, label.trim(), Number(qty) || 1);
    onClose();
  }

  return (
    <div
      className="fixed inset-0"
      style={{
        minHeight: 500,
        background: "rgba(0,0,0,0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "var(--r12)",
        zIndex: 120,
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          width: "100%",
          maxWidth: 520,
          background: "var(--bg-elevated)",
          border: "1px solid var(--border-mid)",
          borderRadius: "var(--r12)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "14px 18px",
            borderBottom: "1px solid var(--border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-data)",
              fontSize: 13,
              fontWeight: 500,
              color: "var(--text-primary)",
              letterSpacing: "0.03em",
            }}
          >
            Override receipt
          </span>

          <button
            onClick={onClose}
            type="button"
            style={{
              background: "none",
              border: "none",
              color: "var(--text-muted)",
              fontSize: 18,
              lineHeight: 1,
            }}
            aria-label="Close override dialog"
          >
            x
          </button>
        </div>

        <div style={{ padding: "16px 18px", display: "grid", gap: 12 }}>
          <div
            style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}
          >
            <select value={action} onChange={(e) => setAction(e.target.value)}>
              <option value="add">add</option>
              <option value="remove">remove</option>
            </select>

            <input
              type="number"
              min={1}
              value={qty}
              onChange={(e) => setQty(e.target.value)}
            />
          </div>

          <select value={label} onChange={(e) => setLabel(e.target.value)}>
            <option value="">Select product label</option>
            <option value="milk_delice">milk_delice</option>
            <option value="juice_diva">juice_diva</option>
            <option value="soapbar_dove_shea">soapbar_dove_shea</option>
            <option value="toothpaste_colgate">toothpaste_colgate</option>
          </select>

          <input
            placeholder="Or type product label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
          ></input>
        </div>

        <div
          style={{
            padding: "12px 18px",
            borderTop: "1px solid var(--border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
          }}
        >
          <button
            type="button"
            className="btn btn-ghost"
            style={{ width: "auto", padding: "7px 16px" }}
            onClick={onClose}
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={disabled}
            className="btn btn-primary"
            style={{ width: "auto", padding: "7px 16px" }}
          >
            Save changes
          </button>
        </div>
      </form>
    </div>
  );
}
