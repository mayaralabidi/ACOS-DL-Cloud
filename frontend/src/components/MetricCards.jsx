export function MetricCards({ session }) {
  const stats = session?.receipt_raw?.stats || {};
  const cards = [
    { label: "Products detected", value: session?.receipt_items?.length ?? 0 },
    { label: "Total", value: `${(session?.total ?? 0).toFixed(2)} TND` },
    { label: "Frames processed", value: stats.frames_processed ?? "-" },
    { label: "Model", value: session?.model_version ?? "-" },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      {cards.map((c) => (
        <div key={c.label} className="bg-gray-50 rounded-lg p-4">
          <p className="text-xs text-gray-500 mb-1">{c.label}</p>
          <p className="text-xl font-semibold text-gray-900">{c.value}</p>
        </div>
      ))}
    </div>
  );
}
