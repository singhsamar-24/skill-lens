import { motion } from "framer-motion";
import { ShieldCheck, TrendingUp } from "lucide-react";
import { useMemo } from "react";
import type { CompareResponse } from "../types";
import { StatusPill } from "./ui";

export function TrustScoreCard({ comparison }: { comparison?: CompareResponse }) {
  const score = useAttemptAdjustedScore(comparison);
  const label = score >= 75 ? "Interview-ready" : score >= 45 ? "Promising proof" : comparison ? "Needs evidence" : "Waiting for analysis";
  const tone = score >= 75 ? "good" : score >= 45 ? "warn" : comparison ? "bad" : "neutral";

  return (
    <section className="relative overflow-hidden rounded-lg border border-line bg-white p-6 shadow-soft">
      <div className="absolute inset-x-0 top-0 h-1 bg-emerald-600" />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-muted">Trust Score</p>
          <div className="mt-3 flex items-end gap-3">
            <span className="text-6xl font-semibold leading-none tracking-normal text-ink">{comparison ? score : "--"}</span>
            <span className="pb-2 text-sm font-semibold text-muted">/ 100</span>
          </div>
        </div>
        <div className="grid h-12 w-12 place-items-center rounded-md bg-emerald-50 text-emerald-700">
          <ShieldCheck size={22} />
        </div>
      </div>
      <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${comparison ? score : 0}%` }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="h-full rounded-full bg-emerald-600"
        />
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <StatusPill tone={tone}>{label}</StatusPill>
        <span className="inline-flex items-center gap-1 text-xs font-medium text-muted">
          <TrendingUp size={14} />
          Real GitHub evidence plus resume alignment
        </span>
      </div>
    </section>
  );
}

function useAttemptAdjustedScore(comparison?: CompareResponse) {
  return useMemo(() => {
    if (!comparison) return 0;

    const baseScore = comparison.evidence_score;
    const skillSignal =
      comparison.verified_skills.length * 7 +
      comparison.github_only_skills.length * 3 -
      comparison.claimed_unproven_skills.length * 2 -
      comparison.missing_skills.filter((skill) => skill.priority === "high").length * 4;
    const confidenceSignal = Math.round(
      comparison.verified_skills.reduce((sum, skill) => sum + skill.confidence, 0) * 10,
    );
    const attemptSignal = Math.floor(Math.random() * 7) - 3;
    const adjustment = Math.max(-5, Math.min(5, Math.round((skillSignal + confidenceSignal) / 12) + attemptSignal));

    return Math.max(0, Math.min(100, baseScore + adjustment));
  }, [comparison]);
}
