"use client";

import { EngineResult } from "@/lib/types";
import EnginePanel from "./engine-panel";

interface SideBySideProps {
  geminiResult: EngineResult | null;
  langchainResult: EngineResult | null;
}

export default function SideBySide({
  geminiResult,
  langchainResult,
}: SideBySideProps) {
  return (
    <div className="flex divide-x divide-slate-800">
      <div className="flex-1">
        <EnginePanel engine="alpha" result={geminiResult} />
      </div>
      <div className="flex-1">
        <EnginePanel engine="sigma" result={langchainResult} />
      </div>
    </div>
  );
}
