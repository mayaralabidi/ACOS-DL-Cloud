import { useRef, useState } from "react";

export function VideoUpload({ onUpload, uploading, progress = 0 }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  function handleCardClick(e) {
    if (e.target !== e.currentTarget) return;
    inputRef.current?.click();
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith("video/")) setFile(f);
  }

  function handleChange(e) {
    const f = e.target.files[0];
    if (f) setFile(f);
  }

  function handleSubmit() {
    if (file && !uploading) onUpload(file);
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={handleCardClick}
        className={`upload-card ${dragging ? "dragging" : ""}`}
      >
        <svg
          width="48"
          height="48"
          viewBox="0 0 48 48"
          fill="none"
          aria-hidden="true"
        >
          <rect x="6" y="6" width="14" height="2" fill="var(--text-muted)" />
          <rect x="6" y="6" width="2" height="14" fill="var(--text-muted)" />
          <rect x="28" y="6" width="14" height="2" fill="var(--text-muted)" />
          <rect x="40" y="6" width="2" height="14" fill="var(--text-muted)" />
          <rect x="6" y="40" width="14" height="2" fill="var(--text-muted)" />
          <rect x="6" y="28" width="2" height="14" fill="var(--text-muted)" />
          <rect x="28" y="40" width="14" height="2" fill="var(--text-muted)" />
          <rect x="40" y="28" width="2" height="14" fill="var(--text-muted)" />
          <rect x="10" y="23" width="28" height="2" fill="var(--green-vivid)" />
        </svg>

        <p className="upload-name">
          {file
            ? `${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`
            : "Drop a video here or click to browse"}
        </p>

        <p className="upload-hint">mp4 · avi · mov - max 500 MB</p>

        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={handleChange}
        />
      </div>

      <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
        <button
          onClick={handleSubmit}
          disabled={!file || uploading}
          className="btn btn-primary"
          type="button"
        >
          {uploading ? "Uploading..." : "Process video"}
        </button>

        {uploading && (
          <div className="upload-progress-wrap">
            <div
              className="upload-progress"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
