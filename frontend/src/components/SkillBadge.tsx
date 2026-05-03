import { memo } from "react";
import type { SkillEvidence } from "../types";
import { confidenceBarClass, levelClass } from "../lib/format";

export const SkillBadge = memo(function SkillBadge({ skill }: { skill: SkillEvidence }) {
  const score = skill.confidence;
  const credibility = skill.credibility?.score ?? Math.round(score * 100);
  return (
    <div className="group rounded-lg border border-line p-4 transition duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-tight">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-ink">{skill.name}</p>
          <p className="mt-1 text-xs text-muted">{credibility}/100 credibility</p>
        </div>
        <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${levelClass(skill.level)}`}>{skill.level}</span>
      </div>
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full transition-all duration-700 ${confidenceBarClass(score)}`} style={{ width: `${Math.max(4, Math.round(score * 100))}%` }} />
      </div>
      {skill.credibility ? (
        <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-muted">
          <span>{skill.credibility.repo_count} repos</span>
          <span>{skill.credibility.commit_count} commits</span>
          <span>{Math.round(skill.credibility.language_share * 100)}% code</span>
        </div>
      ) : null}
      {skill.evidence[0] ? <p className="mt-3 line-clamp-2 text-xs leading-5 text-muted">{skill.evidence[0].detail}</p> : null}
    </div>
  );
});
