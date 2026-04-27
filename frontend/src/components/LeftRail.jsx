const STATUS_MAP = {
  idle: {
    label: "Ready",
    className: "status-idle",
    pulse: false,
  },
  uploading: {
    label: "Uploading",
    className: "status-uploading",
    pulse: true,
  },
  processing: {
    label: "Analysing",
    className: "status-processing",
    pulse: true,
  },
  completed: {
    label: "Completed",
    className: "status-completed",
    pulse: false,
  },
  failed: {
    label: "Failed",
    className: "status-failed",
    pulse: false,
  },
};

function StatusBadge({ status }) {
  const cfg = STATUS_MAP[status] || STATUS_MAP.idle;

  return (
    <div className={`status-badge ${cfg.className}`}>
      <div className={`status-dot ${cfg.pulse ? "status-pulse" : ""}`} />
      <span>{cfg.label}</span>
    </div>
  );
}

function MetricCard({ label, value, accent = false }) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <span className={`metric-value ${accent ? "metric-accent" : ""}`}>
        {value}
      </span>
    </div>
  );
}

export function LeftRail({
  status,
  metrics,
  onOverride,
  onConfirm,
  onNewSession,
  canOverride,
  canConfirm,
  busy,
}) {
  return (
    <aside className="left-rail">
      <StatusBadge status={status} />

      <MetricCard label="items detected" value={metrics.itemCount} />
      <MetricCard
        label="total"
        value={`${metrics.total.toFixed(3)} TND`}
        accent
      />
      <MetricCard
        label="frames processed"
        value={metrics.frames.toLocaleString()}
      />
      <MetricCard
        label="avg confidence"
        value={`${metrics.avgConf.toFixed(1)}%`}
      />

      <div className="left-rail-spacer" />

      <button
        className="btn btn-ghost"
        onClick={onOverride}
        type="button"
        disabled={!canOverride || busy}
      >
        Override items
      </button>

      <button
        className="btn btn-primary"
        onClick={onConfirm}
        type="button"
        disabled={!canConfirm || busy}
      >
        Confirm receipt
      </button>

      <button className="btn btn-danger" onClick={onNewSession} type="button">
        New session
      </button>
    </aside>
  );
}
