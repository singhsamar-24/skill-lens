import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, BriefcaseBusiness, CheckCircle2, ChevronDown, CircleAlert, Info, MinusCircle, ShieldCheck, XCircle } from "lucide-react";
import { EmptyState, Page, Panel, SectionTitle, StatusPill } from "../components/ui";
import { confidenceBarClass, priorityClass, pct } from "../lib/format";
import { useAnalysis } from "../state/analysis-store";
import type { ComparedSkill, CompareResponse, Priority } from "../types";
import { motion } from "framer-motion";

export function Compare() {
  const { comparison } = useAnalysis();

  if (!comparison) {
    return (
      <Page>
        <EmptyState title="No comparison yet" body="Run an analysis from the dashboard to compare resume claims with GitHub evidence." />
      </Page>
    );
  }

  return (
    <Page>
      <div className="mb-12">
        <StatusPill tone="blue">Analysis Report</StatusPill>
        <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink sm:text-5xl lg:text-6xl">
          Evidence <span className="text-accent">Divergence.</span>
        </h1>
        <p className="mt-6 max-w-3xl text-lg leading-relaxed text-muted font-medium">
          We cross-reference your resume claims against real GitHub activity. Verified skills represent your most credible professional narrative.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-[0.72fr_1.28fr]">
        <div className="space-y-8">
          <Panel>
            <SectionTitle kicker="Metrics" title="Credibility Score" description="A quantitative measure of how well your claims align with public code proof." />
            <div className="rounded-[2.5rem] border border-line bg-slate-50/50 p-8 text-center">
              <p className="text-xs font-bold uppercase tracking-widest text-muted">Evidence score</p>
              <p className="mt-4 text-8xl font-black tracking-tighter text-ink">{comparison.evidence_score}%</p>
              <div className="mt-8 h-3 overflow-hidden rounded-full bg-slate-100">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${comparison.evidence_score}%` }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  className="h-full rounded-full bg-accent" 
                />
              </div>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <StatusPill tone="good">Verified: {comparison.verified_skills.length}</StatusPill>
                <StatusPill tone="warn">Weak: {comparison.claimed_unproven_skills.length}</StatusPill>
                <StatusPill tone="bad">Missing: {comparison.missing_skills.length}</StatusPill>
              </div>
            </div>
            
            <div className="mt-8 space-y-4">
               <p className="text-xs font-bold uppercase tracking-widest text-muted">System Recommendations</p>
              {comparison.recommendations.map((recommendation) => (
                <div key={recommendation} className="flex gap-4 rounded-2xl border border-line bg-white p-5 transition-all hover:border-accent/30 hover:shadow-soft">
                  <ShieldCheck className="mt-0.5 shrink-0 text-accent" size={20} />
                  <p className="text-sm font-medium leading-relaxed text-muted">{recommendation}</p>
                </div>
              ))}
            </div>
            
            <Link to="/roadmap" className="group mt-8 inline-flex h-14 w-full items-center justify-center gap-3 rounded-2xl bg-ink px-8 text-base font-bold text-white transition-all hover:bg-slate-800 hover:shadow-xl active:scale-95">
              Generate Growth Roadmap
              <ArrowRight size={20} className="transition-transform group-hover:translate-x-1" />
            </Link>
          </Panel>
          <CareerMatches roles={comparison.career_matches} />
        </div>

        <div className="grid gap-8">
          <SkillGroup
            title="Verified Overlap"
            description="Professional claims fully supported by GitHub activity."
            skills={comparison.verified_skills}
            empty="No verified overlap found yet."
            icon={<CheckCircle2 size={20} />}
            tone="green"
          />
          <SkillGroup
            title="Unproven Claims"
            description="Skills mentioned on resume but not detected in code history."
            skills={comparison.claimed_unproven_skills}
            empty="No unproven resume claims."
            icon={<CircleAlert size={20} />}
            tone="yellow"
          />
          <MissingGroup skills={comparison.missing_skills} role={comparison.target_role} />
          <SkillGroup
            title="Hidden Strengths"
            description="Strong GitHub signals that are missing from your resume."
            skills={comparison.github_only_skills}
            empty="No hidden strengths detected."
            icon={<MinusCircle size={20} />}
            tone="neutral"
          />
        </div>
      </div>
    </Page>
  );
}

function SkillGroup({
  title,
  description,
  skills,
  empty,
  icon,
  tone,
}: {
  title: string;
  description: string;
  skills: ComparedSkill[];
  empty: string;
  icon: ReactNode;
  tone: "green" | "yellow" | "neutral";
}) {
  const toneClass = tone === "green" ? "text-emerald-600 bg-emerald-50" : tone === "yellow" ? "text-amber-600 bg-amber-50" : "text-slate-600 bg-slate-50";

  return (
    <Panel>
      <div className="mb-6 flex items-start gap-4">
        <div className={`grid h-12 w-12 shrink-0 place-items-center rounded-2xl shadow-sm ${toneClass}`}>{icon}</div>
        <div>
          <h2 className="text-xl font-bold text-ink">{title}</h2>
          <p className="mt-1 text-sm font-medium text-muted leading-relaxed">{description}</p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {skills.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-line bg-slate-50/50 p-8 text-center md:col-span-2">
            <p className="text-sm font-medium text-muted">{empty}</p>
          </div>
        ) : null}
        {skills.map((skill, index) => (
          <motion.article 
            key={skill.name} 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="rounded-2xl border border-line p-5 transition-all hover:border-accent/30 hover:bg-slate-50 hover:shadow-soft"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-bold text-ink">{skill.name}</p>
                <p className="mt-1 text-xs font-bold text-muted uppercase tracking-widest">{pct(skill.confidence)} Confidence</p>
              </div>
              <div className="flex shrink-0 flex-col items-end gap-1.5">
                {skill.resume_signal ? <StatusPill tone={skill.resume_signal === "project_backed" ? "good" : "warn"}>{skill.resume_signal}</StatusPill> : null}
                {skill.github_signal ? <StatusPill tone={skill.github_signal === "strong" ? "good" : skill.github_signal === "moderate" ? "warn" : "neutral"}>{skill.github_signal}</StatusPill> : null}
              </div>
            </div>
            <div className="mt-6 h-2 overflow-hidden rounded-full bg-slate-100">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${Math.max(4, Math.round(skill.confidence * 100))}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className={`h-full rounded-full ${confidenceBarClass(skill.confidence)}`} 
              />
            </div>
          </motion.article>
        ))}
      </div>
    </Panel>
  );
}

function MissingGroup({ skills, role }: { skills: CompareResponse["missing_skills"]; role: string }) {
  return (
    <Panel>
      <div className="mb-6 flex items-start gap-4">
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-rose-50 text-rose-600 shadow-sm">
          <XCircle size={20} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-ink">Role Gaps</h2>
          <p className="mt-1 text-sm font-medium text-muted leading-relaxed">Competencies expected for <span className="text-ink font-bold">{role}</span> that are not yet visible.</p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {skills.length ? (
          skills.map((skill, index) => (
            <MissingSkillCard key={skill.name} skill={skill} index={index} />
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-line bg-slate-50/50 p-8 text-center md:col-span-2">
            <p className="text-sm font-medium text-muted">Your evidence already covers the configured role baseline.</p>
          </div>
        )}
      </div>
    </Panel>
  );
}

function MissingSkillCard({ skill, index }: { skill: CompareResponse["missing_skills"][number]; index: number }) {
  const [open, setOpen] = useState(index === 0);
  const borderTone = skill.priority === "high" ? "hover:border-red-200" : skill.priority === "medium" ? "hover:border-amber-200" : "hover:border-slate-300";

  return (
    <motion.article
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`rounded-2xl border border-line bg-white p-5 shadow-sm transition-all ${borderTone} hover:bg-slate-50/70 hover:shadow-soft`}
    >
      <button type="button" onClick={() => setOpen((value) => !value)} className="flex w-full items-start justify-between gap-4 text-left">
        <div>
          <div className="flex items-center gap-2">
            <p className="font-bold text-ink">{skill.name}</p>
            <Tooltip text="Priority blends role expectations with your current evidence gaps." />
          </div>
          <p className="mt-2 text-sm font-medium leading-relaxed text-muted">{skill.reason}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-widest ${priorityClass(skill.priority)}`}>{skill.priority}</span>
          <motion.span animate={{ rotate: open ? 180 : 0 }} className="grid h-8 w-8 place-items-center rounded-full bg-slate-100 text-slate-500">
            <ChevronDown size={16} />
          </motion.span>
        </div>
      </button>
      <motion.div
        initial={false}
        animate={{ height: open ? "auto" : 0, opacity: open ? 1 : 0 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
        className="overflow-hidden"
      >
        <div className="mt-5 border-t border-line pt-5">
          <div className="grid gap-4">
            <InsightBlock label="WHY" body={skill.reason} />
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-muted">WHERE USED</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(skill.usage.length ? skill.usage : ["Production projects"]).map((usage) => (
                  <span key={usage} className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-bold text-slate-700 shadow-sm">
                    {usage}
                  </span>
                ))}
              </div>
            </div>
            <InsightBlock label="IMPACT" body={skill.impact || "Improves your ability to design and ship reliable systems for this role."} />
          </div>
        </div>
      </motion.div>
    </motion.article>
  );
}

