import type { ComparedSkill, EvidenceItem } from "../types";
import { levelClass, pct } from "../lib/format";

function isEvidenceItem(value: EvidenceItem | string): value is EvidenceItem {
  return typeof value !== "string";
}

export function EvidenceList({ title, skills, empty }: { title: string; skills: ComparedSkill[]; empty: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      <div className="mt-3 grid gap-3">
        {skills.length === 0 ? <p className="rounded-lg border border-dashed border-line p-4 text-sm text-muted">{empty}</p> : null}
        {skills.map((skill) => (
          <article key={skill.name} className="rounded-lg border border-line p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold text-ink">{skill.name}</p>
                <p className="mt-1 text-xs text-muted">{pct(skill.confidence)} confidence</p>
              </div>
              <div className="flex gap-2">
                {skill.resume_signal ? <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${levelClass(skill.resume_signal)}`}>{skill.resume_signal}</span> : null}
                {skill.github_signal ? <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${levelClass(skill.github_signal)}`}>{skill.github_signal}</span> : null}
              </div>
            </div>
            <ul className="mt-3 space-y-2">
              {skill.evidence.slice(0, 3).map((item, index) => (
                <li key={index} className="text-sm leading-6 text-muted">
                  {isEvidenceItem(item) ? (
                    item.url ? (
                      <a className="font-medium text-accent hover:underline" href={item.url} target="_blank" rel="noreferrer">
                        {item.source}: {item.detail}
                      </a>
                    ) : (
                      `${item.source}: ${item.detail}`
                    )
                  ) : (
                    item
                  )}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </div>
  );
}
