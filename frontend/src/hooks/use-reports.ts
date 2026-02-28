"use client";

import { useState, useEffect, useCallback } from "react";
import { getReports, getReport, triggerResearch } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { ResearchReport } from "@/lib/types";

interface UseReportsReturn {
  reports: ResearchReport[];
  total: number;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  trigger: (date?: string) => Promise<void>;
  triggering: boolean;
}

export function useReports(): UseReportsReturn {
  const [reports, setReports] = useState<ResearchReport[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triggering, setTriggering] = useState(false);

  const fetchReports = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    setError(null);
    try {
      const data = await getReports(token);
      setReports(data.reports);
      setTotal(data.total);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch reports";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const trigger = useCallback(async (date?: string) => {
    const token = getToken();
    if (!token) return;

    setTriggering(true);
    try {
      await triggerResearch(token, date);
      await fetchReports();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to trigger research";
      setError(message);
    } finally {
      setTriggering(false);
    }
  }, [fetchReports]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  return { reports, total, loading, error, refresh: fetchReports, trigger, triggering };
}

interface UseReportDetailReturn {
  report: ResearchReport | null;
  loading: boolean;
  error: string | null;
}

export function useReportDetail(id: string): UseReportDetailReturn {
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    setLoading(true);
    setError(null);
    getReport(id, token)
      .then((data) => setReport(data))
      .catch((err) => {
        const message =
          err instanceof Error ? err.message : "Failed to fetch report";
        setError(message);
      })
      .finally(() => setLoading(false));
  }, [id]);

  return { report, loading, error };
}
