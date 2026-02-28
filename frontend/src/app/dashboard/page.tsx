"use client";

import AuthGuard from "@/components/auth-guard";
import NavBar from "@/components/nav-bar";
import SideBySide from "@/components/side-by-side";
import ReportCard from "@/components/report-card";
import { useReports } from "@/hooks/use-reports";

export default function DashboardPage() {
  const { reports, loading, error } = useReports();
  const latestReport = reports.length > 0 ? reports[0] : null;

  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#101622]">
        <NavBar />
        <main className="max-w-[1920px] mx-auto">
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-slate-400 text-sm animate-pulse">
                Loading latest report...
              </div>
            </div>
          ) : latestReport ? (
            <SideBySide
              geminiResult={latestReport.gemini_result}
              langchainResult={latestReport.langchain_result}
            />
          ) : (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <p className="text-slate-400 text-sm">No reports yet</p>
                <p className="text-slate-500 text-xs mt-1">
                  Trigger a research run to get started
                </p>
              </div>
            </div>
          )}

          {/* Report History */}
          {reports.length > 1 && (
            <section className="px-6 py-8 border-t border-slate-800">
              <h2 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] mb-4">
                Report History
              </h2>
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {reports.slice(1).map((r) => (
                  <ReportCard key={r.report_id} report={r} />
                ))}
              </div>
            </section>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}
