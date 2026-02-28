"use client";

import { EngineResult, ViralEvent, DeepDive, ConfidenceLevel } from "@/lib/types";

type AgentType = "alpha" | "sigma";

interface EnginePanelProps {
  engine: AgentType;
  result: EngineResult | null;
}

const AGENT_CONFIG = {
  alpha: {
    name: "Agent Alpha",
    subtitle: "Gemini Deep Research",
    color: "#00f2ff",
    icon: "A",
  },
  sigma: {
    name: "Agent Sigma",
    subtitle: "LangChain Research",
    color: "#ff00e5",
    icon: "S",
  },
} as const;

export default function EnginePanel({ engine, result }: EnginePanelProps) {
  const config = AGENT_CONFIG[engine];

  return (
    <div
      className="flex-1 min-w-0 rounded-xl border bg-[#131b2e]/80 overflow-hidden"
      style={{
        borderColor: `${config.color}20`,
        boxShadow: `0 0 30px ${config.color}08, inset 0 1px 0 ${config.color}10`,
      }}
    >
      <AgentHeader config={config} result={result} />

      {!result ? (
        <NoDataState config={config} />
      ) : result.status === "running" ? (
        <RunningState config={config} />
      ) : result.status === "failed" ? (
        <FailedState error={result.error_message} />
      ) : (
        <div className="p-4 space-y-4">
          <TldrCard tldr={result.tldr} color={config.color} />
          <ViralEventsTable events={result.viral_events} color={config.color} />
          <StrategicDeepDives dives={result.deep_dives} color={config.color} />
          <CompletenessFooter audit={result.completeness_audit} color={config.color} />
        </div>
      )}
    </div>
  );
}

function AgentHeader({
  config,
  result,
}: {
  config: (typeof AGENT_CONFIG)[AgentType];
  result: EngineResult | null;
}) {
  const statusText = result?.status ?? "offline";
  const duration = result?.duration_seconds
    ? `${result.duration_seconds.toFixed(1)}s`
    : null;

  return (
    <div
      className="px-4 py-3 flex items-center justify-between border-b"
      style={{ borderColor: `${config.color}15` }}
    >
      <div className="flex items-center gap-3">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold text-white"
          style={{
            backgroundColor: `${config.color}20`,
            boxShadow: `0 0 12px ${config.color}30`,
          }}
        >
          {config.icon}
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">{config.name}</h3>
          <p className="text-[11px] text-gray-500">{config.subtitle}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {duration && (
          <span className="text-[11px] text-gray-500 font-mono">{duration}</span>
        )}
        <StatusBadge status={statusText} color={config.color} />
      </div>
    </div>
  );
}

function StatusBadge({
  status,
  color,
}: {
  status: string;
  color: string;
}) {
  const isActive = status === "completed";
  return (
    <span
      className="text-[10px] font-medium px-2 py-0.5 rounded-full uppercase tracking-wider"
      style={{
        backgroundColor: isActive ? `${color}15` : "rgba(255,255,255,0.05)",
        color: isActive ? color : "#6b7280",
      }}
    >
      {status}
    </span>
  );
}

function NoDataState({ config }: { config: (typeof AGENT_CONFIG)[AgentType] }) {
  return (
    <div className="p-8 text-center">
      <div
        className="w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3"
        style={{ backgroundColor: `${config.color}10` }}
      >
        <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p className="text-sm text-gray-500">No data available</p>
    </div>
  );
}

function RunningState({ config }: { config: (typeof AGENT_CONFIG)[AgentType] }) {
  return (
    <div className="p-8 text-center">
      <svg
        className="animate-spin h-8 w-8 mx-auto mb-3"
        style={{ color: config.color }}
        viewBox="0 0 24 24"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <p className="text-sm text-gray-400">Research in progress...</p>
    </div>
  );
}

function FailedState({ error }: { error: string | null }) {
  return (
    <div className="p-6">
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
        <p className="text-sm text-red-400 font-medium">Research Failed</p>
        {error && <p className="text-xs text-red-400/70 mt-1">{error}</p>}
      </div>
    </div>
  );
}

function TldrCard({ tldr, color }: { tldr: string | null; color: string }) {
  if (!tldr) return null;
  return (
    <div
      className="rounded-lg p-4 border"
      style={{
        backgroundColor: `${color}05`,
        borderColor: `${color}15`,
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color }}>
          TL;DR Intelligence Brief
        </span>
      </div>
      <p className="text-sm text-gray-300 leading-relaxed">{tldr}</p>
    </div>
  );
}

