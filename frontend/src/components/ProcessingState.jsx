export function ProcessingState({ elapsed }) {
  return (
    <div className="processing-card">
      <div className="scan-frame">
        <div className="scan-line" />
      </div>

      <div className="processing-copy">
        <div className="processing-label">Analysing video</div>
        <div className="processing-time">{elapsed}s</div>
      </div>
    </div>
  );
}