function CareerMatches({ roles }: { roles: CompareResponse["career_matches"] }) {
  return (
    <Panel>
      <div className="mb-6 flex items-start gap-4">
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-blue-50 text-blue-600 shadow-sm">
          <BriefcaseBusiness size={20} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-ink">Your Best Career Matches</h2>
          <p className="mt-1 text-sm font-medium leading-relaxed text-muted">Ranked from visible resume and GitHub skill evidence.</p>
        </div>
      </div>
      <div className="space-y-4">
        {roles.length ? roles.map((role, index) => (
          <motion.article
            key={role.role}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06 }}
            className="rounded-2xl border border-line bg-white p-5 shadow-sm transition-all hover:border-blue-200 hover:bg-blue-50/20 hover:shadow-soft"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-muted">#{index + 1} Match</p>
                <h3 className="mt-1 text-lg font-bold text-ink">{role.role}</h3>
              </div>
              <div className="text-right">
                <p className="text-3xl font-black tracking-tight text-ink">{role.match}%</p>
                <p className="mt-1 text-[10px] font-bold uppercase tracking-widest text-muted">{role.salary}</p>
              </div>
            </div>
            <div className="mt-5 h-2.5 overflow-hidden rounded-full bg-slate-100">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${role.match}%` }}
                transition={{ duration: 1.1, ease: "easeOut" }}
                className="h-full rounded-full bg-blue-600"
              />
            </div>
            <p className="mt-4 text-sm font-medium leading-relaxed text-muted">{role.reason}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {role.matched_skills.slice(0, 5).map((skill) => (
                <span key={skill} className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-emerald-700">{skill}</span>
              ))}
            </div>
          </motion.article>
        )) : (
          <div className="rounded-2xl border border-dashed border-line bg-slate-50/50 p-8 text-center">
            <p className="text-sm font-medium text-muted">Career matches will appear once comparison has enough skill evidence.</p>
          </div>
        )}
      </div>
    </Panel>
  );
}

function InsightBlock({ label, body }: { label: string; body: string }) {
  return (
    <div>
      <p className="text-[10px] font-bold uppercase tracking-widest text-muted">{label}</p>
      <p className="mt-2 text-sm font-medium leading-relaxed text-ink">{body}</p>
    </div>
  );
}

function Tooltip({ text }: { text: string }) {
  return (
    <span className="group relative inline-flex">
      <Info size={14} className="text-slate-400" />
      <span className="pointer-events-none absolute left-1/2 top-6 z-10 w-56 -translate-x-1/2 rounded-xl border border-line bg-white p-3 text-xs font-medium leading-relaxed text-muted opacity-0 shadow-soft transition-opacity group-hover:opacity-100">
        {text}
      </span>
    </span>
  );
}