function ViralEventsTable({ events, color }: { events: ViralEvent[]; color: string }) {
  if (events.length === 0) return null;

  return (
    <div>
      <h4
        className="text-[10px] font-bold uppercase tracking-widest mb-2"
        style={{ color }}
      >
        Viral Events ({events.length})
      </h4>
      <div className="overflow-x-auto rounded-lg border border-white/5">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-white/[0.02]">
              <th className="text-left px-3 py-2 text-gray-500 font-medium">Event</th>
              <th className="text-left px-3 py-2 text-gray-500 font-medium">Category</th>
              <th className="text-center px-3 py-2 text-gray-500 font-medium">Impact</th>
              <th className="text-center px-3 py-2 text-gray-500 font-medium">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event, i) => (
              <tr key={i} className="border-t border-white/5 hover:bg-white/[0.02] transition-colors">
                <td className="px-3 py-2 text-gray-300 max-w-[200px] truncate">
                  {event.headline}
                </td>
                <td className="px-3 py-2">
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-white/5 text-gray-400">
                    {event.category}
                  </span>
                </td>
                <td className="px-3 py-2 text-center">
                  <ImpactBar rating={event.impact_rating} color={color} />
                </td>
                <td className="px-3 py-2 text-center">
                  <ConfidenceBadge level={event.confidence} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ImpactBar({ rating, color }: { rating: number; color: string }) {
  const width = Math.min(100, Math.max(0, rating * 10));
  return (
    <div className="flex items-center gap-1.5 justify-center">
      <div className="w-16 h-1.5 rounded-full bg-white/10 overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${width}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-[10px] text-gray-400 font-mono w-4">{rating}</span>
    </div>
  );
}

function ConfidenceBadge({ level }: { level: ConfidenceLevel }) {
  const colors: Record<ConfidenceLevel, string> = {
    high: "text-green-400 bg-green-400/10",
    medium: "text-yellow-400 bg-yellow-400/10",
    low: "text-red-400 bg-red-400/10",
  };
  return (
    <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${colors[level]}`}>
      {level}
    </span>
  );
}

function StrategicDeepDives({ dives, color }: { dives: DeepDive[]; color: string }) {
  if (dives.length === 0) return null;

  return (
    <div>
      <h4
        className="text-[10px] font-bold uppercase tracking-widest mb-2"
        style={{ color }}
      >
        Strategic Deep Dives ({dives.length})
      </h4>
      <div className="space-y-2">
        {dives.map((dive, i) => (
          <details
            key={i}
            className="group rounded-lg border border-white/5 overflow-hidden"
          >
            <summary className="px-3 py-2.5 cursor-pointer hover:bg-white/[0.02] transition-colors flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PriorityDot priority={dive.priority} />
                <span className="text-xs text-gray-300 font-medium">{dive.title}</span>
              </div>
              <svg
                className="w-3.5 h-3.5 text-gray-500 transition-transform group-open:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            <div className="px-3 pb-3 border-t border-white/5 pt-2">
              <p className="text-xs text-gray-400 mb-2">{dive.summary}</p>
              {dive.key_findings.length > 0 && (
                <ul className="space-y-1">
                  {dive.key_findings.map((finding, j) => (
                    <li key={j} className="flex items-start gap-1.5 text-xs text-gray-400">
                      <span style={{ color }} className="mt-0.5">&#8226;</span>
                      {finding}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </details>
        ))}
      </div>
    </div>
  );
}

function PriorityDot({ priority }: { priority: string }) {
  const color =
    priority === "high" ? "bg-red-400" :
    priority === "medium" ? "bg-yellow-400" :
    "bg-gray-400";
  return <span className={`w-1.5 h-1.5 rounded-full ${color}`} />;
}

function CompletenessFooter({
  audit,
  color,
}: {
  audit: EngineResult["completeness_audit"];
  color: string;
}) {
  if (!audit) return null;

  const scorePercent = Math.round(audit.confidence_score * 100);

  return (
    <div
      className="rounded-lg p-3 border"
      style={{
        backgroundColor: `${color}05`,
        borderColor: `${color}10`,
      }}
    >
      <h4
        className="text-[10px] font-bold uppercase tracking-widest mb-2"
        style={{ color }}
      >
        Completeness Audit
      </h4>
      <div className="grid grid-cols-3 gap-3 mb-2">
        <AuditStat label="Verified" value={audit.verified_signals} color={color} />
        <AuditStat label="Sources" value={audit.sources_checked} color={color} />
        <AuditStat label="Confidence" value={`${scorePercent}%`} color={color} />
      </div>
      {audit.gaps.length > 0 && (
        <div className="mt-2 pt-2 border-t" style={{ borderColor: `${color}10` }}>
          <p className="text-[10px] text-gray-500 mb-1">Coverage Gaps:</p>
          <div className="flex flex-wrap gap-1">
            {audit.gaps.map((gap, i) => (
              <span
                key={i}
                className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400"
              >
                {gap}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AuditStat({
  label,
  value,
  color,
}: {
  label: string;
  value: number | string;
  color: string;
}) {
  return (
    <div className="text-center">
      <div className="text-lg font-bold" style={{ color }}>
        {value}
      </div>
      <div className="text-[10px] text-gray-500">{label}</div>
    </div>
  );
}
