import { useEffect, useRef } from "react";

export function usePolling(active, intervalMs, callback) {
  const timerRef = useRef(null);

  useEffect(() => {
    if (!active) {
      clearInterval(timerRef.current);
      return undefined;
    }

    timerRef.current = setInterval(async () => {
      const done = await callback();
      if (done) clearInterval(timerRef.current);
    }, intervalMs);

    return () => clearInterval(timerRef.current);
  }, [active, intervalMs, callback]);
}
