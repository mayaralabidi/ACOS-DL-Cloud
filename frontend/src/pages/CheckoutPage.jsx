import { useCallback, useEffect, useMemo, useState } from "react";

import { ConfidenceChart } from "../components/ConfidenceChart";
import { Header } from "../components/Header";
import { LeftRail } from "../components/LeftRail";
import { OverrideModal } from "../components/OverrideModal";
import { ProcessingState } from "../components/ProcessingState";
import { ReceiptTable } from "../components/ReceiptTable";
import { VideoUpload } from "../components/VideoUpload";
import { usePolling } from "../hooks/usePolling";
import { useSession } from "../hooks/useSession";

export function CheckoutPage() {
  const {
    session,
    loading,
    uploading,
    uploadProgress,
    error,
    upload,
    refresh,
    override,
    confirm,
    reset,
  } = useSession();
  const [showOverride, setShowOverride] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [isHealthy, setIsHealthy] = useState(true);

  const isProcessing = session?.status === "processing";
  const isReady = session?.status === "ready";
  const isConfirmed = session?.status === "confirmed";
  const hasError = session?.status === "cancelled" || Boolean(error);

  const status = uploading
    ? "uploading"
    : isProcessing
      ? "processing"
      : isReady || isConfirmed
        ? "completed"
        : hasError
          ? "failed"
          : "idle";

  useEffect(() => {
    let timer = null;
    if (isProcessing) {
      timer = setInterval(() => setElapsed((v) => v + 1), 1000);
    } else {
      setElapsed(0);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isProcessing]);

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
  }, [session?.id]);

  const pollCallback = useCallback(async () => {
    if (!session?.id) return true;
    const s = await refresh(session.id);
    return (
      s?.status === "ready" ||
      s?.status === "confirmed" ||
      s?.status === "cancelled"
    );
  }, [session?.id, refresh]);

  usePolling(isProcessing, 2000, pollCallback);

  const confidenceItems = useMemo(() => {
    const rawItems = session?.receipt_raw?.items || [];
    const diagnostics = session?.receipt_raw?.diagnostics || [];
    const diagnosticByLabel = new Map(
      diagnostics.map((entry) => [entry.label, entry]),
    );

    return rawItems
      .map((item) => {
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
      })
      .filter((item) => typeof item.confidence === "number");
  }, [session]);

  const metrics = {
    itemCount: session?.receipt_items?.length ?? 0,
    total: Number(session?.total ?? 0),
    frames: Number(
      session?.frame_count ??
        session?.receipt_raw?.stats?.frames_processed ??
        0,
    ),
    avgConf: confidenceItems.length
      ? (confidenceItems.reduce((sum, i) => sum + i.confidence, 0) /
          confidenceItems.length) *
        100
      : 0,
  };

  return (
    <div className="page-shell">
      <Header
        sessionId={session?.id}
        runningTotal={session ? Number(session.total || 0) : null}
        env={import.meta.env.MODE || "dev"}
        isHealthy={isHealthy}
      />

      <div className="dashboard-layout">
        <LeftRail
          status={status}
          metrics={metrics}
          onOverride={() => setShowOverride(true)}
          onConfirm={confirm}
          onNewSession={reset}
          canOverride={isReady}
          canConfirm={isReady}
          busy={loading}
        />

        <main className="main-panel">
          {error ? <div className="error-banner">{error}</div> : null}

          {!session ? (
            <div className="surface-card" style={{ padding: 14 }}>
              <VideoUpload
                onUpload={upload}
                uploading={uploading}
                progress={uploadProgress}
              />
            </div>
          ) : null}

          {isProcessing ? <ProcessingState elapsed={elapsed} /> : null}

          {(isReady || isConfirmed) && (
            <>
              <section className="surface-card">
                <ReceiptTable
                  items={session.receipt_items || []}
                  total={Number(session.total || 0)}
                  confirmedAt={session.confirmed_at}
                />
              </section>

              <section className="surface-card">
                <ConfidenceChart items={confidenceItems} />
              </section>

              {isConfirmed ? (
                <div className="confirmed-pill">
                  SESSION CONFIRMED - RECEIPT SAVED
                </div>
              ) : null}
            </>
          )}
        </main>
      </div>

      <OverrideModal
        open={showOverride}
        onClose={() => setShowOverride(false)}
        onSubmit={override}
        disabled={loading}
      />
    </div>
  );
}
