import { useCallback, useState } from "react";

import {
  confirmSession,
  getSession,
  overrideItem,
  processVideo,
} from "../api/client";

export function useSession() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const upload = useCallback(async (file) => {
    setUploading(true);
    setUploadProgress(0);
    setError(null);
    try {
      const s = await processVideo(file, (event) => {
        if (event.total) {
          setUploadProgress(Math.round((event.loaded * 100) / event.total));
        }
      });
      setSession(s);
      return s;
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      return null;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, []);

  const refresh = useCallback(async (sessionId) => {
    try {
      const s = await getSession(sessionId);
      setSession(s);
      if (s?.status === "cancelled" && s?.error) {
        setError(s.error);
      } else if (s?.status === "ready" || s?.status === "confirmed") {
        setError(null);
      }
      return s;
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      return null;
    }
  }, []);

  const override = useCallback(
    async (action, label, qty = 1) => {
      if (!session) return;
      setLoading(true);
      try {
        const s = await overrideItem(session.id, action, label, qty);
        setSession(s);
      } catch (e) {
        setError(e.response?.data?.detail || e.message);
      } finally {
        setLoading(false);
      }
    },
    [session],
  );

  const confirm = useCallback(async () => {
    if (!session) return;
    setLoading(true);
    try {
      const s = await confirmSession(session.id);
      setSession(s);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [session]);

  const reset = useCallback(() => {
    setSession(null);
    setError(null);
  }, []);

  return {
    session,
    loading,
    uploading,
    error,
    upload,
    uploadProgress,
    refresh,
    override,
    confirm,
    reset,
  };
}
