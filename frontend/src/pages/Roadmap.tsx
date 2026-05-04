import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Building2, ChevronRight, ExternalLink, GraduationCap, Send, Sparkles, Target } from "lucide-react";
import { RoadmapTimeline } from "../components/RoadmapTimeline";
import { Button, EmptyState, Page, Panel, SectionTitle, SkeletonBlock, StatusPill } from "../components/ui";
import { priorityClass } from "../lib/format";
import { useAnalysis } from "../state/analysis-store";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import type { ComparedSkill, MarketCompanyRoadmap, MarketRoadmapResponse } from "../types";

export function Roadmap() {
  const { comparison, roadmap, statuses, generateRoadmap } = useAnalysis();
  const [market, setMarket] = useState<MarketRoadmapResponse>();
  const [marketStatus, setMarketStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [selectedCompany, setSelectedCompany] = useState<MarketCompanyRoadmap | null>(null);

  const userSkills = useMemo(() => {
    if (!comparison) return [];
    return [
      ...comparison.verified_skills.map((skill) => weightedSkill(skill, 1.2)),
      ...comparison.github_only_skills.map((skill) => weightedSkill(skill, 0.9)),
      ...comparison.claimed_unproven_skills.map((skill) => weightedSkill(skill, 0.62)),
    ];
  }, [comparison]);

  useEffect(() => {
    if (!comparison) return;
    let cancelled = false;
    setMarketStatus("loading");
    api
      .marketRoadmap({ target_role: comparison.target_role, user_skills: userSkills })
      .then((response) => {
        if (cancelled) return;
        setMarket(response);
        setSelectedCompany(response.companies[0] ?? null);
        setMarketStatus("ready");
      })
      .catch(() => {
        if (!cancelled) setMarketStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [comparison, userSkills]);

  if (!comparison) {
    return (
      <Page>
        <EmptyState icon={GraduationCap} title="No comparison available" body="Run SkillLens first so the roadmap can use verified gaps and role context." />
      </Page>
    );
  }

  return (
    <Page>
      <div className="mb-12 flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <StatusPill tone="blue">Path to Mastery</StatusPill>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink sm:text-5xl">
            Career <span className="text-accent">Blueprint.</span>
          </h1>
          <p className="mt-4 max-w-2xl text-lg font-medium text-muted leading-relaxed">
            Personalized learning path for <span className="text-ink font-bold">{comparison.target_role}</span> based on your verified evidence gaps.
          </p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Button 
            size="lg"
            variant="accent"
            onClick={generateRoadmap} 
            disabled={statuses.roadmap === "loading"}
            className="w-full sm:w-auto"
          >
            <Sparkles size={18} />
            {roadmap ? "Refresh Roadmap" : "Generate Roadmap"}
          </Button>
        </motion.div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
        <Panel>
          <SectionTitle 
            kicker="Target Areas" 
            title="Focus Skills" 
            description="The most critical competencies you need to bridge your current gap."
          />
          <div className="space-y-4">
            {(roadmap?.focus_skills.length ? roadmap.focus_skills : comparison.missing_skills).map((skill, index) => {
              const name = "skill" in skill ? skill.skill : skill.name;
              const rationale = "rationale" in skill ? skill.rationale : skill.reason;
              return (
                <motion.article 
                  key={name} 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="rounded-2xl border border-line p-5 transition-all hover:border-accent/30 hover:bg-slate-50"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-bold text-ink">{name}</p>
                    <span className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-widest ${priorityClass(skill.priority)}`}>{skill.priority}</span>
                  </div>
                  <p className="mt-4 text-sm font-medium leading-relaxed text-muted">{rationale}</p>
                </motion.article>
              );
            })}
          </div>
        </Panel>

        <Panel>
          <SectionTitle 
            kicker="Progression" 
            title="Milestones" 
            description="A step-by-step timeline generated by our RAG-enhanced mentor engine."
            action={roadmap ? <StatusPill tone="good">Optimized</StatusPill> : <StatusPill>Pending</StatusPill>} 
          />
          {statuses.roadmap === "loading" ? (
            <div className="space-y-4">
              {[0, 1, 2].map((item) => (
                <SkeletonBlock key={item} className="h-40" />
              ))}
            </div>
          ) : roadmap ? (
            <RoadmapTimeline roadmap={roadmap} />
          ) : (
            <EmptyState title="Roadmap Not Generated" body="Generate a Groq-backed plan using your comparison and the learning/job RAG context." />
          )}
        </Panel>
      </div>

      {roadmap ? (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <Panel>
            <SectionTitle kicker="Application" title="Portfolio Projects" description="Real-world projects designed to prove your newly acquired skills." />
            <div className="grid gap-4 md:grid-cols-3">
              {roadmap.portfolio_projects.map((project, index) => (
                <motion.div 
                  key={project} 
                  whileHover={{ y: -5 }}
                  className="rounded-2xl border border-line bg-slate-50/50 p-6 text-sm font-medium leading-relaxed text-muted hover:border-accent/30 hover:bg-white hover:shadow-soft"
                >
                  <span className="mb-4 block h-8 w-8 rounded-lg bg-white text-center font-bold text-accent shadow-sm ring-1 ring-line">
                    {index + 1}
                  </span>
                  {project}
                </motion.div>
              ))}
            </div>
            <div className="mt-8 rounded-2xl bg-ink p-8 text-white shadow-xl">
               <div className="flex items-center gap-3 mb-4">
                 <div className="h-8 w-8 rounded-full bg-accent flex items-center justify-center">
                    <Sparkles size={16} />
                 </div>
                 <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Mentor Note</p>
               </div>
               <p className="text-lg font-medium leading-relaxed italic opacity-90 text-slate-200">"{roadmap.mentor_note}"</p>
            </div>
          </Panel>
        </motion.div>
      ) : null}

      <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mt-8">
        <Panel>
          <SectionTitle
            kicker="Market Map"
            title="Companies Hiring For You"
            description={`India-focused hiring patterns, salary bands, fit scores, and preparation paths for ${comparison.target_role}.`}
            action={marketStatus === "loading" ? <StatusPill tone="blue">Loading</StatusPill> : marketStatus === "error" ? <StatusPill tone="bad">Market map unavailable</StatusPill> : <StatusPill tone="good">Market aware</StatusPill>}
          />
          {marketStatus === "loading" ? (
            <div className="grid gap-4 md:grid-cols-3">
              {[0, 1, 2].map((item) => <SkeletonBlock key={item} className="h-44" />)}
            </div>
          ) : market?.companies.length ? (
            <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
              <div className="grid gap-4 md:grid-cols-2">
                {market.companies.map((company, index) => (
                  <CompanyCard key={company.company} company={company} active={selectedCompany?.company === company.company} index={index} onClick={() => setSelectedCompany(company)} />
                ))}
              </div>
              <CompanyDetail company={selectedCompany ?? market.companies[0]} role={comparison.target_role} />
            </div>
          ) : (
            <EmptyState icon={Building2} title="No company map yet" body="Run a comparison first so SkillLens can map your skills to hiring companies." />
          )}
        </Panel>
      </motion.div>
    </Page>
  );
}

function weightedSkill(skill: ComparedSkill, multiplier: number) {
  return { name: skill.name, weight: Math.min(1.5, Math.max(0.2, skill.confidence * multiplier)) };
}

function CompanyCard({ company, active, index, onClick }: { company: MarketCompanyRoadmap; active: boolean; index: number; onClick: () => void }) {
  return (
    <motion.button
      type="button"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      onClick={onClick}
      className={`rounded-lg border p-5 text-left transition-all ${active ? "border-accent bg-emerald-50/40 shadow-soft" : "border-line bg-white hover:border-accent/40 hover:bg-slate-50"}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-lg font-bold text-ink">{company.company}</p>
          <p className="mt-1 text-xs font-bold uppercase tracking-widest text-muted">{company.salary}</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-black text-ink">{company.fit}%</p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-muted">Fit</p>
        </div>
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        {company.process.slice(0, 4).map((step) => (
          <span key={step} className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-slate-600">
            {step}
          </span>
        ))}
      </div>
      <div className="mt-5 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-accent">
        View prep plan
        <ChevronRight size={14} />
      </div>
    </motion.button>
  );
}

function CompanyDetail({ company, role }: { company: MarketCompanyRoadmap; role: string }) {
  const applyLink = company.apply_link || `https://www.google.com/search?q=${encodeURIComponent(`${company.company} ${role} jobs`)}`;

  return (
    <aside className="rounded-lg border border-line bg-slate-50/60 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-accent">Company Plan</p>
          <h3 className="mt-2 text-2xl font-bold text-ink">{company.company}</h3>
          <p className="mt-2 text-sm font-semibold text-muted">{company.salary}</p>
        </div>
        <div className="rounded-lg bg-white px-4 py-3 text-center shadow-sm ring-1 ring-line">
          <p className="text-2xl font-black text-ink">{company.fit}%</p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-muted">Fit</p>
        </div>
      </div>
      <a
        href={applyLink}
        target="_blank"
        rel="noreferrer"
        className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-ink px-5 text-sm font-bold text-white shadow-soft transition-all hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-xl active:translate-y-0 sm:w-auto"
      >
        <Send size={16} />
        Apply Now
        <ExternalLink size={14} />
      </a>

      <DetailSection title="Skill gaps" icon={<Target size={16} />}>
        <div className="flex flex-wrap gap-2">
          {company.gaps.length ? company.gaps.map((gap) => <StatusPill key={gap} tone="warn">{gap}</StatusPill>) : <StatusPill tone="good">No major gaps</StatusPill>}
        </div>
      </DetailSection>

      <DetailSection title="2-3 week preparation roadmap">
        <ol className="space-y-3">
          {company.prep_plan.map((item, index) => (
            <li key={item} className="flex gap-3 text-sm font-medium leading-6 text-muted">
              <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-white text-xs font-bold text-accent ring-1 ring-line">{index + 1}</span>
              {item}
            </li>
          ))}
        </ol>
      </DetailSection>

      <DetailSection title="Likely question themes">
        <div className="flex flex-wrap gap-2">
          {company.question_themes.map((theme) => (
            <a
              key={theme}
              href={`https://www.youtube.com/results?search_query=${encodeURIComponent(`${theme} interview questions`)}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700 transition-all hover:-translate-y-0.5 hover:border-blue-300 hover:bg-white hover:shadow-sm"
            >
              {theme}
              <ExternalLink size={12} />
            </a>
          ))}
        </div>
      </DetailSection>
    </aside>
  );
}

function DetailSection({ title, icon, children }: { title: string; icon?: ReactNode; children: ReactNode }) {
  return (
    <section className="mt-7 border-t border-line pt-6">
      <div className="mb-4 flex items-center gap-2">
        {icon}
        <p className="text-xs font-bold uppercase tracking-widest text-muted">{title}</p>
      </div>
      {children}
    </section>
  );
}
